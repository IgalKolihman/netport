import json
import sys

import uvicorn

from netport.netport import app


def run():
    try:
        host = sys.argv[1]
    except IndexError:
        host = "0.0.0.0"

    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 80

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
