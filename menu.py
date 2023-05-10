"""
Author: Tomas Dal Farra
Date:
Description:
"""
from tkinter import Tk, Label, Button, Entry, StringVar


class MainMenu:
    """ Class to organize all the menu GUI """

    def __init__(self, master: Tk):
        """
        RemoteControlling main menu
        :param master: tkinter Tk instance (root)
        """
        self.master = master
        self.master.title("RemoteControlling")                           # name of the program
        try:
            self.master.iconbitmap("logo.ico")                           # program logo
        except Exception as err:
            print(f"no logo loaded: {err}")

        # creating gui widgets
        # program name
        self.title = Label(self.master, text="RemoteControlling")
        # guesting part
        self.guesting = Label(self.master, text="Guesting:")
        # connect to host
        self.connect = Button(self.master, text="Connect")
        # Entry host id
        self.text_id = StringVar()
        self.host_id = Entry(self.master, textvariable=self.text_id)
        # guest id (immutable)
        self.guest_id = Label(self.master, text="ID: 123456789")
        self.text_password = StringVar()
        # guest password (mutable)
        self.guest_password = Entry(self.master, width=10, textvariable=self.text_password)
        self.password_label = Label(self.master, text="PASSWORD:")

        # detailing widgets
        self.text_id.set("Enter host id")
        self.text_id.trace_add("write", lambda *args: self.character_limit(self.text_id, 9))
        self.text_password.set("messi123")
        self.text_password.trace_add("write", lambda *args: self.character_limit(self.text_password, 8))

        # positioning widgets
        gcol = 0
        hcol = 3
        self.title.grid(row=0, column=2, padx=10)
        self.guesting.grid(row=1, column=hcol)
        self.connect.grid(row=3, column=hcol)
        self.host_id.grid(row=2, column=hcol)
        self.guest_id.grid(row=1, column=gcol)
        self.password_label.grid(row=2, column=gcol)
        self.guest_password.grid(row=2, column=gcol+1)

    @staticmethod
    def character_limit(text: StringVar, lim):
        """
        Limits characters in an entry
        :param text: text entry tkinter
        :param lim: character limit
        """
        if len(text.get()) > lim:
            text.set(text.get()[:lim])


def main():
    root = Tk()
    MainMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()
