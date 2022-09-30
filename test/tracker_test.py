from client_network import ClientNetwork
from tracker import Tracker


def main():
    # Test
    tracker = Tracker()

    # Register users
    tracker.register("jason", "192.0.0.1", 5000, 5001, 5002)
    tracker.register("ben", "192.0.0.2", 5003, 5004, 5005)
    tracker.register("mary", "192.0.0.3", 5006, 5007, 5008)
    tracker.get_all_ports()

    # Test Follow
    tracker.follow("jason", "ben")
    tracker.follow("jason", "ben")
    print(tracker.query_handles())

    # Test Drop
    tracker.drop("jason", "ben")
    tracker.drop("jason", "ben")
    tracker.follow("ben", "jason")
    print(tracker.query_handles())

    # Test Exit
    tracker.exit("ben")
    tracker.exit("benj")
    print(tracker.query_handles())

    # Test Logical Ring
    tracker.follow("mary", "ben")
    tracker.follow("jason", "ben")
    tracker.tweet("ben", "Test")


if __name__ == '__main__':
    main()
