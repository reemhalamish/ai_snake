from heapq import heappush, heappop
import boardstate


class Heap:
    def __init__(self):
        self.heap = []
        self.pushed = 0

    def push(self, solution):
        heappush(self.heap, (solution.overall_value, solution))
        self.pushed += 1

    def pop(self):
        value, solution = heappop(self.heap)
        return solution

    def __bool__(self):
        return len(self.heap) > 0

    def __len__(self):
        return len(self.heap)

    def get_pushed_amount(self):
        return self.pushed


class Solution:
    def __init__(self, board, distance_so_far, heuristic_value, moves_list):
        self.board = board
        self.distance_so_far = distance_so_far
        self.heuristic_value = heuristic_value
        self.overall_value = distance_so_far + heuristic_value
        self.moves_list = moves_list

    def __repr__(self):
        return "Solution: board:{}, distance:{}, heu_val:{}, overall:{}, moves_list:{}".format(
            str(self.board),
            str(self.distance_so_far),
            str(self.heuristic_value),
            str(self.overall_value),
            "".join([boardstate.BoardState.string(move) + "," for move in self.moves_list])
        )

    def __gt__(self, other):
        # if type(other) != type(self):
        #     raise RuntimeError("can't compare solution with another thing! "+str(type(other)))
        return self.overall_value > other.overall_value