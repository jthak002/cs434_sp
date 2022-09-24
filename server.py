from _thread import *

from network import ServerNetwork


def main():
    server = ServerNetwork()
    server.server_start()
    server_is_running = True

    while server_is_running:
        client, address = server.server_side_socket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))

        start_new_thread(server.multi_threaded_client, (client,))
        server.thread_count += 1
        print('Thread Number: ' + str(server.thread_count))

    server.server_side_socket.close()


if __name__ == '__main__':
    main()
