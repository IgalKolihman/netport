import random
import string
from pathlib import Path

import pytest

from tests.conftest import all_db


def random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


@all_db
def test_path_exist(netport):
    path = Path(".").parent.resolve()
    response = netport.get("/fs/is_path_exist", params={"path": path})

    assert response.status_code == 200
    assert response.json()["data"] is True, f"The server didn't find the path {path}"


@all_db
@pytest.mark.parametrize("path", [p.absolute() for p in list(Path(".").rglob("*.py"))[:10]])
def test_reserve_path(netport, path):
    response = netport.get("/fs/reserve_path", params={"path": path})

    assert response.status_code == 200
    assert response.json()["data"] is True, f"The server didn't reserve the path {path}"


@all_db
@pytest.mark.parametrize("path", [random_string(length) for length in [10, 100, 5]])
def test_reserve_not_existing_path(netport, path):
    response = netport.get("/fs/reserve_path", params={"path": path})

    assert response.status_code == 200
    assert response.json()["data"] is False, f"The server reserved a path that it didn't suppose to: '{path}'"
