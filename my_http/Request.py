import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import parse_qs


@dataclass
class Request:
    path: str
    method: str
    headers: dict = None
    cookies: dict = None
    GET: Optional[dict] = None
    POST: Optional[dict] = None

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.cookies is None:
            self.cookies = {}
        if self.GET is None:
            self.GET = {}
        if self.POST is None:
            self.POST = {}

    @staticmethod
    def from_env(env: dict) -> "Request":
        """
        WSGIインターフェースのenvからリクエストクラスを生成するファクトリーメソッド
        """
        request = Request(path=env["PATH_INFO"], method=env["REQUEST_METHOD"])

        for key, value in env.items():
            if key.startswith("HTTP_"):
                request.headers[key.replace("HTTP_", "")] = value

        if "COOKIE" in request.headers:
            for cookie in re.split(r"; *", request.headers["COOKIE"]):
                if "=" in cookie:
                    key, value = cookie.split(r"=")
                    request.cookies[key] = value

        if request.method == "GET":
            request.GET = parse_qs(env["QUERY_STRING"])

        if request.method == "POST":
            request.POST = parse_qs(env["wsgi.input"].read().decode())

        return request
