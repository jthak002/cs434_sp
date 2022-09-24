import socket


def server_program():
    # get the hostname & initiate port no above 1024
    host = socket.gethostname()
    port = 5000

    # get instance
    server_socket = socket.socket()

    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(1)

    # accept new connection
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

    while True:
        # receiving data stream, but it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()

        # if data is not received break
        if not data:
            break

        print(f"From connected user: " + str(data))
        data = input(' -> ')
        conn.send(data.encode())

    # close the connection
    conn.close()


if __name__ == '__main__':
    server_program()
