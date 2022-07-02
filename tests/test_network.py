import socket

import psutil
import pytest
from src.butler import R_PORT


@pytest.mark.repeat(25)
def test_reserve_empty_port(butler):
    response = butler.get("/networking/get_port")
    assert response.status_code == 200
    assert "port" in response.json().keys()


@pytest.mark.repeat(25)
def test_port_is_not_in_use(butler):
    response = butler.get("/networking/get_port")
    used_port = response.json()["port"]

    response = butler.get(f"/networking/is_port_in_use", params={"port": used_port})
    assert response.json() is False


def test_port_is_in_use(butler):
    test_port = 12345
    with socket.socket() as s:
        s.bind(('', test_port))
        s.listen(1)
        response = butler.get(f"/networking/is_port_in_use", params={"port": test_port})
        assert response.json() is True


@pytest.mark.repeat(25)
def test_port_is_reserved_after_requesting_it(butler):
    response = butler.get("/networking/get_port")
    used_port = response.json()["port"]

    response = butler.get(
        f"/db/is_reserved",
        params={"resource": R_PORT, "value": used_port},
    )

    assert response.json() is True, f"The port {used_port} wasn't reserved in the database"


def test_get_list_of_all_available_interfaces(butler):
    interfaces_data = psutil.net_if_addrs()
    interfaces = list(interfaces_data.keys())

    response = butler.get("/networking/list_interfaces")
    assert all(interface in response.json() for interface in interfaces)
