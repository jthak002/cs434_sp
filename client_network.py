import os
import socket
import json

TRACKER_URL = os.getenv('TRACKER_URL','127.0.0.1')
TRACKER_PORT = int(os.getenv('TRACKER_PORT', '5000'))


class ClientNetwork:
    host: str
    port_tracker: int
    port_peer_left: int
    port_peer_right: int
    socket_tracker: socket.socket
    socket_peer_left: socket.socket
    socket_peer_right: socket.socket
    follower_list: [str]

    def __init__(self, host='127.0.0.1', port_tracker=5001, port_peer_left=5002, port_peer_right=5003):
        print("Initializing the client")
        self.socket_tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_peer_left = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_peer_right = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port_tracker = port_tracker
        self.port_peer_left = port_peer_left
        self.port_peer_right = port_peer_right
        print(f"Client has been initialized with the IP={self.host}, and ports=[{self.port_tracker},"
              f"{self.port_peer_left},{self.port_peer_right} ]")

    def setup(self):
        print(f"trying to bind TRACKER_SOCKET to  the socket@{self.host}:{self.port_tracker}")
        try:
            self.socket_tracker.bind((self.host, self.port_tracker))
        except OSError:
            print(f"port={self.port_tracker} for tracker comms is being used by another process. "
                  f"please try another port.")
            exit(1)
        print("bind successful!")
        print(f"trying to bind LEFT_PEER_SOCKET to the socket@{self.host}:{self.port_peer_left}")
        try:
            self.socket_peer_left.bind((self.host, self.port_peer_left))
        except OSError:
            print(f"port={self.port_peer_left} for peer_LEFT comms is being used by another process. "
                  f"please try another port.")
            exit(1)
        print("bind successful!")
        print(f"trying to bind RIGHT_PEER_SOCKET to the socket@{self.host}:{self.port_peer_right}")
        try:
            self.socket_peer_right.bind((self.host, self.port_peer_right))
        except OSError:
            print(f"port={self.port_peer_left} for peer_RIGHT comms is being used by another process. "
                  f"please try another port.")
            exit(1)
        print("bind successful!")

    def client_register(self, handle: str):

        print("Compiling the REGISTER REQUEST")
        dict_message = {'request': 'register', 'handle': handle, 'source_ip': self.host,
                        'tracker_port': self.port_tracker, 'peer_port_left': self.port_peer_left,
                        'peer_port_right': self.port_peer_right}
        print(f"REGISTER_REQUEST=> {dict_message}")
        binary_request_message = json.dumps(dict_message).encode()
        print(f"REGISTER_REQUEST_BINARY => {binary_request_message}")
        raw_message = None
        while True:
            self.socket_tracker.sendto(binary_request_message, (TRACKER_URL, TRACKER_PORT))
            print(f"sent REGISTER_REQUEST_BINARY to {TRACKER_URL}:{TRACKER_PORT}")
            self.socket_tracker.settimeout(30)
            try:
                raw_message = self.socket_tracker.recvfrom(1024)
                print(f"Received RAW_MESSAGE={raw_message}")
            except TimeoutError:
                print("the previous message to the tracker did not get a response. will try again")
                continue
            break
        if type(raw_message) is tuple and len(raw_message) == 2:
            json_message = raw_message[0].decode()
            src_ip = raw_message[1][0]
            src_port = raw_message[1][1]
            if src_ip == TRACKER_URL and src_port == TRACKER_PORT:
                if json.loads(json_message).get('response') == 'register' and \
                        json.loads(json_message).get('error_code') == 'success':
                    print("The handle {handle}@{self.host}:{self.port_tracker} has registered successfully!")
                elif json.loads(json_message).get('response') == 'register' and \
                        json.loads(json_message).get('error_code') == 'failure':
                    print("The handle {handle}@{self.host}:{self.port_tracker} received failure message from server")
                else:
                    print("received malformed message - printing to console")
                    print(raw_message)
            else:
                print("received unknown message - exiting now")
        else:
            print("error case")

    def close(self):
        self.socket_tracker.close()
        self.socket_peer_left.close()
        self.socket_peer_right.close()