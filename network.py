import os
import socket
import time
import json
from tracker import Tracker

TRACKER_URL = os.getenv('TRACKER_URL','127.0.0.1')
TRACKER_PORT = int(os.getenv('TRACKER_PORT', '5000'))



class ServerNetwork:
    port: int
    host: str
    thread_count = 0

    def __init__(self, host='127.0.0.1', port=5000):
        self.server_side_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tracker = Tracker()
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

    # Get message from client
    def server_recv_mesg(self, test_timeout=-1):
        print("Waiting for message")
        raw_msg = self.server_side_socket.recvfrom(1024)
        print(raw_msg)
        # TEST - this is a statement to test the buffering on the udp socket.
        if test_timeout > 0:
            time.sleep(test_timeout)
        return raw_msg[0], raw_msg[1][0], raw_msg[1][1]

    # Parse message from client and verify json message contains all required key:value pairs
    @staticmethod
    def server_parse_mesg(source_ip: str, source_port: int, message: json):
        try:
            message_dict = json.load(message)
            user_request = message_dict['request']

            if user_request == "register":
                key_array = ['handle', 'source_ip', 'tracker_port', 'peer_port_left', 'peer_port_right']
                for key_check in key_array:
                    if message_dict[key_check] is None:
                        raise json.JSONDecodeError
            elif user_request == "query_users":
                pass
            elif user_request == "follow_user":
                key_array = ['username']
                for key_check in key_array:
                    if message_dict[key_check] is None:
                        raise json.JSONDecodeError
            elif user_request == "drop_user":
                key_array = ['username']
                for key_check in key_array:
                    if message_dict[key_check] is None:
                        raise json.JSONDecodeError
            else:
                raise json.JSONDecodeError

        except json.JSONDecodeError:
            print("Encountered error while decoding JSON - discarding packet.")
            return basic_response(user_request, False)

        return message_dict

    @staticmethod
    def server_route_mesg(self, json_message: dict):
        user_request = json_message.get('request', None)

        if user_request:
            if user_request == "register":
                is_success = self.tracker.register(user_request['handle'], user_request['source_ip'],
                                      user_request['tracker_port'], user_request['peer_port_left'],
                                      user_request['peer_port_right'])

                return basic_response(user_request, is_success)
            elif user_request == "query_users":
                query_results = self.tracker.query_handles()
                return query_handle_response(True, query_results[0], query_results[1]["followers"])
            elif user_request == "follow_user":
                self.tracker.follow(user_request["username_i"], user_request["username_j"])
                return basic_response(user_request, True)
            elif user_request == "drop_user":
                self.tracker.follow(user_request["username_i"], user_request["username_j"])
                return basic_response(user_request, True)
            else:
                print("server_route_mesg found malformed JSON. dropping packet.")
        else:
            print("server_route_mesg found malformed JSON. dropping packet.")

        return basic_response(user_request, False)

    # Send message to client
    def server_send(self, source_ip: str, source_port: int, message: bytes):
        self.server_side_socket.sendto(message, (source_ip, source_port))

    def server_conn_close(self):
        self.server_side_socket.close()


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
        self.socket_tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_peer_left = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_peer_right = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port_tracker = port_tracker
        self.port_peer_left = port_peer_left
        self.port_peer_right = port_peer_right

    def setup(self):
        try:
            self.socket_tracker.bind((self.host, self.port_tracker))
        except OSError:
            print(f"port={self.port_tracker} for tracker comms is being used by another process. "
                  f"please try another port.")
            exit(1)
        try:
            self.socket_peer_left.bind((self.host, self.port_peer_left))
        except OSError:
            print(f"port={self.port_peer_left} for peer_LEFT comms is being used by another process. "
                  f"please try another port.")
            exit(1)
        try:
            self.socket_peer_right.bind((self.host, self.port_peer_right))
        except OSError:
            print(f"port={self.port_peer_left} for peer_RIGHT comms is being used by another process. "
                  f"please try another port.")
            exit(1)

    def client_register(self, handle: str):
        dict_message = {'request': 'register', 'handle': handle, 'source_ip': self.host,
                        'port_tracker': self.port_tracker, 'port_peer_left': self.port_peer_left,
                        'port_peer_right': self.port_peer_right}

        raw_message = None
        while True:
            self.socket_tracker.sendto(json.dumps(dict_message).encode(), (TRACKER_URL, TRACKER_PORT))
            self.socket_tracker.settimeout(30)
            try:
                raw_message = self.socket_tracker.recvfrom(1024)
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


def basic_response(request, is_success):
    if is_success:
        return {'request': request, 'error_code': 'success'}

    return {'request': request, 'error_code': 'failure'}


def query_handle_response(is_success, user_count, list_users):
    if is_success:
        return {'request': 'query_users', 'error_code': 'success', 'num_users': user_count, 'user_list': list_users}

    return {'request': 'query_users', 'error_code': 'failure'}
