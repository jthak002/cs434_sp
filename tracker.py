class Tracker:
    number_of_users = 0
    handles = {}

    def __init__(self):
        pass

    # register @<handle> <IPv4-address> <port>
    def register(self, handle, source_ip, tracker_port, peer_port_left, peer_port_right):
        if not self.check_and_verify(handle, source_ip, (tracker_port, peer_port_left, peer_port_right)):
            self.number_of_users += 1
            self.handles[handle] = {"source_ip": source_ip, "port": (tracker_port, peer_port_left, peer_port_right),
                                    "follower": []}
            return True
        else:
            print("Handle already exist in the database!")
            return False

    def query_handles(self):
        arr_handles = self.get_all_handles()

        return [self.number_of_users, arr_handles]

    # follow @<handlei> @<handlej>
    def follow(self, curr_user_handle, follow_user_handle):
        if curr_user_handle not in self.handles[follow_user_handle]["follower"]:
            self.handles[follow_user_handle]["follower"].append(curr_user_handle)
            self.handles[follow_user_handle]["follower"].sort()
            print("@" + curr_user_handle + " has successfully followed @" + follow_user_handle)
        else:
            print("@" + curr_user_handle + " has already followed @" + follow_user_handle)

    # drop @<handlei> @<handlej>
    def drop(self, curr_user_handle, follow_user_handle):
        try:
            self.handles[follow_user_handle]["follower"].remove(curr_user_handle)
        except ValueError:
            print("@" + curr_user_handle + "did not follow @" + follow_user_handle)

        print("@" + curr_user_handle + "has stop following @" + follow_user_handle)

    def tweet(self, curr_user_handle, tweet_str):
        pass

    def end_tweet(self):
        pass

    def exit(self, curr_user_handle):
        try:
            self.handles.pop(curr_user_handle)
        except KeyError:
            print("@" + curr_user_handle + " does not exist in the database")

        self.number_of_users -= 1

        for user_handle in self.handles:
            try:
                self.handles[user_handle]["follower"].remove(curr_user_handle)
            except ValueError:
                pass

        print("Successfully removed @" + curr_user_handle)

    def get_all_handles(self):
        arr_key = []
        for key, value in self.handles.items():
            arr_key.append(key)

        return arr_key

    def check_and_verify(self, username, ip=None, port=None):
        if username in self.handles:
            if ip and port:
                return ip == self.handles[username]['source_ip'] and port == self.handles[username]['port'][0]
            elif ip or port:
                return False
            # Check if client exist in dictionary
            else:
                return True
        else:
            return False
