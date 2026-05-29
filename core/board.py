from __future__ import annotations

BLACK = 1
WHITE = -1
EMPTY = 0


class Board:
    BLACK = 1
    WHITE = -1
    EMPTY = 0
    SIZE = 8

    def __init__(self):
        self.grid: list[list[int]] = [[EMPTY] * self.SIZE for _ in range(self.SIZE)]
        self._setup_initial()

    def _setup_initial(self):
        mid = self.SIZE // 2
        self.grid[mid - 1][mid - 1] = WHITE
        self.grid[mid - 1][mid]     = BLACK
        self.grid[mid][mid - 1]     = BLACK
        self.grid[mid][mid]         = WHITE

    def copy(self) -> Board:
        new = Board.__new__(Board)
        new.grid = [row[:] for row in self.grid]
        return new

    def get(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def set(self, row: int, col: int, value: int):
        self.grid[row][col] = value

    def count(self, player: int) -> int:
        return sum(cell == player for row in self.grid for cell in row)

    def total_pieces(self) -> int:
        return sum(cell != EMPTY for row in self.grid for cell in row)

    def is_valid_pos(self, row: int, col: int) -> bool:
        return 0 <= row < self.SIZE and 0 <= col < self.SIZE

    def __repr__(self) -> str:
        symbols = {EMPTY: '.', BLACK: 'B', WHITE: 'W'}
        lines = ['  ' + ' '.join(str(i) for i in range(self.SIZE))]
        for i, row in enumerate(self.grid):
            lines.append(f"{i} " + ' '.join(symbols[cell] for cell in row))
        return '\n'.join(lines)