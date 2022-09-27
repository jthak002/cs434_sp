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
    host: str
    port_tracker: int
    port_peer: int
    socket_tracker: socket.socket
    socket_peer: socket.socket
    follower_list: [str]

    def __init__(self, host='127.0.0.1', port_tracker=5001, port_peer=5002):
        self.socket_tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_peer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port_tracker = port_tracker
        self.port_peer = port_peer

    def setup(self):
        try:
            self.socket_tracker.bind((self.host, self.port_tracker))
        except OSError:
            print(f"port={self.port_tracker} for tracker comms is being used by another process. please try another port.")
            exit(1)
        try:
            self.socket_tracker.bind((self.host, self.port_tracker))
        except OSError:
            print(f"port={self.port_peer} for peer comms is being used by another process. please try another port.")
            exit(1)

    def client_register(self):
        pass

    def close(self):
        self.client.close()