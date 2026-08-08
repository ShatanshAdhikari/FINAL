import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    create_action_token,
    verify_action_token,
    verify_action_token_claims,
    validate_password_strength,
    UNUSABLE_PASSWORD,
)
from app.core.email import send_set_password_email, send_password_reset_email
from app.models.user import User

SET_PASSWORD_PURPOSE = "set_password"
RESET_PASSWORD_PURPOSE = "reset_password"

# Reset links are far more sensitive than signup links (they take over a live
# account), so they live much shorter than EMAIL_TOKEN_EXPIRE_MINUTES.
RESET_TOKEN_EXPIRE_MINUTES = 60

logger = logging.getLogger("getfit.auth")


def _build_set_password_link(token: str) -> str:
    return f"{settings.FRONTEND_URL.rstrip('/')}/set-password?token={token}"


def _build_reset_password_link(token: str) -> str:
    return f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={token}"

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _full_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_admin": user.is_admin,
        "is_super_admin": user.is_super_admin,
        "is_verified": user.is_verified,
        "age": user.age,
        "gender": user.gender,
        "weight": user.weight,
        "height": user.height,
        "fitness_level": user.fitness_level,
        "goal": user.goal,
        "activity_level": user.activity_level,
        "workout_frequency": user.workout_frequency,
        "equipment": user.equipment,
        "allergies": user.allergies,
        "diseases": user.diseases,
    }


class UserRegister(BaseModel):
    email: EmailStr
    username: str


class SetPasswordRequest(BaseModel):
    token: str
    password: str


class ResendRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class GoogleAuthRequest(BaseModel):
    credential: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload.get("sub") or 0)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    return user


def _send_confirmation(user: User) -> bool:
    """
    Mint a set-password token and email the confirmation link.

    Never raises: a mail-server failure must not fail account creation. Returns
    True if the email was actually sent, False if it was skipped or errored
    (the user can request a fresh link via /auth/resend-verification).
    """
    try:
        token = create_action_token(user.id, SET_PASSWORD_PURPOSE)
        link = _build_set_password_link(token)
        return send_set_password_email(user.email, user.username, link)
    except Exception:
        logger.exception("Failed to send confirmation email to %s", user.email)
        return False


def _password_stamp(user: User) -> int:
    """
    The account's current password "version" — microseconds since the epoch of
    the last password change, 0 if it has never changed. Reset tokens carry this
    value so a link is rejected once the password moves (i.e. after first use).
    """
    changed = user.password_changed_at
    if not changed:
        return 0
    if changed.tzinfo is None:
        changed = changed.replace(tzinfo=timezone.utc)   # SQLite reads back naive UTC
    return int(changed.timestamp() * 1_000_000)


def _send_reset(user: User) -> bool:
    """
    Mint a reset token bound to the current password stamp and email the link.
    Never raises — a mail failure must not leak which addresses exist.
    """
    try:
        token = create_action_token(
            user.id,
            RESET_PASSWORD_PURPOSE,
            minutes=RESET_TOKEN_EXPIRE_MINUTES,
            extra={"pwd": _password_stamp(user)},
        )
        return send_password_reset_email(
            user.email, user.username, _build_reset_password_link(token),
            RESET_TOKEN_EXPIRE_MINUTES,
        )
    except Exception:
        logger.exception("Failed to send password-reset email to %s", user.email)
        return False


@router.post("/register", status_code=201)
@limiter.limit("10/minute")
def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    """
    Create an unverified account (no password yet) and email a confirmation link
    the user follows to set their password. No session token is issued here —
    the account is unusable until the link is used.
    """
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=UNUSABLE_PASSWORD,   # set later via the emailed link
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    sent = _send_confirmation(user)
    return {
        "message": "Account created. Check your email for a link to set your password.",
        "email": user.email,
        "email_sent": sent,   # False in dev when SMTP isn't configured (link is logged)
    }


@router.post("/set-password", response_model=Token)
@limiter.limit("10/minute")
def set_password(request: Request, data: SetPasswordRequest, db: Session = Depends(get_db)):
    """Consume a set-password token, set the password, verify the account, and log in."""
    user_id = verify_action_token(data.token, SET_PASSWORD_PURPOSE)
    if not user_id:
        raise HTTPException(status_code=400, detail="This link is invalid or has expired")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Account no longer exists")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    err = validate_password_strength(data.password)
    if err:
        raise HTTPException(status_code=422, detail=err)

    user.hashed_password = get_password_hash(data.password)
    user.is_verified = True
    user.password_changed_at = datetime.now(timezone.utc)   # invalidates any outstanding reset link
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": _full_user(user)}


@router.post("/resend-verification")
@limiter.limit("5/minute")
def resend_verification(request: Request, data: ResendRequest, db: Session = Depends(get_db)):
    """Re-send the confirmation link. Always returns the same message (no account enumeration)."""
    user = db.query(User).filter(User.email == data.email).first()
    if user and not user.is_verified and user.is_active:
        _send_confirmation(user)
    return {"message": "If that email needs confirmation, a new link has been sent."}


@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(request: Request, data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Email a password-reset link. Always returns the same message and status
    whether or not the address exists, so this cannot be used to enumerate
    accounts. Deactivated accounts are silently skipped.
    """
    user = db.query(User).filter(User.email == data.email).first()
    if user and user.is_active:
        if user.is_verified:
            _send_reset(user)
        else:
            # Never confirmed their email — the useful link is the original
            # activation one, not a reset.
            _send_confirmation(user)
    return {"message": "If an account exists for that email, a reset link has been sent."}


@router.post("/reset-password", response_model=Token)
@limiter.limit("10/minute")
def reset_password(request: Request, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Consume a reset token, set the new password, and log the user in."""
    payload = verify_action_token_claims(data.token, RESET_PASSWORD_PURPOSE)
    if not payload:
        raise HTTPException(status_code=400, detail="This link is invalid or has expired")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=400, detail="Account no longer exists")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    # Single-use: the stamp baked into the link must still match the account's
    # current one. Any password change since the link was minted breaks the tie.
    if payload.get("pwd") != _password_stamp(user):
        raise HTTPException(status_code=400, detail="This link has already been used")

    err = validate_password_strength(data.password)
    if err:
        raise HTTPException(status_code=422, detail=err)

    user.hashed_password = get_password_hash(data.password)
    user.is_verified = True
    user.password_changed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": _full_user(user)}


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    # Check verification before the password so a pending user gets a clear message
    # (their placeholder hash would otherwise just fail as "invalid credentials").
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please confirm your email and set your password using the link we sent.",
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _full_user(user),
    }


def _unique_username(db: Session, base: str) -> str:
    """Derive a unique username from an email local-part or name."""
    candidate = "".join(c for c in base.lower() if c.isalnum()) or "user"
    candidate = candidate[:20]
    if not db.query(User).filter(User.username == candidate).first():
        return candidate
    i = 1
    while db.query(User).filter(User.username == f"{candidate}{i}").first():
        i += 1
    return f"{candidate}{i}"


@router.post("/google", response_model=Token)
@limiter.limit("10/minute")
def google_login(request: Request, data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Verify a Google ID token (credential from Google Identity Services), then
    upsert the matching user and issue our own JWT. Existing accounts are linked
    by email; new ones are created already-verified (Google vouches for the email).
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google sign-in is not configured on the server")

    import httpx
    try:
        resp = httpx.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": data.credential},
            timeout=10,
        )
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Could not reach Google to verify sign-in")
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google credential")

    info = resp.json()
    if info.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Google credential was issued for a different app")
    if str(info.get("email_verified")).lower() != "true":
        raise HTTPException(status_code=401, detail="Google account email is not verified")

    email = info.get("email")
    sub = info.get("sub")
    if not email or not sub:
        raise HTTPException(status_code=401, detail="Google credential missing email")

    # Match by Google subject first, then by email (link an existing password account).
    user = db.query(User).filter(User.google_sub == sub).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()

    if user:
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")
        # Link Google to this account if not already linked.
        if not user.google_sub:
            user.google_sub = sub
            user.oauth_provider = user.oauth_provider or "google"
        user.is_verified = True
    else:
        user = User(
            email=email,
            username=_unique_username(db, info.get("name") or email.split("@")[0]),
            hashed_password=UNUSABLE_PASSWORD,   # Google-only account; no password login
            is_verified=True,
            oauth_provider="google",
            google_sub=sub,
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": _full_user(user)}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return _full_user(current_user)
