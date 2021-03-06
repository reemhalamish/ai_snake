# python3 from tkinter import *
from Tkinter import Frame, Canvas, PhotoImage
from boardstate import BoardState
from manager_sound import SoundManager
# TILE_SIZE = 20
FRAMES_PER_SECOND = 33
UPDATE_LASER_EVERY_NTH_MS = 10
MS_BETWEEN_FRAMES = 1000//FRAMES_PER_SECOND
BORDER_BETWEEN_TILES_PXL = 5


class GUI(Frame):

    def __init__(self, master, board_state, manager_snake_ai, manager_laser, manager_sound):
        # python3 super().__init__(master)
        Frame.__init__(self, master)
        self._master = master
        self._board = board_state
        self._snake_ai_manager = manager_snake_ai
        self._laser_manager = manager_laser
        self._sound_manager = manager_sound
        self._canvas = self.init_canvas()
        self.important_positions = dict()
        self.pos_to_canvas_handles = dict()
        self.suspicious_tiles_to_delete = set()

        self.laser_photo = 1

        # debugging
        self.debug_snake_length_turns = []

        master.title("Snake")
        master.attributes("-fullscreen", True)
        master.configure(background='white')
        master.bind('<Escape>', lambda e: self.quit_all())
        master.bind('q', lambda e: self.quit_all())
        master.bind('d', lambda e: self.debug())
        master.bind('s', lambda e: self.start_snake())
        master.bind('+', lambda e: self.change_frames_speed(5))
        master.bind('-', lambda e: self.change_frames_speed(-5))

        self.pack()
        if manager_laser.using_laser():
            self.show_laser_on_screen()
        else:
            self.laser_photo = 'start!'
            self.start_snake()

    def init_canvas(self):
        master = self.master
        canvas = Canvas(self, width=master.winfo_screenwidth(), height=master.winfo_screenheight(), bg='black')
        canvas.pack()
        return canvas

    def show_laser_on_screen(self):
        self.master.focus_force()
        canvas = self._canvas
        rows, cols = self._board.get_rows(), self._board.get_cols()
        img = self.laser_photo = PhotoImage(file='pics/black_640_480.gif')
        self.pos_to_canvas_handles['laser_start_pic'] = canvas.create_image(0, 0, image=self.laser_photo, anchor='nw')
        for y in range(img.height()):
            for x in range(img.width()):
                val = self._laser_manager.calculate_pixel((x, y))
                val_x, val_y = val      # x ranges [-1,cols] and y ranges [-1, rows]
                if val_x < 0 or val_x >= cols or val_y < 0 or val_y >= rows:
                    continue
                val_x += 1
                val_y += 1
                # stretch to [1, 255]
                val_x = val_x * 255 // cols
                val_y = val_y * 255 // rows
                color = '#00' + format(val_x, '02x') + format(val_y, '02x')
                img.put(color, (x, y))

    def start_snake(self, _=None):
        if self.laser_photo:
            self._canvas.delete(self.pos_to_canvas_handles.pop('laser_start_pic', None))
            self.laser_photo = None
            self._sound_manager.play_normal_loop()
            self.draw_first_board()
            self.after(MS_BETWEEN_FRAMES, self.next_frame)
            self.after(UPDATE_LASER_EVERY_NTH_MS, self.update_laser)
            self.master.focus_force()


    def draw_first_board(self):
        master, board = self._master, self._board
        for pos, value in board.iterate_important_positions():
            if value > BoardState.TILE_SNAKE_BODY_DEFAULT:
                value = BoardState.TILE_SNAKE_BODY_DEFAULT
            self.important_positions[pos] = value
            handle = self.create_rect(pos, value)
            self.pos_to_canvas_handles[pos] = handle

    def draw_board(self):
        board, important_positions, handles = self._board, self.important_positions, self.pos_to_canvas_handles
        prev_positions = set(important_positions.keys())
        for pos, value in board.iterate_important_positions():
            if pos in prev_positions:
                prev_positions.remove(pos)

            if value > BoardState.TILE_SNAKE_BODY_DEFAULT:
                value = BoardState.TILE_SNAKE_BODY_DEFAULT

            if pos not in important_positions:
                important_positions[pos] = value
                handle = self.create_rect(pos, value)
                handles[pos] = handle
            elif value != important_positions[pos]:
                handle_to_del = handles[pos]
                self._canvas.delete(handle_to_del)
                new_handle = self.create_rect(pos, value)
                handles[pos] = new_handle
                important_positions[pos] = value
            else:   # position and value match, i.e. it's already painted well
                pass

        for pos in prev_positions:
            important_positions.pop(pos)
            self._canvas.delete(handles[pos])

    def redraw_apple(self, pos_to_erase=None):
        board, canvas, important_positions = self._board, self._canvas, self.important_positions
        if pos_to_erase:
            canvas.delete(self.pos_to_canvas_handles[pos_to_erase])
            important_positions.pop(pos_to_erase)

        apple_pos = board.get_apple_position()
        if apple_pos not in important_positions:
            self.pos_to_canvas_handles[apple_pos] = self.create_rect(apple_pos, BoardState.TILE_APPLE)

    def next_frame(self):
        board, ai_manager, laser_manager, sound_manager = \
            self._board, self._snake_ai_manager, self._laser_manager, self._sound_manger
        if board.is_winning_board():
            self._sound_manager.update_chase(SoundManager.NO_CHASE)
            board.create_new_apple()

        next_board = BoardState(board, ai_manager.get_next_move(board))
        self.draw_board()
        self._board = next_board
        self.after(MS_BETWEEN_FRAMES, self.next_frame)

        self.debug_snake_length_turns.append(self._board.get_snake_length())

    def update_laser(self):
        old_apple_pos = self._board.get_apple_position()
        player_position = self._laser_manager.get_player_position_if_valid()
        if player_position and (player_position != old_apple_pos):
            self._board.create_new_apple(player_position)
            self._sound_manager.update_chase(SoundManager.AT_CHASE)
            self.redraw_apple(pos_to_erase=old_apple_pos)
        self.after(UPDATE_LASER_EVERY_NTH_MS, self.update_laser)

    def quit_all(self, _=None):
        print("quitting...")
        self._snake_ai_manager.quit()  # doesn't need as the master.quit() will close all associated daemons with it :)
        self._laser_manager.quit()
        for handle in self.pos_to_canvas_handles:
            self._canvas.delete(handle)
        self._canvas.destroy()
        self.destroy()
        self._master.destroy()
        print("quiting main thread")
        exit()

    @staticmethod
    def get_color_for_tile(tile_value):
        if tile_value == BoardState.TILE_APPLE:
            return '#000'   # INVISIBLE APPLE!! '#f55'   # REDish
        elif tile_value == BoardState.TILE_SNAKE_HEAD:
            return '#08f'   # BLUE greeny
        elif tile_value >= BoardState.TILE_SNAKE_BODY_DEFAULT:
            return '#0f8'   # GREEN bluey
        else:
            return '#000'   # black

    ''' returns x0, y0, x1, y1 '''
    def convert_pos_to_canvas(self, pos):
        pos_x, pos_y = pos
        net_width = self._master.winfo_screenwidth() - (BoardState.get_cols() - 1) * BORDER_BETWEEN_TILES_PXL
        tile_width = net_width // BoardState.get_cols()
        x_start = (tile_width + BORDER_BETWEEN_TILES_PXL) * pos_x
        x_end = x_start + tile_width

        net_height = self._master.winfo_screenheight() - (BoardState.get_rows() - 1) * BORDER_BETWEEN_TILES_PXL
        tile_height = net_height // BoardState.get_rows()
        y_start = (tile_height + BORDER_BETWEEN_TILES_PXL) * pos_y
        y_end = y_start + tile_height

        return x_start, y_start, x_end, y_end

    def create_rect(self, tile_pos, tile_value):
        color = GUI.get_color_for_tile(tile_value)
        x_start, y_start, x_end, y_end = self.convert_pos_to_canvas(tile_pos)
        return self._canvas.create_rectangle(x_start, y_start, x_end, y_end, fill=color)

    def change_frames_speed(self, speed_to_change):
        global MS_BETWEEN_FRAMES
        MS_BETWEEN_FRAMES += speed_to_change
        MS_BETWEEN_FRAMES = max(MS_BETWEEN_FRAMES, 10)

    BOARD_TO_PICNAME = {
        BoardState.TILE_APPLE:              "green",
        BoardState.TILE_SNAKE_HEAD:         "red",
        BoardState.TILE_SNAKE_BODY_DEFAULT: "purple",
        BoardState.TILE_NOTHING:            "white"
    }
