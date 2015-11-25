from tkinter import *
import boardstate
TILE_SIZE = 20
FRAMES_PER_SECOND = 4
MS_BETWEEN_FRAMES = 1000//FRAMES_PER_SECOND

class GUI(Frame):

    def __init__(self, master, board_state, snake_ai):
        super().__init__(master)
        self._master = master
        self._board = board_state
        self._snake_ai = snake_ai
        self._all_pics = dict()
        self.initiate_all_pics()
        self._labels = dict()
        self.initiate_labels()
        self.draw_first_board()

        self.after(MS_BETWEEN_FRAMES, self.next_frame)

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
        for i in range(boardstate.TILES_ROW):
            for j in range(boardstate.TILES_COL):
                w = Label(master, image=pics["white"])
                w.grid(row=j, column=i)
                self._labels[(i,j)] = w

    def draw_first_board(self):
        board_to_pic, pic_to_tkimage = GUI.BOARD_TO_PICNAME, self._all_pics
        all_positions = [(x, y) for x in range(boardstate.TILES_ROW) for y in range(boardstate.TILES_COL)]
        for position, value in self._board.iterate_important_positions():
            print(position, value)
            all_positions.remove(position)
            if value > boardstate.BoardState.TILE_SNAKE_BODY_DEFAULT:
                value = boardstate.BoardState.TILE_SNAKE_BODY_DEFAULT
            self._labels[position].configure(image=pic_to_tkimage[board_to_pic[value]])

        for position in all_positions: # all who left need to be background
            background = boardstate.BoardState.TILE_NOTHING;
            self._labels[position].configure(image=pic_to_tkimage[board_to_pic[background]])

    def draw_board(self, body_positions = [], positions_to_erase=[]):
        pic_to_tkimage, board_to_picname = self._all_pics, GUI.BOARD_TO_PICNAME
        SNAKE_HEAD, SNAKE_BODY, BACKGROUND = boardstate.BoardState.TILE_SNAKE_HEAD, boardstate.BoardState.TILE_SNAKE_BODY_DEFAULT, boardstate.BoardState.TILE_NOTHING
        snake_head_pos = self._board.get_snake_head_position()
        self._labels[snake_head_pos].configure(image=pic_to_tkimage[board_to_picname[SNAKE_HEAD]])
        for pos in body_positions:
            self._labels[pos].configure(image=pic_to_tkimage[board_to_picname[BACKGROUND]])
        for pos in positions_to_erase:
            self._labels[pos].configure(image=pic_to_tkimage[board_to_picname[BACKGROUND]])

    def next_frame(self):
        tiles_to_erase = [self._board.get_snake_tail_position()]
        if self._board.is_final_board():
            return
        next_board = boardstate.BoardState(self._board, self._snake_ai.get_next_move())
        self._board = next_board
        self.draw_board(tiles_to_erase)
        self.after(MS_BETWEEN_FRAMES, self.next_frame)



    BOARD_TO_PICNAME = {
        boardstate.BoardState.TILE_APPLE  : "green",
        boardstate.BoardState.TILE_SNAKE_HEAD : "red",
        boardstate.BoardState.TILE_SNAKE_BODY_DEFAULT : "purple",
        boardstate.BoardState.TILE_NOTHING: "white"
    }