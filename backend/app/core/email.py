"""
Email delivery via Gmail SMTP (STARTTLS).

If SMTP credentials are not configured (SMTP_USER / SMTP_PASS blank), the email
is not sent — instead the message (including any link) is logged to the console.
This keeps the signup flow fully testable in dev before real Gmail credentials
are pasted into .env.

Gmail note: SMTP_PASS must be a 16-character *App Password*
(myaccount.google.com → Security → App passwords), not the account password,
and 2-Step Verification must be enabled on the sending account.
"""
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("getfit.email")


def send_email(to: str, subject: str, html: str, text: str | None = None) -> bool:
    """
    Send an HTML email. Returns True if actually sent via SMTP, False if it was
    only logged (dev fallback). Raises only on an unexpected SMTP error when
    credentials *are* configured.
    """
    sender = settings.SMTP_FROM or settings.SMTP_USER

    if not settings.SMTP_USER or not settings.SMTP_PASS:
        logger.warning(
            "[EMAIL:dev] SMTP not configured — not sending. "
            "To: %s | Subject: %s\n%s",
            to, subject, text or html,
        )
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(text or "Please view this email in an HTML-capable client.")
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)

    logger.info("[EMAIL] Sent '%s' to %s", subject, to)
    return True


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
