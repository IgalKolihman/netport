import random
import string
from pathlib import Path

import pytest


def random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


@pytest.mark.parametrize(
    "path", [p.absolute() for p in list(Path(".").rglob("*.[tT][xX][tT]"))]
)
def test_path_exist(netport, path):
    response = netport.get("/fs/is_path_exist", params={"path": path})

    assert response.status_code == 200
    assert response.json() is True, f"The server didn't find the path {path}"


@pytest.mark.parametrize(
    "path", [p.absolute() for p in list(Path(".").rglob("*.py"))[:10]]
)
def test_reserve_path(netport, path):
    response = netport.get("/fs/reserve_path", params={"path": path})

    assert response.status_code == 200
    assert response.json() is True, f"The server didn't reserve the path {path}"


@pytest.mark.parametrize(
    "path", [random_string(length) for length in range(10, 100, 5)]
)
def test_reserve_not_existing_path(netport, path):
    response = netport.get("/fs/reserve_path", params={"path": path})

    assert response.status_code == 200
    assert (
            response.json() is False
    ), f"The server reserved a path that it didn't suppose to: '{path}'"
