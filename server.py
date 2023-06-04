"""
Author: Tomas Dal Farra
Date: 04/06/2023
Description: Implementation of the server for Remote-Controlling
"""
import logging
import threading
import socket
import ssl
import time
import string
import select


logging.basicConfig(
     filename='server.log',
     level=logging.INFO,
     format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
 )
CHARS = string.ascii_lowercase + string.digits


class Hosts:
    """ Class with all active hosts """
    id_length = 12

    def __init__(self):
        """ initializes the dictionary that contains all hosts """
        # dictionary format: {id: (socket, addr)}
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
        # if isinstance(host_id, str) and host_id[3::4] == "..." and host_id.replace('.', '').isdigit():
        #     return True
        # else:
        #     return False
        if len(host_id) != Hosts.id_length:
            return False
        for char in host_id:
            if char not in CHARS:
                return False
        return True

    def add(self, host_id: str, skt: socket.socket, addr: tuple) -> bool:
        """
        Adds a new active host
        :param host_id: the unique id to identify the host
        :param skt: socket descriptor connected to client
        :param addr: address to later connect between clients
        :return: if the host was appended successfully
        """
        if self.is_id(host_id):
            self.hosts[host_id] = (skt, addr)
            return True
        else:
            return False

    def pop(self, host_id: str) -> tuple[socket.socket, tuple]:
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
    ip = '0.0.0.0'              # ip to bind to
    port = 5010                 # port to bind to
    listen_size = 5             # maximum listen size
    max_buffer = 2048           # maximum receive buffer
    # available commands
    commands = ["PRESENT", "HOSTING", "GUESTING", "REQUEST", "ABORT", "RETRY", "CONNECT", "CONNECTED"]
    cert = "certificate.crt"    # SSL certificate
    key = "privatekey.key"      # SSL key
    id_length = 12

    def __init__(self):
        """ initializes server tcp socket and tls context """
        self.lock = threading.Lock()
        self.active_hosts = Hosts()
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(Server.cert, Server.key)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def handle_data(self, data: list, client_sock: socket.socket, client_addr: tuple):
        """
        Handles different input messages according to protocol
        :param data: message received from the client
        :param client_sock: Socket to communicate with the client
        :param client_addr: Client address (ip, port)
        :return: Response message according to data (when there is no respond then it returns None)
        """
        command = data[0]            # command in data
        args = data[1:]         # arguments of the command
        if command == "PRESENT":
            if not self.active_hosts.add(args[0], client_sock, client_addr):
                self.invalid(client_sock, "invalid id")
            return None
        if command == "GUESTING":
            if args[0] == 'id':                                         # client is giving an id
                if self.active_hosts.is_id(args[1]):                    # if id is in correct format
                    if self.active_hosts.get(args[1]) is not None:      # if there is an active host with this id
                        return "REQUEST password"
                    else:
                        return "RETRY id"
                else:
                    self.invalid(client_sock, "invalid id")
            elif args[0] == 'password':
                pass
            else:
                self.invalid(client_sock, "invalid data")

    def handle_connection(self, client_sock: socket.socket, client_addr: tuple):
        """
        Handles client connection
        :param client_sock: Socket to communicate with the client
        :param client_addr: Client address (ip, port)
        """
        inputs = [client_sock]          # sockets to read from
        outputs = [client_sock]         # socket to write to
        messages = []                   # messages to send
        try:
            while inputs:
                rlist, wlist, xlist = select.select(inputs, outputs, inputs)
                for s in rlist:
                    data = s.recv(Server.max_buffer).decode()
                    if data == "":          # if client closed disconnected
                        inputs.remove(s)
                    else:
                        data_split = self.valid(data)
                        if not data_split:
                            self.invalid(client_sock, "invalid protocol")
                        message = self.handle_data(data_split, client_sock, client_addr)

                for msg in messages:
                    pass
                for s in xlist:
                    pass

        except socket.error as err:
            logging.error(err)
        except ValueError as err:
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
            # handle clients
            while True:
                client_sock, client_addr = secure_server.accept()
                client_sock.setblocking(False)
                # sending socket descriptor on a thread to handle it
                thread = threading.Thread(target=self.handle_connection, args=(client_sock, client_addr),
                                          name=f"Thread{next_name}")
                threads.append(thread)
                next_name += 1
                thread.start()

        except socket.error as err:
            logging.critical(err)
        finally:
            self.server.close()
            for thread in threads:
                thread.join()

    def invalid(self, sock: socket.socket, reason):
        """
        If protocol is invalid then socket aborts
        :param sock: socket connection
        :param reason: reason of the abort message
        """
        self.send_abort(sock, reason)
        raise ValueError(reason)

    @staticmethod
    def send_abort(sock: socket.socket, reason: str):
        """
        Sends to client an ABORT message with its corresponding reason
        :param sock: client socket
        :param reason: reason of the abort message
        """
        sock.send(f"ABORT {reason};;".encode())

    @staticmethod
    def valid(data: str) -> list:
        """
        Validates protocol in data and returns it ordered
        :param data: data from the client to validate its protocol
        :return: if data is valid returns list with command and arguments, if not returns none
        """
        split = data.split()
        if (split[0] not in Server.commands) or (data[-2:] != ';'):
            return []
        elif split[0] == "PRESENT" and len(split) == 2 and len(split[1]) == Server.id_length + 2:
            return [split[0], split[1][:-2]]
        elif split[0] == "HOSTING" and len(split) == 2:
            return [split[0], split[1][:-2]]
        elif split[0] == "GUESTING" and len(split) == 3:
            return [split[0], split[1], split[2][:-2]]
        else:
            return []


def main():
    server = Server()
    server.run_server()


if __name__ == "__main__":
    main()
