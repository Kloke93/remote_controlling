"""
Author: Tomas Dal Farra
Date:
Description:
"""
from tkinter import Tk, Label, Button, Entry, StringVar


class MainMenu:
    """ Class to organize all the menu GUI """

    def __init__(self, master: Tk, user_id: str, password: str):
        """
        RemoteControlling main menu
        :param master: tkinter Tk instance (root)
        """
        self.master = master
        self.master.resizable(width=False, height=False)                    # not resizable
        self.master.title("RemoteControlling")                              # name of the program
        try:
            self.master.iconbitmap("logo.ico")                              # program logo
        except Exception as err:
            print(f"no logo loaded: {err}")

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
        self.connect.configure(text="Connect", command=target)

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


def main():
    root = Tk()
    MainMenu(root, 'abc123456789', 'messi123')
    root.mainloop()


if __name__ == "__main__":
    main()
