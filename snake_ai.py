from random import choice as random_from_seq
from time import time
from boardstate import BoardState
from utils import Heap, Solution



class SnakeAI:
    def __init__(self):
        self.func_to_use = SnakeAI.a_star
        self.moves_to_give = []

    def get_next_move(self, board):
        retval = self.moves_to_give[0]
        if retval == BoardState.MOVE_EMPTY:
            if board.get_snake_length() > 5:
                self.update_moves(board)
        else:
            self.moves_to_give = self.moves_to_give[1:]
        return retval

    ''' returns a tuple - next_board, next_move '''
    # TODO call AI in different thread
    def update_moves(self, board_state):
        start = time()
        next_moves = self.func_to_use(board_state)
        self.moves_to_give = next_moves if next_moves else [BoardState.MOVE_EMPTY]
        end = time()
        print ("calculations took {} ms".format(1000 * (end-start)))
        print("way to go: {}".format("".join([BoardState.string(move) + " --> " for move in self.moves_to_give])))
        #exit()

    @staticmethod
    def dummy(board):
        return [random_from_seq([n_board for n_board, move in board.get_successors()])]


    @staticmethod
    def a_star(board):
        heuristic = SnakeAI.heuristic_for_astar

        first_step = Solution(board, 0, heuristic(board), [])
        print("first step:", first_step)
        all_options = Heap()
        all_options.push(first_step)

        while all_options:  # something left:
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
    def heuristic_for_astar(board):
        head_pos, apple_pos = board.get_snake_head_position(), board.get_apple_position()
        print("from head: {} to apple: {}".format(
            head_pos,
            apple_pos
        ))
        man_dist = BoardState.get_distance_between_positions
        # man_dis = BoardState.get_distance_between_positions(head_pos, apple_pos)

        # idea - create a punish if the snake-tail blocks the way
        #
        # at the rect (head, apple), if there is a snake_pos at every line and every column, then
        #       return min(man_dist(head, pos) + time_to_wait(pos) + man_dist(pos, apple) for pos in snake_body w/o head
        # else:
        #       return man_dist(head, apple)



        # create a punish if the snake-tail blocks the way
        #
        # check the rectangle defined by (snake_head, apple)
        # if this rect is closed all the way, then add the min time you need to wait for it to be opened again
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
            value = value + 1 - BoardState.get_distance_between_positions(head_pos, snake_pos)  # how much actual wait
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
            #print("blocked, returning min: " + str(retval))
            return retval
        else:
            retval = man_dist(head_pos, apple_pos)
            #print("free! returning man_dist: " + str(retval))
            return retval

        # rect is ready. now check with BFS if there is a path between the head and the apple.
        # if there is a path
        #  then return len(path)
        # if no such path is found (SIMULATED BY path_len == 0)
        #  then return min(man_dist(head, pos) + time_to_wait(pos) + man_dist(pos, apple) for pos in snake_body w/o head

        path_len = SnakeAI.get_path_len_for_rect(rect, translate(head_pos), translate(apple_pos))
        if path_len:
            return path_len

        # no path len
        all_snake_positions_plus_times = [
                    man_dist(head_pos, pos) + time_to_wait + man_dist(pos, apple_pos)
                    for pos, time_to_wait in time_to_wait_for_snake_pos_to_clear.items()
            ]
        # print(all_snake_positions_plus_times)
        retval = min(all_snake_positions_plus_times)

        return retval

        '''
        for line in rect: print(line)
        exit(0)
        _ = input()



        return man_dis

        extra_discount = 1/ (board.get_snake_length() + 1)
        total_discount_bonus = 0
        for pos, _ in board.iterate_snake_positions():
            x, y = pos
            dx, dy = abs(x - apple_pos[0]), abs(y - apple_pos[1])
            if \
                not dy \
                or not dx \
                or board.is_at_edge_of_board(pos):
                total_discount_bonus += extra_discount
        # discount if strait line (horizontal \ vertical), or if snake is moving from the edges
        return man_dis # - total_discount_bonus

        '''

    @staticmethod
    def a_star_ver_2(board):
        # first try to A* with a frozen board. i,e, let the head move seperatly from the body until it gets the apple
        #               and store all the positions you traveled in inside visited=set() so that you wont travel twice
        # if successeded - then there is a path, run the ver_1_a_star function
        # if failed, than the head and the apple are in two connectivity components with the tail seperating them
        pass

    @staticmethod
    def get_path_len_for_rect(rect, start_pos, end_pos):
        #print("starting get_path_len_for_rect()")
        visited = set()
        bnd_x, bnd_y = len(rect[0])-1, len(rect)-1
        to_check = [(start_pos, 0)]
        for position, travel_time in to_check:
            #print("position: {}, travel_time: {}".format(position, travel_time))
            if position in visited:
                #print("visited position {}".format(position))
                continue
            if position == end_pos:
                #print("returning {}\n\n".format(travel_time))
                return travel_time
            x, y = position
            if not (0 <= x <= bnd_x and 0 <= y <= bnd_y) or rect[y][x] > 0:  # illegal positions to go through
                #print("bad position {}".format(position))
                continue
            visited.add(position)
            for move in BoardState.ALL_MOVES:
                new_pos = BoardState.add_positions(position, move)
                #print("new_pos: {}".format(new_pos))
                to_check.append((new_pos, travel_time+1))
        # reached here? no path was found
        #print("returning 0\n\n")
        return 0

    ''' try to tackle this rect from both directions - horizontally and vertically
        try from two start points at each
        if found a wall, return True, if all 4 tests came negative return False
    '''
    @staticmethod
    def rect_is_blocked(rect, start_pos, end_pos):
        test_lines = False
        # first two tests - horizontally
        lines = []
        lines_reversed = []
        for line in rect:
            found_obstacle = False
            for i, x in enumerate(line):
                if x: # found an obstacle
                    lines.append(i)
                    found_obstacle = True
                    break
            if not found_obstacle: # at the whole line
                test_lines = True # clear area!
                break
            for i, x in enumerate(reversed(line)):
                if x: # found an obstacle
                    lines_reversed.append(i)
                    break
        if not test_lines: # passed yet
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
            if not found_obstacle: # there is a free column + reached here means lines are free two
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

