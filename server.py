import sys
import json
from server_network import ServerNetwork
import socket
import argparse
from tracker import Tracker


def main():
    parser = argparse.ArgumentParser(description='TWEETER Server Tracker')
    parser.add_argument('--ip', '-i', type=str, help='specify the host ip (default: 127.0.0.1)',
                        default='127.0.0.1')
    parser.add_argument('--port', '-p', type=int, help='specify the server port (default: 41000)',
                        default=41000)
    args = parser.parse_args()

    server = ServerNetwork(host=args.ip, port=args.port)

    try:
        while True:
            # socket.accept() is a TCP method and not a UDP method --> socket.accept() accepts the incoming connection
            # and TCP 3-Way handshake. What we will do for right now is no-multithreading simple packet accepting.
            # client, address = server.server_side_socket.accept()
            # print('Connected to: ' + address[0] + ':' + str(address[1]))
            raw_msg, src_ip, src_port = server.server_recv_mesg()
            dict_message = server.server_parse_mesg(message=raw_msg, source_ip=src_ip, source_port=src_port)

            # tracker code that uses the json message to respond to user goes here
            # Parsing client request
            dict_res = server.server_route_mesg(dict_message, src_ip, src_port)
            if dict_res["request"] == "send_tweet":
                server.server_send(message=dict_res, source_ip=src_ip, source_port=src_port)
                # server.server_side_socket.settimeout(180)
                try:
                    curr_message, src_ip, src_port = server.server_recv_mesg()

                    if json.loads(curr_message.decode()).get('request', None) == "end_tweet" and json.loads(curr_message.decode()).get('handle', None) == json.loads(raw_msg.decode()).get('handle', None):
                        propagation_message = server.server_parse_mesg(message=raw_msg, source_ip=src_ip, source_port=src_port)
                        propagation_res = server.server_route_mesg(propagation_message, src_ip, src_port)
                        server.server_send(message=propagation_res, source_ip=src_ip, source_port=src_port)
                        continue

                    continue
                except (TimeoutError, socket.timeout):
                    print("Propagation failed...")
                    break
            else:
                server.server_send(message=dict_res, source_ip=src_ip, source_port=src_port)

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt Exception: User Initiated Server Shutdown - Exiting Now.")
        server.server_conn_close()
        sys.exit(0)


if __name__ == '__main__':
    main()
