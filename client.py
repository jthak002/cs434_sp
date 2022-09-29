from client_network import ClientNetwork


def main():
    client = ClientNetwork()
    client.setup()
    client.client_register('jthak002')
    client.client_register('isahoo1')
    client.client_register('jthak002')
    client.client_query_handles()
if __name__ == '__main__':
    main()
