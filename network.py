import socket

ECHO = 0
TWEET = 1


class ServerNetwork:
    def __init__(self):
        self.server_side_socket = socket.socket()
        self.host = socket.gethostname()
        self.port = 5000
        self.thread_count = 0

    def server_start(self):
        try:
            self.server_side_socket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))

        self.server_side_socket.listen(5)
        print('Server has started... Socket is listening...')

    def close(self):
        self.server_side_socket.close()

    def multi_threaded_client(self, connection):
        connection.send(str.encode('Server is working:'))
        thread_is_running = True

        while thread_is_running:
            data = connection.recv(2048)
            response = data.decode('utf-8')

            if response.response_spliter() == ECHO:
                response = '0,' + data.decode('utf-8')
            elif response.response_spliter() == TWEET:
                pass

            if not data:
                break

            connection.sendall(str.encode(response))

        connection.close()


class ClientNetwork:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = socket.gethostname()
        self.port = 5000
        self.addr = (self.server, self.port)

    def close(self):
        self.client.close()

    def connect(self):
        try:
            self.client.connect(self.addr)
            res = self.client.recv(1024).decode("utf-8")
            print(res)
        except socket.error as e:
            print(str(e))

    def send(self, message):
        try:
            self.client.send(str.encode(message))
            res = self.client.recv(1024)
            return res

        except socket.error as e:
            print(e)


def response_spliter(res):
    res_str_list = res.split(',')

    return res_str_list
