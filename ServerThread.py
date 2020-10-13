import traceback
from datetime import datetime
from threading import Thread
import os
import datetime


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

    def __init__(self, client_socket):
        super().__init__()
        self.socket = client_socket

    def run(self):
        # noinspection PyBroadException
        try:
            # クライアントから受け取ったメッセージを代入（4096は受け取れるバイト数）
            msg_from_client = self.socket.recv(4096)
            path: str = msg_from_client.decode().split("\r\n")[0].split(" ")[1]
            extend: str = path.rsplit(".", maxsplit=1)[1]
            print(path)

            # 受け取ったメッセージをファイルに書き込む
            with open("server_recv.txt", "wb") as f:
                f.write(msg_from_client)

            # 要求されたファイルのパス
            normalized_path = os.path.normpath(path)
            # パスの正規化
            requested_file_path = self.DOCUMENT_ROOT + normalized_path
            is_exists = os.path.exists(requested_file_path)
            # ファイルがなければ404エラーを返す
            if is_exists:
                # ステータスコード
                status_code = "HTTP/1.1 200 OK\n"
                # レスポンスヘッダ
                date = f"Date: {self._get_date()}\n"
                server = "Server: Nao/0.1\n"
                connection = "Connection: Close\n"
                content_type = f"Content-type: {self.CONTENT_TYPE_MAP[extend]}\n"
                blank_line = "\n"
                # 送り返す用のメッセージをファイルから読み込む
                with open(requested_file_path, "rb") as f:
                    msg_to_client = (status_code + date + server + connection + content_type + blank_line).encode()\
                                    + f.read()
                # メッセージを送り返す
                self.socket.send(msg_to_client)

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
            print(traceback.format_exc())

        finally:
            self.socket.close()
            print("通信を終了しました")

    def get_content_type(self, ext: str):
        return self.CONTENT_TYPE_MAP.get(ext, default="application/octet-stream")

    @staticmethod
    def _get_date() -> str:
        return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
