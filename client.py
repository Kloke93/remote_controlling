"""
Author: Tomas Dal Farra
Date:
Description: Communication handling module
"""
import socket


class Client:
    """ General client """
    server_port = 5010
    max_buffer = 2048

    def __init__(self, ip):
        """
        Initiates client communication sockets
        :param ip: servers ip
        """
        self.server_ip = ip
        self.server_address = (self.server_ip, Client.server_port)

        # socket
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_client.bind(("0.0.0.0", Client.server_port))           # every udp packet in the port

    def run_client(self):
        """ starts client communication """

        data = self.udp_client.recvfrom(Client.max_buffer)[0]
        return data


class ClientGuest(Client):
    """ Client communications for guest mode """
    pass


class ClientHost(Client):
    """ Client communications for host mode """
    pass


def main():
    """ tests classes """
    c = Client('127.0.0.1')
    c.run_client()


if __name__ == "__main__":
    main()



