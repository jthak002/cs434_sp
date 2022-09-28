from network import ClientNetwork


def main():
    client = ClientNetwork()
    client.setup()
    client.client_register('jthak002')

if __name__ == '__main__':
    main()
