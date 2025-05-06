import time
from fastapi.testclient import TestClient
from app.oauth2 import create_access_token


def test_performance_under_load(client: TestClient, test_user):

    token = create_access_token({"user_id": test_user["id"]})
    start_time = time.time()
    for _ in range(100):
        response = client.get(
            "/posts/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    end_time = time.time()
    duration = end_time - start_time
    assert duration < 5


def test_db_query_performance(client: TestClient, test_user):

    token = create_access_token({"user_id": test_user["id"]})
    start_time = time.time()
    res = client.get(
        "/posts/", headers={"Authorization": f"Bearer {token}"})
    elapsed_time = time.time() - start_time
    assert elapsed_time < 1
