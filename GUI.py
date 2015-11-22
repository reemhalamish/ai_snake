from tkinter import *
import board
TILE_SIZE = 20

class GUI(Frame):

    def __init__(self, master, board_state):
        super().__init__(master)
        self._master = master
        self._board = board_state
        self._all_pics = dict()
        self.initiate_all_pics()
        self._labels = dict()
        self.initiate_labels()
        # master.minsize(width=TILE_SIZE * board.TILES_ROW, height=TILE_SIZE * board.TILES_COL)
        # master.maxsize(width=TILE_SIZE * board.TILES_ROW, height=TILE_SIZE * board.TILES_COL)
        self.draw_board()

    def initiate_all_pics(self):
        for filepath in (
            "green",
            "red",
            "purple",
            "white"
        ):
            image = PhotoImage(file="pics\\" + filepath + ".gif")
            self._all_pics[filepath] = image

    def initiate_labels(self):
        master, pics = self._master, self._all_pics
        for i in range(board.TILES_ROW):
            for j in range(board.TILES_COL):
                w = Label(master, image=pics["white"])
                w.grid(row=i, column=j)
                self._labels[(i,j)] = w

    def draw_board(self):
        board_to_pic, pic_to_tkimage = GUI.BOARD_TO_PICNAME, self._all_pics
        for position, value in self._board.iterate_important_positions():
            self._labels[position].configure(image=pic_to_tkimage[board_to_pic[value]])



    BOARD_TO_PICNAME = {
        board.Board.APPLE  : "green",
        board.Board.S_HEAD : "red",
        board.Board.S_BODY : "purple",
        board.Board.NOTHING: "white"
    }