from random import randint as random_range, choice as random_from_seq

'''
# max
TILES_ROWS = 55
TILES_COLS = 30
'''

# normal
TILES_ROWS = 12
TILES_COLS = 18
TILES_DEPTHS = 10

SNAKE_INIT_LENGTH = 3
SNAKE_MAX_LENGTH = 70
MAX_TURNS_SAVE_LEAVE_TAIL = 9


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
    MOVE_EMPTY = (0, 0)
    ALL_MOVES = (MOVE_D, MOVE_R, MOVE_U, MOVE_L)

    def __init__(self, i_have_parent=None, movement_from_parent = None):
        if i_have_parent:
            self._copy(i_have_parent, movement_from_parent)
        else:
            self._snake_positions_list = []     # head first!
            self._snake_length = SNAKE_INIT_LENGTH
            self._apple_pos = None   # will be initiated

            '''
            self.init_debugging_snake()
            '''
            try:
                self.init_random_snake()
            except IndexError:  # the random snake somehow crushed into himself at some point
                self.init_base_snake()  # create a very simple snake instead

    ''' copies existing board state and then updates it by the movement '''
    def _copy(self, other, movement):
        snake_positions_list = other._snake_positions_list[:]
        snake_len = other.get_snake_length()
        assert(len(snake_positions_list) == snake_len)

        leave_prev_tail = 0
        if hasattr(other, "leave_tail"):
            leave_prev_tail = min(other.leave_tail, MAX_TURNS_SAVE_LEAVE_TAIL)
        if snake_len >= SNAKE_MAX_LENGTH:
            leave_prev_tail = 0

        snake_head_pos = BoardState.add_positions(movement, other.get_snake_head_position())
        empty_move_now = snake_head_pos == snake_positions_list[0]

        # normal state
        if not empty_move_now:  # update the snake
            snake_positions_list.insert(0, snake_head_pos)
            if leave_prev_tail:
                leave_prev_tail -= 1
            else:  # cut the tail off
                snake_positions_list = snake_positions_list[:-1]

        # empty move state - when you can cut
        elif snake_len >= SNAKE_INIT_LENGTH:
            snake_positions_list = snake_positions_list[:-1]
            leave_prev_tail += 1
            #  cut the tail anyway
            #  just remember to restore it later (if not too big)

        if leave_prev_tail:
            self.leave_tail = leave_prev_tail

        # commit changes to the new board state
        self._snake_length = len(snake_positions_list)
        self._snake_positions_list = snake_positions_list
        self._apple_pos = other.get_apple_position()

    def init_debugging_snake(self):
        apple_pos = (3, 3)
        snake_head = (0,0)
        snake_rest = [
            (0,1),
            (1,1),
            (1,2),
            (1,3),
            (1,4),
            (1,5),
            (2,5),
            (3,5),
            (4,5),
            (5,5),
            (5,4),
            (5,3),
            (5,2),
            (5,1),
            (4,1),
            (3,1),
            (2,1),
            (2,2),
            (2,3),
            (2,4),
            (3,4)
        ]

        self._snake_positions_list = [snake_head] + snake_rest
        self._snake_length = len(self._snake_positions_list)
        self._apple_pos = apple_pos

    def init_random_snake(self):
        apple = (random_range(0, BoardState.get_cols() - 1), random_range(0, BoardState.get_rows() - 1))
        self._apple_pos = apple

        snake_head = None
        while True:
            snake_head = (
                random_range(0, BoardState.get_cols() - 1),
                random_range(0, BoardState.get_rows() - 1))
            if apple != snake_head:
                self._snake_positions_list.append(snake_head)
                break

        snake_cur_pos = snake_head
        for snake_body_depth in range(BoardState.TILE_SNAKE_BODY_DEFAULT, SNAKE_INIT_LENGTH+1):
            snake_next_pos = random_from_seq(list(self._get_closest_blank_points(snake_cur_pos)))
            self._snake_positions_list.append(snake_next_pos)
            snake_cur_pos = snake_next_pos

    def init_base_snake(self):
        width, height = BoardState.get_cols(), BoardState.get_rows()
        self._snake_positions_list = []
        apple_pos = (width - 1, height - 1)
        self._apple_pos = apple_pos

        for i in range(self._snake_length):
            pos_y = i // width
            pos_x = i % width
            if pos_y % 2:
                pos_x = width - 1 - pos_x
            new_snake_pos = (pos_x, pos_y)
            self._snake_positions_list.insert(0, new_snake_pos)

    @staticmethod
    def get_closest_points(position):
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
        return 0 <= x < BoardState.get_cols() and 0 <= y < BoardState.get_rows()

    def _is_captured_by_snake(self, position):
        return position in self._snake_positions_list
        # return self.get_tile(position) <= BoardState.TILE_NOTHING
        # return position not in self._snake_positions

    ''' DOESNT RETURN THE APPLE POSITION IF IS NEAR! '''
    def _get_closest_blank_points(self, position):
        is_in_board = BoardState._is_inside_board
        add_positions = BoardState.add_positions
        for move in BoardState.ALL_MOVES:
            new_pos = add_positions(position, move)
            if is_in_board(new_pos) and new_pos not in self._snake_positions_list and new_pos != self._apple_pos:
                yield new_pos

    @staticmethod
    def add_positions(pos_a, pos_b):
        return pos_a[0] + pos_b[0], pos_a[1] + pos_b[1]

    @staticmethod
    def get_cols():
        return TILES_COLS

    @staticmethod
    def get_rows():
        return TILES_ROWS

    def get_snake_length(self):
        return self._snake_length

    def get_snake_head_position(self):
        return self._snake_positions_list[0]

    def get_snake_tail_position(self):
        return self._snake_positions_list[-1]

    def get_apple_position(self):
        return self._apple_pos

    '''
    returns TILE_NOTHING, TILE_SNAKE_HEAD, TILE_SNAKE_BODY, or TILE_APPLE
    '''
    def get_tile(self, position):
        for index, pos in enumerate(self._snake_positions_list):
            if pos == position:
                return index+1  # index starts from 0, SNAKE_HEAD starts from 1
        if position == self._apple_pos:
            return BoardState.TILE_APPLE
        return BoardState.TILE_NOTHING

    '''
    iterator yielding objects that looks like -
    ((x,y), value)
    watch out! there is no check that apple_pos doesn't collide with one of the snake's positions!
    '''
    def iterate_snake_positions(self):
        for i, pos in enumerate(self._snake_positions_list):
                    yield (pos, i+1)  # i starts from 0, SNAKE_HEAD starts from 1

    def iterate_important_positions(self):
        # python3        yield from self.iterate_snake_positions()
        for i, pos in self.iterate_snake_positions():
            yield i, pos
        yield self._apple_pos, BoardState.TILE_APPLE


    ''' deprecated '''
    def get_full_2d_board(self):
        result = [[0 for _ in range(BoardState.get_rows())] for _ in range(BoardState.get_cols())]
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
        lost = self.is_losing_board()
        return won or lost

    def is_winning_board(self):
        return self.get_snake_head_position() == self.get_apple_position()

    def is_losing_board(self):
        lost = True
        # try to find even one valid move
        for move in self._get_all_valid_moves():
            if move != BoardState.MOVE_EMPTY:
                lost = False
                break
        return lost

    ''' used as a checking function to see if need a new solver '''
    def is_critical_change_from(self, prev_board):
        return self._apple_pos != prev_board.get_apple_position()

    def create_new_apple(self, position = None):
        if position:
            if not self._is_captured_by_snake(position):
                self._apple_pos = position
            return

        # else: a new apple has been created because a snake bytes the old one
        while True:
            apple = (random_range(0, BoardState.get_cols() - 1), random_range(0, BoardState.get_rows() - 1))
            if not self._is_captured_by_snake(apple):
                self._apple_pos = apple
                break
        self.leave_tail = True  # for the next generations

    @staticmethod
    def is_at_edge_of_board(pos):
        x, y = pos
        return x == 0 or x == (TILES_ROWS - 1) or y == 0 or y == (TILES_COLS - 1)

    def _get_all_valid_moves(self):
        moves_yelled = 0
        for move in BoardState.ALL_MOVES:
            new_snake_head = BoardState.add_positions(self.get_snake_head_position(), move)
            if BoardState._is_inside_board(new_snake_head) and not self._is_captured_by_snake(new_snake_head):
                yield move
                moves_yelled += 1
        # if not moves_yelled:
        #     yield BoardState.MOVE_EMPTY

    @staticmethod
    def get_distance_between_positions(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def __repr__(self):
        return "HeadPos: {}, ApplePos: {}".format(self._snake_positions_list[0], self._apple_pos)

    @staticmethod
    def string(move):
        return BoardState.move_to_string[move]

    move_to_string = {
        MOVE_L : "Left",
        MOVE_R : "Right",
        MOVE_U : "Up",
        MOVE_D : "Down",
        MOVE_EMPTY : "Don't move"
    }
