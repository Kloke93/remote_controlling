"""
Author: Tomas Dal Farra
Date: 29/05/2023
Description: Module to execute data received for computer devices (monitor, keyboard and mouse)
"""
import time

import pyautogui


class UseKeyBoard:
    """ Execute commands in keyboard """

    @staticmethod
    def press(key):
        """
        Presses down a key
        :param key: The key to be pressed down
        """
        pyautogui.keyDown(key)

    @staticmethod
    def release(key):
        """
        Releases a key
        :param key: The key to be released up
        """
        pyautogui.keyUp(key)


class UseMouse:
    """ Execute commands in mouse """

    @staticmethod
    def press(x, y, button):
        """
        presses a mouse button
        :param x: x position where the press happens
        :param y: y position where the press happens
        :param button: the button to be pressed
        """
        pyautogui.mouseDown(x, y, button)

    @staticmethod
    def release(x, y, button):
        """
        releases a mouse button
        :param x: x position where the release happens
        :param y: y position where the release happens
        :param button: the button to be released
        """
        pyautogui.mouseUp(x, y, button)

    @staticmethod
    def move(x, y):
        """
        Moves mouse cursor to an x y position
        :param x: x position to move
        :param y: y position to move
        """
        pyautogui.moveTo(x, y)

    @staticmethod
    def scroll(delta, x, y):
        """
        Execute a scroll
        :param delta: Amount of scrolling to perform
        :param x: x position where the scroll happens
        :param y: y position where the scroll happens
        """
        pyautogui.scroll(delta, x, y)


def main():
    time.sleep(10)
    pyautogui.write("sorry nir I will get my project done", interval=0.25)


if __name__ == "__main__":
    main()
