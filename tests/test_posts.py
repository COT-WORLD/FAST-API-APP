from fastapi.testclient import TestClient
import pytest
from app.schemas import PostOut, PostSchema

def test_get_all_posts(authorised_client, test_posts):
    res = authorised_client.get("/posts/")
    def check_post_schema(post):
        return PostOut(**post)
    post_map = map(check_post_schema, res.json())
    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200

def test_unauthorised_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401

def test_get_one_post(authorised_client, test_posts):
    res = authorised_client.get(f"/posts/{test_posts[0].id}")
    post=PostOut(**res.json())
    assert res.status_code == 200
    assert post.Post.id == test_posts[0].id
    assert post.Post.title == test_posts[0].title
    assert post.Post.content == test_posts[0].content
    assert post.Post.owner_id == test_posts[0].owner_id

def test_unauthorised_user_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

def test_get_one_post_not_exist(authorised_client, test_posts):
    res = authorised_client.get("/posts/8888")
    assert res.status_code == 404


@pytest.mark.parametrize("title, content, published", [
    ("Awesome new title", "Awesome new content", True),
    ("James andrew books", "Those are motivational books", False),
    ("Python programming", "Deep dive into python world", True),
    ("Rust programming", "Deep dive into rust world", False),
])
def test_create_posts(authorised_client, test_user, test_posts,  title, content, published):
    res = authorised_client.post("/posts/", json={"title":title, "content":content, "published":published})
    created_post = PostSchema(**res.json())

    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']


def test_unauthorised_user_create_post(client, test_user, test_posts):
    res = client.post("/posts/", json={"title":"Awesome new title", "content":"Awesome new content", "published":True})    
    assert res.status_code == 401


def test_delete_post(authorised_client, test_posts):
    res = authorised_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204

def test_unauthorised_user_delete_post(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

def test_delete_other_user_post(authorised_client, test_posts):
    res = authorised_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 401

def test_delete_post_not_exist(authorised_client, test_posts):
    res = authorised_client.delete("/posts/8888")
    assert res.status_code == 404

def test_update_post(authorised_client, test_posts, test_user):
    res = authorised_client.put(f"/posts/{test_posts[0].id}", json={"title":"Awesome new title", "content":"Awesome new content", "published":True})
    updated_post = PostSchema(**res.json())    
    assert res.status_code == 200
    assert updated_post.id == test_posts[0].id
    assert updated_post.title == test_posts[0].title
    assert updated_post.content == test_posts[0].content
    assert updated_post.published == test_posts[0].published
    assert updated_post.owner_id == test_user['id']

def test_unauthorised_user_update_post(client, test_posts):
    res = client.put(f"/posts/{test_posts[0].id}", json={"title":"Updated title", "content":"Updated content", "published":True})    
    assert res.status_code == 401

def test_update_other_user_post(authorised_client, test_posts):
    res = authorised_client.put(f"/posts/{test_posts[3].id}", json={"title":"Updated title", "content":"Updated content", "published":True})
    assert res.status_code == 401

def test_update_post_not_exist(authorised_client, test_posts):
    res = authorised_client.put(f"/posts/88888", json={"title":"Updated title", "content":"Updated content", "published":True})
    assert res.status_code == 404