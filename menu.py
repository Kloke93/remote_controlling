"""
Author: Tomas Dal Farra
Date:
Description:
"""
import tkinter as tk


class Menu:
    """ Class to organize all the menu GUI """

    def __init__(self):
        """ Menu initializer """
        self.root = tk.Tk()


def motion(event):
    x, y = event.x, event.y
    print(x, y)


def main():
    window = tk.Tk()
    window.bind('<Motion>', motion)
    window.mainloop()


if __name__ == "__main__":
    main()
