import socket
from network import ClientNetwork, response_spliter

ACK = 0
UPDATE_RING = 1


# Key-Value pair how the tweet should be forwarded
tweet_forward = {}


def initialize_server():
    client_multi_socket = ClientNetwork()
    client_multi_socket.connect()

    return client_multi_socket


def server_response_parser(message_to_send, response_list):
    if int(response_list[0]) == ACK:
        if message_to_send == response_list[1]:
            print("Message Sent Successfully! ")
        else:
            print("Message Corrupted! ")
    elif int(response_list[1]) == UPDATE_RING:
        print(response_list)


def main():
    client_multi_socket = initialize_server()
    is_running = True

    while is_running:
        message_to_send = input('> ')
        response = client_multi_socket.send(message_to_send).decode('utf-8')
        response_list = response_spliter(response)

        server_response_parser(message_to_send, response_list)

    client_multi_socket.close()


if __name__ == '__main__':
    main()
