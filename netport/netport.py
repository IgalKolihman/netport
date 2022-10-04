import time
import socket
import datetime
import subprocess
from os.path import exists

import psutil
from redis.client import Redis
from fastapi import FastAPI, Request
from redis import exceptions as redis_errors

R_PORT = "PORT"
R_PATH = "PATH"
R_PROCESS = "PROCESS"


class Database:
    def __init__(self, host: str = "localhost", port: int = 6379):
        try:
            self._db = Redis(host=host, port=port, db=0)
            self._db.ping()

        except redis_errors.TimeoutError:
            raise TimeoutError("Couldn't connect to the Redis database")

    def is_reserved(self, resource: str, value):
        """Check if the requested resource is already reserved."""
        for client in self.get_all_clients():
            for _ in self.get_client_resources(client, resource, value):
                return True

        return False

    def reserve(self, client_ip: str, resource: str, value):
        """Reserve some resource for a client."""
        if self.is_reserved(resource, value):
            return False

        return (
                self._db.hset(
                    client_ip,
                    f"{resource}:{value}",
                    datetime.datetime.utcfromtimestamp(time.time()).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                )
                == 1
        )

    def get_client_resources(
            self, client_ip: str, resource_regex: str = "*", value_regex: str = "*"
    ):
        """Get all the client resources that match the resource regex pattern."""
        return self._db.hscan_iter(client_ip, match=f"{resource_regex}:{value_regex}")

    def release_resource(self, client_ip: str, resource: str, value):
        return self._db.hdel(client_ip, f"{resource}:{value}")

    def release_client(self, client_ip: str):
        return self._db.delete(client_ip) == 1

    def get_all_clients(self):
        return self._db.scan(cursor=0, match="*")[1]


app = FastAPI()
db = Database()
running_processes = []


def _is_port_in_use(port: int):
    """Checks if the given port is in use.

    Args:
        port (int): The port to use

    Returns:
        bool. If the port is in use.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


@app.get("/db/reserve")
def reserve(request: Request, resource: str, value):
    return db.reserve(client_ip=request.client.host, resource=resource, value=value)


@app.get("/db/is_reserved")
def is_reserved(resource: str, value: str):
    """Checks if the given port is in use.

    Args:
        resource (str): The resource type
        value (str): The value of the resource

    Returns:
        bool. If the port is in use.
    """
    return db.is_reserved(resource, value)


@app.get("/db/my_resources")
def my_resources(request: Request, resource: str):
    return db.get_client_resources(request.client.host, resource)


@app.get("/db/get_client_resources")
def get_client_resources(client_ip: str, resource: str = "*", value: str = "*"):
    return db.get_client_resources(client_ip, resource, value)


@app.get("/db/release_resource")
def release_resource(request: Request, resource: str, value):
    return db.release_resource(request.client.host, resource, value) == 1


@app.get("/db/release_client")
def release_client(request: Request):
    return db.release_client(request.client.host) == 1


@app.get("/db/get_all_clients")
def get_all_clients():
    return db.get_all_clients()


@app.get("/networking/get_port")
def get_port(request: Request, port: int = None):
    """Get an empty port.

    Opens a socket on random port, gets its port number, and closes the socket.

    This action is not atomic, so race condition is possible...
    """
    if port and not _is_port_in_use(port):
        if db.reserve(request.client.host, R_PORT, port):
            return {"port": port}

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        _, port = s.getsockname()
        if db.reserve(request.client.host, R_PORT, port):
            return {"port": port}

    return False


@app.get("/networking/is_port_in_use")
def is_port_in_use(port: int):
    """Checks if the given port is in use.

    Args:
        port (int): The port to use

    Returns:
        bool. If the port is in use.
    """
    return _is_port_in_use(port)


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


@app.get("/fs/is_path_exist")
def is_path_exist(path: str):
    return exists(path.strip())


@app.get("/fs/reserve_path")
def reserve_path(request: Request, path: str):
    if not exists(path):
        return False

    return db.reserve(request.client.host, R_PATH, path)


@app.get("/shell/execute_command")
def execute_command(command: str):
    return (
            subprocess.call(
                command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            == 0
    )


@app.get("/shell/run_process")
def run_process(request: Request, command: str):
    if db.reserve(request.client.host, R_PROCESS, command):
        process = subprocess.Popen(command.split(" "))
        running_processes.append(process)
        return process.pid

    return -1


@app.get("/shell/is_process_running")
def is_process_running(name: str):
    for proc in psutil.process_iter():
        try:
            if name.lower() in proc.name().lower():
                return proc.name()

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return False
