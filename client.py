"""
Author: Tomas Dal Farra
Date: 04/06/2023
Description: Client communication handling module
"""
import logging
import socket
import ssl
import select
from dataexct import UseKeyBoard, UseMouse
from OpenSSL import crypto
import os


def cert_gen():
    """
    Generates a self-signed certificate and a private key
    based on https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python
    """
    email_address = "emailAddress"
    common_name = "commonName"
    country_name = "NT"
    locality_name = "localityName"
    state_or_province_name = "stateOrProvinceName"
    organization_name = "organizationName"
    organization_unit_name = "organizationUnitName"
    serial_number = 0
    validity_start_in_seconds = 0
    validity_end_in_seconds = 365 * 24 * 60 * 60   # 1 year
    cert_file = 'certificate.crt'
    key_file = 'privatekey.key'

    # generate key
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 4096)
    # create self-signed certificate
    cert = crypto.X509()
    cert.get_subject().C = country_name
    cert.get_subject().ST = state_or_province_name
    cert.get_subject().L = locality_name
    cert.get_subject().O = organization_name
    cert.get_subject().OU = organization_unit_name
    cert.get_subject().CN = common_name
    cert.get_subject().emailAddress = email_address
    cert.set_serial_number(serial_number)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validity_end_in_seconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    with open(cert_file, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(key_file, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode("utf-8"))


class Client:
    """ General client """
    client_port = 5012
    server_port = 5010
    max_buffer = 256
    # available commands that arrive to client
    commands = ["GUESTING", "REQUEST", "ABORT", "RETRY", "CONNECT"]

    def __init__(self, ip, user_id, sock, context):
        """
        Initiates client communication sockets
        :param ip: servers ip
        :param user_id: unique id of the user
        :param sock: socket descriptor to communicate with server (better if its over ssl)
        :param context: ssl context
        """
        self.id = user_id
        self.server_ip = ip
        self.server_address = (self.server_ip, Client.server_port)
        self.context = context
        self.secure_client = sock

    def present(self):
        """ starts client communication, connects to server and sends present """
        # try
        self.secure_client.connect((self.server_ip, Client.server_port))
        self.secure_client.send(f'PRESENT {self.id};;'.encode())
        # except socket.error

    def connected(self):
        """"""
        self.secure_client.send(self.protocol('connected').encode())
        self.secure_client.close()

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
        :param data: data from the server to validate its protocol
        :return: if data is valid returns list with command and arguments, if not returns empty list
        """
        split = data.split()
        if (split[0] not in Client.commands) or (data[-2:] != ';;'):
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
        elif split[0] == "RETRY" and len(split) == 2:
            return [split[0], split[1][:-2]]
        else:
            return []


class ClientGuest(Client):
    """ Client communications for guest mode """

    def __init__(self, server_ip, user_id, sock, context):
        """
        initializes the guest socket
        :param server_ip: servers ip
        :param user_id: unique id of the user
        :param sock: socket descriptor
        :param context: ssl context
        """
        super().__init__(server_ip, user_id, sock, context)

        self.guest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.guest.setblocking(False)
        self.secure_guest = None         # SSL wrapped socket when we already know the
        self.guest_mode = False          # server communication blocks?

    def connect_id(self, host_id: str) -> int:
        """
        Sends a host id to the server
        :param host_id: host's id
        :return: if the id was correct -1, if not how much time to wait to continue communication
        """
        # Adapts server connection for guest mode
        if not self.guest_mode:
            self.secure_client.setblocking(True)  # communication with the server blocks
            self.secure_client.settimeout(120)  # if server does not answer in two minutes something happened
            self.guest_mode = True
        # ---------------------------------------
        self.secure_client.send(self.protocol('guesting', 'id', host_id).encode())
        data = self.secure_client.recv(Client.max_buffer).decode()
        print(data)
        data = self.valid(data)
        if data:
            if data[0] == "REQUEST" and data[1] == "password":
                return -1
            elif data[0] == "RETRY" and data[1].isnumeric():
                return int(data[1])     # > 0
            elif data[0] == "ABORT":
                raise Exception(data[1])
            else:
                raise ValueError("Not an appropriate answer from the server")

    def connect_password(self, password: str) -> tuple[str, int]:
        """
        Sends a password to the server
        :param password: host's password
        :return: host address to connect, if not succeeded,
        it returns (RETRY, time to wait)
        """
        self.secure_client.send(self.protocol('guesting', 'password', password).encode())
        data = self.secure_client.recv(Client.max_buffer).decode()
        print(data)
        data = self.valid(data)
        if data:
            if data[0] == "CONNECT" and data[2].isnumeric():
                return data[1], int(data[2])
            elif data[0] == "RETRY" and data[1].isnumeric():
                return data[0], int(data[1])
            elif data[0] == "ABORT":
                raise Exception(data[1])
            else:
                raise ValueError("Not an appropriate answer from the server")
        else:
            raise ValueError("Not an appropriate answer from the server")

    def connect_to_host(self, ip: str, port: int) -> bool:
        """
        Establishes connection with the host
        :param ip: hosts ip
        :param port: hosts port
        :return: if it succeeded establishing connection
        """
        try:
            self.secure_guest = self.context.wrap_socket(self.guest, server_hostname=ip)
            self.secure_guest.connect((ip, port))
            print("connected to host")
            return True
        except socket.error:
            return False
        # finally


class ClientHost(Client):
    """ Client communications for host mode """
    listen_size = 1
    cert = 'certificate.crt'
    key = 'privatekey.key'
    # possible commands from a guest to execute
    exct_commands = ('MOUSEPRESS', 'MOUSERELEASE', 'MOUSEMOVE', 'MOUSESCROLL', 'KEYPRESS', 'KEYRELEASE')

    def __init__(self, server_ip, user_id, sock, context):
        """
        initializes the host socket
        :param server_ip: servers ip
        :param user_id: unique id of the user
        :param sock: socket descriptor
        :param context: ssl context
        """
        super().__init__(server_ip, user_id, sock, context)
        # ssl context
        if not (os.path.exists(ClientHost.cert) and os.path.exists(ClientHost.key)):
            # if there is no certificate it creates one
            cert_gen()
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(ClientHost.cert, ClientHost.key)

        self.connection_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secure_connect = None         # SSL wrapped socket to establish a connection
        self.secure_host = None            # # SSL wrapped socket when we already know the guest
        self.messages = []

        # hardware
        self.keyboard = UseKeyBoard()
        self.mouse = UseMouse()

    def message_server(self, message):
        """
        Adds a message to send to server
        :param message: message for server (already over protocol)
        """
        self.messages.append(message)

    def communicate(self):
        """ Communicates with server """
        value = None            # does not return
        if not self.secure_client.getblocking():
            rlist, wlist, xlist = select.select([self.secure_client], [self.secure_client], [self.secure_client])

            # exception
            for s in xlist:
                s.close()
                raise socket.error("Error in the server connection")
            # read
            for s in rlist:
                data = s.recv(Client.max_buffer).decode()
                print(data)

                if data == "":
                    # disconnect
                    self.secure_client.close()
                    self.messages.clear()

                commands = data.split(';;')
                for command in commands:
                    command = self.valid(command+';;')
                    if command:
                        if command[0] == "GUESTING" and command[1] == "password":
                            value = command[2]          # will return the password received
                        elif command[0] == "ABORT":
                            raise Exception(command[1])
            # write
            for message in self.messages:
                if self.secure_client in wlist:
                    self.secure_client.send(message.encode())
                    self.messages.remove(message)
        else:
            value = '-1'
        return value

    def connect_host(self):
        """ Connects host server to have a connection with a guest """
        self.secure_host, _ = self.secure_connect.accept()

    def get_guest(self) -> tuple[str, int]:
        """
        Gets guest's address
        :return: guest's address (ip, port)
        """
        return self.secure_host.getpeername()

    def start_host(self):
        """
        Starts host side communication
        """
        try:
            super().present()
            self.connection_host.bind(('0.0.0.0', Client.client_port+3))             # accepts a connection from anyone
            self.connection_host.listen(ClientHost.listen_size)
            self.secure_connect = self.context.wrap_socket(self.connection_host, server_side=True)
        except socket.error as err:
            logging.critical(err)

    def hosting(self):
        """ Handles communication with a guest """
        rlist, _, xlist = select.select([self.secure_host], [], [self.secure_host])
        # exception
        for s in xlist:
            s.close()
            raise socket.error("Error in the host connection")
        # read
        for s in rlist:
            data = s.recv(Client.max_buffer).decode()
            print(data)

            if data == "":
                # disconnect
                self.secure_client.close()

            messages = data.split(";;")        # separate between messages
            for message in messages:
                message = self.valid_exct(message)
                if message:
                    command = message[0]
                    args = message[1:]
                    self.handle_exct(command, *args)

    def handle_exct(self, command, *args):
        """
        Executes different commands according to the protocol
        :param command: command to execute
        :param args: arguments of the command
        """
        if command[:3] == 'KEY':
            command = command[3:]       # takes only the action in the command
            if command == 'PRESS':
                self.keyboard.press(args[0])
            else:           # command is RELEASE
                self.keyboard.release(args[0])
        else:               # command is a mouse command
            command = command[5:]       # takes only the action in the command
            if command == 'PRESS':
                self.mouse.press(args[0], args[1], args[2])
            elif command == 'RELEASE':
                self.mouse.release(args[0], args[1], args[2])
            elif command == 'MOVE':
                self.mouse.move(args[0], args[1])
            else:           # command is scroll
                self.mouse.scroll(args[0], args[1], args[2])

    @staticmethod
    def valid_exct(instruction):
        """
        Validates protocol in instruction to execute and returns it ordered
        :param instruction: data from the guest to validate its protocol
        :return: if data is valid returns list with command and arguments, if not returns empty list
        """
        split = instruction.split()
        if split[0] not in ClientHost.exct_commands:
            return []
        elif (split[0] == 'MOUSEPRESS' or split[0] == 'MOUSERELEASE') and len(split) == 4:
            return split
        elif (split[0] == 'KEYPRESS' or split[0] == 'KEYRELEASE') and len(split) == 2:
            return split
        elif split[0] == 'MOUSEMOVE' and len(split) == 3:
            return split
        elif split[0] == 'MOUSESCROLL' and len(split) == 5:
            return split
        else:
            return []


def main():
    """ tests classes """
    pass


if __name__ == "__main__":
    main()
