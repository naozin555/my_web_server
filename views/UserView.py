from my_http.Request import Request
from my_http.Response import Response, HTTP_STATUS
from views.BaseView import BaseView


class UserView(BaseView):
    def get(self, request: Request) -> Response:
        if request.session:
            name = request.session.get("name")
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

        return Response(
            status=HTTP_STATUS.FOUND,
            headers={"Location": "/user"},
            session={"name": request.POST["user_name"][0]}
        )
