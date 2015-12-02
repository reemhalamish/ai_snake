from tkinter import *
from boardstate import BoardState
TILE_SIZE = 20
FRAMES_PER_SECOND = 35
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
        self.draw_first_board()  # initiate the labels inside

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
    #
    # def initiate_labels(self):
    #     for y in range(board.get_height()):
    #         for x in range(board.get_width()):
    #

    def draw_first_board(self):
        master, board = self._master, self._board
        board_to_pic, pic_to_tkimage = GUI.BOARD_TO_PICNAME, self._all_pics
        for y, row in enumerate(board.get_full_2d_board()):
            for x, value in enumerate(row):
                if value > BoardState.TILE_SNAKE_BODY_DEFAULT:
                    value = BoardState.TILE_SNAKE_BODY_DEFAULT
                w = Button(master,
                           image=pic_to_tkimage[board_to_pic[value]],
                           command=lambda gui=self, pos=(y, x): GUI.click(gui, pos)) # TODO only patch, resolve!
                w.grid(row=y, column=x)
                self._labels[(x, y)] = w
        #
        # all_positions = [(x, y) for y in range(self._board.get_height()) for x in range(self._board.get_width())]
        # for position, value in self._board.iterate_important_positions():
        #     all_positions.remove(position)
        #     if value > BoardState.TILE_SNAKE_BODY_DEFAULT:
        #         value = BoardState.TILE_SNAKE_BODY_DEFAULT
        #     self._labels[position].configure(image=pic_to_tkimage[board_to_pic[value]])
        #
        # for position in all_positions:  # all who left need to be background
        #     background = BoardState.TILE_NOTHING
        #     self._labels[position].configure(image=pic_to_tkimage[board_to_pic[background]])

    def draw_board(self, prev_board, new_board):
        SNAKE_HEAD, SNAKE_BODY, BACKGROUND = BoardState.TILE_SNAKE_HEAD, \
                                             BoardState.TILE_SNAKE_BODY_DEFAULT, \
                                             BoardState.TILE_NOTHING

        pic_to_tkimage, board_to_picname = self._all_pics, GUI.BOARD_TO_PICNAME

        for y, row in enumerate(new_board.get_full_2d_board()):
            for x, value in enumerate(row):
                if value > SNAKE_BODY: value = SNAKE_BODY

                pos = (x, y)
                self._labels[pos].configure(image=pic_to_tkimage[board_to_picname[value]])

                '''
        old_positions = {position: value for position, value in prev_board.iterate_snake_positions()}
        new_positions = {position: value for position, value in new_board.iterate_snake_positions()}
        for position in old_positions:
            if position not in new_positions:
                self._labels[position].configure(image=pic_to_tkimage[board_to_picname[BACKGROUND]])
        for position, new_v in new_positions.items():
            new_v = new_v if new_v <= SNAKE_BODY else SNAKE_BODY
            old_v = old_positions[position] if position in old_positions else BACKGROUND
            old_v = SNAKE_BODY if old_v > SNAKE_BODY else old_v
            if new_v != old_v:
                self._labels[position].configure(image=pic_to_tkimage[board_to_picname[new_v]])

        # draw the head position
        self._labels[new_board.get_snake_head_position()].configure(image=pic_to_tkimage[board_to_picname[SNAKE_HEAD]])
        '''

    def redraw_apple(self, pos_to_erase = None):
        APPLE, NOTHING = BoardState.TILE_APPLE, BoardState.TILE_NOTHING
        pic_to_tkimage, board_to_picname = self._all_pics, GUI.BOARD_TO_PICNAME
        self._labels[self._board.get_apple_position()].configure(image=pic_to_tkimage[board_to_picname[APPLE]])
        if pos_to_erase:
            self._labels[pos_to_erase].configure(image=pic_to_tkimage[board_to_picname[NOTHING]])


    def next_frame(self):
        # if self._board.is_final_board():
        if self._board.is_winning_board():
            self._board.create_new_apple()
            # # self.redraw_apple()
            # self.after(MS_BETWEEN_FRAMES, self.next_frame)
            # return
            # # else:
            # #     self.after(5 * 1000, self.quit)

        next_board = BoardState(self._board, self._snake_ai.get_next_move(self._board))
        self.draw_board(self._board, next_board)
        self._board = next_board
        self.after(MS_BETWEEN_FRAMES, self.next_frame)

    @staticmethod
    def click(self, position):
        old_apple_pos = self._board.get_apple_position()
        self._board.create_new_apple(position)
        self.redraw_apple(pos_to_erase=old_apple_pos)
        self._snake_ai.get_next_move(self._board)

    def quit(self, event=None):
        self._master.quit()
        self._snake_ai.quit()

    BOARD_TO_PICNAME = {
        BoardState.TILE_APPLE:              "green",
        BoardState.TILE_SNAKE_HEAD:         "red",
        BoardState.TILE_SNAKE_BODY_DEFAULT: "purple",
        BoardState.TILE_NOTHING:            "white"
    }