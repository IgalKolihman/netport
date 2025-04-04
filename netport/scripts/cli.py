"""Running netport from the cli"""

import json
import os

import uvicorn
from cleo.application import Application
from cleo.commands.command import Command
from cleo.helpers import option
from loguru import logger

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 80


class GenerateOpenApiCommand(Command):
    name = "generate-openapi"
    description = "Generate netport OpenAPI scheme in a JSON file"
    options = [
        option(
            long_name="path",
            short_name="p",
            description="Path to save the generated OpenAPI scheme",
        ),
    ]

    def handle(self):
        scheme_path = self.option("path") or "netport_openapi.json"
        self.generate_open_api_scheme(scheme_path)

    @staticmethod
    def generate_open_api_scheme(scheme_path):
        from netport.netport import app

        scheme = app.openapi()
        with open(scheme_path, "w") as scheme_file:
            json.dump(scheme, scheme_file, indent=4)

        logger.success(f"The Netport scheme was exported to {scheme_path}")


class RunNetportCommand(Command):
    name = "run"
    description = "Run netport from the CLI"
    options = [
        option(
            long_name="host",
            short_name="H",
            description="IP address to bind the app to",
        ),
        option(
            long_name="port",
            short_name="p",
            description="Port to bind the app to",
        ),
        option(
            long_name="redis",
            short_name="r",
            description="Address and port to connect to the redis DB. The correct format is: '<ip addr>:<port>:<db>'",
            flag=False,
        ),
    ]

    def handle(self):
        host = self.option("host") or DEFAULT_HOST
        port = int(self.option("port")) or DEFAULT_PORT

        if self.option("redis"):
            redis_addr, redis_port, redis_db = self.option("redis").split(":")
            os.environ["NETPORT_REDIS_HOST"] = redis_addr
            os.environ["NETPORT_REDIS_PORT"] = redis_port
            os.environ["NETPORT_REDIS_DB"] = redis_db

        from netport.netport import run_app

        uvicorn.run(run_app, host=host, port=port, log_level="info", factory=True)


def main():
    application = Application()
    application.add(GenerateOpenApiCommand())
    application.add(RunNetportCommand())
    application.run()


if __name__ == "__main__":
    main()
