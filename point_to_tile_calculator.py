import math

from cv2 import flann_Index

X, Y = 0, 1
EPSILON = 0.000001      # used to avoid (number/another_number=0) bu using (another_number+EPSILON)


class PointToTileCalculator():
    def __init__(self, rows, columns, pTopLeft, pTopRight, pBotLeft, pBotRight):
        self.rows = rows
        self.columns = columns
        self.pTopLeft = pTopLeft
        self.pTopRight = pTopRight
        self.pBotLeft = pBotLeft
        self.pBotRight = pBotRight

        self.row_solution_info = dict()
        self.col_solution_info = dict()

        self._get_row = self._create_row_tile_function()
        self._get_col = self._create_col_tile_function()

    def _create_row_tile_function(self):
        global X, Y
        p0, p1, p2, p3 = self.pTopLeft, self.pTopRight, self.pBotLeft, self.pBotRight
        left_y_diff = p2[Y] - p0[Y]
        right_y_diff = p3[Y] - p1[Y]
        if left_y_diff == right_y_diff:
            # create a MAKBILIT solution
            return self._row_makbilit_solution

        # else - create an intersect_point solution
        intersection_point = line_intersection((p0, p1), (p2, p3))
        f_rows = float(self.rows)
        if left_y_diff > right_y_diff:
            # create right-intersect solution
            assert intersection_point[X] >= max([p[X] for p in [p0, p1, p2, p3]])
            self.row_solution_info["right_intersection"] = intersection_point
            # add rows slopes:
            rows_slopes = []
            for i in range(self.rows + 1):  # WITH upper slope, WITH lower slope
                p0x, p0y, p2x, p2y = float(p0[X]), float(p0[Y]), float(p2[X]), float(p2[Y])
                ix, iy = float(intersection_point[X]), float(intersection_point[Y])
                row_position_x = p0x + (p2x - p0x) * (float(i) / f_rows)
                row_position_y = p0y + (p2y - p0y) * (float(i) / f_rows)
                row_slope = (row_position_y - iy) / (row_position_x - ix)
                rows_slopes.append(row_slope)

            # assert decreasing order
            for slope, next_slope in zip(rows_slopes[:], rows_slopes[1:]):
                assert next_slope < slope
            self.row_solution_info["rows_slopes"] = rows_slopes

            return self._row_right_intersect_triangle

        else:
            # create left-increasing solution
            assert intersection_point[X] <= min([p[X] for p in [p0, p1, p2, p3]])
            self.row_solution_info["left_intersection"] = intersection_point
            # add rows slopes:
            rows_slopes = []
            for i in range(self.rows + 1):  # WITH upper slope, WITH lower slope
                p0x, p0y, p2x, p2y = float(p1[X]), float(p1[Y]), float(p3[X]), float(p3[Y])
                ix, iy = float(intersection_point[X]), float(intersection_point[Y])
                row_position_x = p0x + (p2x - p0x) * (float(i) / f_rows)
                row_position_y = p0y + (p2y - p0y) * (float(i) / f_rows)
                row_slope = (row_position_y - iy) / (row_position_x - ix)
                rows_slopes.append(row_slope)

            # assert increasing order
            for slope, next_slope in zip(rows_slopes[:], rows_slopes[1:]):
                assert next_slope > slope
            self.row_solution_info["rows_slopes"] = rows_slopes

            return self._row_left_intersect_triangle

    def _create_col_tile_function(self):
        global X, Y
        p0, p1, p2, p3 = self.pTopLeft, self.pTopRight, self.pBotLeft, self.pBotRight
        top_x_diff = p1[X] - p0[X]
        bot_x_diff = p3[X] - p2[X]
        if top_x_diff == bot_x_diff:
            # create a MAKBILIT solution
            return self._col_makbilit_solution

        # else - intersecting point exists
        global EPSILON
        intersection_point = line_intersection((p0, p2), (p1, p3))
        f_cols = float(self.columns)
        if (top_x_diff > bot_x_diff):
            # create a trinagle from bottom
            assert intersection_point[Y] >= max([p[Y] for p in [p0, p1, p2, p3]])
            self.col_solution_info["bot_intersection"] = intersection_point
            # add cols slopes:
            cols_slopes = []
            for i in range(self.columns + 1):  # WITH leftmost slope, WITH rightmost slope
                p2x, p2y, p3x, p3y = float(p0[X]), float(p0[Y]), float(p1[X]), float(p1[Y])
                ix, iy = float(intersection_point[X]), float(intersection_point[Y])
                col_pos_x = p2x + (p3x - p2x) * (float(i) / f_cols)
                col_pos_y = p2y + (p3y - p2y) * (float(i) / f_cols)
                if col_pos_y == iy:
                    col_pos_y += EPSILON
                # COL SLOPE IS 1/original!!  [usually m = delta(y) / delta(x)]
                # I did it to avoid [HUGE MINUS, INF, HUGE PLUS] in the cols_slopes
                col_slope = (col_pos_x - ix) / (col_pos_y - iy)
                cols_slopes.append(col_slope)

            # assert decreasing order
            for slope, next_slope in zip(cols_slopes[:], cols_slopes[1:]):
                assert next_slope < slope
            self.col_solution_info["cols_slopes"] = cols_slopes

            return self._col_bot_intersect_triangle
        else:
            # create a triangle from top
            assert intersection_point[Y] <= min([p[Y] for p in [p0, p1, p2, p3]])
            self.col_solution_info["top_intersection"] = intersection_point
            # add cols slopes:
            cols_slopes = []
            for i in range(self.columns + 1):  # WITH leftmost slope, WITH rightmost slope
                p2x, p2y, p3x, p3y = float(p2[X]), float(p2[Y]), float(p3[X]), float(p3[Y])
                ix, iy = float(intersection_point[X]), float(intersection_point[Y])
                col_pos_x = p2x + (p3x - p2x) * (float(i) / f_cols)
                col_pos_y = p2y + (p3y - p2y) * (float(i) / f_cols)
                if col_pos_y == iy:
                    col_pos_y += EPSILON
                # COL SLOPE IS 1/original!!  [usually m = delta(y) / delta(x)]
                # I did it to avoid [HUGE MINUS, INF, HUGE PLUS] in the cols_slopes
                col_slope = (col_pos_x - ix) / (col_pos_y - iy)
                cols_slopes.append(col_slope)

            # assert increasing order
            for slope, next_slope in zip(cols_slopes[:], cols_slopes[1:]):
                assert next_slope > slope
            self.col_solution_info["cols_slopes"] = cols_slopes

            return self._col_top_intersect_triangle

    def _col_makbilit_solution(self, p):
        global X, Y
        cols = self.columns
        p0, p1, p2, p3 = self.pTopLeft, self.pTopRight, self.pBotLeft, self.pBotRight
        p0x, p0y, p1x, p1y = float(p0[X]), float(p0[Y]), float(p1[X]), float(p1[Y])
        p2x, p2y, p3x, p3y = float(p2[X]), float(p2[Y]), float(p3[X]), float(p3[Y])
        px, py = float(p[X]), float(p[Y])

        p_right = (p3x - p1x) * ((py - p1y) / (p3y - p1y)) + p1x
        p_left = (p2x - p0x) * ((py - p0y) / (p2y - p0y)) + p0x
        # pay attention as p_right > p_left
        yahas = (px - p_left) / (p_right - p_left)
        cur_col = math.floor(yahas * cols)

        # stay in the world of snake (or at least, just right outside)
        cur_col = max(cur_col, -1)
        cur_col = min(cur_col, cols)

        return int(cur_col)

    def _row_makbilit_solution(self, p):
        global X, Y
        rows = self.rows
        p0, p1, p2, p3 = self.pTopLeft, self.pTopRight, self.pBotLeft, self.pBotRight
        p0x, p0y, p1x, p1y = float(p0[X]), float(p0[Y]), float(p1[X]), float(p1[Y])
        p2x, p2y, p3x, p3y = float(p2[X]), float(p2[Y]), float(p3[X]), float(p3[Y])
        px, py = float(p[X]), float(p[Y])

        p_high = (p1y - p0y) * ((px - p0x)/(p1x - p0x)) + p0y
        p_low = ((p3y - p2y) * ((px - p2x)/(p3x - p2x))) + p2y
        # PAY ATTENTION! p_low > p_high as y goes from0 at top to inf while moving down!!
        yahas = (py - p_high) / (p_low - p_high)
        cur_row = math.floor(yahas * rows)

        # stay in the world of snake (or at least, just right outside)
        cur_row = max(cur_row, -1)
        cur_row = min(cur_row, rows)

        return int(cur_row)

    def _col_top_intersect_triangle(self, p):
        intersection, cols_slopes = self.col_solution_info["top_intersection"], self.col_solution_info["cols_slopes"]
        i_x, i_y = intersection
        p_x, p_y = p
        if p_y == i_y:
            global EPSILON
            p_y += EPSILON

        cur_slope = (p_x - i_x) / (p_y - i_y)
        for tile_index, (slope, next_slop) in enumerate(zip(cols_slopes, cols_slopes[1:])):
            # slopes are really increasing
            if next_slop >= cur_slope >= slope:
                return tile_index

        # reached here? you are more than the max or less than the min. let's check
        first_slope = cols_slopes[0]
        if slope <= first_slope:
            return -1
        return self.columns  # else

    def _col_bot_intersect_triangle(self, p):
        intersection, cols_slopes = self.col_solution_info["bot_intersection"], self.col_solution_info["cols_slopes"]
        i_x, i_y = intersection
        p_x, p_y = p
        if p_y == i_y:
            global EPSILON
            p_y += EPSILON

        cur_slope = (p_x - i_x) / (p_y - i_y)
        for tile_index, (slope, next_slop) in enumerate(zip(cols_slopes, cols_slopes[1:])):
            # slopese are really decreasing
            if slope >= cur_slope >= next_slop:
                return tile_index

        # reached here? you are more than the max or less than the min. let's check
        first_slope = cols_slopes[0]
        if slope >= first_slope:
            return -1
        return self.columns  # else

    def _row_left_intersect_triangle(self, p):
        intersection, rows_slopes = self.row_solution_info["left_intersection"], self.row_solution_info["rows_slopes"]
        i_x, i_y = intersection
        p_x, p_y = p

        cur_slope = (p_y - i_y) / (p_x - i_x)
        for tile_index, (slope, next_slope) in enumerate(zip(rows_slopes, rows_slopes[1:])):
            # slopes in are a really increasing order
            if slope <= cur_slope <= next_slope:
                return tile_index

        # reached here? you are not part of the snake world. let's check:
        if cur_slope < rows_slopes[0]:
            return -1
        return self.rows

    def _row_right_intersect_triangle(self, p):
        intersection, rows_slopes = self.row_solution_info["right_intersection"], self.row_solution_info["rows_slopes"]
        i_x, i_y = intersection
        p_x, p_y = p

        cur_slope = (p_y - i_y) / (p_x - i_x)
        for tile_index, (slope, next_slope) in enumerate(zip(rows_slopes, rows_slopes[1:])):
            # slopes in are a really decreasing order
            if next_slope <= cur_slope <= slope:
                return tile_index

        # reached here? you are not part of the snake world. let's check:
        if cur_slope > rows_slopes[0]:
            return -1
        return self.rows

    def get_tile(self, point):
        return self._get_col(point), self._get_row(point)


# helper function from http://stackoverflow.com/questions/20677795/find-the-point-of-intersecting-lines
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return float(a[0]) * float(b[1]) - float(a[1]) * float(b[0])

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    print("intersection point for {} and {} is {}".format(
        line1, line2, (x,y)
    ))
    return x, y

# TESTS
# a = PointToTileCalculator(4, 3, (0,0), (4,0), (0,4), (4,4))
# print(a.get_tile((0.8, 0.8)))
# print(a.get_tile((-1, -1)))
# b = PointToTileCalculator(4, 3, (1,0), (3,0), (1,3), (3,5))
# print(b.get_tile((4, 30)))
# b = PointToTileCalculator(4, 3, (1.0000001,0), (3,0), (1,8), (3,4))
# print(b.get_tile((2, 4.0)))
# print(b.get_tile((2.999, 4.0)))
# print(b.get_tile((2.999, 0)))
# print(b.get_tile((2.999, 2.2)))
# print(b.get_tile((4.4, 2)))
# print(b.get_tile((4.4, -0.001)))
# p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y = float(p0[X]), float(p0[Y]), float(p1[X]), float(p1[Y]), float(p2[X]), float(p2[Y]), float(p3[X]), float(p3[Y])

