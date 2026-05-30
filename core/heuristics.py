from __future__ import annotations
from core.board import Board, BLACK, WHITE, EMPTY
from core.rules import get_legal_moves

CORNERS = [(0, 0), (0, 7), (7, 0), (7, 7)]

# Tabla de pesos posicionales: esquinas=100, X-squares=-50, bordes=10, etc.
POSITION_WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   1,   1,   1,   1,  -2,  10],
    [  5,  -2,   1,   1,   1,   1,  -2,   5],
    [  5,  -2,   1,   1,   1,   1,  -2,   5],
    [ 10,  -2,   1,   1,   1,   1,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]


def get_phase(board: Board) -> str:
    total = board.total_pieces()
    if total < 20:
        return 'opening'
    if total < 50:
        return 'midgame'
    return 'endgame'


def _mobility(board: Board, player: int) -> float:
    my_moves  = len(get_legal_moves(board, player))
    opp_moves = len(get_legal_moves(board, -player))
    denom = my_moves + opp_moves
    if denom == 0:
        return 0.0
    return 100.0 * (my_moves - opp_moves) / denom


def _corner_control(board: Board, player: int) -> float:
    my_corners  = sum(1 for r, c in CORNERS if board.get(r, c) == player)
    opp_corners = sum(1 for r, c in CORNERS if board.get(r, c) == -player)
    denom = my_corners + opp_corners
    if denom == 0:
        return 0.0
    return 100.0 * (my_corners - opp_corners) / denom


def _positional_score(board: Board, player: int) -> float:
    my_score  = 0
    opp_score = 0
    for r in range(8):
        for c in range(8):
            cell = board.get(r, c)
            if cell == player:
                my_score += POSITION_WEIGHTS[r][c]
            elif cell == -player:
                opp_score += POSITION_WEIGHTS[r][c]
    total = abs(my_score) + abs(opp_score)
    if total == 0:
        return 0.0
    return 100.0 * (my_score - opp_score) / total


def _stability(board: Board, player: int) -> float:
    """Cuenta fichas estables ancladas desde esquinas confirmadas."""
    stable_mine = 0
    stable_opp  = 0
    for r, c in CORNERS:
        owner = board.get(r, c)
        if owner == player:
            stable_mine += 1
        elif owner == -player:
            stable_opp += 1
    denom = stable_mine + stable_opp
    if denom == 0:
        return 0.0
    return 100.0 * (stable_mine - stable_opp) / denom


def _piece_count(board: Board, player: int) -> float:
    my  = board.count(player)
    opp = board.count(-player)
    denom = my + opp
    if denom == 0:
        return 0.0
    return 100.0 * (my - opp) / denom


def evaluate(board: Board, player: int) -> float:
    phase = get_phase(board)

    if phase == 'opening':
        return (_mobility(board, player)       * 0.50 +
                _corner_control(board, player) * 0.30 +
                _positional_score(board, player) * 0.20)

    if phase == 'midgame':
        return (_mobility(board, player)         * 0.30 +
                _corner_control(board, player)   * 0.40 +
                _stability(board, player)        * 0.15 +
                _positional_score(board, player) * 0.15)

    # cierre de partida
    return (_piece_count(board, player)    * 0.50 +
            _stability(board, player)      * 0.30 +
            _corner_control(board, player) * 0.20)
