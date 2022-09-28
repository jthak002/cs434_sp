import socket
import time
import json

from tracker import Tracker


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
                self.tracker.register(user_request['handle'], user_request['source_ip'],
                                      user_request['tracker_port'], user_request['peer_port_left'],
                                      user_request['peer_port_right'])
                return basic_response(user_request, True)
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
        pass

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


def basic_response(request, is_success):
    if is_success:
        return {'request': request, 'error_code': 'success'}

    return {'request': request, 'error_code': 'failure'}


def query_handle_response(is_success, user_count, list_users):
    if is_success:
        return {'request': 'query_users', 'error_code': 'success', 'num_users': user_count, 'user_list': list_users}

    return {'request': 'query_users', 'error_code': 'failure'}
