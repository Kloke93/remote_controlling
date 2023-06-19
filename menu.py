"""
Author: Tomas Dal Farra
Date: 04/06/2023
Description: Implements the GUI for Remote-Controlling
"""
import sys
from tkinter import Tk, Label, Button, Entry, StringVar
import cv2 as cv
from inputsend import InputKeySend, InputMouseSend
from datacomp import StreamDecode
import socket
import ctypes
from PIL import ImageTk, Image


class Menu:
    """ Base class for all menus """

    def __init__(self, master: Tk):
        """
        Remote-Controlling base menu
        :param master: tkinter Tk instance (root)
        """
        self.master = master
        self.master.resizable(width=False, height=False)  # not resizable
        self.master.title("RemoteControlling")  # name of the program
        try:
            self.master.iconbitmap("logo.ico")  # program logo
        except Exception as err:
            print(f"no logo loaded: {err}")


class MainMenu(Menu):
    """ Class to organize all the main menu GUI """

    def __init__(self, master: Tk, user_id: str, password: str):
        """
        RemoteControlling main menu
        :param master: tkinter Tk instance (root)
        :param user_id: id of the user
        :param password: password of the user
        """
        super().__init__(master)

        # creating gui widgets
        # program name
        self.title = Label(self.master, text="RemoteControlling")
        # guesting part
        self.guesting = Label(self.master, text="Guesting:")
        # update password
        self.up_password = Button(self.master, text="Update")
        # connect to host
        self.connect = Button(self.master, text="Connect")
        # Entry host id
        self.text_id = StringVar()
        self.host_id = Entry(self.master, width=17, textvariable=self.text_id)
        # guest id (immutable)
        self.guest_id = Label(self.master, text=f"ID: {user_id}")
        self.text_password = StringVar()
        # guest password (mutable)
        self.guest_password = Entry(self.master, width=12, textvariable=self.text_password)
        self.password_label = Label(self.master, text="PASSWORD:")

        # detailing widgets
        self.text_id.set("host id")
        self.text_id.trace_add("write", lambda *args: self.character_limit(self.text_id, 12))
        self.text_password.set(password)
        self.text_password.trace_add("write", lambda *args: self.character_limit(self.text_password, 10))

        # positioning widgets
        gcol = 0
        hcol = 3
        self.title.grid(row=0, column=2, padx=15)
        self.guesting.grid(row=1, column=hcol)
        self.up_password.grid(row=3, column=gcol)
        self.connect.grid(row=3, column=hcol)
        self.host_id.grid(row=2, column=hcol)
        self.guest_id.grid(row=1, column=gcol)
        self.password_label.grid(row=2, column=gcol)
        self.guest_password.grid(row=2, column=gcol+1)

    def connect_to(self, target):
        """
        Sets the target function of the connect button
        :param target: Target function of the button
        It is supposed to be targeted to some socket connection
        """
        # target function gets host_id entry
        self.connect.configure(text="Connect", command=lambda: target(self.host_id.get()))

    def update_to(self, target):
        """
        Sets the target function of the up_password button
        :param target: Target function of the button
        It is supposed to be targeted to some database updater from text in password entry
        """
        self.up_password.configure(text="Update", command=target)

    @staticmethod
    def character_limit(text: StringVar, lim):
        """
        Limits characters in an entry
        :param text: text entry tkinter
        :param lim: character limit
        """
        if len(text.get()) > lim:
            text.set(text.get()[:lim])


class PasswordMenu(Menu):
    """ Interface to ask from user password """

    def __init__(self, master: Tk):
        """
        Remote-Controlling password menu
        :param master: tkinter Tk instance (root)
        """
        super().__init__(master)

        # creating gui widgets
        # program name
        self.title = Label(self.master, text="RemoteControlling")
        # password prompt
        self.text_password = StringVar()
        self.host_password = Entry(self.master, width=17, textvariable=self.text_password)
        # send button
        self.send_password = Button(self.master, text="Send")

        # detailing widgets
        self.text_password.set("enter password")

        # positioning widgets
        padx = 50
        pady = 7
        self.title.grid(row=0, padx=padx, pady=pady)
        self.host_password.grid(row=1, padx=padx, pady=pady)
        self.send_password.grid(row=2, padx=padx, pady=pady)

    def send_to(self, target):
        """
        Sets the target function of the send_password button
        :param target: Target function of the button
        It is supposed to be targeted to some socket send password function
        """
        self.send_password.configure(text="Send", command=lambda: target(self.host_password.get()))


class DisconnectMenu(Menu):
    """ Exit button for the connection """

    def __init__(self, master: Tk):
        """
        Remote-Controlling disconnect menu
        :param master: tkinter Tk instance (root)
        """
        super().__init__(master)

        # creating gui widgets
        # program name
        self.title = Label(self.master, text="RemoteControlling")
        # send button
        self.disconnect = Button(self.master, text="Disconnect")

        # positioning widgets
        padx = 50
        pady = 7
        self.title.grid(row=0, padx=padx, pady=pady)
        self.disconnect.grid(row=1, padx=padx, pady=pady)


class VisualizeMenu(Menu):
    """ Class to see video stream """

    def __init__(self, master: Tk, sock: socket.socket, width=1920, height=1080):
        """
        Creates an instance of VisualizeMenu
        :param master: tkinter Tk instance (root)
        :param width: video width
        :param height: video height
        """
        super().__init__(master)

        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        # screen width and height
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        if width == screensize[0] and height == screensize[1]:
            self.master.attributes('-fullscreen', True)
        else:
            self.master.geometry(f'{width}x{height}')

        self.displayer = Label(self.master)
        self.displayer.pack()
        # sending events
        InputMouseSend(self.master, sock)
        InputKeySend(self.master, sock)
        # decoder
        ip, port = sock.getpeername()
        self.width = width
        self.height = height
        self.decoder = StreamDecode(width, height, f'udp://{ip}:{port-1}')
        self.decoder.run_decoder()

    def update_image(self):
        """ Updates images that we are seeing """
        # sys.stdout.flush()
        image = self.decoder.read_stdout()
        if image:
            image = Image.frombytes('RGB', (self.width, self.height), image)
            image = ImageTk.PhotoImage(image)
            self.displayer.image = image
            self.displayer.configure(image=image)
        self.master.after(1, self.update_image)


def main():
    root = Tk()
    # MainMenu(root, 'abc123456789', 'messi123')
    # PasswordMenu(root)
    # DisconnectMenu(root)
    # menu = VisualizeMenu(root)
    # try:
    #     root.after(0, menu.update_image)
    #     root.mainloop()
    # finally:
    #     menu.decoder.close()


if __name__ == "__main__":
    main()
