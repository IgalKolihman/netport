import os
import json

import pytest
from fastapi.testclient import TestClient

from netport.netport import run_app

all_db = pytest.mark.parametrize("netport", (True, False), indirect=True)


def pytest_addoption(parser):
    parser.addini("redis", "Redis database address, port and db to use for testing.")


def pop_env_key(env_key: str):
    """Pop environment variable from the memory without raising KeyError exception."""
    try:
        os.environ.pop(env_key)

    except KeyError:
        pass


@pytest.fixture()
def netport(pytestconfig, request):
    """Netport app fixture.

    request.param should be a boolean that indicates whether to use the redis database or the local.
    If the value it True - use redis, else use local database.

    Args:
        pytestconfig: global pytest configuration.
        request: pytest request fixture.

    Returns:
        TestClient. Netport's fastapi client.
    """
    if request.param:
        redis_conn = json.loads(pytestconfig.getini("redis").replace("'", '"'))
        os.environ["NETPORT_REDIS_HOST"] = redis_conn["host"]
        os.environ["NETPORT_REDIS_PORT"] = redis_conn["port"]
        os.environ["NETPORT_REDIS_DB"] = redis_conn["db"]

    try:
        client = TestClient(run_app())
        yield client

        # Release any resources that were reserved during the test
        if request.param:
            response = client.get("/db/release_client")
            assert (
                    response.status_code == 200
            ), "Something went wrong while releasing the client"

    finally:
        pop_env_key("NETPORT_REDIS_HOST")
        pop_env_key("NETPORT_REDIS_PORT")
        pop_env_key("NETPORT_REDIS_DB")
