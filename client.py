import socket
from network import ClientNetwork


def initialize_server():
    client_multi_socket = ClientNetwork()
    client_multi_socket.connect()

    return client_multi_socket


def main():
    is_running = True
    client_multi_socket = initialize_server()

    while is_running:
        message_to_send = input('> ')
        client_multi_socket.send(message_to_send)

    client_multi_socket.close()


if __name__ == '__main__':
    main()
