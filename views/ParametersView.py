from my_http.Request import Request
from my_http.Response import Response, HTTP_STATUS


from views.BaseView import BaseView


class ParametersView(BaseView):
    @staticmethod
    def get(request: Request) -> Response:
        """
        リクエストメソッドがGETだった時の処理
        """
        return Response(status=HTTP_STATUS.OK, body=str(request.GET).encode())

    @staticmethod
    def post(request: Request) -> Response:
        """
        リクエストメソッドがPOSTだった時の処理
        """
        return Response(status=HTTP_STATUS.OK, body=str(request.POST).encode())
