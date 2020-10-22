from typing import Callable, List


class WSGIApplication:
    @staticmethod
    def application(env: dict, start_response: Callable[[str, List[tuple]], None]):
        """
        env:
            リクエストヘッダーの情報がdictで渡されてくる
            refs) https://www.python.org/dev/peps/pep-3333/#environ-variables
            例）
            env = [
                "HTTP_METHOD": "POST",
                "PATH_INFO": "/index.html"
            ]

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
        method = env["REQUEST_METHOD"]
        path = env["PATH_INFO"]

        # start_responseを一度だけコールする
        # 固定で200 OKにする
        # Content-typeも固定でhtmlにする
        start_response('200 OK', [('Content-type', 'text/html')])

        # レスポンスボディを返す
        # ex) '<h1>METHOD: POST, PATH: /index.html</h1>'
        return [f'<h1>METHOD: {method}, PATH: {path}</h1>'.encode()]
