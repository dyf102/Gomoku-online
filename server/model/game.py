
EMPTY = 0
BLACK = 1
WHITE = -1

STATUS_EMPTY = 11
STATUS_WAITING = 12
STATUS_FIGHTING = 13
STATUS_SET = (STATUS_EMPTY, STATUS_WAITING, STATUS_FIGHTING)


class Game(object):

    def __init__(self, host_id, host_name, guest_id, guest_name):
        self.host_id = host_id
        self.host_name = host_name
        self.guest_id = guest_id
        self.guest_name = guest_name
        self.host_color = self.guest_color = 0  # undefined
        self.board = [[EMPTY for _ in xrange(15)] for _ in xrange(15)]
        self.status = STATUS_EMPTY

    def get_status(self):
        return self.status

    def set_status(self, new_status):
        assert new_status in STATUS_SET
        self.status = new_status

    def __str__(self):
        return '{} vs {}'.format(self.host_name, self.guest_name)

    def set_host_black(self):
        self.host_color = BLACK
        self.guest_color = WHITE

    def set_host_white(self):
        self.host_color = WHITE
        self.guest_color = BLACK

    def is_win(self, x, y, color):
        if x < 0 or x > 15 or y < 0 or y > 15 or color == EMPTY:
            return False
        return self.check_x(x, y, color) or \
            self.check_y(x, y, color) or \
            self.check_right_diagonal(x, y, color) or \
            self.check_left_diagonal(x, y, color)

    def check_x(self, x, y, color):
        board = self.board
        counter = 0
        i = x
        j = x
        left_move = False
        right_move = False
        # x axis
        while board[i][y] == color and board[j][y] == color:
            if i - 1 >= 0 and board[i - 1][y] == color:
                i -= 1
                counter += 1
                left_move = True
            if j + 1 < 15 and board[j + 1][y] == color:
                j += 1
                counter += 1
                right_move = True
            if counter == 4:
                return True
            if left_move is False and right_move is False:
                break
        return False

    def check_y(self, x, y, color):
        board = self.board
        # y axis
        counter = 0
        i = j = y
        up_move = down_move = False
        while board[x][i] == color and board[x][j] == color:
            if i - 1 >= 0 and board[x][i - 1] == color:
                i -= 1
                counter += 1
                up_move = True
            if j + 1 < 15 and board[x][j + 1] == color:
                j += 1
                counter += 1
                down_move = True
            if counter == 4:
                return True
            if down_move is False and up_move is False:
                break
        return False

    def check_right_diagonal(self, x, y, color):
        board = self.board
        # check diagonal
        counter = 0
        i = j = 0
        up_move = down_move = False
        while board[x + i][y - i] == color and board[x - j][y + j] == color:
            if y - i >= 0 and x + i < 15 and board[x + i][y - i] == color:
                i += 1
                counter += 1
                up_move = True
            if y + j < 15 and x - j >= 0 and board[x - j][y + j] == color:
                j += 1
                counter += 1
                down_move = True
            if counter == 4:
                return True
            if down_move is False and up_move is False:
                break
        return False

    def check_left_diagonal(self, x, y, color):
        board = self.board
        # check diagonal
        counter = 0
        i = j = 0
        up_move = down_move = False
        while board[y - i][x + i] == color and board[y + j][x - j] == color:
            if y - i >= 0 and x + i < 15 and board[y - i][x + i] == color:
                i += 1
                counter += 1
                up_move = True
            if y + j < 15 and x - j >= 0 and board[y + j][x - j] == color:
                j += 1
                counter += 1
                down_move = True
            if counter == 4:
                return True
            if down_move is False and up_move is False:
                break
        return False
