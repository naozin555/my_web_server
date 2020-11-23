from datetime import datetime

from my_http.Request import Request
from my_http.Response import Response, HTTP_STATUS
from views.BaseView import BaseView


class NowView(BaseView):
    @staticmethod
    def get(request: Request) -> Response:
        current_time_str = f"<html><body><h1>now is {datetime.now()}</h1></body></html>"
        return Response(status=HTTP_STATUS.OK, body=current_time_str.encode())
