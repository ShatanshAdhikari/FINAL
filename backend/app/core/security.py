from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt as _bcrypt
from app.core.config import settings


# Accounts that have never set a password (email-pending or OAuth-only) store
# this sentinel, which is not a valid bcrypt hash and can never match.
UNUSABLE_PASSWORD = "!"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or hashed_password == UNUSABLE_PASSWORD:
        return False
    try:
        return _bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        # Malformed/placeholder hash → treat as no-match rather than 500.
        return False


def validate_password_strength(password: str) -> Optional[str]:
    """Return an error message if the password is too weak, else None."""
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not any(c.isalpha() for c in password):
        return "Password must contain at least one letter"
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number"
    return None


def get_password_hash(password: str) -> str:
    return _bcrypt.hashpw(
        password.encode("utf-8"),
        _bcrypt.gensalt(),
    ).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def create_action_token(
    user_id: int,
    purpose: str,
    minutes: Optional[int] = None,
    extra: Optional[dict] = None,
) -> str:
    """
    Signed, short-lived token for a specific out-of-band action (e.g. setting a
    password from an emailed link). The `purpose` claim prevents a token minted
    for one action — or a login JWT — from being accepted for another.

    `extra` adds further claims (e.g. the password-reset flow's single-use
    stamp); it cannot override sub/purpose/exp.
    """
    expire = datetime.utcnow() + timedelta(
        minutes=minutes if minutes is not None else settings.EMAIL_TOKEN_EXPIRE_MINUTES
    )
    to_encode = dict(extra or {})
    to_encode.update({"sub": str(user_id), "purpose": purpose, "exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_action_token_claims(token: str, purpose: str) -> Optional[dict]:
    """
    Return the full payload if the token is valid AND matches `purpose`, else
    None. Use this when the caller needs claims beyond `sub` (see
    verify_action_token for the common case).
    """
    payload = decode_token(token)
    if not payload or payload.get("purpose") != purpose:
        return None
    try:
        int(payload.get("sub"))
    except (TypeError, ValueError):
        return None
    return payload


def verify_action_token(token: str, purpose: str) -> Optional[int]:
    """Return the user id if the token is valid AND matches `purpose`, else None."""
    payload = verify_action_token_claims(token, purpose)
    return int(payload["sub"]) if payload else None
