"""
Email delivery. Three backends, chosen at runtime:

  1. SendGrid (HTTPS API) — used when SENDGRID_API_KEY is set. Top priority:
     works on hosts that block SMTP (like Render) *and* supports single-sender
     verification, so it can email arbitrary recipients without a verified
     domain.
  2. Resend (HTTPS API) — used when RESEND_API_KEY is set. Also HTTPS-only, but
     needs a verified domain to reach recipients other than the account owner.
  3. Gmail SMTP (STARTTLS) — fallback for local dev when only SMTP creds are
     set. SMTP_PASS must be a 16-char Gmail *App Password* (not the account
     password) with 2-Step Verification enabled.

If none is configured the message (including any link) is logged to the
console so the signup flow stays testable in dev.
"""
import logging
import re
import smtplib
from email.message import EmailMessage

import requests

from app.core.config import settings

logger = logging.getLogger("getfit.email")

RESEND_ENDPOINT = "https://api.resend.com/emails"
SENDGRID_ENDPOINT = "https://api.sendgrid.com/v3/mail/send"


def _parse_sender(raw: str) -> dict:
    """Parse 'Name <email>' or bare 'email' into SendGrid's {email[, name]}."""
    match = re.match(r"^\s*(.*?)\s*<\s*(.+?)\s*>\s*$", raw)
    if match:
        name, addr = match.group(1), match.group(2)
        return {"email": addr, "name": name} if name else {"email": addr}
    return {"email": raw.strip()}


def _send_via_sendgrid(to: str, subject: str, html: str, text: str | None) -> bool:
    """Send through the SendGrid HTTP API. Returns False (never raises) on error."""
    try:
        resp = requests.post(
            SENDGRID_ENDPOINT,
            headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}"},
            json={
                "personalizations": [{"to": [{"email": to}]}],
                "from": _parse_sender(settings.SENDGRID_FROM),
                "subject": subject,
                "content": [
                    {"type": "text/plain",
                     "value": text or "Please view this email in an HTML-capable client."},
                    {"type": "text/html", "value": html},
                ],
            },
            timeout=20,
        )
    except requests.RequestException:
        logger.exception("[EMAIL] SendGrid request failed for %s", to)
        return False

    if resp.status_code >= 400:
        # SendGrid returns a JSON error body — surface it for debugging.
        logger.error(
            "[EMAIL] SendGrid rejected send to %s (HTTP %s): %s",
            to, resp.status_code, resp.text[:500],
        )
        return False

    logger.info("[EMAIL] Sent '%s' to %s via SendGrid", subject, to)
    return True


def _send_via_resend(to: str, subject: str, html: str, text: str | None) -> bool:
    """Send through the Resend HTTP API. Returns False (never raises) on error."""
    try:
        resp = requests.post(
            RESEND_ENDPOINT,
            headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
            json={
                "from": settings.RESEND_FROM,
                "to": [to],
                "subject": subject,
                "html": html,
                "text": text or "Please view this email in an HTML-capable client.",
            },
            timeout=20,
        )
    except requests.RequestException:
        logger.exception("[EMAIL] Resend request failed for %s", to)
        return False

    if resp.status_code >= 400:
        # Resend returns a JSON error body — surface it for debugging.
        logger.error(
            "[EMAIL] Resend rejected send to %s (HTTP %s): %s",
            to, resp.status_code, resp.text[:500],
        )
        return False

    logger.info("[EMAIL] Sent '%s' to %s via Resend", subject, to)
    return True


def _send_via_smtp(to: str, subject: str, html: str, text: str | None) -> bool:
    """Send through Gmail SMTP. Returns False (never raises) on error."""
    sender = settings.SMTP_FROM or settings.SMTP_USER
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(text or "Please view this email in an HTML-capable client.")
    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
    except OSError:
        logger.exception("[EMAIL] SMTP send failed for %s", to)
        return False

    logger.info("[EMAIL] Sent '%s' to %s via SMTP", subject, to)
    return True


def send_email(to: str, subject: str, html: str, text: str | None = None) -> bool:
    """
    Send an HTML email. Returns True if actually sent, False if it errored or
    was only logged (dev fallback). Never raises.

    Backend priority: SendGrid (HTTPS) → Resend (HTTPS) → Gmail SMTP → dev log.
    """
    if settings.SENDGRID_API_KEY and settings.SENDGRID_FROM:
        return _send_via_sendgrid(to, subject, html, text)

    if settings.RESEND_API_KEY:
        return _send_via_resend(to, subject, html, text)

    if settings.SMTP_USER and settings.SMTP_PASS:
        return _send_via_smtp(to, subject, html, text)

    logger.warning(
        "[EMAIL:dev] No email backend configured — not sending. "
        "To: %s | Subject: %s\n%s",
        to, subject, text or html,
    )
    return False


def send_set_password_email(to: str, username: str, link: str) -> bool:
    """Send the account-confirmation / set-password email."""
    subject = "Confirm your GetFit account & set your password"
    html = f"""\
<div style="font-family:Arial,Helvetica,sans-serif;max-width:520px;margin:auto;
            border:1px solid #eee;border-radius:12px;padding:32px">
  <h2 style="color:#16a34a;margin-top:0">Welcome to GetFit, {username}! 💪</h2>
  <p>Thanks for signing up. To activate your account, confirm your email and
     set a password by clicking the button below.</p>
  <p style="text-align:center;margin:28px 0">
    <a href="{link}"
       style="background:#16a34a;color:#fff;text-decoration:none;
              padding:12px 28px;border-radius:8px;font-weight:bold;display:inline-block">
      Set my password
    </a>
  </p>
  <p style="color:#666;font-size:13px">
    Or paste this link into your browser:<br>
    <a href="{link}">{link}</a>
  </p>
  <p style="color:#999;font-size:12px;margin-top:24px">
    This link expires in 24 hours. If you didn't create a GetFit account,
    you can safely ignore this email.
  </p>
</div>"""
    text = (
        f"Welcome to GetFit, {username}!\n\n"
        f"Confirm your email and set your password here:\n{link}\n\n"
        f"This link expires in 24 hours. If you didn't sign up, ignore this email."
    )
    return send_email(to, subject, html, text)
