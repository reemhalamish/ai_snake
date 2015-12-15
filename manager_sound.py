import winsound

PLAYFULL_THEME = r'sounds\happy3.wav'
CHASE_THEME = r'sounds\snake_chase.wav'


class SoundManager:
    NO_CHASE = False
    AT_CHASE = True

    def __init__(self):
        self.st_chase = False
        self.play_normal_loop()

    def update_chase(self, is_chase):
        if is_chase != self.st_chase:
            self.st_chase = is_chase
            if is_chase:
                SoundManager.play_chase()
            else:
                SoundManager.play_normal_loop()

    @staticmethod
    def play_normal_loop():
        winsound.PlaySound(PLAYFULL_THEME, winsound.SND_FILENAME | winsound.SND_NODEFAULT | winsound.SND_LOOP | winsound.SND_ASYNC)

    @staticmethod
    def play_chase():
        winsound.PlaySound(CHASE_THEME, winsound.SND_FILENAME | winsound.SND_NODEFAULT | winsound.SND_LOOP | winsound.SND_ASYNC)
