from random import randint as random_range, choice as random_from_seq

TILES_ROW = 10
TILES_COL = 10
SNAKE_INIT_LENGTH = 3

class Board():
    NOTHING     = 0
    S_HEAD      = 1
    S_BODY      = 2
    APPLE       = 3

    def __init__(self):
        self._width = TILES_ROW
        self._height = TILES_COL
        self._array2d = [[0 for i in range(TILES_ROW)] for i in range(TILES_COL)]
        self.init_random_snake()

    def init_random_snake(self):
        apple = (random_range(0, TILES_ROW -1), random_range(0, TILES_COL-1))
        while True:
            snake_head = (random_range(0, TILES_ROW-1), random_range(0, TILES_COL-1))
            if apple != snake_head:
                self._assign(apple, Board.APPLE)
                self._assign(snake_head, Board.S_HEAD)
                break
        snake_cur_pos = snake_head
        for i in range(SNAKE_INIT_LENGTH):
            snake_next_pos = random_from_seq(self._get_closest_blank_points(snake_cur_pos))
            self._assign(snake_next_pos, Board.S_BODY)
            snake_cur_pos = snake_next_pos

        for row in self._array2d:
            print(row)



    ''' assign new value to a given position=(x,y) '''
    def _assign(self, position, value):
        x, y = position
        self._array2d[x][y] = value

    def _get_closest_points(self, position):
        x, y =  position
        all_positions = [(x-1, y),
                         (x+1, y),
                         (x, y+1),
                         (x, y-1)]
        return [(x,y) for x,y in all_positions
                if
                0 <= x < TILES_COL and
                0 <= y < TILES_ROW
                ]

    def _get_closest_blank_points(self, position):
        return [(x,y) for x, y in self._get_closest_points(position) if self._array2d[x][y] == Board.NOTHING]

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    '''
    returns NOTHING, S_HEAD, S_BODY, or APPLE
    '''
    def get_tile(self, x, y):
        return self._array2d[x][y]

    '''
    iterator throwing objects that looks like -
    ((x,y), value)
    '''
    def iterate_important_positions(self):
        for i in range(TILES_ROW):
            for j in range(TILES_COL):
                value = self._array2d[i][j]
                if value: # not NOTHING
                    yield ((i, j), value)