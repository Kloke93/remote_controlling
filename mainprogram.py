"""
Author: Tomas Dal Farra
Date:
Description: Execute the main program
"""
from tkinter import Tk
from menu import MainMenu
from dataget import InputMouse, InputKeyBoard
from database import DataBase
from client import Client
import cv2 as cv


def main():
    db = DataBase()
    root = Tk()
    mouse = InputMouse(root)
    keyboard = InputKeyBoard(root)
    MainMenu(root, db.get_id(), db.get_password())
    mouse.bind_window()
    keyboard.bind_window()
    root.mainloop()
    db.close()


if __name__ == "__main__":
    main()
