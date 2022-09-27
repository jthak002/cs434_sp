class Tracker:
    number_of_users = 0
    handles = {}
    follow = {}
    logical_ring = []

    def __init__(self):
        pass

    def register(self, handle, ip_address, port):
        self.number_of_users += 1
        self.handles[handle] = {"ip_address": ip_address, "port": port, "follower": []}

    def query_handles(self):
        return [self.number_of_users, self.handles]

    def follow(self, curr_user_handle, follow_user_handle):
        if curr_user_handle not in self.handles[follow_user_handle]["follower"]:
            self.handles[follow_user_handle]["follower"].append(curr_user_handle)
            self.handles[follow_user_handle]["follower"].sort()

    def drop(self, curr_user_handle, follow_user_handle):
        self.handles[follow_user_handle]["follower"].remove(curr_user_handle)

    def tweet(self, curr_user_handle, tweet_str):
        logical_ring_list = self.handles[curr_user_handle]['follower']
        for follower in logical_ring_list:
            print(follower)

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
