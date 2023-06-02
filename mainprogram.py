"""
Author: Tomas Dal Farra
Date:
Description: Execute the main program
"""
import socket
from tkinter import Tk
from menu import MainMenu
from dataget import InputMouse, InputKeyBoard
from database import DataBase
from client import Client
import cv2 as cv


def main():
    db = DataBase()
    root = Tk()
    InputMouse(root)
    InputKeyBoard(root)
    MainMenu(root, db.get_id(), db.get_password())
    root.mainloop()
    db.close()


if __name__ == "__main__":
    main()
