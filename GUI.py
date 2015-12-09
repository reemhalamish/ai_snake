# python3 from tkinter import *
from Tkinter import Frame, Canvas
from boardstate import BoardState
# TILE_SIZE = 20
FRAMES_PER_SECOND = 35
MS_BETWEEN_FRAMES = 1000//FRAMES_PER_SECOND
BORDER_BETWEEN_TILES_PXL = 5


class GUI(Frame):

    def __init__(self, master, board_state, snake_ai):
        # python3 super().__init__(master)
        Frame.__init__(self, master)
        self._master = master
        self._board = board_state
        self._snake_ai = snake_ai
        # self._all_pics = dict()
        # self.initiate_all_pics()
        # self._labels = dict()
        self._canvas = None  # will be initated
        self.important_positions = dict()
        self.pos_to_canvas_handles = dict()
        self.suspicious_tiles_to_delete = set()
        self.draw_first_board()  # initiate the labels inside

        # debugging
        self.debug_snake_length_turns = []

        master.title("Snake")
        master.attributes("-fullscreen", True)
        master.configure(background='white')
        master.bind('<Escape>', self.quit)
        master.bind('q', self.quit)
        master.bind('d', self.debug)
        self.pack()

        self.after(MS_BETWEEN_FRAMES, self.next_frame)

    # def initiate_all_pics(self):
    #     for filepath in (
    #         "green",
    #         "red",
    #         "purple",
    #         "white"
    #     ):
    #         image = PhotoImage(file="pics\\" + filepath + ".gif")
    #         self._all_pics[filepath] = image
    #
    # def initiate_labels(self):
    #     for y in range(board.get_height()):
    #         for x in range(board.get_width()):
    #

    def draw_first_board(self):
        master, board = self._master, self._board
        canvas = Canvas(self, width=master.winfo_screenwidth()-2, height=master.winfo_screenheight()-2, bg='black') # TODO SHOW remove the -2 later
        canvas.pack()
        self._canvas = canvas
        for pos, value in board.iterate_important_positions():
            if value > BoardState.TILE_SNAKE_BODY_DEFAULT:
                value = BoardState.TILE_SNAKE_BODY_DEFAULT
            self.important_positions[pos] = value
            handle = self.createRect(pos, value)
            self.pos_to_canvas_handles[pos] = handle





    #
    # def draw_first_board_old(self):
    #     master, board = self._master, self._board
    #     board_to_pic, pic_to_tkimage = GUI.BOARD_TO_PICNAME, self._all_pics
    #     BACKGROUND = BoardState.TILE_NOTHING
    #     bg_positions = set()
    #     important_positions = dict()
    #     for x in range(BoardState.get_width()):
    #         for y in range(BoardState.get_height()):
    #             bg_positions.add((x, y))
    #     for pos, value in board.iterate_important_positions():
    #         bg_positions.remove(pos)
    #         if value > BoardState.TILE_SNAKE_BODY_DEFAULT:
    #             value = BoardState.TILE_SNAKE_BODY_DEFAULT
    #         important_positions[pos] = value
    #
    #     for pos in bg_positions:
    #         x, y = pos
    #         w = Button(master,
    #                    image=pic_to_tkimage[board_to_pic[BACKGROUND]],
    #                    command=lambda gui=self, pos=(x, y): GUI.click(gui, pos)) # TODO only patch, resolve!
    #         w.grid(row=y, column=x)
    #         self._labels[(x, y)] = w
    #
    #     for pos, value in important_positions.items():
    #         x, y = pos
    #         w = Button(master,
    #                    image=pic_to_tkimage[board_to_pic[value]],
    #                    command=lambda gui=self, pos=(x, y): GUI.click(gui, pos)) # TODO only patch, resolve!
    #         w.grid(row=y, column=x)
    #         self._labels[(x, y)] = w
    #         self.suspicious_tiles_to_delete.add(pos)
    #     #
    #     # for y, row in enumerate(board.get_full_2d_board()):
    #     #     for x, value in enumerate(row):
    #     #         if value > BoardState.TILE_SNAKE_BODY_DEFAULT:
    #     #             value = BoardState.TILE_SNAKE_BODY_DEFAULT
    #
    #     #
    #     # all_positions = [(x, y) for y in range(self._board.get_height()) for x in range(self._board.get_width())]
    #     # for position, value in self._board.iterate_important_positions():
    #     #     all_positions.remove(position)
    #     #     if value > BoardState.TILE_SNAKE_BODY_DEFAULT:
    #     #         value = BoardState.TILE_SNAKE_BODY_DEFAULT
    #     #     self._labels[position].configure(image=pic_to_tkimage[board_to_pic[value]])
    #     #
    #     # for position in all_positions:  # all who left need to be background
    #     #     background = BoardState.TILE_NOTHING
    #     #     self._labels[position].configure(image=pic_to_tkimage[board_to_pic[background]])
    #
    # def draw_board_old(self, prev_board, new_board):
    #     SNAKE_HEAD, SNAKE_BODY, BACKGROUND = BoardState.TILE_SNAKE_HEAD, \
    #                                          BoardState.TILE_SNAKE_BODY_DEFAULT, \
    #                                          BoardState.TILE_NOTHING
    #
    #     pic_to_tkimage, board_to_picname = self._all_pics, GUI.BOARD_TO_PICNAME
    #
    #     suspicious = set()
    #     new_positions = dict()
    #     # The very point of "suspicious" is that for every frame, you need only to erase places that the snake were in
    #     # so you save them and pass them to the next frame
    #
    #     for pos, value in self._board.iterate_important_positions():
    #         if value > SNAKE_BODY:
    #             value = SNAKE_BODY
    #         new_positions[pos] = value
    #         suspicious.add(pos)
    #         if pos in self.suspicious_tiles_to_delete:
    #             self.suspicious_tiles_to_delete.remove(pos)
    #
    #     for pos in self.suspicious_tiles_to_delete:
    #         self._labels[pos].configure(image=pic_to_tkimage[board_to_picname[BACKGROUND]])
    #     for pos, value in new_positions.items():
    #         self._labels[pos].configure(image=pic_to_tkimage[board_to_picname[value]])
    #
    #     self.suspicious_tiles_to_delete = suspicious
    #     #
    #     # for y, row in enumerate(new_board.get_full_2d_board()):
    #     #     for x, value in enumerate(row):
    #     #         if value > SNAKE_BODY: value = SNAKE_BODY
    #     #
    #     #         pos = (x, y)
    #     #
    #     #         # TODO debugging, remove
    #     #         if value == BoardState.TILE_APPLE:
    #     #                 print("draw_board", "apple position:", pos)
    #     #
    #     #
    #     #         self._labels[pos].configure(image=pic_to_tkimage[board_to_picname[value]])
    #
    #     '''
    #     old_positions = {position: value for position, value in prev_board.iterate_snake_positions()}
    #     new_positions = {position: value for position, value in new_board.iterate_snake_positions()}
    #     for position in old_positions:
    #         if position not in new_positions:
    #             self._labels[position].configure(image=pic_to_tkimage[board_to_picname[BACKGROUND]])
    #     for position, new_v in new_positions.items():
    #         new_v = new_v if new_v <= SNAKE_BODY else SNAKE_BODY
    #         old_v = old_positions[position] if position in old_positions else BACKGROUND
    #         old_v = SNAKE_BODY if old_v > SNAKE_BODY else old_v
    #         if new_v != old_v:
    #             self._labels[position].configure(image=pic_to_tkimage[board_to_picname[new_v]])
    #
    #     # draw the head position
    #     self._labels[new_board.get_snake_head_position()].configure(image=pic_to_tkimage[board_to_picname[SNAKE_HEAD]])
    #     '''

    def draw_board(self, prev_board, new_board):
        board, important_positions, handles = self._board, self.important_positions, self.pos_to_canvas_handles
        prev_positions = set(important_positions.keys())
        for pos, value in board.iterate_important_positions():
            if pos in prev_positions:
                prev_positions.remove(pos)

            if value > BoardState.TILE_SNAKE_BODY_DEFAULT:
                value = BoardState.TILE_SNAKE_BODY_DEFAULT

            if pos not in important_positions:
                important_positions[pos] = value
                handle = self.createRect(pos, value)
                handles[pos] = handle
            elif value != important_positions[pos]:
                handle_to_del = handles[pos]
                self._canvas.delete(handle_to_del)
                new_handle = self.createRect(pos, value)
                handles[pos] = new_handle
                important_positions[pos] = value
            else:   # position and value match, i.e. it's already painted well
                pass

        for pos in prev_positions:
            important_positions.pop(pos)
            self._canvas.delete(handles[pos])

    def redraw_apple(self, pos_to_erase = None):
        board, canvas, important_positions = self._board, self._canvas, self.important_positions
        if pos_to_erase:
            canvas.delete(self.pos_to_canvas_handles[pos_to_erase])
            important_positions.pop(pos_to_erase)

        apple_pos = board.get_apple_position()
        if apple_pos not in important_positions:
            self.pos_to_canvas_handles[apple_pos] = self.createRect(apple_pos, BoardState.TILE_APPLE)


    def redraw_apple_old(self, pos_to_erase = None):
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

        self.debug_snake_length_turns.append(self._board.get_snake_length())

    @staticmethod
    def click(self, position):
        old_apple_pos = self._board.get_apple_position()
        self._board.create_new_apple(position)
        self.redraw_apple(pos_to_erase=old_apple_pos)
        self._snake_ai.get_next_move(self._board)

    def debug(self, event=None):
        print("snake length MEMUTZA", sum(self.debug_snake_length_turns)/len(self.debug_snake_length_turns))

    def quit(self, event=None):
        self._snake_ai.quit() # doesn't need as the master.quit() will close all associated daemons with it :)
        # self.debug()
        self._master.quit()


    @staticmethod
    def getColorForTile(tileValue):
        if tileValue == BoardState.TILE_APPLE:
            return '#f55'   # REDish
        elif tileValue == BoardState.TILE_SNAKE_HEAD:
            return '#08f'   # BLUE greeny
        elif tileValue >= BoardState.TILE_SNAKE_BODY_DEFAULT:
            return '#0f8'   # GREEN bluey
        else:
            return '#000'   # black

    ''' returns x0, y0, x1, y1 '''
    def convert_pos_to_canvas(self, pos):
        pos_x, pos_y = pos
        net_width = self._master.winfo_screenwidth() - (BoardState.get_width()-1) * BORDER_BETWEEN_TILES_PXL
        tile_width = net_width // BoardState.get_width()
        x_start = (tile_width + BORDER_BETWEEN_TILES_PXL) * pos_x
        x_end = x_start + tile_width

        net_height = self._master.winfo_screenheight() - (BoardState.get_height()-1) * BORDER_BETWEEN_TILES_PXL
        tile_height = net_height // BoardState.get_height()
        y_start = (tile_height + BORDER_BETWEEN_TILES_PXL) * pos_y
        y_end = y_start + tile_height

        return x_start, y_start, x_end, y_end

    def createRect(self, tile_pos, tile_value):
        color = GUI.getColorForTile(tile_value)
        x_start, y_start, x_end, y_end = self.convert_pos_to_canvas(tile_pos)
        return self._canvas.create_rectangle(x_start, y_start, x_end, y_end, fill=color)


    BOARD_TO_PICNAME = {
        BoardState.TILE_APPLE:              "green",
        BoardState.TILE_SNAKE_HEAD:         "red",
        BoardState.TILE_SNAKE_BODY_DEFAULT: "purple",
        BoardState.TILE_NOTHING:            "white"
    }