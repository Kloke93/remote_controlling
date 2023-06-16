"""
Author: Tomas Dal Farra
Date: 04/06/2023
Description: Execute the main program for Remote-Controlling
"""
import time
from database import DataBase
from tkinter import Tk
from menu import MainMenu, PasswordMenu, VisualizeMenu
from client import ClientHost, ClientGuest
from datacomp import ScreenEncode
import socket
import threading
import ssl


class GuestMode:
    """ Class to handle guest mode """

    def __init__(self, database: DataBase, guest: ClientGuest):
        """
        Initializes a GuestMode instance
        :param database: database with local id and password
        :param guest: guest socket to communicate with server
        """
        self.root = Tk()
        self.db = database
        self.guest = guest

    def connect_id_handler(self, host_id):
        """
        Handles the connection button for the guest mode
        :param host_id: host's id
        """
        sec = self.guest.connect_id(host_id)
        if sec == -1:
            self.root.destroy()
            # self.root = Tk()
        else:
            # temporal
            time.sleep(sec)

    def connect_password_handler(self, password):
        """
        Handles the send button for the guest mode
        :param password: host's password
        """
        ip, port = self.guest.connect_password(password)
        if ip == "RETRY":
            time.sleep(port)
        else:
            if self.guest.connect_to_host(ip, port):
                self.root.destroy()

    def visual_menu(self):
        """ Runs tkinter visualize menu """
        menu = VisualizeMenu(self.root, self.guest.secure_guest, 1366, 768)
        try:
            self.root.after(0, menu.update_image())
            self.root.mainloop()
        finally:
            menu.decoder.close()

    def password_menu(self):
        """ Runs tkinter password window """
        menu = PasswordMenu(self.root)
        menu.send_to(self.connect_password_handler)
        self.root.mainloop()
        self.root = Tk()

    def main_menu(self):
        """ Runs tkinter main window """
        menu = MainMenu(self.root, self.db.get_id(), self.db.get_password())
        menu.connect_to(self.connect_id_handler)
        self.root.mainloop()
        self.root = Tk()

    def run(self):
        """ Runs the program """
        self.main_menu()
        self.password_menu()
        self.visual_menu()


class HostMode:
    """ Class to handle host mode """
    def __init__(self, server_ip, database, skt, lock):
        """
        Initializes a HostMode instance
        :param server_ip: server's ip
        :param database: database with local id and password
        :param skt: socket to communicate with the server
        :param lock: threading lock to handle multithreaded operations
        """
        self.db = database
        self.host = ClientHost(server_ip, self.db.get_id(), skt, lock)
        self.host.start_host()      # first present as a host
        self.host_mode = False
        self.encoder = None         # = ScreenEncoder(...)
        self.exit = threading.Event()       # event to exit capturing

    def main_host(self):
        """ Puts host mode actions in order for a thread """
        self.waiting_host()
        self.handle_hosting()

    def waiting_host(self):
        """ Waits as a host to receive a password from the server """
        while True:
            password = self.host.communicate()              # gets password from server
            if password is not None:                        # if there is a password
                if password == self.db.get_password():      # if password is correct password
                    self.host.message_server(self.host.protocol('connect', str(self.host.client_port)))
                    self.host.communicate()
                    self.host.connect_host()        # this blocks (connects to guest)
                    self.host_mode = True
                    break
                elif password == '-1':
                    break
                else:
                    self.host.message_server(self.host.protocol('retry', '0'))

    def handle_hosting(self):
        """ Handles communication with guest if host mode """
        if self.host_mode:
            self.host.connected()
            ip = self.host.get_guest()
            self.encoder = ScreenEncode(f'udp://{ip}:{self.host.client_port - 1}')
            self.encoder.run_encoder()
            try:
                thread = threading.Thread(target=self.thread_capture, name="CaptureThread")
                thread.start()              # starts thread_capture
                while True:
                    self.host.hosting()
            finally:
                self.exit.set()         # stop capturing
                self.encoder.close()    # close encoder

    def thread_capture(self):
        """ Until the connection is down, capture to an encoder """
        while not self.exit:
            self.encoder.capture()


def create_secure_client(ip):
    """
    Creates secure client socket over ssl
    :param ip: servers ip
    """
    # create ssl context
    context = ssl.create_default_context()
    # allow self-signed certificates
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # secured tcp socket
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_client = context.wrap_socket(tcp_client, server_hostname=ip)
    return secure_client


def main():
    """ Combines all the program functionalities and runs it"""
    server_ip = '127.0.0.1'
    db = DataBase()
    skt = create_secure_client(server_ip)               # creates an SSL socket (SSL socket, SSL context)
    lock = threading.Lock()                             # for blocking variations in socket between host and guest
    guest = ClientGuest(server_ip, db.get_id(), skt, lock)
    guest_handler = GuestMode(db, guest)                # creates GuestMode instance
    host = HostMode(server_ip, db, skt, lock)           # creates HostMode instance
    thread = threading.Thread(target=host.main_host, name="HostThread")
    thread.start()              # hosting mode ready

    guest_handler.run()

    thread.join()
    db.close()


if __name__ == "__main__":
    main()
