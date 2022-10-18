import socket
import os
import sys
import json

PROPAGATION_TIMEOUT = 60
PROPAGATION_RETRIES = 3


class LogicalNetwork(object):
    left_neighbor_list: []
    right_neighbor_list: []
    left_socket: socket.socket
    right_socket: socket.socket
    hostname: str

    def __init__(self, left_socket, right_socket, hostname):
        self.left_socket = left_socket
        self.right_socket = right_socket
        self.hostname = hostname

    @staticmethod
    def _send_success_message(snd_socket: socket.socket, for_request: str, destination: str, port: int, success=True,
                              additional_args=None):
        dict_message = {'request': for_request, 'error_code': 'success' if success else 'failure'}
        if additional_args is not None and type(additional_args) == dict:
            for key, value in additional_args.items():
                dict_message[key] = value
        snd_socket.sendto(json.dumps(dict_message).encode(), (destination, port))

    def tweet_message(self, message_string: str, follower_list: []):
        # 1. Send the tweet down the chain to be propagated.
        dict_message = {'request': 'send_tweet', 'chain_owner': self.hostname,
                        'follower_list': follower_list}
        print(f"Compiling the SEND_TWEET REQUEST=> {dict_message}")
        binary_request = json.dumps(dict_message).encode()
        raw_message = None
        next_peer = self.find_left_neighbor(follower_list)
        while True:
            self.left_socket.sendto(binary_request, (next_peer[0], next_peer[2]))
            self.left_socket.settimeout(30)
            try:
                raw_message = self.left_socket.recvfrom(1024)
                print(f'received raw_message = {raw_message}')
            except TimeoutError:
                print(f"the previous message to the peer {next_peer[0]}:{next_peer[1]} did not get a response. "
                      f"will try again")
                continue
            break
        # 2. Checking if the peer to whom the tweet was sent to received it successfully.
        if type(raw_message) is tuple and len(raw_message) == 2:
            json_message = raw_message[0].decode()
            src_ip = raw_message[1][0]
            src_port = raw_message[1][1]
            if src_ip == next_peer[0] and src_port == next_peer[2]:
                # Sanity check - making sure response came from next peer
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                if json.loads(json_message).get('request') == 'send_tweet' and \
                        json.loads(json_message).get('error_code') == 'success':
                    pass
                elif json.loads(json_message).get('request') == 'send_tweet' and \
                        json.loads(json_message).get('error_code') == 'failure':
                    print("Could not send the tweet to the next peer in line.")
                    return
                else:
                    print("received malformed message - printing to console")
                    print(raw_message)
            else:
                print("received message from unknown source - exiting now")
        else:
            print("error_case: the data picked from UDP wasn't valid UDP Tuple response.")
        # 3. listening on the right port if the last peer in line sends a correct response. Will wait
        # PROPAGATION_TIMEOUT mins
        self.right_socket.settimeout(PROPAGATION_TIMEOUT)
        retries = 0
        while retries < PROPAGATION_RETRIES:
            try:
                prop_confirm = self.right_socket.recvfrom(1024)
                prop_confirm_message = json.loads(prop_confirm[0].decode())
                if prop_confirm_message.get('request', None) == 'send_tweet':
                    if prop_confirm_message.get('chain_owner', None) == self.hostname:
                        print('TWEET PROPAGATED SUCCESSFULLY!')
                        LogicalNetwork._send_success_message(for_request='send_tweet',
                                                             success=True, destination=prop_confirm[1][0],
                                                             port=prop_confirm[1][0], additional_args=None,
                                                             snd_socket=self.right_socket)
                    else:
                        print("Received a TWEET message with another "
                              "`chain_owner`: {}.".format(prop_confirm_message.get('chain_owner', None)))
                        #
                        # wip: process this after the current tweet has propagated.
                        self.process_and_forward_tweet(bypass_recv=True, message=prop_confirm_message)
                        continue
                else:
                    print(f"Received an unexpected message AFTER SEND_TWEET: {prop_confirm}")
            except TimeoutError:
                pass

    def process_and_forward_tweet(self, bypass_recv=False, message=None):
        if not bypass_recv:
            self.right_socket.settimeout(5)
            recv_tweet = self.right_socket.recvfrom(1024)
            message = recv_tweet
        tweet_payload = json.loads(message.decode())
        if tweet_payload.get('request', None) == 'send_tweet':
            try:
                tweet_text =
                next_peer =
            except KeyError:
                print(f"One of the keys required in the message was missing. {sys.exc_info()}")

        else:
            print("received a malformed message.")


        pass

    def find_left_neighbor(self, tuple_list):
        next_tuple = None
        for index in range(0, len(tuple_list)):
            if tuple_list[index][0] is self.hostname:
                return next_tuple if next_tuple is not None else tuple_list[1]
            else:
                next_tuple = user_tuple[index + 1]
        return None

    def find_right_neighbor(self, tuple_list):
        next_tuple = None
        for user_tuple in tuple_list:
            if user_tuple[0] is self.hostname:
                return prev_tuple if prev_tuple is not None else tuple_list[-1]
            else:
                prev_tuple = user_tuple
        return None