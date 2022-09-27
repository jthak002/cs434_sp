import socket
import time
import json

class ServerNetwork:
    port: int
    host: str
    thread_count = 0

    def __init__(self,host='127.0.0.1', port=5000):
        self.server_side_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        self.thread_count = 0

    def server_start(self):
        try:
            self.server_side_socket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))
        # Note to Wei: We do not use the socket.listen() class for UDP connections because the protocol is stateless and
        # packets are unorganized.
        # https://stackoverflow.com/questions/8194323/why-the-listen-function-call-is-not-needed-when-use-udp-socket
        # self.server_side_socket.listen(5)
        print('Server has started... Socket is listening...')

    def server_recv_mesg(self, test_timeout=-1):
        print("Waiting for message")
        raw_msg = self.server_side_socket.recvfrom(1024)
        print(raw_msg)
        # TEST - this is a statement to test the buffering on the udp socket.
        if test_timeout > 0:
            time.sleep(test_timeout)
        return raw_msg[0], raw_msg[1][0], raw_msg[1][1]

    @staticmethod
    def server_parse_mesg(source_ip: str, source_port, message: bytes):
        try:
            json_message = json.loads(message.decode())
        except json.JSONDecodeError:
            print("Encountered error while decoding JSON - discarding packet.")
            return
        json_message.update("src_ip", source_ip)
        json_message.update("src_port", source_port)
        return json_message

    '''
    @staticmethod
    def server_route_mesg(json_message:dict):
        user_request = json_message.get('request', None)
        if user_request:
            if user_request == 'query_handles':
                pass
        else:
            print("server_route_mesg found malformed JSON. dropping packet.")
    '''

    def server_conn_close(self):
        self.server_side_socket.close()


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

            print(res.decode('utf-8'))

        except socket.error as e:
            print(e)
