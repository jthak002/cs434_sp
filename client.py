from client_network import ClientNetwork
import re
import argparse

register_rexp = re.compile('^register [a-zA-Z0-9]{1,15}$')
query_rexp = re.compile('^query users$')
follow_rexp = re.compile('^follow [a-zA-Z0-9]{1,15}\ [a-zA-Z0-9]{1,15}$')
drop_rexp = re.compile('^drop [a-zA-Z0-9]{1,15}$')
tweet_cmd = 'tweet'

client: ClientNetwork


def non_interactive_function():
    client.client_wait_for_tweet()


def interactive_function():
    print('\n=============INTERACTIVE_MODE=============')
    input_cmd = input("enter the command:\n1. register <handle>\n2. query users\n3. follow <user_i> <user_j>\n"
                      "4. drop <user>\n5. tweet\n6. back\n7. exit\n")
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    if register_rexp.match(input_cmd.strip()):
        handle = input_cmd.split()[1]
        client.client_register(handle)
        return
    elif query_rexp.match(input_cmd.strip()):
        client.client_query_handles()
        return
    elif follow_rexp.match(input_cmd.strip()):
        handle_i = input_cmd.split()[1]
        handle_j = input_cmd.split()[2]
        client.client_follow_handle(handle_i, handle_j)
    elif drop_rexp.match(input_cmd.strip()):
        handle = input_cmd.split()[1]
        client.client_drop_handle(handle)
        return
    elif input_cmd.strip() == 'tweet':
        tweet_message = input("Enter the message you want to tweet! ")
        client.client_tweet_out(tweet_message=tweet_message)
    elif input_cmd.strip() == 'back':
        return
    elif input_cmd.strip() == 'exit':
        client.client_exit_handle()
        client.close()
        exit(0)
    else:
        print("invalid command - try again.")
        interactive_function()
        return


def work_loop():
    try:
        print('==========================================')
        print("Press Ctrl + C to go into interactive mode <i.e. to enter commands>")
        while True:
            non_interactive_function()
    except KeyboardInterrupt:
        try:
            interactive_function()
        except KeyboardInterrupt:
            ## insert exit() logic here.
            print("User has chosen to exit the program. exiting now()")
            exit(0)
    work_loop()


def main():
    parser = argparse.ArgumentParser(description='TWEETER Client')
    parser.add_argument('--ip', '-i', type=str, help='specify the host ip (default: 127.0.0.1)',
                        default='127.0.0.1')
    parser.add_argument('--tracker_port', '-tp', type=int, help='specify the tracker port (default: 5001)',
                        default=41001)
    parser.add_argument('--left_port', '-lp', type=int, help='specify the left port (default: 5002)',
                        default=41002)
    parser.add_argument('--right_port', '-rp', type=int, help='specify the right port (default: 5003)',
                        default=41003)
    args = parser.parse_args()
    print("Welcome to Tweeter!")
    global client
    client = ClientNetwork(host=args.ip, port_tracker=args.tracker_port, port_peer_left=args.left_port,
                           port_peer_right=args.right_port)
    client.setup()
    work_loop()


if __name__ == '__main__':
    main()
