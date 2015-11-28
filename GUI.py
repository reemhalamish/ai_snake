from tkinter import *
import boardstate
TILE_SIZE = 20
FRAMES_PER_SECOND = 20
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

        master.bind('q', self.quit)

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
                self._labels[(i, j)] = w

    def draw_first_board(self):
        board_to_pic, pic_to_tkimage = GUI.BOARD_TO_PICNAME, self._all_pics
        all_positions = [(x, y) for x in range(boardstate.TILES_ROW) for y in range(boardstate.TILES_COL)]
        for position, value in self._board.iterate_important_positions():
            all_positions.remove(position)
            if value > boardstate.BoardState.TILE_SNAKE_BODY_DEFAULT:
                value = boardstate.BoardState.TILE_SNAKE_BODY_DEFAULT
            self._labels[position].configure(image=pic_to_tkimage[board_to_pic[value]])

        for position in all_positions: # all who left need to be background
            background = boardstate.BoardState.TILE_NOTHING;
            self._labels[position].configure(image=pic_to_tkimage[board_to_pic[background]])

    def draw_board(self, prev_board, new_board):
        SNAKE_BODY, BACKGROUND = boardstate.BoardState.TILE_SNAKE_BODY_DEFAULT, boardstate.BoardState.TILE_NOTHING
        pic_to_tkimage, board_to_picname = self._all_pics, GUI.BOARD_TO_PICNAME

        old_positions = {position: value for position, value in prev_board.iterate_snake_positions()}
        new_positions = {position: value for position, value in new_board.iterate_snake_positions()}
        for position in old_positions:
            if position not in new_positions:
                self._labels[position].configure(image=pic_to_tkimage[board_to_picname[BACKGROUND]])
        for position in new_positions:
            old_v = old_positions[position] if position in old_positions else BACKGROUND
            old_v = SNAKE_BODY if old_v > SNAKE_BODY else old_v
            new_v = new_positions[position] if new_positions[position] <= SNAKE_BODY else SNAKE_BODY
            if new_v != old_v:
                self._labels[position].configure(image=pic_to_tkimage[board_to_picname[new_v]])

    def redraw_apple(self):
        APPLE = boardstate.BoardState.TILE_APPLE
        pic_to_tkimage, board_to_picname = self._all_pics, GUI.BOARD_TO_PICNAME
        self._labels[self._board.get_apple_position()].configure(image=pic_to_tkimage[board_to_picname[APPLE]])

    def next_frame(self):
        if self._board.is_final_board():
            if self._board.is_winning_board():
                self._board.create_new_apple()
                self.redraw_apple()
                self._snake_ai.update_moves(self._board)
                self.after(MS_BETWEEN_FRAMES, self.next_frame)
            else:
                self.after(5 * 1000, self.quit)
            return
        next_board = boardstate.BoardState(self._board, self._snake_ai.get_next_move(self._board))
        self.draw_board(self._board, next_board)
        self._board = next_board
        self.after(MS_BETWEEN_FRAMES, self.next_frame)

    def quit(self, event=None):
        self._master.quit()

    BOARD_TO_PICNAME = {
        boardstate.BoardState.TILE_APPLE  : "green",
        boardstate.BoardState.TILE_SNAKE_HEAD : "red",
        boardstate.BoardState.TILE_SNAKE_BODY_DEFAULT : "purple",
        boardstate.BoardState.TILE_NOTHING: "white"
    }