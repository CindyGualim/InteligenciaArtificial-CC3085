from __future__ import annotations
import random
import time
from core.board import Board, BLACK, WHITE
from core.algorithms import AlphaBeta, Expectimax, MCTS
from core.rules import get_legal_moves


class OthelloAgent:
    TIME_LIMIT = 2.0  # segundos máximos por jugada

    DIFFICULTY: dict = {
        'easy':       {'algorithm': 'alpha_beta',  'max_depth': 2},
        'medium':     {'algorithm': 'alpha_beta',  'max_depth': 4},
        'hard':       {'algorithm': 'alpha_beta',  'max_depth': 6},
        'mcts':       {'algorithm': 'mcts',        'iterations': 600},
        'expectimax': {'algorithm': 'expectimax',  'max_depth': 4},
    }

    def __init__(self, player: int, difficulty: str = 'medium'):
        self.player     = player
        self.difficulty = difficulty
        cfg = self.DIFFICULTY[difficulty]

        if cfg['algorithm'] == 'alpha_beta':
            self.algorithm = AlphaBeta(max_depth=cfg['max_depth'])
        elif cfg['algorithm'] == 'mcts':
            self.algorithm = MCTS(iterations=cfg['iterations'])
        elif cfg['algorithm'] == 'expectimax':
            self.algorithm = Expectimax(max_depth=cfg['max_depth'])
        else:
            raise ValueError(f"Algoritmo desconocido: {cfg['algorithm']}")

    def choose_move(self, board: Board) -> tuple[tuple | None, float]:
        """Elige el mejor movimiento dentro del límite de tiempo configurado."""
        move, score = self.algorithm.search(board, self.player,
                                            time_limit=self.TIME_LIMIT)

        # Alternativa de seguridad: si la búsqueda no encontró movimiento, elegir uno legal al azar
        if move is None:
            moves = get_legal_moves(board, self.player)
            if moves:
                move = random.choice(moves)

        return move, score

    @property
    def nodes_explored(self) -> int:
        return self.algorithm.nodes_explored
