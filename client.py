"""
Author: Tomas Dal Farra
Date: 04/06/2023
Description: Client communication handling module
"""
import logging
import socket
import ssl


class Client:
    """ General client """
    server_port = 5010
    max_buffer = 2048
    # available commands that arrive to client
    commands = ["GUESTING", "REQUEST", "ABORT", "RETRY", "CONNECT"]

    def __init__(self, ip, user_id):
        """
        Initiates client communication sockets
        :param ip: servers ip
        :param user_id: unique id of the user
        """
        self.id = user_id
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

    def run_client(self):
        """ starts client communication, connects to server and sends present """
        # try
        self.secure_client.connect((self.server_ip, 5010))
        self.secure_client.send(f'PRESENT {self.id};;'.encode())
        # except socket.error
        # finally

    @staticmethod
    def protocol(command: str, *args: str) -> str:
        """
        Converts command and arguments to the appropriate protocol
        :param command: command according to protocol
        :param args: arguments of the command according to protocol
        :return: appropriate message over protocol
        """
        # protocol:
        # COMMAND arg1 arg2 ... arg;;
        command = command.upper()
        args = " ".join(args)
        return f"{command} {args};;"

    @staticmethod
    def valid(data: str) -> list:
        """
        Validates protocol in data and returns it ordered
        :param data: data from the client to validate its protocol
        :return: if data is valid returns list with command and arguments, if not returns empty list
        """
        split = data.split()
        if (split[0] not in Client.commands) or (data[-2:] != ';'):
            return []
        elif split[0] == "GUESTING" and len(split) == 3:
            # the first argument is a text writing what is the second item telling
            # GUESTING id/password id/password
            return [split[0], split[1], split[2][:-2]]
        elif split[0] == "REQUEST" and len(split) == 2:
            # REQUEST id/password
            return [split[0], split[1][:-2]]
        elif split[0] == "ABORT" and len(split) == 2:
            # ABORT reason
            return [split[0], split[1][:-2]]
        elif split[0] == "CONNECT" and len(split) == 3:
            # CONNECT ip port
            return [split[0], split[1], split[2][:-2]]
        else:
            return []


class ClientGuest(Client):
    """ Client communications for guest mode """

    def run_guest(self):
        try:
            super().run_client()
            self.secure_client.recv(Client.max_buffer)
        except socket.error as err:
            logging.critical(err)
        finally:
            self.secure_client.close()


class ClientHost(Client):
    """ Client communications for host mode """

    def run_host(self):
        try:
            super().run_client()
        except socket.error as err:
            logging.critical(err)
        finally:
            self.secure_client.close()


def main():
    """ tests classes """
    c = Client('127.0.0.1')
    c.run_client()


if __name__ == "__main__":
    main()



