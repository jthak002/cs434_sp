import socket


class Network:
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

            print(res.decode('utf-8'))

        except socket.error as e:
            print(e)
