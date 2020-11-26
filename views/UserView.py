from uuid import uuid4

from my_http.Request import Request
from my_http.Response import Response, HTTP_STATUS
from session import SESSIONS
from views.BaseView import BaseView


class UserView(BaseView):
    def get(self, request: Request) -> Response:
        session_id = request.cookies.get("session_id")
        session = SESSIONS.get(session_id)
        if session:
            name = session.get("name")
        else:
            name = ""

        body = f"""\
        <html>
        <body>
            <h1>ようこそ [ {name or "名無し"} ] さん！
            <form method="post">
                名前変更: <input type="text" name="user_name"></input>

                <input type="submit" value="送信">
            </form>
        </body>
        </html>
        """

        return Response(body=body.encode(), status=HTTP_STATUS.OK)

    def post(self, request: Request) -> Response:
        # Cookieからsession_idを取得
        if "session_id" not in request.cookies:
            session_id = str(uuid4())
        else:
            session_id = request.cookies["session_id"]

        SESSIONS[session_id] = {"name": request.POST["user_name"][0]}

        return Response(
            status=HTTP_STATUS.FOUND,
            headers={"Location": "/user"},
            cookies={"session_id": session_id},
        )
