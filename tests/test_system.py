import re
import uuid
import socket
import platform

import psutil
from tests.conftest import all_db


@all_db
def test_get_system_info(netport):
    system_data = {
        "platform": platform.system(),
        "platform-release": platform.release(),
        "platform-version": platform.version(),
        "architecture": platform.machine(),
        "hostname": socket.gethostname(),
        "ip-address": socket.gethostbyname(socket.gethostname()),
        "mac-address": ":".join(re.findall("..", "%012x" % uuid.getnode())),
        "processor": platform.processor(),
        "ram": str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB",
    }

    assert (
        system_data == netport.get("/system/get_system_info").json()["data"]
    ), "Returned wrong values for the system info"
