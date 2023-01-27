from typing import Any
from dataclasses import dataclass

R_PORT = "PORT"
R_PATH = "PATH"
R_PROCESS = "PROCESS"


@dataclass
class Response:
    """Response format for every api command.

    Every response from the netport server will have the save stracture:
    {
        "data": <Response>
    }
    """

    data: Any
