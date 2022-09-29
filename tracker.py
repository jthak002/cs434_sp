class Tracker:
    number_of_users = 0
    handles = {}

    def __init__(self):
        pass

    # register @<handle> <IPv4-address> <port>
    def register(self, handle, source_ip, tracker_port, peer_port_left, peer_port_right):
        arr_handles = self.get_all_handles()
        for curr_handle in arr_handles:
            if handle == curr_handle:
                print("Handle already exist in the database!")
                return False

        self.number_of_users += 1
        self.handles[handle] = {"source_ip": source_ip, "tracker_port": tracker_port, "peer_port_left": peer_port_left,
                                "peer_port_right": peer_port_right, "follower": []}

        return True

    def query_handles(self):
        arr_handles = self.get_all_handles()

        return [self.number_of_users, arr_handles]

    # follow @<handlei> @<handlej>
    def follow(self, curr_user_handle, follow_user_handle):
        if curr_user_handle not in self.handles[follow_user_handle]["follower"]:
            self.handles[follow_user_handle]["follower"].append(curr_user_handle)
            self.handles[follow_user_handle]["follower"].sort()

    # drop @<handlei> @<handlej>
    def drop(self, curr_user_handle, follow_user_handle):
        self.handles[follow_user_handle]["follower"].remove(curr_user_handle)

    def tweet(self, curr_user_handle, tweet_str):
        pass

    def end_tweet(self):
        pass

    def exit(self, curr_user_handle):
        self.handles.pop(curr_user_handle)
        self.number_of_users -= 1

        for user_handle in self.handles:
            try:
                self.handles[user_handle]["follower"].remove(curr_user_handle)
            except ValueError:
                pass

    def get_all_handles(self):
        arr_key = []
        for key, value in self.handles.items():
            arr_key.append(key)

        return arr_key


"""
# Test
tracker = Tracker()

# Register users
tracker.register("jason", "192.0.0.1", [5000, 5001, 5002])
tracker.register("ben", "192.0.0.2", [5003, 5004, 5005])
tracker.register("mary", "192.0.0.3", [5006, 5007, 5008])

# Test Follow
tracker.follow("jason", "ben")
tracker.follow("jason", "ben")
# print(tracker.query_handles())

# Test Drop
# tracker.drop("jason", "ben")
# tracker.follow("ben", "jason")
# print(tracker.query_handles())

# Test Exit
# tracker.exit("ben")
# print(tracker.query_handles())

# Test Logical Ring
tracker.follow("mary", "ben")
tracker.follow("jason", "ben")
tracker.tweet("ben", "Test")
"""
