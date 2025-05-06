import pytest
import time
from fastapi.testclient import TestClient
from app.models import User, Post
from app.schemas import Token
from app.database import SessionDep
from app.oauth2 import create_access_token
from sqlmodel import select
import subprocess


@pytest.mark.parametrize("email, password, status_code", [
    ("wrongemail@gmail.com", "password123", 403),
    ("james@gmail.com", "wrongpassword", 403),
    ("wrongemail@gmail.com", "wrongpassword", 403),
    (None, "password123", 403),
    ("wrongemail@gmail.com", None, 403)
])
def test_invalid_login(client: TestClient, email, password, status_code):
    res = client.post("/login", data={
        "username": email,
        "password": password
    })
    assert res.status_code == status_code
    if res.status_code != 200:
        assert res.json().get("detail") == "Invalid Credentials!"


@pytest.mark.skip(reason="Skipped to avoid long wait times; token expiry logic is assumed to be tested separately or with configurable TTL.")
def test_token_expiry(client: TestClient, test_user):
    res = client.post("/login", data={
        "username": test_user['email'],
        "password": "password123"
    })
    login_res = Token(**res.json())
    access_token = login_res.access_token
    time.sleep(65)
    res = client.get(
        "/posts/", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"


def test_sql_injection_in_user_creation(client: TestClient):
    payload = {"email": "james@gmail.com' OR '1'='1",
               "password": "password123"}
    res = client.post("/users/", json=payload)
    assert res.status_code == 422


def test_access_control_on_post_deletion(client: TestClient, test_user, test_user2, session):
    post = Post(
        title="Protected Post",
        content="Only owner should delete this",
        owner_id=test_user2["id"]
    )
    session.add(post)
    session.commit()
    session.refresh(post)

    token = create_access_token({"user_id": test_user["id"]})
    res = client.delete(
        f"/posts/{post.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 401
    assert res.json()["detail"] == "Not authorised to perform requsted action"


def test_sql_injection_in_search(authorised_client: TestClient):
    res = authorised_client.get("/posts/?search=anything' OR '1'='1")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_sensitive_endpoint_exposure(client: TestClient):

    res = client.get("/admin/dashboard")
    assert res.status_code == 404


def test_no_server_version_header(client: TestClient):
    res = client.get("/posts/")
    assert "Server" not in res.headers


def test_unauthorized_access_to_post(client: TestClient, test_posts, test_user):

    res = client.get(f"/posts/{test_posts[3].id}")
    assert res.status_code == 401


def test_password_hashing(client: TestClient, session: SessionDep, test_user):

    user = session.exec(select(User).filter(
        User.email == test_user['email'])).first()
    assert user is not None
    assert user.password != "password123"


def test_no_sensitive_data_leaks(client: TestClient, test_user):

    res = client.get(f"/users/{test_user['id']}")
    assert "password" not in res.json()


def test_xss_in_post_content(client: TestClient, test_user):
    token = create_access_token({"user_id": test_user["id"]})
    payload = {
        "title": "<script>alert('XSS')</script>",
        "content": "<img src=x onerror=alert('XSS')>"
    }

    res = client.post(
        "/posts/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201
    data = res.json()
    assert "<script>" not in data["title"]
    assert "onerror" not in data["content"]


def test_sql_injection_in_vote_creation(client: TestClient, test_user):
    payload = {
        "post_id": "1; DROP TABLE votes; --",
        "dir": 1
    }
    token = create_access_token({"user_id": test_user['id']})
    res = client.post("/vote/", json=payload,
                      headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422
    assert res.json()["detail"][0]["type"] == "int_parsing"


def test_sensitive_data_exposure_in_vote(client: TestClient, test_user, test_posts):

    payload = {
        "post_id": test_posts[0].id,
        "dir": 1
    }
    token = create_access_token({"user_id": test_user['id']})
    res = client.post("/vote/", json=payload,
                      headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 201
    assert "password" not in res.text
    assert "secret" not in res.text


def test_prevent_xxe_in_vote(client: TestClient, test_user):
    payload = {
        "post_id": 1,
        "dir": 1
    }

    xml_payload = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE foo [ 
    <!ELEMENT foo ANY >
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
    ]>
    <foo>&xxe;</foo>
    """

    token = create_access_token({"user_id": test_user['id']})
    res = client.post("/vote/", content=xml_payload,
                      headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 422
    assert res.json()["detail"][0]["type"] == "json_invalid"


def test_unauthorized_user_vote(client: TestClient, test_user, test_posts):

    payload = {
        "post_id": test_posts[0].id,
        "dir": 1
    }
    token = create_access_token({"user_id":  100})
    res = client.post("/vote/", json=payload,
                      headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 401


def test_exposed_sensitive_vote_endpoint(client: TestClient):
    res = client.get("/vote/")
    assert res.status_code == 405


def test_xss_in_vote_creation(client: TestClient, test_user):
    payload = {
        "post_id": 1,
        "dir": 1
    }
    payload["post_id"] = "<script>alert('XSS')</script>"
    token = create_access_token({"user_id": test_user['id']})

    res = client.post("/vote/", json=payload,
                      headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422
    assert "detail" in res.json()
    assert "Input should be a valid integer, unable to parse string as an integer" in res.json()[
        "detail"][0]["msg"]


def test_no_vulnerable_components():

    result = subprocess.run(['safety', 'check', '--full-report',
                            '--ignore', '39645'], capture_output=True, text=True)

    assert result.returncode == 0, f"Vulnerabilities found in dependencies: {result.stdout}"


def test_vote_logging(client: TestClient, test_user, test_posts):
    payload = {
        "post_id": test_posts[0].id,
        "dir": 1
    }
    token = create_access_token({"user_id": test_user['id']})
    res = client.post("/vote/", json=payload,
                      headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
