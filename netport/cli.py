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
