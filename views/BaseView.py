from my_http.Request import Request
from my_http.Response import Response, HTTP_STATUS


class BaseView:
    def get_response(self, request: Request) -> Response:
        """
        /parameters のパスにきたリクエストに対して、適切なレスポンスを生成して返す
        :param request:
        :return:
        """
        if request.method == "GET":
            return self.get(request)
        elif request.method == "POST":
            return self.post(request)
        else:
            return Response(status=HTTP_STATUS.METHOD_NOT_ALLOWED)

    @staticmethod
    def get(request: Request) -> Response:
        return Response(status=HTTP_STATUS.METHOD_NOT_ALLOWED)

    @staticmethod
    def post(request: Request) -> Response:
        return Response(status=HTTP_STATUS.METHOD_NOT_ALLOWED)
