import pytest
from fastapi.testclient import TestClient

from netport.netport import app


@pytest.fixture()
def netport():
    client = TestClient(app)
    yield client

    # Release all the resources that the test reserved during the execution
    response = client.get("/db/release_client")
    assert (
        response.status_code == 200
    ), "Something went wrong while releasing the client"
