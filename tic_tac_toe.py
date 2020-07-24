"""
Tic-Tac-Toe
"""

from copy import deepcopy

X = 'X'
O = 'O'
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """

    return [
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY]
    ]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    counts = {
        X: 0,
        O: 0,
        EMPTY: 0
    }

    for i in board:
        for j in i:
            counts[j] += 1

    return X if counts[X] == counts[O] else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    return {(i, j) for i, row in enumerate(board) for j, col in enumerate(row) if col is EMPTY}


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    i, j = action

    if board[i][j] is not EMPTY:
        raise Exception('Invalid move. Position is not empty.')

    new = deepcopy(board)

    new[i][j] = player(board)

    return new


def winner_by_array(board):
    """
    Returns the winner, if any, of the game based on the rows and columns of the board.
    """

    for i in board:
        if i.count(X) == len(i):
            return X
        elif i.count(O) == len(i):
            return O

    for i in zip(*deepcopy(board)):
        if i.count(X) == len(i):
            return X
        elif i.count(O) == len(i):
            return O

    return None


def winner_by_diagonal(board):
    """
    Returns the winner, if any, of the game based on both diagonals of the board.
    """

    diagonal = {
        X: 0,
        O: 0,
        EMPTY: 0
    }

    anti = deepcopy(diagonal)

    for i in range(len(board)):
        diagonal[board[i][i]] += 1
        anti[board[i][-i - 1]] += 1

    if diagonal[X] == len(board) or anti[X] == len(board):
        return X
    elif diagonal[O] == len(board) or anti[O] == len(board):
        return O

    return None


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    array = winner_by_array(board)
    diagonal = winner_by_diagonal(board)

    for i in {array, diagonal}:
        if i:
            return i

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    return winner(board) or all(sum(board, list()))


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    win = winner(board)

    return 1 if win == X else -1 if win == O else 0


def max_value(board, alpha, beta):
    if terminal(board):
        return utility(board), None

    choice = None
    value = float('-inf')

    for action in actions(board):
        minimum = min_value(result(board, action), alpha, beta)[0]

        if minimum > value:
            value = minimum
            choice = action

        alpha = max(alpha, value)

        if alpha >= beta:
            break

    return value, choice


def min_value(board, alpha, beta):
    if terminal(board):
        return utility(board), None

    choice = None
    value = float('inf')

    for action in actions(board):
        maximum = max_value(result(board, action), alpha, beta)[0]

        if maximum < value:
            value = maximum
            choice = action

        beta = min(beta, value)

        if beta <= alpha:
            break

    return value, choice


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        return None

    next_ = player(board)

    if next_ == X:
        return max_value(board, float('-inf'), float('inf'))[1]
    elif next_ == O:
        return min_value(board, float('-inf'), float('inf'))[1]
