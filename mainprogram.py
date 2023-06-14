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
        menu = VisualizeMenu(self.root, self.guest.secure_guest)
        self.root.after(0, menu.update_image())
        self.root.mainloop()

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


def handle_hosting(db, skt, context, server_ip, lock):
    """ Handles hosting """
    host = ClientHost(server_ip, db.get_id(), skt, context, lock)
    host.start_host()  # first present as a host
    host_mode = False
    while True:
        password = host.communicate()
        if password is not None:
            if password == db.get_password():
                host.message_server(host.protocol('connect', str(host.client_port)))
                host.communicate()
                host.connect_host()  # this blocks
                host_mode = True
                break
            elif password == '-1':
                break
            else:
                host.message_server(host.protocol('retry', '0'))
    if host_mode:
        ip, port = host.get_guest()
        encoder = ScreenEncode(f'udp://{ip}:{port}')
        encoder.run_encoder()
        try:
            while True:
                host.hosting()
                encoder.capture()
        finally:
            encoder.close()


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
    return secure_client, context


def main():
    """ Combines all the program functionalities and runs it"""
    server_ip = '127.0.0.1'
    db = DataBase()
    skt, context = create_secure_client(server_ip)               # creates an SSL socket (SSL socket, SSL context)
    lock = threading.Lock()
    guest = ClientGuest(server_ip, db.get_id(), skt, context, lock)
    guest_handler = GuestMode(db, guest)
    thread = threading.Thread(target=handle_hosting, args=(db, skt, context, server_ip, lock), name="HostThread")
    thread.start()              # hosting mode ready

    guest_handler.run()

    thread.join()
    db.close()


if __name__ == "__main__":
    main()
