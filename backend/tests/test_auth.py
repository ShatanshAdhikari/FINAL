import pytest

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
ME_URL = "/auth/me"


def test_register_success(client):
    res = client.post(REGISTER_URL, json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepassword",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["username"] == "testuser"


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "username": "user1", "password": "pass"}
    client.post(REGISTER_URL, json=payload)
    res = client.post(REGISTER_URL, json={**payload, "username": "user2"})
    assert res.status_code == 400
    assert "Email" in res.json()["detail"]


def test_register_duplicate_username(client):
    client.post(REGISTER_URL, json={"email": "a@example.com", "username": "dupuser", "password": "pass"})
    res = client.post(REGISTER_URL, json={"email": "b@example.com", "username": "dupuser", "password": "pass"})
    assert res.status_code == 400
    assert "Username" in res.json()["detail"]


def test_login_with_email(client):
    client.post(REGISTER_URL, json={"email": "login@example.com", "username": "loginuser", "password": "mypassword"})
    res = client.post(LOGIN_URL, data={"username": "login@example.com", "password": "mypassword"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_with_username(client):
    client.post(REGISTER_URL, json={"email": "uname@example.com", "username": "unameuser", "password": "mypassword"})
    res = client.post(LOGIN_URL, data={"username": "unameuser", "password": "mypassword"})
    assert res.status_code == 200


def test_login_wrong_password(client):
    client.post(REGISTER_URL, json={"email": "wrong@example.com", "username": "wronguser", "password": "correct"})
    res = client.post(LOGIN_URL, data={"username": "wrong@example.com", "password": "incorrect"})
    assert res.status_code == 401


def test_login_nonexistent_user(client):
    res = client.post(LOGIN_URL, data={"username": "nobody@example.com", "password": "pass"})
    assert res.status_code == 401


def test_get_me_authenticated(client):
    client.post(REGISTER_URL, json={"email": "me@example.com", "username": "meuser", "password": "pass"})
    login = client.post(LOGIN_URL, data={"username": "me@example.com", "password": "pass"})
    token = login.json()["access_token"]
    res = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"


def test_get_me_unauthenticated(client):
    res = client.get(ME_URL)
    assert res.status_code == 401
