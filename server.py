import sys

from server_network import ServerNetwork
from tracker import Tracker


message_queue = []


def initialize_socket():
    server = ServerNetwork()
    server.server_start()
    return server


def context_resume():
    pass

def main():
    server = ServerNetwork()
    server.server_start()
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
                server.server_side_socket.settimeout(180)
                try:
                    propagation_message = server.server_recv_mesg()
                    if propagation_message['request'] == "end_tweet":
                        if propagation_message['handle'] == dict_message["handle"]:
                            print(f"Received Propagation Termination: {propagation_message}")
                            break
                    else:
                        message_queue.append(propagation_message)
                        continue
                except TimeoutError:
                    print("Propagation failed...")
                    break

                context_resume()
            else:
                server.server_send(message=dict_res, source_ip=src_ip, source_port=src_port)

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt Exception: User Initiated Server Shutdown - Exiting Now.")
        server.server_conn_close()
        sys.exit(0)


if __name__ == '__main__':
    main()
