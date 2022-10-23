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
    port_tracker: int
    port_left: int
    port_right: int
    handle: str

    def __init__(self, left_socket, right_socket, hostname, port_tracker, port_left, port_right, handle):
        self.left_socket = left_socket
        self.right_socket = right_socket
        self.hostname = hostname
        self.port_tracker = port_tracker
        self.port_left = port_left
        self.port_right = port_right
        self.handle = handle
        self._tuple = (hostname, port_tracker, port_left, port_right, handle)

    # Support functions
    @staticmethod
    def _send_success_message(snd_socket: socket.socket, for_request: str, destination: str, port: int, success=True,
                              additional_args=None):
        """
        a helper function that sends a success/failure based on the value of `success` from the `snd_socket`
        socket.socket object to `destination` and `port` by compiling the parameters into a dictionary and including the
        `additional_args` dictionary into the message.
        success message from the dictionary that is compiled using
        :param snd_socket: socket object to send the message from.
        :param for_request: the field to be used to populate the `request` portion of the JSON message
        :param destination: IP of destination
        :param port: port of the destination
        :param success: whether `error_code` should show `success` or `failure`
        :param additional_args: Addtional arguments for the body of the JSON message
        :return:
        """
        dict_message = {'request': for_request, 'error_code': 'success' if success else 'failure'}
        if additional_args is not None and type(additional_args) == dict:
            for key, value in additional_args.items():
                dict_message[key] = value
        snd_socket.sendto(json.dumps(dict_message).encode(), (destination, port))

    def _verify_sender(self, message_sender_tuple: tuple[str, int], addressee_tuple: tuple[str, int]):
        """
        verify if the tuple specified in the message matches the host:port we are expecting a message from.
        :param message_sender_tuple: tuple containing host:port
        :param addressee_tuple: tuple containing host:port
        :return:
        """
        return message_sender_tuple[0] == addressee_tuple[0] and message_sender_tuple[1] == addressee_tuple[1]

    def _verify_success_response(self, request_type: str, raw_message: tuple[b'', tuple[str, int,]]):
        """
        verify if the message received from another client indicates successful transmission or not
        :param request_type: request type --> to verify if the message received is for the same action.
        :param raw_message: the raw message that we get from the reading the socket contents using recvfrom()
        :return: True or False based on the action on the remote client was successful.
        """
        try:
            mesg_payload = json.loads(raw_message[0].decode())
            mesg_request_type = mesg_payload.get('request')
            mesg_request_bool = True if mesg_request_type == request_type else False
            error_code = mesg_payload.get('error_code')
            error_code_bool = True if error_code == 'success' else False
            return mesg_request_bool and error_code_bool
        except KeyError:
            print("encountered malformed message while checking verifying success response of message")
            return False

    def print_tweet(self, message: str, src_handle: str):
        """
        function to pretty print the tweet.
        :param message: tweet message
        :param src_handle: the handle that originated the tweet.
        :return:
        """
        print("\n#############################################")
        print('\n' + src_handle + " tweeted: " + message + '\n')

    def set_handle(self, handle):
        """
        function to set the handle - when the logical_network object in ClientNetwork is initialized, it is setup with
        no handle - this function is called after the ClientNetwork() function is called.
        :param handle: tweeter handle.
        :return:
        """
        self.handle = handle
        self._tuple = (self.hostname, self.port_tracker, self.port_left, self.port_right, self.handle)

    # Logical Ring Functions
    def find_left_neighbor(self, follower_list, owner_tuple, my_list=False):
        """
        Find the left neighbour given the follower list. the left neighbour of the last member of the list is the owner
        i.e. the person all the people in the list are following.
        :param follower_list: list of tuples of all users
        :param owner_tuple: tuple of the followee of all users in the follower_list
        :param my_list: flag that this function is being called by the owner of the list - they won't be int he list, so
        their left neighbour is the first person in the list.
        :return: tuple containing details of the left neighbour
        """
        # for the owner of the follower list the left neighbor will be the 1st person in
        # the alphabetically sorted list
        if my_list:
            return follower_list[0] if len(follower_list) > 0 else None
        # for everyone else navigating the list.
        for index in range(0, len(follower_list)):
            if follower_list[index][4] == self.handle:
                # for the last person on any follower list, the left neighbor will be the owner in that list.
                if index is len(follower_list) - 1:
                    return owner_tuple
                # for everyone else it will be the next person in the list
                else:
                    return follower_list[index + 1]
        # error case
        print("error_case: traversed whole follower_list but did not find the left_neighbor.")
        return None

    def find_right_neighbor(self, follower_list, owner_tuple, my_list=False):
        """
        Find the right neighbour given the follower list. the right neighbour of the first member of the list is the
        owner i.e. the person all the people in the list are following.
        :param follower_list: list of tuples of all users
        :param owner_tuple: tuple of the followee of all users in the follower_list
        :param my_list: flag that this function is being called by the owner of the list - they won't be in the list, so
        their right neighbour is the first person in the list.
        :return: tuple containing details of the right neighbour
        """
        # for the owner of the follower list the right neighbor will be the last person in
        # the alphabetically sorted list
        if my_list:
            return follower_list[-1] if len(follower_list) > 0 else None
        prev_tuple = self._tuple
        for user_tuple in follower_list:
            if user_tuple[4] == self.handle:
                return prev_tuple if prev_tuple is not None else owner_tuple
            else:
                prev_tuple = user_tuple
        # error case
        print("error_case: traversed whole follower_list but did not find the right_neighbor.")
        return None

    # Tweet Actions
    def tweet_message(self, message_string: str, follower_list: []):
        # 1. Send the tweet down the chain to be propagated.
        dict_message = {'request': 'send_tweet', 'chain_owner': self._tuple, 'follower_list': follower_list,
                        'tweet': message_string}
        print(f"Compiling the SEND_TWEET REQUEST=> {dict_message}")
        binary_request = json.dumps(dict_message).encode()
        next_peer = self.find_left_neighbor(follower_list=follower_list, owner_tuple=self._tuple, my_list=True)
        print(f"found the LEFT_PEER with the information {next_peer}")
        while True:
            self.left_socket.sendto(binary_request, (next_peer[0], next_peer[3]))
            self.left_socket.settimeout(30)
            try:
                raw_message = self.left_socket.recvfrom(1024)
                verify_status = self._verify_success_response(raw_message=raw_message, request_type='send_tweet')
                verify_sender = self._verify_sender(message_sender_tuple=raw_message[1], addressee_tuple=(next_peer[0],
                                                                                                          next_peer[3]))
                if verify_status and verify_sender:
                    print(f"LEFT_PEER {next_peer[4]}@{next_peer[0]}:{next_peer[3]} CONFIRMED receipt of tweet.")
                    pass
                else:
                    if verify_status:
                        print("SEND_TWEET received a success message from another source than expected.")
                        continue
                    if verify_sender:
                        print("SEND_TWEET received a message from another message than what was expected.")
                    print(f"SEND_TWEET: DEBUG: {raw_message}")
                    continue
            except (TimeoutError, socket.timeout):
                print(f"the previous message to the peer {next_peer[0]}:{next_peer[3]} did not get a response. "
                      f"will try again")
                continue
            break
        # 2. listening on the right port if the last peer in line sends a correct response. Will wait
        # PROPAGATION_TIMEOUT mins
        self.right_socket.settimeout(PROPAGATION_TIMEOUT)
        retries = 0
        while retries < PROPAGATION_RETRIES:
            try:
                prop_confirm = self.right_socket.recvfrom(1024)
                prop_confirm_message = json.loads(prop_confirm[0].decode())
                if prop_confirm_message.get('request', None) == 'send_tweet':
                    chain_owner_tuple = prop_confirm_message.get('chain_owner', (None, None, None, None, None))
                    if chain_owner_tuple[0] == self._tuple[0] and chain_owner_tuple[1] == self._tuple[1] and \
                            chain_owner_tuple[2] == self._tuple[2] and chain_owner_tuple[3] == self._tuple[3] and \
                            chain_owner_tuple[4] == self._tuple[4]:
                        print('TWEET PROPAGATED SUCCESSFULLY!')
                        self.print_tweet(message=message_string, src_handle=self.handle)
                        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                        self._send_success_message(for_request='send_tweet',
                                                             success=True, destination=prop_confirm[1][0],
                                                             port=prop_confirm[1][1], additional_args=None,
                                                             snd_socket=self.right_socket)
                        return True
                    else:
                        print("Received a TWEET message with another "
                              "`chain_owner`: {}.".format(prop_confirm_message.get('chain_owner', None)))
                        # todo: process this tweet from another user.
                        self.process_and_forward_tweet(bypass_recv=True, raw_message=prop_confirm)
                        continue
                else:
                    print(f"Received an unexpected message AFTER SEND_TWEET: {prop_confirm}")
            except (TimeoutError, socket.timeout):
                print(f"Encountered TIMEOUT while propagating the tweet - Will try again."
                      f" Retry({retries}/{PROPAGATION_RETRIES}) ")
                retries += 1
                pass
        return False

    def process_and_forward_tweet(self, bypass_recv=False, raw_message: tuple[b'', tuple[str, int]] = None,
                                  tweet_recv_timeout: int = 5):
        recv_tweet = None
        if not bypass_recv:
            try:
                self.right_socket.settimeout(tweet_recv_timeout)
                recv_tweet = self.right_socket.recvfrom(1024)
            except (TimeoutError, socket.timeout):
                return
        message = raw_message if bypass_recv else recv_tweet
        sender = message[1]
        self._send_success_message(for_request='send_tweet', success=True, destination=sender[0], port=sender[1],
                                   snd_socket=self.right_socket)

        tweet_payload = json.loads(message[0].decode())
        next_peer = None
        tweet_text = None
        tweet_owner = None
        if tweet_payload.get('request', None) == 'send_tweet':
            try:
                print(f'tweet_payload --> {tweet_payload}') # remove after done.
                tweet_owner = tweet_payload.get('chain_owner')
                tweet_text = tweet_payload.get('tweet')
                tweet_owner_follower_list = tweet_payload.get('follower_list')
                print(f"received tweet-message from {tweet_owner[4]}@{tweet_owner[0]} --> {tweet_payload}")
                next_peer = self.find_left_neighbor(follower_list=tweet_owner_follower_list,
                                                    owner_tuple=tweet_owner, my_list=False)
            except KeyError:
                print(f"One of the keys required in the message was missing. {sys.exc_info()}")
            while True:
                # forward the raw message from the previous sender to the new one.
                self.left_socket.sendto(message[0], (next_peer[0], next_peer[3]))
                self.left_socket.settimeout(30)
                try:
                    raw_message = self.left_socket.recvfrom(1024)
                    print(f'received raw_message = {raw_message}')
                    if self._verify_success_response(request_type='send_tweet', raw_message=raw_message):
                        self.print_tweet(message=tweet_text, src_handle=tweet_owner[4])
                        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                        break
                    else:
                        continue
                except (TimeoutError, socket.timeout):
                    print(f"the previous message to the peer {next_peer[0]}:{next_peer[1]} did not get a response. "
                          f"will try again")
                    continue
        else:
            print("received a malformed message.")