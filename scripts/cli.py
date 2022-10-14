"""Running netport from the cli

Usage:
    netport -h | --help
    netport -g [<path>]
    netport [-H <host>] [-p <port>] [--redis=<redis-address>]

Options:
  -h --help             Show this screen.
  --redis=<redis-address>   Address and port to connect to the redis DB.
                        The correct format is: "<ip addr>:<port>:<db>"
  -H --host             IP address to bind the app to [default: 0.0.0.0].
  -p --port             Port to bind the app to [default: 80].
  -g                    Generate netport openapi scheme in a json file.

Examples:
    netport -H 127.0.0.1 -p 1234 --redis=192.168.1.125:6379:0
    netport --host 127.0.0.1 --port 1234 --redis=192.168.1.125:6379:0
    netport -g api.json
    netport -g /home/user/api.json
"""
import os
import json

import uvicorn
from docopt import docopt

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 80


def generate_open_api_scheme(scheme_path: None):
    from netport.netport import app

    if scheme_path is None:
        scheme_path = "netport_openapi.json"

    scheme = app.openapi()
    with open(scheme_path, "w") as scheme_file:
        json.dump(scheme, scheme_file)

    print(f"The Netport scheme was exported to {scheme_path}")


def main():
    args = docopt(__doc__)
    if args["-g"]:
        generate_open_api_scheme(args["<path>"])
        exit()

    host = args["<host>"] if args["--host"] else DEFAULT_HOST
    port = args["<port>"] if args["--port"] else DEFAULT_PORT

    if args["--redis"]:
        redis_addr, redis_port, redis_db = args["--redis"].split(":")
        os.environ["NETPORT_REDIS_HOST"] = redis_addr
        os.environ["NETPORT_REDIS_PORT"] = redis_port
        os.environ["NETPORT_REDIS_DB"] = redis_db

    from netport.netport import run_app

    uvicorn.run(run_app, host=host, port=int(port), log_level="info", factory=True)


if __name__ == '__main__':
    main()
