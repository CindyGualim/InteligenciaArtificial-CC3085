from __future__ import annotations
from core.board import Board, BLACK, WHITE, EMPTY

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0,  -1),           (0,  1),
              (1,  -1), (1,  0), (1,  1)]


def get_flips(board: Board, row: int, col: int, player: int) -> list[tuple[int, int]]:
    if board.get(row, col) != EMPTY:
        return []
    opponent = -player
    all_flips: list[tuple[int, int]] = []
    for dr, dc in DIRECTIONS:
        line: list[tuple[int, int]] = []
        r, c = row + dr, col + dc
        while board.is_valid_pos(r, c) and board.get(r, c) == opponent:
            line.append((r, c))
            r += dr
            c += dc
        if line and board.is_valid_pos(r, c) and board.get(r, c) == player:
            all_flips.extend(line)
    return all_flips


def is_valid_move(board: Board, row: int, col: int, player: int) -> bool:
    return board.get(row, col) == EMPTY and bool(get_flips(board, row, col, player))


def get_legal_moves(board: Board, player: int) -> list[tuple[int, int]]:
    moves = []
    for r in range(Board.SIZE):
        for c in range(Board.SIZE):
            if is_valid_move(board, r, c, player):
                moves.append((r, c))
    return moves


def apply_move(board: Board, row: int, col: int, player: int) -> Board:
    new_board = board.copy()
    new_board.set(row, col, player)
    for r, c in get_flips(board, row, col, player):
        new_board.set(r, c, player)
    return new_board


def is_game_over(board: Board) -> bool:
    return not get_legal_moves(board, BLACK) and not get_legal_moves(board, WHITE)


def get_winner(board: Board) -> int | None:
    b = board.count(BLACK)
    w = board.count(WHITE)
    if b > w:
        return BLACK
    if w > b:
        return WHITE
    return None