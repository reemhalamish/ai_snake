from thread_laser_capture import ThreadLaserCapture
from point_to_tile_calculator import PointToTileCalculator
from time import sleep

TIME_TO_SLEEP_SECS = 0.01


class LaserManager:
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows
        self.player_place = None  # in pixels!
        self.topleft = None
        self.topright = None
        self.botleft = None
        self.botright = None
        self.calc_player_place_to_snake_pos = None
        self.frames_since_last_change = 0
        self.laser_capture_daemon = ThreadLaserCapture(self)
        self.laser_capture_daemon.start()

    def start_when_ready(self):
        while not self.calc_player_place_to_snake_pos:
            sleep(TIME_TO_SLEEP_SECS)
        return

    def init_calculator(self, pTopLeft, pTopRight, pBotLeft, pBotRight):
        print(pTopLeft, pTopRight, pBotLeft, pBotRight)
        calc = PointToTileCalculator(self.rows, self.columns, pTopLeft, pTopRight, pBotLeft, pBotRight)
        self.calc_player_place_to_snake_pos = calc

    ''' returns a position in snake world, can return positions out side the grid! '''
    def get_player_position(self):
        self.frames_since_last_change += 1
        return self.calc_player_place_to_snake_pos.get_tile(self.player_place)

    def update_player_place(self, new_place):
        self.player_place = new_place
        self.frames_since_last_change = 0

    def calculate_pixel(self, pixel):
        return self.calc_player_place_to_snake_pos.get_tile(pixel)

    def quit(self):
        self.laser_capture_daemon.exit_async()
        self.laser_capture_daemon.join()


