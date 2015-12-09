import GUI
from boardstate import BoardState
from snake_ai import SnakeAI
from thread_laser_capture import LaserTracker

# python3 from tkinter import Tk
from Tkinter import Tk
'''
laser_tracker = LaserTracker()
laser_tracker.run()

'''
init_board = BoardState()
snake_mind = SnakeAI(init_board)
root = Tk()
GUI.GUI(root, init_board, snake_mind)
root.mainloop()
