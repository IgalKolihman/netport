import pytest
from fastapi.testclient import TestClient
from redis.client import Redis

from src.butler import app


@pytest.fixture()
def butler():
    client = TestClient(app)
    yield client

    # Release all the resources that the test reserved during the execution
    response = client.get("/db/release_client")
    assert (
        response.status_code == 200
    ), "Something went wrong while releasing the client"
