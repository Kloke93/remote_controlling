"""
Author: Tomas Dal Farra
Date:
Description:
"""
import logging
import threading
import socket
import ssl
import time


class ActiveHost:
    """ Class with all active hosts """

    def __init__(self):
        """ initializes the dictionary that contains all hosts """
        # dictionary format: {id: socket}
        self.hosts = {}

    @staticmethod
    def is_id(host_id: str) -> bool:
        """
        Checks if hosts id is a valid id
        :param host_id: hosts id
        :return: if the id is valid
        """
        # ID_LENGTH = 15
        # id in format: ddd.ddd.ddd.ddd
        if isinstance(host_id, str) and host_id[3::4] == "..." and host_id.replace('.', '').isdigit():
            return True
        else:
            return False

    def add(self, host_id: str, skt: socket.socket) -> bool:
        """
        Adds a new active host
        :param host_id: the unique id to identify the host
        :param skt: this host socket to communicate
        :return: if the host was appended successfully
        """
        if self.is_id(host_id):
            self.hosts[host_id] = skt
            return True
        else:
            return False

    def pop(self, host_id: str) -> socket.socket:
        """
        Removes a host (is not active)
        :param host_id: the unique id to identify the host
        :return: removed hosts
        """
        return self.hosts.pop(host_id, None)

    def get(self, host_id: str) -> socket.socket:
        """
        Gets the host's socket according to their id
        :param host_id: the unique id to identify the host
        :return: corresponding host's socket
        """
        return self.hosts.get(host_id)


class Server:
    """ Defines the server to communicate with the clients """
    ip = '0.0.0.0'
    port = 5678
    listen_size = 5
    commands = ["HOSTING", "GUESTING", "REQUEST", "ABORT", "RETRY", "CONNECT"]
    cert = "certificate.crt"
    key = "privatekey.key"

    def __init__(self):
        """ initializes server tcp socket and tls context """
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(Server.cert, Server.key)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def validate(data: str) -> bool:
        """
        Validates protocol in data
        :param data: data from the client to validate its protocol
        :return: if data is valid according to the protocol
        """
        split = data.split()
        if (split[0] not in Server.commands) or (data[-1] != ';'):
            return False
        elif split[0] == "HOSTING" and len(split) == 2:
            return True
        elif split[0] == "GUESTING" and len(split) == 3:
            return True
        else:
            return False

    @staticmethod
    def handle_client(client_sock: socket.socket, client_addr: tuple):
        """
        Handles client connection
        :param client_sock: Socket to communicate with the client
        :param client_addr: Client address
        """
        try:
            pass
        except socket.error as err:
            logging.error(err)
        finally:
            client_sock.close()

    def run_server(self):
        """ Runs server """
        threads = []
        next_name = 1
        try:
            self.server.bind((Server.ip, Server.port))
            self.server.listen(Server.listen_size)
            secure_server = self.context.wrap_socket(self.server, server_side=True)
            while True:
                client_sock, client_addr = secure_server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_sock, client_addr),
                                          name=f"Thread{next_name}")
                thread.start()

        except socket.error as err:
            logging.critical(err)
        finally:
            self.server.close()
            for thread in threads:
                thread.join()


if __name__ == "__main__":
    pass
