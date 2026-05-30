from __future__ import annotations
import time
from core.board import Board, BLACK, WHITE, EMPTY
from core.rules import get_legal_moves, apply_move, is_game_over, get_winner


class GameEngine:
    def __init__(self):
        self.board = Board()
        self.current_player: int = BLACK
        self.game_over: bool = False
        self.winner: int | None = None
        self.move_history: list[tuple[int, int, int]] = []
        # Métricas expuestas a la interfaz gráfica
        self.last_nodes: int = 0
        self.last_time: float = 0.0
        self.last_eval: float = 0.0

    # API

    def get_legal_moves(self) -> list[tuple[int, int]]:
        return get_legal_moves(self.board, self.current_player)

    def make_move(self, row: int, col: int) -> bool:
        if self.game_over:
            return False
        if (row, col) not in self.get_legal_moves():
            return False
        self.board = apply_move(self.board, row, col, self.current_player)
        self.move_history.append((self.current_player, row, col))
        self._advance_turn()
        return True

    def make_ai_move(self, algorithm) -> tuple[int, int] | None:
        t0 = time.perf_counter()
        move, score = algorithm.search(self.board, self.current_player)
        self.last_time = time.perf_counter() - t0
        self.last_nodes = algorithm.nodes_explored
        self.last_eval = score
        if move:
            self.make_move(move[0], move[1])
        else:
            self._advance_turn()
        return move

    def get_score(self) -> tuple[int, int]:
        return self.board.count(BLACK), self.board.count(WHITE)

    def reset(self):
        self.__init__()

    # Métodos internos

    def _advance_turn(self):
        next_player = -self.current_player
        if get_legal_moves(self.board, next_player):
            self.current_player = next_player
        elif get_legal_moves(self.board, self.current_player):
            pass  # el jugador actual conserva el turno (el oponente no tiene movimientos)
        else:
            self.game_over = True
            self.winner = get_winner(self.board)