import os
import socket
import json
import time

from logical_network import LogicalNetwork

TRACKER_URL = os.getenv('TRACKER_URL','127.0.0.1')
TRACKER_PORT = int(os.getenv('TRACKER_PORT', '41000'))


class ClientNetwork:
    host: str
    port_tracker: int
    port_peer_left: int
    port_peer_right: int
    socket_tracker: socket.socket
    socket_peer_left: socket.socket
    socket_peer_right: socket.socket
    num_users: int
    user_list: [tuple]
    follower_list: [str]
    handle: str
    logic_network: LogicalNetwork

    def __init__(self, host='127.0.0.1', port_tracker=41001, port_peer_left=41002, port_peer_right=41003):
        """
        Constructor that initializes the client-network object. This class is representative of all the client
        actions that are performed - ever option displayed on the client.py file maps to a function in the class
        :param host: the IP address of the client
        :param port_tracker: the port that is used by the tracker
        :param port_peer_left: the port used for communication with the left neighbour
        :param port_peer_right: the port used for communication with the right neighbour
        """
        print("Initializing the client")
        self.socket_tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_peer_left = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_peer_right = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port_tracker = port_tracker
        self.port_peer_left = port_peer_left
        self.port_peer_right = port_peer_right
        self.user_list = []
        self.num_users = 0
        self.handle = ''
        print(f"Client has been initialized with the IP={self.host}, and ports=[{self.port_tracker},"
              f"{self.port_peer_left},{self.port_peer_right} ]")

    # helper functions
    def _send_message_tracker(self, message_action: str, binary_request: b''):
        """
        this is a private helper function that takes the dictionary containing the message that we want to send to the
        tracker. it usually contains the action to be performed (register, follow, query users etc.) and some additional
        information that is used to perform that action (username_i , username_j for a follow request). The function
        keeps trying until it receives a response from the server, timing out 30s after it initially sends the server a
        message. after it receives a response, it returns to the calling function.

        :param message_action: the action being performed by sending this message.
        :param binary_request: the binary encoded json message (from protocol.txt) that is sent to the tracker.
        :return: this returns a tuple with a binary encoded envelope containing json response from the server.
        """
        raw_message = None
        while True:
            self.socket_tracker.sendto(binary_request, (TRACKER_URL, TRACKER_PORT))
            print(f"sent {message_action} to {TRACKER_URL}:{TRACKER_PORT}")
            self.socket_tracker.settimeout(30)
            try:
                raw_message = self.socket_tracker.recvfrom(1024)
                print(f"Received RAW_MESSAGE={raw_message}")
            except (TimeoutError, socket.timeout):
                print("the previous message to the tracker did not get a response. will try again")
                continue
            break
        return raw_message

    def _process_message_confirm(self, raw_message: tuple[b'', ()], action: str, return_items: list[str] = None):
        """
        this is a private helper function that processes the raw message that is received from the _send_message_tracker
        function. the work flow of this function and the verification steps undertaken by this function are basically:
        1. parse the message and verify it is indeed a valid UDP response - has to be a tuple with the binary payload
        and a tuple with src_ip and src_port.
        2. ensure the source port and sourceip are the TRACKER_PORT and TRACKER_PORT respectively. also, make sure this
        is a response for a valid action you performed on the server; if there were multiple actions requested by the
        client simultaneously, this would be useful. for us this is purely a sanity check.
        3. If the error_code is actually a success, then look into the binary envelope and get the contents.
        4. use the return_items list as a flag to determine if the caller wants some part of the response e.g we want
        the `num_users` and `user_list` from a `query_users` response, the `follower_list` during a `send_tweet`
        response.
        :param raw_message: tuple returned by the socket recvfrom() function with binary payload and
        :param action: the action you wanted to perform for which you got the response from the server
        :param return_items: any items that you got in the response to your request to the tracker. follower list,
        user list num users etc.
        :return:
            return_payload (dict) - dictionary containing the information you requested from the server
            status_code (bool) - a boolean value specifying if the server completed your action successfully or not.
        """
        status_code = False
        return_payload = {}
        if type(raw_message) is tuple and len(raw_message) == 2:
            json_message = raw_message[0].decode()
            src_ip = raw_message[1][0]
            src_port = raw_message[1][1]
            message_json = json.loads(json_message)
            if src_ip == TRACKER_URL and src_port == TRACKER_PORT:
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                if message_json.get('request') == action and \
                        message_json.get('error_code') == 'success':
                    print(f'@{self.host}\'s request for action {action} was processed by the tracker successfully')
                    status_code = True
                    if return_items:
                        for item in return_items:
                            try:
                                return_payload[item] = message_json.get(item)
                            except KeyError:
                                print(f'could not find {item} in the raw_message response for \'{action}\'')
                elif message_json.get('request') == action and \
                        message_json.get('error_code') == 'failure':
                    print(f"Tracker responded with a failure message when performing {action} for {self.handle}")
                else:
                    print("received malformed message - printing to console")
                    print(raw_message)
            else:
                print("received unknown message - exiting now")
        else:
            print("error case")
        return return_payload, status_code

    def setup(self):
        """
        The setup function that binds the sockets that belong to this class to the respective ports that are defined in
        the constructor. prints errors if binding is not possible. This step also initializes the
        logical_network (LogicalNetwork) class that handles the P2P functionality.
        :return: None
        """
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
        print("Setup the LogicalNetwork Object for this client -->")
        self.logic_network = LogicalNetwork(hostname=self.host, port_tracker=self.port_tracker,
                                            port_left=self.port_peer_left, port_right=self.port_peer_right,
                                            left_socket=self.socket_peer_left, right_socket=self.socket_peer_right,
                                            handle=self.handle)

    def client_register(self, handle: str):
        """
        function to compile the register function message and confirm the registration of the function. also, sets the
        handle is the server responds for a successful registration for the function.
        :param handle: the handle tyou want to register - has to not be currently logged in.
        :return: None
        """
        dict_message = {'request': 'register', 'handle': handle, 'source_ip': self.host,
                        'tracker_port': self.port_tracker, 'peer_port_left': self.port_peer_left,
                        'peer_port_right': self.port_peer_right}
        print(f"Compiling the REGISTER REQUEST=> {dict_message}")
        binary_request_message = json.dumps(dict_message).encode()
        raw_message = self._send_message_tracker(message_action='register', binary_request=binary_request_message)
        _, status_code = self._process_message_confirm(action='register', raw_message=raw_message, return_items=None)
        if status_code:
            self.handle = handle
            print(f"The handle {handle}@{self.host}:{self.port_tracker} has registered successfully!")
            self.logic_network.set_handle(self.handle)

    def client_query_handles(self):
        """
        Query the list of active users from the user. display the list if the server responds with True.
        :return:
        """
        if self.handle == '':
            print("cannot query user w/o registering. please register before sending the query command")
            return
        dict_message = {'request': 'query_users'}
        print(f"Compiling the QUERY USERS REQUEST=> {dict_message}")
        binary_request_message = json.dumps(dict_message).encode()
        raw_message = self._send_message_tracker(message_action='query_users', binary_request=binary_request_message)
        requested_items, status_code = self._process_message_confirm(action='query_users', raw_message=raw_message,
                                                                     return_items=['num_users', 'user_list'])
        if status_code:
            self.num_users = requested_items.get('num_users', 0)
            print(f"number of users online => {self.num_users}")
            self.user_list = requested_items.get('user_list', [])
            print_string = "The list of users is:\n"
            for user in self.user_list:
                print_string = print_string + user + '\n'
            print(print_string)
        else:
            print("query_users failed. try again later.")

    def client_follow_handle(self, my_handle:str, peer_handle: str):
        """
        function to follow a particular user from the list of online users.
        :param my_handle: user's own handle
        :param peer_handle: the handle who you want to follow.
        :return:
        """
        action = 'follow_user'
        if self.handle == '':
            print("cannot follow user w/o registering. please register before sending the follow command")
            return
        if self.handle != my_handle:
            print("you are trying to impersonate another user - will not register.")
            return
        dict_message = {'request': 'follow_user', 'username_i': self.handle, 'username_j': peer_handle}
        print(f"Compiling the FOLLOW HANDLE REQUEST=> {dict_message}")
        binary_request_message = json.dumps(dict_message).encode()
        raw_message = self._send_message_tracker(message_action=action, binary_request=binary_request_message)
        _, status_code = self._process_message_confirm(action=action, raw_message=raw_message, return_items=None)

    def client_drop_handle(self, peer_handle: str):
        """
        function to send the drop message.
        :param peer_handle: the handle fo the suer you want to stop following.
        :return:
        """
        action = 'drop_user'
        if self.handle == '':
            print("cannot drop user w/o registering. please register before sending the drop command")
            return
        dict_message = {'request': 'drop_user', 'username_i': self.handle, 'username_j': peer_handle}
        print(f"Compiling the DROP HANDLE REQUEST=> {dict_message}")
        binary_request_message = json.dumps(dict_message).encode()
        raw_message = self._send_message_tracker(message_action=action, binary_request=binary_request_message)
        _, status_code = self._process_message_confirm(raw_message=raw_message, action=action, return_items=None)

    def client_exit_handle(self):
        """
        the function that calls the exit functionality and exits the ring based on the response of the server. if the
        server returns a failure, aborts the exit process. the server returns a blanket abort if there is a tweet
        propagation going on.
        :return:
        """
        action = 'exit'
        if self.handle == '':
            print("user has not registered yet - can exit cleanly.")
            return
        dict_message = {'request': 'exit', 'username': self.handle}
        print(f"Compiling the EXIT HANDLE REQUEST=> {dict_message}")
        binary_request_message = json.dumps(dict_message).encode()
        raw_message = self._send_message_tracker(message_action=action, binary_request=binary_request_message)
        _, status_code = self._process_message_confirm(raw_message=raw_message, action=action, return_items=None)
        if status_code:
            self.close()
        else:
            print("cannot exit now -> a tweet is being propagated in the logical ring that you're a part of.")

    def client_tweet_out(self, tweet_message:str):
        """
        sends the message to the server letting it know there is a tweet propagation happening. server responds with a
        follower list and denies all exit requests of the followers unless the tweet has been propagated.
        :param tweet_message: contents of the tweet
        :return:
        """
        if self.handle == '':
            print("cannot tweet w/o registering. please register before sending the `tweet` command")
            return
        action = 'send_tweet'
        print(f"-->Tweeting out {tweet_message} from {self.handle}@{self.handle} ")
        dict_message = {'request': action, 'handle': self.handle}
        print(f"Compiling the {action} Request=> {dict_message}")
        binary_request_message = json.dumps(dict_message).encode()
        raw_message = self._send_message_tracker(message_action=action, binary_request=binary_request_message)
        return_items, _ = self._process_message_confirm(action=action, raw_message=raw_message,
                                                     return_items=['follower_list'])
        # creating the logical ring and propagate tweet
        self.client_tweet_out_auxillary(tweet_message=tweet_message, follower_list=return_items['follower_list'])
        # tweet propagation completed/timed-out --> proceed now.
        action = 'end_tweet'
        print(f"-->right_neighbor confirmed, propagation of tweet.")
        dict_message = {'request': action, 'handle': self.handle}
        print(f"Compiling the {action} Request=> {dict_message}")
        binary_request_message = json.dumps(dict_message).encode()
        raw_message = self._send_message_tracker(message_action=action, binary_request=binary_request_message)
        self._process_message_confirm(action=action, raw_message=raw_message)

    def client_tweet_out_auxillary(self, tweet_message: str, follower_list: []):
        """
        the function that actually initiates the tweet propagation using the self.logical_network(LogicalNetwork)
        object. verifies the tweet has been propagated by waiting for the right neighbor to send the tweet to the user.
        the tweet sender is also able to process and forward tweets from other users while it waits for its own tweet to
        come back to it.
        :param tweet_message: the string that has the message.
        :param follower_list: list of followers returned in response to the
        :return:
        """
        if len(follower_list):
            # if follower_list > 0, only then create logical ring
            print("-->creating a logical ring of {} followers and propagating tweet")
            self.logic_network.tweet_message(message_string=tweet_message, follower_list=follower_list)
        else:
            # if follower_list=0, just display the tweet and tell the server that the tweet broadcast has completed.
            print("-->user does not have followers - tweet will only be visible to self.")
            self.logic_network.print_tweet(message=tweet_message, src_handle=self.handle)

    def client_wait_for_tweet(self, wait_timeout: int = 5):
        """
        the function that is called by the non_interactive() loop that repeatedly calls the process_and_forward function,
        which listens on the peer_port_right until a send_tweet message is received. uses the follower_list to determine
        the left-right neighbors to propogate and confirm the propagation of the tweet.
        :param wait_timeout: custom timeout to change the amount of time the socket should wait.
        :return:
        """
        if self.handle == '':
            # no registration - cannot wait for tweet.
            return
        self.logic_network.process_and_forward_tweet(tweet_recv_timeout=wait_timeout)

    def close(self):
        """
        function that ends and unbinds the socket freeing up the ports gracefully.
        :return:
        """
        self.socket_tracker.close()
        self.socket_peer_left.close()
        self.socket_peer_right.close()
