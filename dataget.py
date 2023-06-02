"""
Author: Tomas Dal Farra
Date: 13/04/2023
Description: Module to get all user input and screen output
"""
from string import ascii_letters
from tkinter import Tk
from mss import mss
import numpy as np
import cv2 as cv
import time


class InputMouse:
    """ class to gather all the mouse input over a tkinter window """
    buttons = ('left', 'middle', 'left')    # translate buttons number to left middle and right

    def __init__(self, master: Tk):
        """
        Creates an instance of InputMouse
        :param master: tkinter Tk instance (root) to take the Mouse events from
        """
        self.master = master
        self.buttons_pressed = 0            # how many buttons are being pressed
        self.pos = (0, 0)                   # last mouse position (x, y)

    def bind_window(self):
        """ Binds master window to InputMouse event handlers """
        self.master.bind("<Button>", self.press)
        self.master.bind("<ButtonRelease>", self.release)
        self.master.bind("<Motion>", self.move)
        self.master.bind("<MouseWheel>", self.scroll)       # in Windows OS

    def press(self, event):
        """
        A mouse button was pressed
        :param event: <Button> tkinter event
        event -> num = which mouse button was clicked (1=left, 2=middle, 3=right)
            x = x coordinate
            y = y coordinate
        :return: a tuple with the event elements and translated num (x, y, button)
        """
        self.buttons_pressed += 1
        self.pos = (event.x, event.y)
        return self.pos + (InputMouse.buttons[event.num],)

    def release(self, event):
        """
        A mouse button was released
        :param event: <ButtonRelease> tkinter event
        event -> num = which mouse button was clicked (1=left, 2=middle, 3=right)
            x = x coordinate
            y = y coordinate
        :return: a tuple with the event elements and translated num (x, y, button)
        """
        self.buttons_pressed -= 1
        self.pos = (event.x, event.y)
        return self.pos + (InputMouse.buttons[event.num],)

    def move(self, event):
        """
        The mouse has been moved while holding a button
        :param event: <Motion> tkinter event
        event -> x = x coordinate
            y = y coordinate
        :return: a tuple with the event elements (x, y)
        """
        # if there is a button pressed
        if self.buttons_pressed:
            event_pos = (event.x, event.y)
            # if the difference in any of axis is more than 5 then it's far enough
            is_far = abs(self.pos[0] - event_pos[0]) > 5 or abs(self.pos[0] - event_pos[0]) > 5
            if self.buttons_pressed and is_far:
                self.pos = event_pos
                return event_pos

    @staticmethod
    def scroll(event):
        """
        The mouse wheel was rolled
        :param event: <MouseWheel> tkinter event
        event -> delta = amount of scrolling
            x = x coordinate
            y = y coordinate
            state = if it is vertical or horizontal scroll
        :return: a tuple with the event elements (delta, x, y, state)
        """
        return event.delta, event.x, event.y, event.state


class InputKeyBoard:
    """ class to gather all the keyboard input over a tkinter window """

    def __init__(self, master: Tk):
        """
        Creates an instance of InputKeyBoard
        :param master: tkinter Tk instance (root) to take the keyboard events from
        """
        self.master = master

    def bind_window(self):
        """ Binds master window to InputMouse event handlers """
        self.master.bind("<Key>", self.press)
        self.master.bind("<KeyRelease>", self.release)

    def press(self, event):
        """
        A key was pressed
        :param event: <Key> tkinter event
        event -> keycode = numeric code that identifies the key
            x = x coordinate
            y = y coordinate
            char = regular ASCII character
            keysym = the key's string name for special keys
            state = an integer describing the state of all the modifier keys
        :return: corresponding clicked key
        """
        # if it is not a special key
        if event.char != '' and event.char in ascii_letters:
            key = event.char
        else:
            key = self.special_key_adapter(event.keysym)
        return key

    def release(self, event):
        """
        A key was released
        :param event: <KeyRelease> tkinter event
        event -> keycode = numeric code that identifies the key
            x = x coordinate
            y = y coordinate
            keysym = the key's string name
            state = an integer describing the state of all the modifier keys
        :return: corresponding released key
        """
        # if it is not a special key
        if event.char != '' and event.char in ascii_letters:
            key = event.char
        else:
            key = self.special_key_adapter(event.keysym)
        return key

    @staticmethod
    def special_key_adapter(key: str) -> str:
        """
        Translater keysym from special keys to a PyAutoGUI compatible version
        :param key: special key string to be translated
        :return: Adapted key
        """
        if key[:7] == 'Control':
            key = 'ctrl' + key[7:]
        if key[-2:] == "_L":
            key = key[:-2] + 'left'
        elif key[-2:] == "_R":
            key = key[:-2] + 'right'
        key = key.lower()
        key = key.replace('_', '')
        return key


class VideoGather:
    """ Class to capture all video"""

    def __init__(self, sector=1):
        """
        Video capturer initializer
        :param sector: which monitor to capture.
        zero represents all monitors combined, and one is the main monitor.
        """
        self.sct = mss()                            # mss instance to handle screen-capturing
        self.monitor = self.sct.monitors[sector]    # the coordinates and size of the box to capture. (monitor in mss)

    def get_frame(self) -> np.ndarray:
        """
        Captures screen frame in rgb
        :return: image frame in rgb
        """
        image = self.sct.grab(self.monitor)
        # noinspection PyTypeChecker
        frame = np.array(image)
        frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)            # changes image format from bgr to rgb
        return frame_rgb

    def close(self):
        """ Closes mss instance """
        self.sct.close()


def test_fps(lim=100) -> str:
    """
    Testes how many fps does the capture function achieve
    :param lim: frame limit to test time (the larger, the more accurate the test)
    :return: how many frames per second are achieved
    """
    i = 0
    times = []
    video = VideoGather()
    while i < lim:
        start = time.time()
        frame = video.get_frame()
        cv.imshow("Capture", frame)
        times.append(time.time() - start)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        i += 1
    video.close()
    avg_time = sum(times) / len(times)
    return f"FPS: {1 / avg_time}"


if __name__ == "__main__":
    print(test_fps(1000))
    # try:
    #     inp = InputGather()
    #     inp.mouse_listener.start()
    #     inp.mouse_listener.join()
    # finally:
    #     sys.exit()
