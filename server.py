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

    def add(self, host_id: str, skt: socket.socket) -> bool:
        """
        Adds a new active host
        :param host_id: the unique id to identify the host
        :param skt: socket descriptor connected to client
        :return: if the host was appended successfully
        """
        if self.is_id(host_id):
            self.hosts[host_id] = skt
            print(f'{host_id} is connected')
            return True
        else:
            return False

    def pop(self, host_id: str) -> socket.socket:
        """
        Removes a host (is not active)
        :param host_id: the unique id to identify the host
        :return: removed hosts socket
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
    max_buffer = 256            # maximum receive buffer
    # available commands that arrive to server
    commands = ["PRESENT", "GUESTING", "REQUEST", "ABORT", "RETRY", "CONNECT", "CONNECTED"]
    cert = "certificate.crt"    # SSL certificate
    key = "privatekey.key"      # SSL key
    id_length = 12

    def __init__(self):
        """ initializes server tcp socket and tls context """
        # ssl context
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(Server.cert, Server.key)
        # sockets
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(False)
        self.waiting_clients = []               # active host waiting and/or potential guests
        # host and guest handling
        self.active_hosts = Hosts()
        self.threads = []
        self.next_name = 1                      # next thread name
        self.messages = []                      # messages for client in format (socket, data)

    def handle_connection(self, data: str, skt: socket.socket):
        """
        Handles a client that is in process of establishing a connection.
        It handles their messages according to the protocol identifying themselves
        with the server or giving host id (PRESENT or GUESTING command messages)
        :param skt: socket of the client
        :param data: data to handle received from socket
        It also appends a response to the client to the messages list
        """
        data = self.valid(data)                 # data processed
        print(data)
        if not data:                            # if data isn't valid
            self.invalid(skt, f"invalid protocol")
        command = data[0]                       # command in data
        args = data[1:]                         # arguments of the command
        if command == "PRESENT":
            if not self.active_hosts.add(args[0], skt):
                self.invalid(skt, "invalid id " + args[0])
        elif command == "GUESTING":
            if args[0] == 'id':                                         # client is giving an id
                if self.active_hosts.is_id(args[1]):                    # if id is in correct format
                    host = self.active_hosts.get(args[1])
                    if host is not None:                                # if there is an active host with this id
                        # sending sockets descriptors on a thread to handle them
                        print(f"{skt.getpeername()} is connecting to {host.getpeername()}")
                        thread = threading.Thread(target=self.handle_communication, args=(host, skt),
                                                  name=f"Thread{self.next_name}")
                        self.threads.append(thread)
                        self.next_name += 1
                        # these clients are not waiting anymore
                        self.waiting_clients.remove(skt)
                        self.waiting_clients.remove(host)
                        thread.start()
                    else:
                        self.messages.append((skt, self.protocol("retry", '3')))
                else:
                    self.messages.append((skt, self.protocol("retry", '3')))

    def handle_communication(self, host: socket.socket, guest: socket.socket):
        """
        Handles client communication
        :param host: Socket to communicate with the host client
        :param guest: Socket to communicate with the guest client
        """
        clients = [host, guest]
        # messages to send (skt to send, data)
        messages = [(guest, self.protocol('request', 'password'))]
        try:
            while clients:
                rlist, wlist, xlist = select.select(clients, clients, clients)
                # exceptions
                for s in xlist:
                    print(f'there is an exception in {s}')
                    clients.remove(s)
                    messages.append((clients[0], self.protocol('abort', "The other end had an error")))

                # read from host
                if host in rlist:
                    data = host.recv(Server.max_buffer).decode()
                    print(data)
                    if data == "":  # if client closed disconnected
                        clients.remove(host)
                        messages.append((guest, self.protocol('abort', "The other end disconnected")))
                    data = self.valid(data)     # data processed

                    if not data:                # if data isn't valid
                        messages.append((host, self.protocol('abort', "invalid protocol")))
                        messages.append((guest, self.protocol('abort', "invalid protocol from the host")))

                    command = data[0]           # command in data
                    args = data[1:]             # arguments of the command
                    if command == "RETRY":
                        messages.append([host, "RETRY 1;"])     # add time progressively
                    elif command == "CONNECT":
                        messages.append([host, (host.getpeername()[0], args[0])])
                    elif command == "CONNECTED":
                        clients.remove(host)

                # read from guest
                if guest in rlist:
                    data = guest.recv(Server.max_buffer).decode()
                    print(data)
                    if data == "":              # if client closed disconnected
                        clients.remove(guest)
                        messages.append((host, self.protocol('abort', "The other end disconnected")))

                    data = self.valid(data)     # data processed
                    if not data:                # if data isn't valid
                        messages.append((guest, self.protocol('abort', "invalid protocol")))
                        messages.append((host, self.protocol('abort', "invalid protocol from the guest")))

                    command = data[0]           # command in data
                    args = data[1:]             # arguments of the command
                    if command == "GUESTING":
                        if args[0] == 'password':
                            messages.append([guest, f"GUESTING {args[0]} {args[1]}"])
                    elif command == "CONNECTED":
                        clients.remove(guest)

                # write
                for msg in messages:
                    s = msg[0]
                    if s in wlist:
                        s.send(msg[1].encode())
                        messages.remove(msg)
                    if msg[1][:5] == "ABORT":
                        clients.remove(s)
        except socket.error as err:
            logging.error(err)
        except ValueError as err:
            logging.error(err)
        finally:
            host.close()
            guest.close()

    def run_server(self):
        """ Runs server """
        try:
            self.server.bind((Server.ip, Server.port))
            self.server.listen(Server.listen_size)
            secure_server = self.context.wrap_socket(self.server, server_side=True)
            # handle clients
            while True:
                rlist, wlist, xlist = select.select([secure_server] + self.waiting_clients,
                                                    self.waiting_clients,
                                                    [secure_server] + self.waiting_clients)
                # exceptions
                for s in xlist:
                    print(f'there is an exception in {s}')
                    if s is secure_server:
                        raise socket.error("Exception in server socket")
                    else:
                        self.waiting_clients.remove(s)
                # read
                for s in rlist:
                    if s is secure_server:          # if there are new clients
                        client_sock, _ = secure_server.accept()
                        self.waiting_clients.append(client_sock)
                    else:                           # communication with client that is in process of a connection
                        data = s.recv(Server.max_buffer).decode()
                        print('received ' + data)
                        if data == "":              # if client closed disconnected
                            self.waiting_clients.remove(s)
                        else:
                            try:
                                self.handle_connection(data, s)
                            except ValueError():
                                s.close()
                # write
                for msg in self.messages:
                    s = msg[0]
                    if s in wlist:
                        s.send(msg[1].encode())
                        self.messages.remove(msg)

        except socket.error as err:
            logging.critical(err)
        finally:
            for client in self.waiting_clients:
                client.close()
            self.server.close()
            for thread in self.threads:
                thread.join()

    def invalid(self, sock: socket.socket, reason):
        """
        If protocol is invalid then socket aborts
        :param sock: socket connection
        :param reason: reason of the abort message
        """
        self.send_abort(sock, reason)
        raise ValueError(reason)

    def send_abort(self, sock: socket.socket, reason: str):
        """
        Sends to client an ABORT message with its corresponding reason
        :param sock: client socket
        :param reason: reason of the abort message
        """
        sock.send(self.protocol("abort", reason).encode())

    @staticmethod
    def valid(data: str) -> list:
        """
        Validates protocol in data and returns it ordered
        :param data: data from the client to validate its protocol
        :return: if data is valid returns list with command and arguments, if not returns empty list
        """
        split = data.split()
        if (split[0] not in Server.commands) or (data[-2:] != ';;'):
            return []
        elif split[0] == "PRESENT" and len(split) == 2 and len(split[1]) == Server.id_length + 2:
            return [split[0], split[1][:-2]]
        elif split[0] == "GUESTING" and (split[1] == 'id' or split[1] == 'password'):
            return [split[0], split[1], split[2][:-2]]
        else:
            return []

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


def main():
    server = Server()
    server.run_server()


if __name__ == "__main__":
    main()
