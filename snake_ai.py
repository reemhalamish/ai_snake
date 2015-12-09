from boardstate import BoardState
from thread_ai import ThreadAStar

CRITICAL_MOVES_TO_OPEN_NEW_SOLVER = 5


class SnakeAI:
    def __init__(self, starting_board):
        # self.func_to_use = SnakeAI.a_star
        self.board = starting_board
        self.moves_to_give = []
        self.moves_since_last_solver_activated = 0
        self.solver_daemon = self.initiate_solver(starting_board)

    def get_next_move(self, board):
        self.moves_since_last_solver_activated += 1
        if not self.moves_to_give:
            if self.moves_since_last_solver_activated >= CRITICAL_MOVES_TO_OPEN_NEW_SOLVER:
                self.start_new_task_for_solver(board)
                self.moves_since_last_solver_activated = 0

            return BoardState.MOVE_EMPTY

        elif board.is_critical_change_from(self.board):
            self.start_new_task_for_solver(board)
            self.board = board
            return BoardState.MOVE_EMPTY

        else:
            retval, self.moves_to_give = self.moves_to_give[0], self.moves_to_give[1:]
            # dont need the lock since we dont CHANGE the list, only copy to a different pointer!
            return retval

    def initiate_solver(self, board_state):
        solver_thread = ThreadAStar(board_state, self.moves_to_give)
        solver_thread.start()  # notice that start() is a method from Thread, which calls run() that we defined :)
        return solver_thread

    def start_new_task_for_solver(self, new_board):
        self.moves_to_give = []
        self.solver_daemon.solve_new_search(new_board, self.moves_to_give)

    def quit(self):
        self.solver_daemon.exit_async()
        self.solver_daemon.join()

