import os
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
        # Do not use the socket.listen() class for UDP connections because the protocol is stateless and
        # packets are unorganized.
        # https://stackoverflow.com/questions/8194323/why-the-listen-function-call-is-not-needed-when-use-udp-socket
        print("Server has started... Socket is listening...")

    # Get message from client
    def server_recv_mesg(self, test_timeout=-1):
        print()
        print("==========================================")
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
            message_dict = json.loads(message.decode())
            user_request = message_dict['request']

            if user_request == "register":
                key_array = ['handle', 'source_ip', 'tracker_port', 'peer_port_left', 'peer_port_right']
                ServerNetwork.key_checker(key_array, message_dict)
            elif user_request == "query_users":
                pass
            elif user_request == "follow_user":
                key_array = ['username_i', 'username_j']
                ServerNetwork.key_checker(key_array, message_dict)
            elif user_request == "drop_user":
                key_array = ['username_i', 'username_j']
                ServerNetwork.key_checker(key_array, message_dict)
            elif user_request == "send_tweet":
                # While the user is creating the tweet, we just need to provide the follower list to
                # the user and set a timeout to ensure that the end tweet is received before the server
                # can process any request. Because there is a case where you need to ensure that no one
                # can exit especially those that are part of the logical ring.
                #
                # While doing that, you also need to ensure that any incoming message during that timeout
                # that are not part of the logical ring, is added to a message queue. Do also note that
                # the message queue can drop message if the buffer size exceeds.
                key_array = ['request', 'handle']
                ServerNetwork.key_checker(key_array, message_dict)
            elif user_request == "end_tweet":
                key_array = ['request', 'handle']
                ServerNetwork.key_checker(key_array, message_dict)
            elif user_request == "exit":
                key_array = ['username']
                ServerNetwork.key_checker(key_array, message_dict)
            else:
                raise json.JSONDecodeError

        except json.JSONDecodeError:
            print("Encountered error while decoding JSON - discarding packet.")
            return basic_response(user_request, False)

        return message_dict

    @staticmethod
    def key_checker(key_array, message_dict):
        for key_check in key_array:
            if message_dict[key_check] is None:
                raise json.JSONDecodeError

    def server_route_mesg(self, json_message: dict, src_ip, src_port):
        user_request = json_message.get('request', None)

        if user_request:
            if user_request == "register":
                is_success = self.tracker.register(json_message['handle'], json_message['source_ip'],
                                      json_message['tracker_port'], json_message['peer_port_left'],
                                      json_message['peer_port_right'])

                if is_success:
                    print("@" + json_message['handle'] + " has been successfully registered!")
                else:
                    print("@" + json_message['handle'] + " failed to register!")

                return basic_response(user_request, is_success)
            elif user_request == "query_users":
                query_results = self.tracker.query_handles()

                if query_results is not None:
                    print("Query Handle successfully generated!")

                return query_handle_response(True, query_results[0], query_results[1])
            elif user_request == "follow_user":
                if self.tracker.check_and_verify(json_message.get("username_i", None), src_ip, src_port):
                    if json_message.get("username_i", None) == json_message.get("username_j", None):
                        print("Users cannot follow themself!")
                        return basic_response(user_request, False)

                    if self.tracker.follow(json_message.get("username_i", None), json_message.get("username_j", None)):
                        return basic_response(user_request, True)
                    else:
                        return basic_response(user_request, False)
                else:
                    print("User source IP and source Port do not match username - IMPERSONATION")
                    return basic_response(user_request, False)
            elif user_request == "drop_user":
                if self.tracker.check_and_verify(json_message.get("username_i", None), src_ip, src_port):
                    if json_message.get("username_i", None) == json_message.get("username_j", None):
                        print("Given username are the same. Please enter 2 different usernames!")
                        return basic_response(user_request, False)

                    self.tracker.drop(json_message.get("username_i", None), json_message.get("username_j", None))
                    return basic_response(user_request, True)
                else:
                    print("User source IP and source Port do not match username - IMPERSONATION")
                    return basic_response(user_request, False)
            elif user_request == "send_tweet":
                # Follower List need to contain all the information about the all the followers of that
                # particular user
                if self.tracker.check_and_verify(json_message.get("handle", None), src_ip, src_port):
                    follower_tuple_list = self.tracker.tweet(json_message.get("handle", None))
                    return tweet_response(follower_tuple_list, True)
                else:
                    print("User source IP and source Port do not match username - IMPERSONATION")
                    return tweet_response(None, False)
            elif user_request == "end_tweet":
                if self.tracker.check_and_verify(json_message.get("handle", None), src_ip, src_port):
                    return basic_response(user_request, True)
                else:
                    print("User source IP and source Port do not match username - IMPERSONATION")
                    return tweet_response(None, False)
            elif user_request == "exit":
                if self.tracker.check_and_verify(json_message.get("username", None), src_ip, src_port):
                    self.tracker.exit(json_message.get("username", None))
                    return basic_response(user_request, True)
                else:
                    print("User source IP and source Port do not match username - IMPERSONATION")
                    return basic_response(user_request, False)
            else:
                print("Invalid user request found in JSON! dropping packet...")
        else:
            print("No user request is found in JSON! dropping packet...")

        return basic_response(user_request, False)

    # Send message to client
    def server_send(self, source_ip: str, source_port: int, message: bytes):
        self.server_side_socket.sendto(json.dumps(message).encode(), (source_ip, source_port))

    def server_conn_close(self):
        self.server_side_socket.close()


def basic_response(request, is_success):
    if is_success:
        return {'request': request, 'error_code': 'success'}

    return {'request': request, 'error_code': 'failure'}


def query_handle_response(is_success, user_count, list_users):
    if is_success:
        return {'request': 'query_users', 'error_code': 'success', 'num_users': user_count, 'user_list': list_users}

    return {'request': 'query_users', 'error_code': 'failure'}


def tweet_response(follower_tuple_list, is_success):
    if is_success:
        return {'request': 'send_tweet', 'error_code': 'success', 'follower_list': follower_tuple_list}

    return {'request': 'send_tweet', 'error_code': 'failure'}
