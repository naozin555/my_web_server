# coding: UTF-8
import socket
import datetime
import os


class TCPServer:
    document_root = "src/"

    def main(self):
        # create an INET(IPv4), STREAMing socket socketのインスタンスを生成
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket to a public host, and a well-known port 8080番ポート向けにきた通信を受け取る設定
        server_socket.bind(("localhost", 8080))
        # become a server socket 待ち受けモードになる
        server_socket.listen(1)

        print("クライアント接続を待ちます。")
        (client_socket, address) = server_socket.accept()
        print("クライアント接続")

        # クライアントから受け取ったメッセージを代入（4096は受け取れるバイト数）
        msg_from_client = client_socket.recv(4096)
        # 受け取ったメッセージをファイルに書き込む
        with open("server_recv.txt", "wb") as f:
            f.write(msg_from_client)
        path: str = msg_from_client.decode().split("\r\n")[0].split(" ")[1][1:]

        # ステータスコード
        status_code = "HTTP/1.1 200 OK\n"

        # レスポンスヘッダ
        date = f"Date: {self._get_date()}\n"
        server = "Server: Nao/0.1\n"
        connection = "Connection: Close\n"
        content_type = "Content-type: text/html\n"
        blank_line = "\n"

        # 送り返す用のメッセージをファイルから読み込む
        with open(os.path.join(self.document_root, path), "rb") as f:
            msg_to_client = (status_code + date + server + connection + content_type + blank_line).encode() + f.read()

        # メッセージを送り返す
        client_socket.send(msg_to_client)

        client_socket.close()
        print("通信を終了しました")

    @staticmethod
    def _get_date() -> str:
        return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')


if __name__ == '__main__':
    TCPServer().main()
