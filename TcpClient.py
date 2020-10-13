import socket


class TCPClient:
    def main(self):
        # create an INET(IPv4), STREAMing socket socketのインスタンスを生成
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # サーバーに接続
        client_socket.connect(("localhost", 8080))

        # サーバーに送るメッセージをファイルから読み込む
        with open("client_send.txt", "rb") as f:
            msg_to_server = f.read()

        # client.txtの内容をサーバーに送信。
        client_socket.send(msg_to_server)

        # サーバーから受け取ったメッセージを代入（4096は受け取れるバイト数）
        msg_from_server = client_socket.recv(4096)

        # 受け取ったメッセージをファイルに書き込む
        with open("client_recv.txt", "wb") as f:
            f.write(msg_from_server)

        client_socket.close()


if __name__ == '__main__':
    TCPClient().main()
