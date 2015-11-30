from random import choice as random_from_seq
from time import time
from boardstate import BoardState
from utils import Heap, Solution
from thread_ai import ThreadAStar, threadLock

CRITICAL_AMOUNT_OF_MOVES_TO_OPEN_NEW_SOLVER = 5


class SnakeAI:
    def __init__(self, starting_board):
        # self.func_to_use = SnakeAI.a_star
        self.board = starting_board
        self.moves_to_give = []
        self.moves_since_last_solver_activated = 0
        self.solvers_initiated = 0
        self.solver_daemon = self.initiate_solver(starting_board)

    def get_next_move(self, board):
        self.moves_since_last_solver_activated += 1
        if not self.moves_to_give:
            if board.is_critical_change_from(self.board):
                self.start_new_task_for_solver(board)
                self.board = board
            elif self.moves_since_last_solver_activated >= CRITICAL_AMOUNT_OF_MOVES_TO_OPEN_NEW_SOLVER:
                print("too many moves passed, starting a new search")
                self.start_new_task_for_solver(board)
                self.moves_since_last_solver_activated = 0

            return BoardState.MOVE_EMPTY

        else:
            threadLock.acquire()
            retval, self.moves_to_give = self.moves_to_give[0], self.moves_to_give[1:]
            threadLock.release()
            return retval

    def initiate_solver(self, board_state):
        solver_thread = ThreadAStar(board_state, self.moves_to_give, self.solvers_initiated)
        solver_thread.start()  # notice that start() is a method from Thread, which calls run() that we defined :)
        print("solver_thread", solver_thread)
        return solver_thread

    def start_new_task_for_solver(self, new_board):
        self.moves_to_give = []
        self.solver_daemon.solve_new_search(new_board, self.moves_to_give)

    '''

    @staticmethod
    def a_star(board):
        heuristic = lambda board_state : min(SnakeAI.check_rectangle_head_apple(board_state), SnakeAI.chase_your_tail(board_state))

        first_step = Solution(board, 0, heuristic(board), [])
        print("first step:", first_step)
        all_options = Heap()
        all_options.push(first_step)

        while all_options:  # something left:
            end = time()
            cur_solution = all_options.pop()
            if cur_solution.board.is_winning_board():
                print ("found a way to eat the apple used only {} vertices!".format(all_options.get_pushed_amount()))
                return cur_solution.moves_list
            if cur_solution.board.is_losing_board():
                continue
            for n_board, move in cur_solution.board.get_successors():
                n_moves_list = cur_solution.moves_list[:] + [move]
                n_walked_so_far = cur_solution.distance_so_far + 1
                n_heuristic_v = heuristic(n_board)
                all_options.push(Solution(n_board, n_walked_so_far, n_heuristic_v, n_moves_list))
        return []

    @staticmethod
    def check_rectangle_head_apple(board):
        head_pos, apple_pos = board.get_snake_head_position(), board.get_apple_position()
        # print("from head: {} to apple: {}".format(
        #     head_pos,
        #     apple_pos
        # ), end=" ")
        man_dist = BoardState.get_distance_between_positions

        # idea - create a punish if the snake-tail blocks the way
        #
        # at the rect (head, apple), if there is a snake_pos at every line and every column, then
        #       return min(man_dist(head, pos) + time_to_wait(pos) + man_dist(pos, apple) for pos in snake_body w/o head
        # else:
        #       return man_dist(head, apple)

        dims = (head_pos[0] - apple_pos[0], head_pos[1] - apple_pos[1])
        rect_start_point = (min(head_pos[0], apple_pos[0]), min(head_pos[1], apple_pos[1]))
        rect_end_point = (max(head_pos[0], apple_pos[0]), max(head_pos[1], apple_pos[1]))
        translate = lambda pos : (pos[0] - rect_start_point[0], pos[1] - rect_start_point[1])
        in_bounderies = lambda pos : \
            rect_start_point[0] <= pos[0] <= rect_end_point[0] and \
            rect_start_point[1] <= pos[1] <= rect_end_point[1]

        time_to_wait_for_snake_pos_to_clear = dict()
        rect = [[0 for _ in range(abs(dims[1])+1)] for _ in range(abs(dims[0])+1)]
        for snake_pos, value in board.iterate_snake_positions():
            value = board.get_snake_length() + 1 - value  # how much time it has left
            value = value + 1 - man_dist(head_pos, snake_pos)  # how much actual wait
            if value < 0:  # when the snake will be there when this part in the tail will be gone
                value = 0
            if (not value) or (not in_bounderies(snake_pos)):  # doesnt need to wait or not part of the rect anyway
                continue
            time_to_wait_for_snake_pos_to_clear[snake_pos] = value
            translated_pos = translate(snake_pos)
            # print("start point: {} end point {} lines {} columns {} position {} translated {} in_boundaries {}".format(
            #     rect_start_point,
            #     rect_end_point,
            #     len(rect),
            #     len(rect[0]),
            #     snake_pos,
            #     translated_pos,
            #     in_bounderies(snake_pos)
            # ))
            x, y = translated_pos
            rect[x][y] = value
        translated_head = translate(head_pos)
        x, y = translated_head
        rect[x][y] = 0
        # translated_apple = translate(apple_pos)
        # x, y = translated_apple
        # rect[x][y] = -1
        # DEBUG
        # print("rect:")
        # for line in rect:
        #     print(line)

        # providing we have the rect, try to see if it's blocked. If yes, return min(...), else return man_dist
        if SnakeAI.rect_is_blocked(rect, translate(head_pos), translate(apple_pos)):
            all_snake_positions_plus_times = [
                    time_to_wait + man_dist(head_pos, pos) + man_dist(pos, apple_pos)
                    for pos, time_to_wait in time_to_wait_for_snake_pos_to_clear.items()
            ]
            retval = min(all_snake_positions_plus_times)
            # print("blocked, returning min: " + str(retval))
            return retval
        else:
            retval = man_dist(head_pos, apple_pos)
            # print("free! returning man_dist: " + str(retval))
            return retval
    '''

