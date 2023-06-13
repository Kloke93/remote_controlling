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
import cv2 as cv
import socket
import threading


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
            self.root = Tk()
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
                self.root = Tk()

    def visual_menu(self):
        """ Runs tkinter visualize menu """
        menu = VisualizeMenu(self.root, self.guest.secure_guest)
        self.root.after(0, menu.update_image())
        self.root.mainloop()

    def password_menu(self):
        """ Runs tkinter password window """
        menu = PasswordMenu(self.root)
        menu.send_password()
        self.root.mainloop()

    def main_menu(self):
        """ Runs tkinter main window """
        menu = MainMenu(self.root, self.db.get_id(), self.db.get_password())
        menu.connect_to(self.connect_id_handler)
        self.root.mainloop()

    def run(self):
        """ Runs the program """
        self.main_menu()
        self.password_menu()
        self.visual_menu()


def main():
    """ Combines all the program functionalities and runs it"""
    db = DataBase()
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    guest = ClientGuest('127.0.0.1', db.get_id(), skt)
    mode_handler = GuestMode(db, guest)
    thread = threading.Thread(target=mode_handler.run, name="GuestThread")

    host = ClientHost('127.0.0.1', db.get_id(), skt)
    host.start_host()                               # first present as a host
    thread.start()                                  # be prepared for guest mode
    host_mode = False
    while True:
        password = host.communicate()
        if password is not None:
            if password == db.get_password():
                host.message_server(host.protocol('connect', str(host.client_port+3)))
                host.connect_host()         # this blocks
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

    thread.join()
    db.close()


if __name__ == "__main__":
    main()
