import pytest
from sqlmodel import SQLModel, select
from app.main import app
from app.database import settings, get_session
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.models import Post
from app.oauth2 import create_access_token


@pytest.fixture(name="session", scope="function")
def session_fixture():
    engine = create_engine(settings.test_database_url)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user(client):
    res = client.post("/users/", json={
        "email": "james@gmail.com",
        "password": "password123"
    })
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = "password123"
    return new_user

@pytest.fixture(name="test_user2")
def test_user2(client):
    res = client.post("/users/", json={
        "email": "ann@gmail.com",
        "password": "password123"
    })
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = "password123"
    return new_user

@pytest.fixture(name="token")
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})

@pytest.fixture(name="authorised_client")
def authorised_client(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture(name="test_posts")
def test_posts(test_user, test_user2, session):
    post_data = [{
        "title": "First title",
        "content": "First Content",
        "owner_id": test_user["id"]
    }, {
        "title": "Second title",
        "content": "Second Content",
        "owner_id": test_user["id"]
    }, {
        "title": "Third title",
        "content": "Third Content",
        "owner_id": test_user["id"]
    },
    {
        "title": "Four title",
        "content": "Four Content",
        "owner_id": test_user2["id"]
    }]

    def create_post_model(post):
        return Post(**post)

    post_map = map(create_post_model, post_data)

    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    posts=session.exec(select(Post)).all()
    return posts
