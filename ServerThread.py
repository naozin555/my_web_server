import traceback
import socket
from datetime import datetime
from threading import Thread
import os
import datetime
from typing import Iterable, List

from WSGIApplication import WSGIApplication


class ServerThread(Thread):
    DOCUMENT_ROOT = "src"
    CONTENT_TYPE_MAP = {
        "html": "text/html",
        "htm": "text/html",
        "txt": "text/plain",
        "css": "text/css",
        "js": "application/javascript",
        "png": "image/png",
        "jpg": "image/jpg",
        "jpeg": "image/jpg",
        "gif": "image/gif",
    }

    response_line: str
    response_headers: List[tuple]

    def __init__(self, client_socket: socket):
        super().__init__()
        self.socket = client_socket

    def run(self):
        print("Worker: 処理開始")
        # noinspection PyBroadException
        try:
            # クライアントから受け取ったメッセージを代入（4096は受け取れるバイト数）
            msg_from_client = self.socket.recv(4096)
            # 受け取ったメッセージをファイルに書き込む
            with open("server_recv.txt", "wb") as f:
                f.write(msg_from_client)

            # リクエストメソッド
            request_method: str = msg_from_client.decode().split("\r\n")[0].split(" ")[0]
            # 要求されたファイルのパス
            path: str = msg_from_client.decode().split("\r\n")[0].split(" ")[1]
            extend: str = path.rsplit(".", maxsplit=1)[1]
            normalized_path = os.path.normpath(path)  # パスの正規化
            requested_file_path = self.DOCUMENT_ROOT + normalized_path
            is_exists = os.path.exists(requested_file_path)

            # ファイルがなければ404エラーを返す
            if is_exists:
                # envを作る
                env = {
                    # HTTPリクエストのヘッダーの情報を、WSGIのルールに従って正しく作る
                    # refs) https://www.python.org/dev/peps/pep-3333/#environ-variables
                    "REQUEST_METHOD": request_method,
                    "PATH_INFO": requested_file_path
                }

                # start_responseを作る
                def start_response(response_line: str, response_headers: List[tuple]):
                    """start_responseが呼ばれたときに、response_lineとheadersの情報をWSGIサーバーが受け取って保持できるようにする"""
                    self.response_line = response_line  # ステータスコード
                    self.response_headers = response_headers  # レスポンスヘッダ

                body_bytes_list: Iterable[bytes] = WSGIApplication().application(env, start_response)

                # body_bytes_listをもとにレスポンスを作る
                output_bytes = b""
                output_bytes += self.get_response_header()  # レスポンスヘッダ
                output_bytes += "\r\n".encode()  # 改行
                output_bytes += self.get_response_body(body_bytes_list)  # レスポンスボディ

                self.socket.send(output_bytes)

            else:
                # ステータスコード
                status_code = "HTTP/1.1 404 Not Found\n"
                # レスポンスヘッダ
                date = f"Date: {self._get_date()}\n"
                server = "Server: Nao/0.1\n"
                connection = "Connection: Close\n"
                content_type = f"Content-type: {self.CONTENT_TYPE_MAP[extend]}\n"
                blank_line = "\n"
                # 送り返す用のメッセージを生成
                with open(os.path.join(self.DOCUMENT_ROOT, "404error.html"), "rb") as f:
                    msg_to_client = (status_code + date + server + connection + content_type + blank_line).encode() \
                                    + f.read()
                # メッセージを送り返す
                self.socket.send(msg_to_client)

        except Exception:
            print("Worker: " + traceback.format_exc())

        finally:
            self.socket.close()
            print("Worker: 通信を終了しました")

    def get_content_type(self, ext: str):
        if ext != "" or ext not in self.CONTENT_TYPE_MAP:
            return "application/octet-stream"
        return self.CONTENT_TYPE_MAP[ext]

    def get_response_header(self) -> bytes:
        """start_responseがコールされた結果をもとに、レスポンスヘッダーを取得する"""
        # ex) "HTTP/1.1 200 OK"
        status_line = "HTTP/1.1 " + self.response_line + "\r\n"

        # ex)
        # response_headersはどこで作ってんの？
        # self.response_headers = [("key1", "value1"), ("key2, value2")]
        # header_text_list = ["key1: value1", "key2: value2"]
        # header_text = "key1: value1\r\n key2: value2"
        header_text_list = (": ".join(response_header) for response_header in self.response_headers)  # ジェネレータ
        header_text = "\r\n".join(header_text_list) + "\r\n"

        header = b""
        header += status_line.encode()
        header += header_text.encode()
        return header

    @staticmethod
    def get_response_body(body_bytes_list: Iterable[bytes]) -> bytes:
        """レスポンスボディを取得する"""
        return b"".join(body_bytes_list)

    @staticmethod
    def _get_date() -> str:
        return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
