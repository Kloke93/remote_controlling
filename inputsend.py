from dataget import InputMouse, InputKeyBoard
from socket import socket
from tkinter import Tk


class InputMouseSend(InputMouse):
    """
    Gets all mouse input from tkinter and sends them on socket.
    protocol: Action(data);;
    """

    def __init__(self, master: Tk, skt: socket):
        """
        Creates an instance of InputMouseSend
        :param master: tkinter Tk instance (root) to take the events from
        :param skt: socket descriptor to send data on socket (with the program protocol)
        """
        super().__init__(master)
        self.skt = skt

    def press(self, event):
        """
        Gets data from press method from an InputMouse instance,
        then writes protocol over this data and finally sends it on socket
        """
        data = super().press(event)
        protocol_data = f"MousePress{data};;"
        self.skt.send(protocol_data.encode())

    def release(self, event):
        """
        Gets data from release method from an InputMouse instance,
        then writes protocol over this data and finally sends it on socket
        """
        data = super().release(event)
        protocol_data = f"MouseRelease{data};;"
        self.skt.send(protocol_data.encode())

    def move(self, event):
        """
        Gets data from move method from an InputMouse instance,
        then writes protocol over this data and finally sends it on socket
        """
        data = super().move(event)
        if data is not None:
            protocol_data = f"MouseMove{data};;"
            self.skt.send(protocol_data.encode())

    def scroll(self, event):
        """
        Gets data from scroll method from an InputMouse instance,
        then writes protocol over this data and finally sends it on socket
        """
        data = super().scroll(event)
        protocol_data = f"MouseScroll{data};;"
        self.skt.send(protocol_data.encode())


class InputKeySend(InputKeyBoard):
    """ Gets all keyboard input from tkinter and sends them on socket """

    def __init__(self, master: Tk, skt: socket):
        """
        Creates an instance of InputKeySend
        :param master: tkinter Tk instance (root) to take the events from
        :param skt: socket descriptor to send data on socket (with the program protocol)
        """
        super().__init__(master)
        self.skt = skt

    def press(self, event):
        """
        Gets data from press method from an InputKeyBoard instance,
        then writes protocol over this data and finally sends it on socket
        """
        data = super().press(event)
        protocol_data = f"KeyPress{data};;"
        self.skt.send(protocol_data.encode())

    def release(self, event):
        """
        Gets data from release method from an InputKeyBoard instance,
        then writes protocol over this data and finally sends it on socket
        """
        data = super().release(event)
        protocol_data = f"KeyRelease{data};;"
        self.skt.send(protocol_data.encode())
