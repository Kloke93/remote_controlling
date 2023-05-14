"""
Author: Tomas Dal Farra
Date: 13/04/2023
Description: Module to get all user input and screen output
"""

from mss import mss
import numpy as np
import cv2 as cv
import time


class InputGather:
    """ class to gather all data needed """
    def __init__(self):
        """ initializer """
        pass

    @staticmethod
    def on_click(x, y, bottom, pressed):
        """ A mouse bottom was clicked """
        pass

    @staticmethod
    def on_scroll(x, y, dx, dy):
        """ Mouse scroll """
        pass


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
        frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
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
