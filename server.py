from _thread import *

from network import ServerNetwork
from tracker import Tracker


def initialize_socket():
    server = ServerNetwork()
    server.server_start()
    return server


def main():
    server = initialize_socket()
    tracker = Tracker()
    server_is_running = True

    while server_is_running:
        client, address = server.server_side_socket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))

        start_new_thread(server.multi_threaded_client, (client,))
        server.thread_count += 1
        print('Thread Number: ' + str(server.thread_count))

    server.close()


if __name__ == '__main__':
    main()
