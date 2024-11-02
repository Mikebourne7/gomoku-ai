"""Freestyle Gomoku rules and a depth-limited alpha-beta opponent."""

SIZE = 15
HUMAN, COMPUTER = 1, -1
DIRECTIONS = ((1, 0), (0, 1), (1, 1), (1, -1))
WIN_SCORE = 100_000_000

# Each entry gives the values for zero, one, and two open ends.
LINE_WEIGHTS = {
    1: (0, 1, 3),
    2: (0, 8, 30),
    3: (0, 55, 300),
    4: (0, 700, 4_000),
}


def inside(row, col):
    return 0 <= row < SIZE and 0 <= col < SIZE


class Game:
    def __init__(self):
        self.board = [[0] * SIZE for _ in range(SIZE)]
        self.history = []
        self.turn = HUMAN
        self.winner = 0

    @property
    def finished(self):
        return self.winner != 0 or len(self.history) == SIZE * SIZE

    def play(self, row, col):
        if self.finished or not inside(row, col) or self.board[row][col]:
            return False
        player = self.turn
        self.board[row][col] = player
        self.history.append((row, col, player))
        if winning_move(self.board, row, col, player):
            self.winner = player
        self.turn = -player
        return True

    def undo_turn(self):
        while self.history:
            row, col, player = self.history.pop()
            self.board[row][col] = 0
            if player == HUMAN:
                break
        self.turn = HUMAN
        self.winner = 0


def _ray(board, row, col, dr, dc, player):
    row += dr
    col += dc
    length = 0
    while inside(row, col) and board[row][col] == player:
        length += 1
        row += dr
        col += dc
    return length, int(inside(row, col) and board[row][col] == 0)


def _lines(board, row, col, player):
    for dr, dc in DIRECTIONS:
        before, open_before = _ray(board, row, col, -dr, -dc, player)
        after, open_after = _ray(board, row, col, dr, dc, player)
        yield 1 + before + after, open_before + open_after


def winning_move(board, row, col, player):
    return any(length >= 5 for length, _ in _lines(board, row, col, player))


def _candidates(board, player):
    occupied = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c]]
    if not occupied:
        return [(SIZE // 2, SIZE // 2)]

    nearby = set()
    for row, col in occupied:
        for r in range(max(0, row - 1), min(SIZE, row + 2)):
            for c in range(max(0, col - 1), min(SIZE, col + 2)):
                if board[r][c] == 0:
                    nearby.add((r, c))

    def priority(move):
        row, col = move
        attack = _move_score(board, row, col, player)
        defense = _move_score(board, row, col, -player)
        center_distance = abs(row - SIZE // 2) + abs(col - SIZE // 2)
        return (-attack - defense, center_distance, row, col)

    moves = sorted(nearby, key=priority)
    wins = [move for move in moves if winning_move(board, *move, player)]
    blocks = [move for move in moves if winning_move(board, *move, -player)]
    return wins[:1] or blocks or moves[:8]


def _move_score(board, row, col, player):
    score = 0
    for length, open_ends in _lines(board, row, col, player):
        if length >= 5:
            return WIN_SCORE
        score += LINE_WEIGHTS[length][open_ends]
    return score


def _position_score(board, player):
    score = 0
    for row, cells in enumerate(board):
        for col, stone in enumerate(cells):
            if not stone:
                continue
            for dr, dc in DIRECTIONS:
                previous_row, previous_col = row - dr, col - dc
                has_previous = inside(previous_row, previous_col)
                if has_previous and board[previous_row][previous_col] == stone:
                    continue
                before = int(has_previous and board[previous_row][previous_col] == 0)
                after_length, after = _ray(board, row, col, dr, dc, stone)
                length = min(4, after_length + 1)
                score += (player * stone) * LINE_WEIGHTS[length][before + after]
    return score


def _search(board, player, depth, alpha, beta, remaining):
    if remaining == 0:
        return 0, None
    if depth == 0:
        return _position_score(board, player), None

    best_score = -WIN_SCORE * 2
    best_move = None
    for row, col in _candidates(board, player):
        board[row][col] = player
        try:
            if winning_move(board, row, col, player):
                score = WIN_SCORE + depth
            else:
                reply, _ = _search(board, -player, depth - 1, -beta, -alpha, remaining - 1)
                score = -reply
        finally:
            board[row][col] = 0
        if score > best_score:
            best_score, best_move = score, (row, col)
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return best_score, best_move


def computer_move(game, depth):
    """Return an AI move without changing the game state."""
    if game.finished or game.turn != COMPUTER:
        return None
    limit = WIN_SCORE * 2
    _, move = _search(game.board, COMPUTER, depth, -limit, limit, SIZE * SIZE - len(game.history))
    return move
