import winsound

THEME_MUSIC_PATH = r'souds\game_theme_8_bit.wav'
EATING_SOUND_PATH = r'sounds\snake_eat_apple.wav'


class SoundManager:
    def __init__(self):
        pass

    @staticmethod
    def play_eating_sound(self=None):
        winsound.PlaySound(EATING_SOUND_PATH, winsound.SND_FILENAME | winsound.SND_NODEFAULT | winsound.SND_ASYNC)

    @staticmethod
    def play_repeat_music_theme(self=None):
        winsound.PlaySound(THEME_MUSIC_PATH, winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_NODEFAULT | winsound.SND_ASYNC)
