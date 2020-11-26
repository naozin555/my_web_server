from my_http.Request import Request
from my_http.Response import Response, HTTP_STATUS
from views.BaseView import BaseView


class SetCookieView(BaseView):
    @staticmethod
    def get(request: Request) -> Response:
        """
        :return: Cookieを設定して返す
        """
        body = "cookies"
        body += str(request.cookies)
        return Response(status=HTTP_STATUS.OK, body=body.encode(),
                        cookies={"test_cookie3": "hoge3", "test_cookie4": "hoge4"})
