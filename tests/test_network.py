import socket

import psutil
import pytest
from tests.conftest import all_db
from netport.netport import R_PORT


@all_db
@pytest.mark.repeat(10)
def test_reserve_empty_port(netport):
    response = netport.get("/networking/get_port")
    assert response.status_code == 200
    assert "port" in response.json().keys()


@all_db
@pytest.mark.repeat(10)
def test_port_is_not_in_use(netport):
    response = netport.get("/networking/get_port")
    used_port = response.json()["port"]

    response = netport.get("/networking/is_port_in_use", params={"port": used_port})
    assert response.json() is False


@all_db
def test_port_is_in_use(netport):
    test_port = 12345
    with socket.socket() as s:
        s.bind(("", test_port))
        s.listen(1)
        response = netport.get(
            "/networking/is_port_in_use", params={"port": test_port}
        )
        assert response.json() is True


@all_db
@pytest.mark.repeat(10)
def test_port_is_reserved_after_requesting_it(netport):
    response = netport.get("/networking/get_port")
    used_port = response.json()["port"]

    response = netport.get(
        "/db/is_reserved",
        params={"resource": R_PORT, "value": used_port},
    )

    assert (
            response.json() is True
    ), f"The port {used_port} wasn't reserved in the database"


@all_db
def test_get_list_of_all_available_interfaces(netport):
    interfaces_data = psutil.net_if_addrs()
    interfaces = list(interfaces_data.keys())

    response = netport.get("/networking/list_interfaces")
    assert all(interface in response.json() for interface in interfaces)
