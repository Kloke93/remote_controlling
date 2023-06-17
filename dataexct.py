"""
Author: Tomas Dal Farra
Date: 29/05/2023
Description: Module to execute data received for computer devices (monitor, keyboard and mouse)
"""
from threading import Thread
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
    def press(x: int, y: int, button):
        """
        presses a mouse button
        :param x: x position where the press happens
        :param y: y position where the press happens
        :param button: the button to be pressed
        """
        pyautogui.mouseDown(x, y, button)

    @staticmethod
    def release(x: int, y: int, button):
        """
        releases a mouse button
        :param x: x position where the release happens
        :param y: y position where the release happens
        :param button: the button to be released
        """
        pyautogui.mouseUp(x, y, button)

    @staticmethod
    def move(x: int, y: int):
        """
        Moves mouse cursor to an x y position
        :param x: x position to move
        :param y: y position to move
        """
        pyautogui.moveTo(x, y)

    @staticmethod
    def scroll(delta, x: int, y: int):
        """
        Execute a scroll
        :param delta: Amount of scrolling to perform
        :param x: x position where the scroll happens
        :param y: y position where the scroll happens
        """
        pyautogui.scroll(delta, x, y)


def main():
    mouse = UseMouse()
    Thread(target=mouse.move, args=(0, 0)).start()


if __name__ == "__main__":
    main()
