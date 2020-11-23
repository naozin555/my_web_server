from my_http.Request import Request
from my_http.Response import Response, HTTP_STATUS


class HeadersView:
    @staticmethod
    def get(request: Request) -> Response:
        """
        /headers のパスにきたリクエストに対して、headerの内容をレスポンスとして返す
        :param request:
        :return:
        """
        body_str = ""
        for key, value in request.headers.items():
            body_str += f"{key}: {value}<br>"
        return Response(status=HTTP_STATUS.OK, body=body_str.encode())
