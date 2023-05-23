"""
Author: Tomas Dal Farra
Date: 13/04/2023
Description: Module to get all user input and screen output
"""
from tkinter import Tk
from mss import mss
import numpy as np
import cv2 as cv
import time


class InputMouse:
    """ class to gather all the mouse input over a tkinter window """
    def __init__(self, master: Tk):
        """
        Creates an instance of InputMouse
        :param master: tkinter Tk instance (root) to take the Mouse events from
        """
        self.master = master
        self.buttons_pressed = 0            # how many buttons are being pressed

    def bind_window(self):
        """ Binds master window to InputMouse event handlers """
        self.master.bind("<Button>", self.press)
        self.master.bind("<ButtonRelease>", self.release)
        self.master.bind("<Motion>", self.move)

    def press(self, event):
        """
        A mouse button was clicked
        :param event: <Button> tkinter event
        event -> num = which mouse button was clicked;
        x = x coordinate
        y = y coordinate
        """
        print(repr(event))
        self.buttons_pressed += 1

    def release(self, event):
        """
        A mouse button was released
        :param event: <ButtonRelease> tkinter event
        event -> num = which mouse button was clicked;
        x = x coordinate
        y = y coordinate
        """
        print(repr(event))
        self.buttons_pressed -= 1

    def move(self, event):
        """
        The mouse has been moved while holding a button
        :param event: <Motion> tkinter event
        event -> num = which mouse button was clicked;
        x = x coordinate
        y = y coordinate
        """
        if self.buttons_pressed:        # if buttons_pressed is equal to 0 it's not necessary to get the mouse motion
            print(repr(event))


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
