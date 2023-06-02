"""
Author: Tomas Dal Farra
Date:
Description: Communication handling module
"""
import logging
import socket
import ssl


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

        # create ssl context
        context = ssl.create_default_context()
        # allow self-signed certificates
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        # secured tcp socket
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secure_client = context.wrap_socket(tcp_client, server_hostname=ip)

        # udp sockets
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_client.bind(("0.0.0.0", Client.server_port))           # every udp packet in the port

    def run_client(self):
        """ starts client communication """
        try:
            self.secure_client.connect((self.server_ip, 5010))
            self.secure_client.send('hola'.encode())
            print(self.secure_client.recv().decode())
        except socket.error as err:
            logging.critical(err)
        finally:
            self.secure_client.close()
            self.udp_client.close()


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



