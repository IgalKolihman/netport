import socket
import subprocess
from os.path import exists

import psutil
from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/networking/get_port")
def get_port():
    """Get an empty port.

    Opens a socket on random port, gets its port number, and closes the socket.

    This action is not atomic, so race condition is possible...
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        _, port = s.getsockname()
        return {"port": port}


@app.get("/networking/is_port_in_use")
def is_port_in_use(port: int):
    """Checks if the given port is in use.

    Args:
        port (int): The port to use

    Returns:
        bool. If the port is in use.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


@app.get("/networking/whats_my_ip")
def whats_my_ip(request: Request):
    """Example of how to get clients ip.

    will be used for locking stuff for each user.
    """
    return request.client.host


@app.get("/networking/list_interfaces")
def list_interfaces():
    """List all open network interfaces.

    Returns:
        list. Network interfaces.
    """
    interfaces = psutil.net_if_addrs()
    return list(interfaces.keys())


@app.get("/fs/is_exists")
def is_exists(path: str):
    return exists(path.strip())


@app.get("/fs/is_exists")
def is_exists(path: str):
    return exists(path.strip())


@app.get("/fs/is_process_running")
def is_process_running(name: str):
    for proc in psutil.process_iter():
        try:
            if name.lower() in proc.name().lower():
                return proc.name()

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return False


@app.get("/shell/execute_command")
def execute_command(command: str):
    return (
        subprocess.call(
            command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        == 0
    )
