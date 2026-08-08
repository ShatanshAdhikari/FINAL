import pytest

from app.core.database import SessionLocal
from app.core.security import create_action_token
from app.routes.auth import RESET_PASSWORD_PURPOSE, _password_stamp
from app.models.user import User

REGISTER_URL = "/auth/register"
SET_PASSWORD_URL = "/auth/set-password"
FORGOT_PASSWORD_URL = "/auth/forgot-password"
RESET_PASSWORD_URL = "/auth/reset-password"
LOGIN_URL = "/auth/login"
ME_URL = "/auth/me"

STRONG_PW = "securepass1"
NEW_PW = "brandnewpw2"


def _set_password_token(email: str) -> str:
    """Mint the set-password token the confirmation email would have contained."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None, "user was not created by register"
        return create_action_token(user.id, "set_password")
    finally:
        db.close()


def _reset_token(email: str) -> str:
    """Mint the reset token the forgot-password email would have contained."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None, "user does not exist"
        return create_action_token(
            user.id, RESET_PASSWORD_PURPOSE, extra={"pwd": _password_stamp(user)}
        )
    finally:
        db.close()


def _register_and_activate(client, email, username, password=STRONG_PW):
    """Full new-user flow: register → follow emailed link → set password (auto-login)."""
    client.post(REGISTER_URL, json={"email": email, "username": username})
    token = _set_password_token(email)
    return client.post(SET_PASSWORD_URL, json={"token": token, "password": password})


# ── Registration ──────────────────────────────────────────────────────────────

def test_register_creates_unverified_account_without_token(client):
    res = client.post(REGISTER_URL, json={"email": "test@example.com", "username": "testuser"})
    assert res.status_code == 201
    data = res.json()
    assert "access_token" not in data          # no session until password is set
    assert data["email"] == "test@example.com"
    assert data["email_sent"] is False         # SMTP not configured in tests → link logged


def test_register_duplicate_email(client):
    client.post(REGISTER_URL, json={"email": "dup@example.com", "username": "user1"})
    res = client.post(REGISTER_URL, json={"email": "dup@example.com", "username": "user2"})
    assert res.status_code == 400
    assert "Email" in res.json()["detail"]


def test_register_duplicate_username(client):
    client.post(REGISTER_URL, json={"email": "a@example.com", "username": "dupuser"})
    res = client.post(REGISTER_URL, json={"email": "b@example.com", "username": "dupuser"})
    assert res.status_code == 400
    assert "Username" in res.json()["detail"]


# ── Set password (emailed link) ───────────────────────────────────────────────

def test_set_password_activates_and_logs_in(client):
    res = _register_and_activate(client, "setpw@example.com", "setpwuser")
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["is_verified"] is True


def test_set_password_rejects_weak_password(client):
    client.post(REGISTER_URL, json={"email": "weak@example.com", "username": "weakuser"})
    token = _set_password_token("weak@example.com")
    res = client.post(SET_PASSWORD_URL, json={"token": token, "password": "short"})
    assert res.status_code == 422


def test_set_password_rejects_invalid_token(client):
    res = client.post(SET_PASSWORD_URL, json={"token": "not-a-real-token", "password": STRONG_PW})
    assert res.status_code == 400


# ── Forgot / reset password ───────────────────────────────────────────────────

def test_forgot_password_same_response_for_unknown_email(client):
    _register_and_activate(client, "known@example.com", "knownuser")
    known = client.post(FORGOT_PASSWORD_URL, json={"email": "known@example.com"})
    unknown = client.post(FORGOT_PASSWORD_URL, json={"email": "ghost@example.com"})
    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json()          # no account enumeration


def test_reset_password_changes_password_and_logs_in(client):
    _register_and_activate(client, "reset@example.com", "resetuser")
    client.post(FORGOT_PASSWORD_URL, json={"email": "reset@example.com"})

    res = client.post(RESET_PASSWORD_URL, json={"token": _reset_token("reset@example.com"), "password": NEW_PW})
    assert res.status_code == 200
    assert "access_token" in res.json()

    assert client.post(LOGIN_URL, data={"username": "reset@example.com", "password": NEW_PW}).status_code == 200
    assert client.post(LOGIN_URL, data={"username": "reset@example.com", "password": STRONG_PW}).status_code == 401


def test_reset_token_is_single_use(client):
    _register_and_activate(client, "once@example.com", "onceuser")
    token = _reset_token("once@example.com")

    assert client.post(RESET_PASSWORD_URL, json={"token": token, "password": NEW_PW}).status_code == 200
    replay = client.post(RESET_PASSWORD_URL, json={"token": token, "password": "thirdpassword3"})
    assert replay.status_code == 400
    assert "already been used" in replay.json()["detail"]


def test_reset_rejects_set_password_token(client):
    """A token minted for a different purpose must not be accepted here."""
    client.post(REGISTER_URL, json={"email": "purpose@example.com", "username": "purposeuser"})
    token = _set_password_token("purpose@example.com")
    res = client.post(RESET_PASSWORD_URL, json={"token": token, "password": NEW_PW})
    assert res.status_code == 400


def test_reset_rejects_weak_password(client):
    _register_and_activate(client, "weakreset@example.com", "weakresetuser")
    res = client.post(RESET_PASSWORD_URL, json={"token": _reset_token("weakreset@example.com"), "password": "short"})
    assert res.status_code == 422


def test_reset_rejects_invalid_token(client):
    res = client.post(RESET_PASSWORD_URL, json={"token": "not-a-real-token", "password": NEW_PW})
    assert res.status_code == 400


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_after_activation_with_email(client):
    _register_and_activate(client, "login@example.com", "loginuser")
    res = client.post(LOGIN_URL, data={"username": "login@example.com", "password": STRONG_PW})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_after_activation_with_username(client):
    _register_and_activate(client, "uname@example.com", "unameuser")
    res = client.post(LOGIN_URL, data={"username": "unameuser", "password": STRONG_PW})
    assert res.status_code == 200


def test_login_blocked_before_verification(client):
    client.post(REGISTER_URL, json={"email": "unverified@example.com", "username": "unverifieduser"})
    res = client.post(LOGIN_URL, data={"username": "unverified@example.com", "password": STRONG_PW})
    assert res.status_code == 403


def test_login_wrong_password(client):
    _register_and_activate(client, "wrong@example.com", "wronguser")
    res = client.post(LOGIN_URL, data={"username": "wrong@example.com", "password": "incorrect9"})
    assert res.status_code == 401


def test_login_nonexistent_user(client):
    res = client.post(LOGIN_URL, data={"username": "nobody@example.com", "password": STRONG_PW})
    assert res.status_code == 401


# ── /auth/me ──────────────────────────────────────────────────────────────────

def test_get_me_authenticated(client):
    activate = _register_and_activate(client, "me@example.com", "meuser")
    token = activate.json()["access_token"]
    res = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"


def test_get_me_unauthenticated(client):
    res = client.get(ME_URL)
    assert res.status_code == 401


# ── Google SSO ────────────────────────────────────────────────────────────────

def test_google_login_not_configured(client):
    # GOOGLE_CLIENT_ID is unset in the test env → endpoint reports unavailable.
    res = client.post("/auth/google", json={"credential": "anything"})
    assert res.status_code == 503
