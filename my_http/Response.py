from dataclasses import dataclass
from enum import Enum


# noinspection PyPep8Naming
class HTTP_STATUS(Enum):
    OK = "200 OK"

    FOUND = "302 Found"

    NOT_FOUND = "404 Not Found."
    METHOD_NOT_ALLOWED = "405 Method Not Allowed"

    SERVER_ERROR = "500 Internal Server Error"


@dataclass
class Response:
    status: HTTP_STATUS = HTTP_STATUS.OK
    content_type: str = "text/html; charset=utf-8;"
    headers: dict = None
    cookies: dict = None
    body: bytes = b""

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.cookies is None:
            self.cookies = {}
