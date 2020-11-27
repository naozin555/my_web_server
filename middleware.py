from uuid import uuid4

from my_http.Request import Request
from my_http.Response import Response
from session import SESSIONS


class SessionMiddleware:
    def __init__(self, next):
        self.next = next

    def get_response(self, request: Request) -> Response:
        # sessionに関するcookieがあったら、Requestオブジェクトに追加する
        session_id = request.cookies.get("session_id")
        session = SESSIONS.get(session_id)

        if session:
            request.session = session

        # レスポンスを取得する
        response = self.next.get_response(request)

        # レスポンスにsessionがセットされていたら、セッションストレージを変更する
        if response.session:
            # セッションが発行されていなければ、このタイミングで発行する
            if not session:
                session_id = str(uuid4())
                SESSIONS[session_id] = {}
                response.cookies = {"session_id": session_id}

            for key, value in response.session.items():
                SESSIONS[session_id][key] = value

        return response
