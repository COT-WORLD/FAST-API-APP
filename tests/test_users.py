from fastapi.testclient import TestClient
import jwt
import pytest
from app.schemas import UserSchema, Token
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.database import settings


def test_root(client: TestClient):
    res = client.get("/")
    assert res.json().get(
        'message') == "Hello World successfully deployed on Render via CICD pipeline(Github Actions)"


def test_create_user(session: Session, client: TestClient):
    res = client.post("/users/", json={
        "email": "john@gmail.com",
        "password": "password123"
    })
    new_user = UserSchema(**res.json())
    assert new_user.email == "john@gmail.com"
    assert res.status_code == 201


@pytest.mark.parametrize("email, password, status_code", [
    ("wrongemail@gmail.com", "password123", 403),
    ("james@gmail.com", "wrongpassword", 403),
    ("wrongemail@gmail.com", "wrongpassword", 403),
    (None, "password123", 403),
    ("wrongemail@gmail.com", None, 403)
])
def test_login_user(session: Session, client: TestClient, email, password, status_code):
    res = client.post("/login", data={
        "username": email,
        "password": password
    })
    if res.status_code != 200:
        assert res.json().get("detail") == "Invalid Credentials!"
    assert res.status_code == status_code


def test_login_user_token_check(client: TestClient, test_user):
    res = client.post("/login", data={
        "username": "james@gmail.com",
        "password": "password123"
    })
    login_res = Token(**res.json())
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200
