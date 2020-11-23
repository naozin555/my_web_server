import socket

from ServerThread import ServerThread


class Main:
    @staticmethod
    def main():
        # create an INET(IPv4), STREAMing socket socketのインスタンスを生成
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket to a public host, and a well-known port 8080番ポート向けにきた通信を受け取る設定
        server_socket.bind(("localhost", 8080))
        # become a server socket 待ち受けモードになる
        server_socket.listen(10)

        while True:
            print("Main: クライアント接続を待ちます。")
            (client_socket, address) = server_socket.accept()
            print("Main: クライアント接続")

            thread = ServerThread(client_socket=client_socket)
            thread.start()
            print("スレッド起動完了")


if __name__ == '__main__':
    Main().main()
