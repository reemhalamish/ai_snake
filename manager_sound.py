import winsound

THEME_MUSIC_PATH = r'sounds\game_theme_8_bit.wav'
EATING_SOUND_PATH = r'sounds\snake_eat_apple.wav'

PLAYFULL_THEME = r'sounds\happy2.wav'
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
                self.play_chase()
            else:
                self.play_normal_loop()

    def play_normal_loop(self):
        winsound.PlaySound(PLAYFULL_THEME, winsound.SND_FILENAME | winsound.SND_NODEFAULT | winsound.SND_LOOP | winsound.SND_ASYNC)

    def play_chase(self):
        winsound.PlaySound(CHASE_THEME, winsound.SND_FILENAME | winsound.SND_NODEFAULT | winsound.SND_LOOP | winsound.SND_ASYNC)

    @staticmethod
    def play_eating_sound(self=None):
        winsound.PlaySound(EATING_SOUND_PATH, winsound.SND_FILENAME | winsound.SND_NODEFAULT | winsound.SND_ASYNC)

    @staticmethod
    def play_repeat_music_theme(self=None):
        winsound.PlaySound(THEME_MUSIC_PATH, winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_NODEFAULT | winsound.SND_ASYNC)
