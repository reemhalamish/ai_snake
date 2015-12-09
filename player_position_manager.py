from thread_laser_capture import ThreadLaserCapture

class PlayerPositionManager():
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows
        self.frames_since_last_change = 0
        self.player_pos = None
        self.topleft = None
        self.topright = None
        self.botleft = None
        self.botright = None
        self.laser_capture_daemon = ThreadLaserCapture()

        # TODO some initation for the corners

    ''' returns a position in snake '''
    def get_player_position(self):
        return self.player_pos

    def update_player_position(self, new_pos):
        self.player_pos = new_pos

    def convert_laser_place_to_player_pos(self, laser_place):
        """
        the idea is like that - if you have some polygon with
        :param laser_place: in pixels, as captured by thread_laser_capture
        :return: None
        """
        pass



