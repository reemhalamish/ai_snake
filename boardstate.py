from random import randint as random_range, choice as random_from_seq

TILES_ROW = 10
TILES_COL = 10
SNAKE_INIT_LENGTH = 5


class BoardState:
    TILE_APPLE = -1
    TILE_NOTHING = 0
    TILE_SNAKE_HEAD = 1
    TILE_SNAKE_BODY_DEFAULT = 2   # and so on...
    # snake will be:        head ---> 1, 2, 3, 4, 5 <--- tail

    MOVE_U = (0, -1)
    MOVE_D = (0, 1)
    MOVE_R = (1, 0)
    MOVE_L = (-1, 0)
    ALL_MOVES = (MOVE_D, MOVE_L, MOVE_U, MOVE_R)

    def __init__(self, i_have_parent=None, parent_movement=None, leave_prev_tail=False):
        self._width = TILES_ROW
        self._height = TILES_COL
        if i_have_parent:
            self._copy(i_have_parent, parent_movement, leave_prev_tail)
        else:
            self._snake_positions = dict()
            self._snake_length = SNAKE_INIT_LENGTH
            self._snake_head_pos = None   # will be initiated
            self._snake_tail_pos = None   # will be initiated
            self._apple_pos = None   # will be initiated
            self.init_random_snake()

    ''' copies existing board state and then updates it by the movement '''
    def _copy(self, other, movement, leave_prev_tail):
        snake_len = other.get_snake_length()
        snake_tail_position = None  # will be initiated in a second
        if leave_prev_tail:
            snake_len += 1
            snake_tail_position = other.get_snake_tail_position()
        snake_positions = {}
        for position, value in other.iterate_snake_positions():
            value += 1
            if value > snake_len:
                # will be true only if NOT leave_prev_tail, only for the last tile (the tail)
                continue   # ignore the snake's prev tail
            elif value == snake_len and not leave_prev_tail: # this is the tail
                snake_tail_position = position
            snake_positions[position] = value

        # now for the snake's head
        snake_head = BoardState.add_positions(movement, other.get_snake_head_position())
        snake_positions[snake_head] = BoardState.TILE_SNAKE_HEAD

        # commit changes to the new board state
        self._snake_positions = snake_positions
        self._snake_length = snake_len
        self._snake_head_pos = snake_head
        self._snake_tail_pos = snake_tail_position
        self._apple_pos = other.get_apple_position()


    def init_random_snake(self):
        apple = (random_range(0, TILES_ROW-1), random_range(0, TILES_COL-1))
        self._apple_pos = apple

        snake_head = None
        while True:
            snake_head = (random_range(0, TILES_ROW-1), random_range(0, TILES_COL-1))
            if apple != snake_head:
                self._assign(snake_head, BoardState.TILE_SNAKE_HEAD)
                self._snake_head_pos = snake_head
                break

        snake_cur_pos = snake_head
        for snake_body_depth in range(BoardState.TILE_SNAKE_BODY_DEFAULT, SNAKE_INIT_LENGTH+1):
            snake_next_pos = random_from_seq(self._get_closest_blank_points(snake_cur_pos))
            self._assign(snake_next_pos, snake_body_depth)
            snake_cur_pos = snake_next_pos
        self._snake_tail_pos = snake_cur_pos

    ''' assign new value to a given position=(x,y) '''
    def _assign(self, position, value):
        if value:   # not TILE_NOTHING
            self._snake_positions[position] = value
        else:   # if got TILE_NOTHING, and something there, pop it out
            self._snake_positions.pop(position)

    @staticmethod
    def _get_closest_points(position):
        x, y = position
        all_positions = [(x-1, y),
                         (x+1, y),
                         (x, y+1),
                         (x, y-1)]
        return [(x,y) for x,y in all_positions
                if BoardState._is_inside_board((x, y))
                ]

    @staticmethod
    def _is_inside_board(position):
        x, y = position
        return 0 <= x < TILES_COL and 0 <= y < TILES_ROW

    def _is_not_captured_by_snake(self, position):
        return position not in self._snake_positions

    def _get_closest_blank_points(self, position):
        return [close for close in BoardState._get_closest_points(position) if close not in self._snake_positions]
        # i.e. already taken

    @staticmethod
    def add_positions(pos_a, pos_b):
        return pos_a[0] + pos_b[0], pos_a[1] + pos_b[1]

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_snake_length(self):
        return self._snake_length

    def get_snake_head_position(self):
        return self._snake_head_pos

    def get_snake_tail_position(self):
        return self._snake_tail_pos

    def get_apple_position(self):
        return self._apple_pos

    '''
    returns TILE_NOTHING, TILE_SNAKE_HEAD, TILE_SNAKE_BODY, or TILE_APPLE
    '''
    def get_tile(self, x, y):
        try:
            position = (x,y)
            return self._snake_positions[position]
        except KeyError:
            return BoardState.TILE_NOTHING

    '''
    iterator yielding objects that looks like -
    ((x,y), value)
    '''
    def iterate_snake_positions(self):
        yield from self._snake_positions.items()

    def iterate_important_positions(self):
        yield from self.iterate_snake_positions()

        if self._apple_pos not in self._snake_positions:  # not eaten
            yield self._apple_pos, BoardState.TILE_APPLE

    def get_full_2d_board(self):
        result = [[0 for _ in range(TILES_ROW)] for _ in range(TILES_COL)]
        for (x, y), value in self.iterate_important_positions():
            result[x][y] = value
        return result

    '''
    generates tuples in the pattern -
    successor_state, action
    when successor_is is a brand new board, and action is one of (MOVE_U\D\R\L)
    '''
    def get_successors(self):
        for move in self._get_all_valid_moves():
            yield BoardState(self, move), move

    def is_final_board(self):
        won = self.is_winning_board()
        lost =self.is_losing_board()
        return won or lost

    def is_winning_board(self):
        return self._snake_head_pos == self._apple_pos

    def is_losing_board(self):
        lost = True
        for _ in self._get_all_valid_moves():
            lost = False
            break
        return lost

    def _get_all_valid_moves(self):
        for move in BoardState.ALL_MOVES:
            new_snake_head = BoardState.add_positions(self._snake_head_pos, move)
            if BoardState._is_inside_board(new_snake_head) and self._is_not_captured_by_snake(new_snake_head):
                yield move

    @staticmethod
    def get_distance_between_positions(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])