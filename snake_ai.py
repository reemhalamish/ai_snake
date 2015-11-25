from random import choice as random_from_seq
from boardstate import BoardState
from utils import Heap, Solution


class SnakeAI:
    def __init__(self):
        self.func_to_use = SnakeAI.a_star
        self.moves_to_give = []

    def get_next_move(self):
        retval = self.moves_to_give[0]
        self.moves_to_give = self.moves_to_give[1:]
        return retval


    ''' returns a tuple - next_board, next_move '''
    # TODO call AI in different thread
    def update_moves(self, board_state):
        if board_state.is_final_board():
            self.moves_to_give = [] # TODO empty move or something
        self.moves_to_give = self.func_to_use(board_state)  # TODO change the dummy

    @staticmethod
    def dummy(board):
        return [random_from_seq([n_board for n_board, move in board.get_successors()])]


    @staticmethod
    def a_star(board):
        heuristic = lambda board : BoardState.get_distance_between_positions(board.get_snake_head_position(), board.get_apple_position())

        first_step = Solution(board, 0, heuristic(board), [])
        print("first step:", first_step)
        all_options = Heap()
        all_options.push(first_step)

        while all_options:  # something left:
            cur_solution = all_options.pop()
            if cur_solution.board.is_winning_board():
                print ("found a way to eat the apple!")
                print (cur_solution.moves_list)
                print ("used only {} vertices!".format(all_options.get_pushed_amount()))
                return cur_solution.moves_list
            if cur_solution.board.is_losing_board():
                continue
            for n_board, move in cur_solution.board.get_successors():
                n_moves_list = cur_solution.moves_list[:] + [move]
                n_walked_so_far = cur_solution.distance_so_far + 1
                n_heuristic_v = heuristic(n_board)
                all_options.push(Solution(n_board, n_walked_so_far, n_heuristic_v, n_moves_list))
        return []