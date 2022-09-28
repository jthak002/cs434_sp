import sys

from server_network import ServerNetwork
from tracker import Tracker


def initialize_socket():
    server = ServerNetwork()
    server.server_start()
    return server


def main():
    server = ServerNetwork()
    server.server_start()
    try:
        while True:
            # socket.accept() is a TCP method and not a UDP method --> socket.accept() accepts the incoming connection
            # and TCP 3-Way handshake. What we will do for right now is no-multithreading simple packet accepting.
            # client, address = server.server_side_socket.accept()
            # print('Connected to: ' + address[0] + ':' + str(address[1]))
            raw_msg, src_ip, src_port = server.server_recv_mesg(test_timeout=10)
            dict_message = server.server_parse_mesg(message=raw_msg, source_ip=src_ip, source_port=src_port)

            # tracker code that uses the json message to respond to user goes here
            # Parsing client request
            dict_res = server.server_route_mesg(dict_message)
            server.server_send(message=dict_res, source_ip=src_ip, source_port=src_port)

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt Exception: User Initiated Server Shutdown - Exiting Now.")
        server.server_conn_close()
        sys.exit(0)


if __name__ == '__main__':
    main()
