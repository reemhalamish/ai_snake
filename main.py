import GUI
from boardstate import BoardState
from snake_ai import SnakeAI

from tkinter import Tk

init_board = BoardState()
snake_mind = SnakeAI(init_board)
root = Tk()
GUI.GUI(root, init_board, snake_mind)
root.mainloop()
