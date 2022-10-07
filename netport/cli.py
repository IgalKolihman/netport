import json
import os
import sys

import uvicorn

from netport.netport import app

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 80


def run():
    host = os.environ.get("NETPORT_HOST", DEFAULT_HOST)
    port = int(os.environ.get("NETPORT_PORT", DEFAULT_PORT))

    uvicorn.run(app, host=host, port=port)


def generate_open_api_scheme():
    try:
        scheme_path = sys.argv[1]

    except IndexError:
        scheme_path = "netport_openapi.json"

    scheme = app.openapi()
    with open(scheme_path, "w") as scheme_file:
        json.dump(scheme, scheme_file)

    print(f"The Netport scheme was exported to {scheme_path}")
