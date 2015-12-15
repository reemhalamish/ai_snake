import GUI
from boardstate import BoardState
from manager_ai import SnakeAIManager
from manager_laser import LaserManager
from manager_sound import SoundManager

# python3 from tkinter import Tk
from Tkinter import Tk

laser_manager = LaserManager(BoardState.get_cols(), BoardState.get_rows())
laser_manager.start_when_ready()   # starts when all 4 corners captured
sound_manager = SoundManager()
init_board = BoardState()
snake_mind = SnakeAIManager(init_board)
root = Tk()
GUI.GUI(root, init_board, snake_mind, laser_manager, sound_manager)
root.mainloop()
