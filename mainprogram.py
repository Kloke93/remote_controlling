"""
Author: Tomas Dal Farra
Date:
Description: Execute the main program
"""
from tkinter import Tk
from menu import MainMenu
from dataget import InputMouse, InputKeyBoard
from client import Client
import cv2 as cv


def main():
    root = Tk()
    mouse = InputMouse(root)
    keyboard = InputKeyBoard(root)
    MainMenu(root)
    mouse.bind_window()
    keyboard.bind_window()
    root.mainloop()


if __name__ == "__main__":
    main()
