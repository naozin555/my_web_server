# -*- coding: utf-8 -*-
import re
import socket
import traceback
from io import BytesIO
from sys import stdout
from threading import Thread
from typing import List, Iterable, Dict, Tuple

from WSGIApplication import WSGIApplication


class StartResponse:
    status: str
    response_headers: Iterable[Tuple[str, str]]

    def __call__(self, status: str, response_headers: Iterable[Tuple[str, str]], exec_info=None):
        self.status = status
        self.response_headers = response_headers


class ServerThread(Thread):
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

    response_status: str
    response_headers: List[Tuple[str, str]]

    def __init__(self, client_socket: socket):
        super().__init__()
        self.socket = client_socket

    def run(self):
        print("Worker: 処理開始")
        # noinspection PyBroadException
        try:
            # クライアントから受け取ったメッセージを代入
            request: bytes = self.socket.recv(4096)

            # requestをパースする
            method, path, protocol, request_headers, request_body = self.parse_request(request)

            # WSGI Application用のenvを生成
            env = self.build_env(method, path, protocol, request_headers, request_body)

            # WSGI Application用のstart_responseを生成
            start_response = StartResponse()

            # WSGIアプリケーションのapplicationを呼び出す
            body_bytes_list: Iterable[bytes] = WSGIApplication().application(env, start_response)

            # 呼び出し結果をもとにレスポンスを生成する
            output_bytes = self.get_status_line(start_response.status)  # ステータスライン
            output_bytes += self.get_response_header(start_response.response_headers, path)  # ヘッダー
            output_bytes += b"\r\n"  # 空行
            output_bytes += self.get_response_body(body_bytes_list)  # ボディ

            print(f"######## send message ##########\n{output_bytes.decode()}")

            self.socket.send(output_bytes)

        except Exception:
            print("Worker: " + traceback.format_exc())

        finally:
            self.socket.close()
            print("Worker: 通信を終了しました")

    def start_response(self, status, headers):
        self.response_status = status
        self.response_headers = headers

    def parse_request(self, request: bytes) -> Tuple[str, str, str, Dict[str, str], bytes]:
        # request_lineを抽出
        request_line_raw, remain = request.split(b"\r\n", maxsplit=1)
        request_line = request_line_raw.decode()
        # メソッド、パス、プロトコルを取得
        method, path, protocol = request_line.split(" ", maxsplit=2)

        # request headerを抽出、パース
        header_raw, body = remain.split(b"\r\n\r\n", maxsplit=1)
        print(body)
        header_str = header_raw.decode()
        headers = self.parse_headers(header_str)

        return method, path, protocol, headers, body

    @staticmethod
    def parse_headers(header_str: str) -> Dict[str, str]:
        header_lines = header_str.split("\r\n")
        header_tuples = (tuple(re.split(r": *", header_line, maxsplit=1)) for header_line in header_lines)
        return {
            header_tuple[0]: header_tuple[1]
            for header_tuple
            in header_tuples
        }

    @staticmethod
    def build_env(method: str, path: str, protocol: str, headers: Dict[str, str], body: bytes) -> dict:
        split_path = path.split("?", maxsplit=1)
        env = {
            "REQUEST_METHOD": method.upper(),
            "PATH_INFO": split_path[0],
            "QUERY_STRING": split_path[1] if len(split_path) > 1 else "",
            "SERVER_PROTOCOL": protocol,
            "CONTENT_TYPE": headers.get("Content-Type", ""),
            "wsgi.version": (1, 0, 1),
            "wsgi.url_scheme": protocol,
            "wsgi.input": BytesIO(body),
            "wsgi.errors": stdout,
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
            "wsgi.run_once": False,
        }

        # HTTP_Variables
        for header_key, header_value in headers.items():
            key = "HTTP_" + header_key.upper().replace("-", "_")
            env[key] = header_value

        print(f"########## env:\n{env}")

        return env

    def get_content_type(self, path: str):
        split_path = path.rsplit(".", maxsplit=1)
        ext = split_path[1] if len(split_path) > 1 else ""

        return self.CONTENT_TYPE_MAP.get(ext, "application/octet-stream")

    @staticmethod
    def get_status_line(status: str) -> bytes:
        # ex) "HTTP/1.1 200 OK"
        return ("HTTP/1.1 " + status + "\r\n").encode()

    # noinspection SpellCheckingInspection
    def get_response_header(self, response_headers: Iterable[Tuple[str, str]], path: str) -> bytes:
        includes_content_type = False

        header = ""
        for response_header in response_headers:
            if response_header[0] == "Content-Type":
                includes_content_type = True
            header += ": ".join(response_header) + "\r\n"

        # WSGIアプリケーションから受け取ったヘッダーにContent-Typeがなければ、補完する
        if not includes_content_type:
            header = f"Content-Type: {self.get_content_type(path)}\r\n" + header

        return header.encode()

    @staticmethod
    def get_response_body(body_bytes_list: Iterable[bytes]) -> bytes:
        return b"".join(body_bytes_list)
