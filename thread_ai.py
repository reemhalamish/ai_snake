#!/usr/bin/python

import threading
from time import time, sleep
from utils import Solution, Heap
from boardstate import BoardState

'''
Object of this class gets a board to solve, the function that solves it, and a list in which it will put the result
If the problem isn't solved within 300 ms, it just returns without doing anything
'''

TIME_TO_SOLVE_SECS = 0.8
TIME_TO_SLEEP_SECS = 0.01

threadLock = threading.Lock()


class ThreadAStar(threading.Thread):
    def __init__(self, board_to_solve, list_to_put_results):
        super(ThreadAStar, self).__init__()
        self.daemon = True

        self.return_list = list_to_put_results
        self.board = board_to_solve
        self.start_new_search = False
        self.need_to_exit = False
        self.idle = False

    def run(self):
        while True:
            if self.need_to_exit:
                break
            if self.idle:
                sleep(TIME_TO_SLEEP_SECS)
                continue
            self.start_new_search = False
            first_step = Solution(self.board, 0, heuristic(self.board), [])
            all_options = Heap()
            all_options.push(first_step)
            all_options.push(first_step)

            while len(all_options) > 1 and not self.start_new_search:
                # something left at the pool
                # and no solution has been found yet
                cur_solution = all_options.pop()
                if cur_solution.board.is_winning_board():
                    self.return_results(cur_solution.moves_list)
                    self.idle = True
                    break

                elif cur_solution.board.is_losing_board():
                    continue
                else:
                    for n_board, move in cur_solution.board.get_successors():
                        n_moves_list = cur_solution.moves_list[:] + [move]
                        n_walked_so_far = cur_solution.distance_so_far + 1
                        n_heuristic_v = heuristic(n_board)
                        all_options.push(Solution(n_board, n_walked_so_far, n_heuristic_v, n_moves_list))
            # didn't find any solution
            self.idle = True
            continue

        print("ai daemon dies now")

    def return_results(self, results):
        threadLock.acquire()
        self.return_list[:] = results
        threadLock.release()

    def solve_new_search(self, new_board, new_list_to_put_results):
        threadLock.acquire()
        self.return_list = new_list_to_put_results
        self.board = new_board
        self.start_new_search = True
        self.idle = False
        threadLock.release()

    def exit_async(self):
        self.need_to_exit = True

''' heuristics and helper functions '''


def heuristic(board_state):
    return min(check_rectangle_head_apple(board_state), chase_your_tail(board_state))


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
    if _h_rect_is_blocked(rect, translate(head_pos), translate(apple_pos)):
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


def _h_get_path_len_for_rect(rect, start_pos, end_pos):
    # print("starting get_path_len_for_rect()")
    visited = set()
    bnd_x, bnd_y = len(rect[0])-1, len(rect)-1
    to_check = [(start_pos, 0)]
    for position, travel_time in to_check:
        # print("position: {}, travel_time: {}".format(position, travel_time))
        if position in visited:
            # print("visited position {}".format(position))
            continue
        if position == end_pos:
            # print("returning {}\n\n".format(travel_time))
            return travel_time
        x, y = position
        if not (0 <= x <= bnd_x and 0 <= y <= bnd_y) or rect[y][x] > 0:  # illegal positions to go through
            # print("bad position {}".format(position))
            continue
        visited.add(position)
        for move in BoardState.ALL_MOVES:
            new_pos = BoardState.add_positions(position, move)
            # print("new_pos: {}".format(new_pos))
            to_check.append((new_pos, travel_time+1))
    # reached here? no path was found
    # print("returning 0\n\n")
    return 0


''' try to tackle this rect from both directions - horizontally and vertically
    try from two start points at each
    if found a wall, return True, if all 4 tests came negative return False
'''
def _h_rect_is_blocked(rect, start_pos, end_pos):
    test_lines = False
    # first two tests - horizontally
    lines = []
    lines_reversed = []
    for line in rect:
        found_obstacle = False
        for i, x in enumerate(line):
            if x:  # found an obstacle
                lines.append(i)
                found_obstacle = True
                break
        if not found_obstacle:   # at the whole line
            test_lines = True   # clear area!
            break
        for i, x in enumerate(reversed(line)):
            if x:  # found an obstacle
                lines_reversed.append(i)
                break
    if not test_lines:  # passed yet
        lines_test_passed = all([abs(o1 - o2) > 1 for o1, o2 in zip(lines, lines[1:])])
        reversed_lines_test_passed = all([abs(o1 - o2) > 1 for o1, o2 in zip(lines_reversed, lines_reversed[1:])])
        if not (reversed_lines_test_passed and lines_test_passed): # there is a continuous obstacle
            return True

    # next two test - vertically
    cols = []
    cols_reversed = []
    for j in range(len(rect[0])):
        found_obstacle = False
        for i in range(len(rect)):
            val = rect[i][j]
            if val:  # found an obstacle
                cols.append(i)
                found_obstacle = True
                break
        if not found_obstacle:  # there is a free column + reached here means lines are free two
            return False
        for i in reversed(range(len(rect))):
            val = rect[i][j]
            if val:  # found an obstacle
                cols_reversed.append(i)
                break

    # reached here means we need to check the jumps between every column
    columns_test_passed = all([abs(o1 - o2) > 1 for o1, o2 in zip(cols, cols[1:])])
    reversed_columns_test_passed = all([abs(o1 - o2) > 1 for o1, o2 in zip(cols_reversed, cols_reversed[1:])])

    return not(columns_test_passed and reversed_columns_test_passed)


def chase_your_tail(board):
    head_pos, apple_pos = board.get_snake_head_position(), board.get_apple_position()
    man_dist = BoardState.get_distance_between_positions

    minimum_movement = float("inf")
    for snake_pos, value in board.iterate_snake_positions():
        value = board.get_snake_length() + 1 - value  # how much time it has left before disappearing
        value = value + 1 - man_dist(head_pos, snake_pos)  # how much actual wait if we get out now
        if value < 0:  # when the snake will be there when this part in the tail will be gone
            value = 0
            minimum_movement = min(minimum_movement,
                                   man_dist(head_pos, snake_pos) + value + man_dist(snake_pos, apple_pos))
    # print("minimum chase_your_tail(): {}".format(minimum_movement), end=" ")
    return minimum_movement
