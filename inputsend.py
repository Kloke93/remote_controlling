"""
Author: Tomas Dal Farra
Date: 02/06/2023
Description: Adapts events from tkinter send them on socket with protocol for Remote-Controlling
"""
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
        x = data[0]
        y = data[1]
        button = data[2]
        protocol_data = self.protocol("mousepress", x, y, button)
        self.skt.send(protocol_data.encode())

    def release(self, event):
        """
        Gets data from release method from an InputMouse instance,
        then writes protocol over this data and finally sends it on socket
        """
        data = super().release(event)
        x = data[0]
        y = data[1]
        button = data[2]
        protocol_data = self.protocol("mouserelease", x, y, button)
        self.skt.send(protocol_data.encode())

    def move(self, event):
        """
        Gets data from move method from an InputMouse instance,
        then writes protocol over this data and finally sends it on socket
        """
        data = super().move(event)
        x = data[0]
        y = data[1]
        if data is not None:
            protocol_data = self.protocol("mousemove", x, y)
            self.skt.send(protocol_data.encode())

    def scroll(self, event):
        """
        Gets data from scroll method from an InputMouse instance,
        then writes protocol over this data and finally sends it on socket
        """
        data = super().scroll(event)
        delta = data[0]
        x = data[1]
        y = data[2]
        state = data[3]
        protocol_data = self.protocol("mousescroll", delta, x, y, state)
        self.skt.send(protocol_data.encode())

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
        key = super().press(event)
        protocol_data = self.protocol("keypress", key)
        self.skt.send(protocol_data.encode())

    def release(self, event):
        """
        Gets data from release method from an InputKeyBoard instance,
        then writes protocol over this data and finally sends it on socket
        """
        key = super().release(event)
        protocol_data = self.protocol("keyrelease", key)
        self.skt.send(protocol_data.encode())

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
