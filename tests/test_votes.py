from fastapi.testclient import TestClient
import pytest

from app.models import Vote


@pytest.fixture(name="test_vote")
def test_vote(test_posts, session, test_user):
    new_vote = Vote(post_id=test_posts[3].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()


def test_create_vote_on_post(authorised_client, test_posts):
    res = authorised_client.post(
        "/vote/", json={"post_id": test_posts[0].id, "dir": 1})
    vote = res.json()
    assert res.status_code == 201
    assert vote["message"] == "Successfully added vote"


def test_vote_twice_votes(authorised_client, test_vote, test_posts, test_user):
    res = authorised_client.post(
        "/vote/", json={"post_id": test_posts[3].id, "dir": 1})
    vote = res.json()
    assert res.status_code == 409
    assert vote["detail"] == f"user {test_user["id"]} has already voted on post {test_posts[3].id}"


def test_delete_vote_on_post(authorised_client, test_posts):
    res = authorised_client.post(
        "/vote/", json={"post_id": test_posts[0].id, "dir": 0})
    vote = res.json()
    assert res.status_code == 404
    assert vote["detail"] == "Vote not found"


def test_delete_vote_not_exist(authorised_client, test_posts):
    res = authorised_client.post(
        "/vote/", json={"post_id": test_posts[3].id, "dir": 0})
    vote = res.json()
    assert res.status_code == 404
    assert vote["detail"] == "Vote not found"


def test_vote_post_not_exist(authorised_client, test_posts):
    res = authorised_client.post("/vote/", json={"post_id": 555, "dir": 1})
    vote = res.json()
    assert res.status_code == 404
    assert vote["detail"] == "post with id: 555 doesn't exist"


def test_vote_on_post_unauthorised_user(client, test_posts):
    res = client.post("/vote/", json={"post_id": test_posts[0].id, "dir": 1})
    vote = res.json()
    assert res.status_code == 401
    assert vote["detail"] == "Not authenticated"
