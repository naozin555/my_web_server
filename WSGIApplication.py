import traceback
from typing import Callable, List, Iterable, Dict

from my_http.Request import Request
from my_http.Response import Response, HTTP_STATUS
from views.HeadsersView import HeadersView
from views.ParametersView import ParametersView
from views.NowView import NowView
from views.SetCookieView import SetCookieView


class WSGIApplication:
    env: dict
    start_response: Callable[[str, List[tuple]], None]

    DOCUMENT_ROOT = "./resources"
    DOCUMENT_404 = "./resources/404.html"

    URL_VIEWS = {
        "/now": NowView(),
        "/parameters": ParametersView(),
        "/headers": HeadersView(),
        "/set_cookie": SetCookieView(),
    }

    def application(self, env: dict, start_response: Callable[[str, Iterable[tuple]], None]):
        """
        env:
            リクエストヘッダーの情報がdictで渡されてくる
            refs) https://www.python.org/dev/peps/pep-3333/#environ-variables
            例）
            env = {
                "HTTP_METHOD": "POST",
                "PATH_INFO": "/index.html"
            }
        start_response:
            レスポンスヘッダーの内容を、WSGIサーバーへ伝えるための関数(or Callable)。
            WSGIアプリケーション内で一度だけコールする。
            コールするときは、第一引数にレスポンスライン、第２引数にレスポンスヘッダーを渡してコールする。
            例）
            start_response(
                '200 OK',
                [
                    ('Content-type', 'text/plain; charset=utf-8'),
                    ('Connection', 'Closed')
                ]
            )
        """

        self.env = env
        self.start_response = start_response

        request = Request.from_env(env)
        path = request.path

        # noinspection PyBroadException
        try:
            if path in self.URL_VIEWS:
                response: Response = self.URL_VIEWS[path].get_response(request)

                self._start_response_by_response(response)
                return [response.body]

            try:
                body = self._get_file_content(path)
                self._start_ok()
                return [body]

            except OSError:
                with open(self.DOCUMENT_404, "rb") as f:
                    self._start_not_found()
                    return [f.read()]

        except Exception:
            stream = env["wsgi.errors"]
            stream.write(traceback.format_exc())
            self._start_server_error()
            return [b"<html><body><h1>500 Internal Server Error</h1></body></html>"]

    def _get_file_content(self, path: str) -> bytes:
        with open(self.DOCUMENT_ROOT + path, "rb") as f:
            return f.read()

    def _start_ok(self, headers: Dict[str, str] = None) -> None:
        if headers is None:
            headers = {}

        status = HTTP_STATUS.OK
        self.start_response(str(status), [(key, value) for key, value in headers.items()])

    def _start_not_found(self) -> None:
        status = HTTP_STATUS.NOT_FOUND
        self.start_response(str(status), [("Content-Type", "text/html")])

    def _start_server_error(self) -> None:
        status = HTTP_STATUS.SERVER_ERROR
        self.start_response(str(status), [("Content-Type", "text/html")])

    def _start_response_by_response(self, response: Response) -> None:
        status = str(response.status)

        response.headers["Content-Type"] = response.content_type
        headers = [(key, value) for key, value in response.headers.items()]

        for key, value in response.cookies.items():
            headers.append(("Set-Cookie", f"{key}={value}"))

        self.start_response(status, headers)
