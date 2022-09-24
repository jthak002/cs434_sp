import socket
from _thread import *


# Global
server_side_socket = socket.socket()
host = socket.gethostname()
port = 5000
thread_count = 0


def server_start():
    try:
        server_side_socket.bind((host, port))
    except socket.error as e:
        print(str(e))


    server_side_socket.listen(5)
    print('Server has started... Socket is listening...')


def multi_threaded_client(connection):
    connection.send(str.encode('Server is working:'))

    while True:
        data = connection.recv(2048)
        response = 'Message Received: ' + data.decode('utf-8')

        if not data:
            break

        connection.sendall(str.encode(response))

    connection.close()


def main():
    global thread_count, server_side_socket

    server_start()

    while True:
        client, address = server_side_socket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))

        start_new_thread(multi_threaded_client, (client,))
        thread_count += 1
        print('Thread Number: ' + str(thread_count))

    server_side_socket.close()


if __name__ == '__main__':
    main()
