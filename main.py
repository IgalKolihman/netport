import socket

import psutil
from fastapi import FastAPI

app = FastAPI()


@app.get("/get_port")
def get_port():
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.bind(('localhost', 0))
    _, port = so.getsockname()
    so.close()
    return {"port": port}


@app.get("/is_port_in_use")
def is_port_in_use(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


@app.get("/is_process_running")
def is_process_running(name: str):
    for proc in psutil.process_iter():
        try:
            if name.lower() in proc.name().lower():
                return proc.name()

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return False
