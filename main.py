import GUI
from board import Board

from tkinter import Tk

board = Board()
root = Tk()
GUI.GUI(root, board)
root.mainloop()