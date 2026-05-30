from __future__ import annotations
import math
import random
import time
from core.board import Board, BLACK, WHITE
from core.rules import get_legal_moves, apply_move, is_game_over, get_winner
from core.heuristics import evaluate

INF = float('inf')

# Señal interna — se lanza cuando expira el tiempo de búsqueda
class _Timeout(Exception):
    pass

# Minimax puro (sin poda) — solo para comparación en benchmark

class Minimax:
    def __init__(self, max_depth: int = 4):
        self.max_depth      = max_depth
        self.nodes_explored = 0
        self._deadline      = INF  # límite de tiempo en perf_counter

    def search(self, board: Board, player: int,
               time_limit: float = INF) -> tuple[tuple | None, float]:
        self.nodes_explored = 0
        self._deadline = time.perf_counter() + time_limit
        moves = get_legal_moves(board, player)
        if not moves:
            return None, evaluate(board, player)
        best_move, best_score = None, -INF
        try:
            for move in moves:
                nb = apply_move(board, move[0], move[1], player)
                score = self._minimax(nb, self.max_depth - 1, False, player)
                if score > best_score:
                    best_score, best_move = score, move
        except _Timeout:
            pass
        return best_move, best_score

    def _minimax(self, board: Board, depth: int, is_max: bool, root_player: int) -> float:
        self.nodes_explored += 1
        if self.nodes_explored % 1000 == 0 and time.perf_counter() > self._deadline:
            raise _Timeout()

        current = root_player if is_max else -root_player
        moves   = get_legal_moves(board, current)

        if not moves:
            if is_game_over(board):
                w = get_winner(board)
                return 10000 if w == root_player else (-10000 if w else 0)
            # Regla de paso: el jugador actual no tiene movimientos — se recursa sin decrementar profundidad
            return self._minimax(board, depth, not is_max, root_player)

        if depth == 0:
            return evaluate(board, root_player)

        if is_max:
            value = -INF
            for move in moves:
                nb = apply_move(board, move[0], move[1], current)
                value = max(value, self._minimax(nb, depth - 1, False, root_player))
            return value
        else:
            value = INF
            for move in moves:
                nb = apply_move(board, move[0], move[1], current)
                value = min(value, self._minimax(nb, depth - 1, True, root_player))
            return value

# Alpha-Beta con Profundizacion Iterativa y control de tiempo

class AlphaBeta:
    def __init__(self, max_depth: int = 6):
        self.max_depth      = max_depth
        self.nodes_explored = 0
        self._deadline      = INF

    def search(self, board: Board, player: int,
               time_limit: float = INF) -> tuple[tuple | None, float]:
        """profundizacion iterativa: profundiza hasta que expira time_limit o alcanza max_depth."""
        self._deadline      = time.perf_counter() + time_limit
        self.nodes_explored = 0

        moves = get_legal_moves(board, player)
        if not moves:
            return None, evaluate(board, player)

        best_move, best_score = moves[0], -INF

        for depth in range(1, self.max_depth + 1):
            if time.perf_counter() > self._deadline:
                break
            try:
                move, score = self._root_search(board, player, depth)
                best_move, best_score = move, score
            except _Timeout:
                break  # conservar el resultado del último nivel completo

        return best_move, best_score

    def search_fixed(self, board: Board, player: int,
                     depth: int | None = None,
                     time_limit: float = INF) -> tuple[tuple | None, float]:
        """Alpha-Beta a profundidad fija (sin profundizacion iterativa). Usado por el benchmark."""
        d = depth if depth is not None else self.max_depth
        self.nodes_explored = 0
        self._deadline      = time.perf_counter() + time_limit
        moves = get_legal_moves(board, player)
        if not moves:
            return None, evaluate(board, player)
        try:
            return self._root_search(board, player, d)
        except _Timeout:
            return moves[0], -INF

    def _root_search(self, board: Board, player: int, depth: int
                     ) -> tuple[tuple, float]:
        best_move, best_score = None, -INF
        alpha = -INF
        for move in get_legal_moves(board, player):
            nb    = apply_move(board, move[0], move[1], player)
            score = self._alpha_beta(nb, depth - 1, alpha, INF, False, player)
            if score > best_score:
                best_score, best_move = score, move
            alpha = max(alpha, best_score)
        if best_move is None:
            best_move = get_legal_moves(board, player)[0]
        return best_move, best_score

    def _alpha_beta(self, board: Board, depth: int, alpha: float, beta: float,
                    is_max: bool, root_player: int) -> float:
        self.nodes_explored += 1
        if self.nodes_explored % 500 == 0 and time.perf_counter() > self._deadline:
            raise _Timeout()

        current = root_player if is_max else -root_player
        moves   = get_legal_moves(board, current)

        if not moves:
            if is_game_over(board):
                w = get_winner(board)
                return 10000 if w == root_player else (-10000 if w else 0)
            # Regla de paso: se recursa sin decrementar profundidad
            return self._alpha_beta(board, depth, alpha, beta, not is_max, root_player)

        if depth == 0:
            return evaluate(board, root_player)

        if is_max:
            value = -INF
            for move in moves:
                nb    = apply_move(board, move[0], move[1], current)
                value = max(value, self._alpha_beta(nb, depth-1, alpha, beta, False, root_player))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = INF
            for move in moves:
                nb    = apply_move(board, move[0], move[1], current)
                value = min(value, self._alpha_beta(nb, depth-1, alpha, beta, True, root_player))
                beta  = min(beta, value)
                if alpha >= beta:
                    break
            return value

# Expectimax con control de tiempo

class Expectimax:
    def __init__(self, max_depth: int = 4):
        self.max_depth      = max_depth
        self.nodes_explored = 0
        self._deadline      = INF

    def search(self, board: Board, player: int,
               time_limit: float = INF) -> tuple[tuple | None, float]:
        """profundizacion iterativa con nodos de azar para el oponente."""
        self._deadline      = time.perf_counter() + time_limit
        self.nodes_explored = 0
        moves = get_legal_moves(board, player)
        if not moves:
            return None, evaluate(board, player)
        best_move, best_score = moves[0], -INF
        for depth in range(1, self.max_depth + 1):
            if time.perf_counter() > self._deadline:
                break
            try:
                move, score = self._root_search(board, player, depth)
                best_move, best_score = move, score
            except _Timeout:
                break
        return best_move, best_score

    def _root_search(self, board: Board, player: int, depth: int
                     ) -> tuple[tuple, float]:
        best_move, best_score = None, -INF
        for move in get_legal_moves(board, player):
            nb    = apply_move(board, move[0], move[1], player)
            score = self._expectimax(nb, depth - 1, False, player)
            if score > best_score:
                best_score, best_move = score, move
        if best_move is None:
            best_move = get_legal_moves(board, player)[0]
        return best_move, best_score

    def _expectimax(self, board: Board, depth: int, is_max: bool, root_player: int) -> float:
        self.nodes_explored += 1
        if self.nodes_explored % 500 == 0 and time.perf_counter() > self._deadline:
            raise _Timeout()

        current = root_player if is_max else -root_player
        moves   = get_legal_moves(board, current)

        if not moves:
            if is_game_over(board):
                w = get_winner(board)
                return 10000 if w == root_player else (-10000 if w else 0)
            # Regla de paso: se recursa sin decrementar profundidad
            return self._expectimax(board, depth, not is_max, root_player)

        if depth == 0:
            return evaluate(board, root_player)

        if is_max:
            value = -INF
            for move in moves:
                nb    = apply_move(board, move[0], move[1], current)
                value = max(value, self._expectimax(nb, depth-1, False, root_player))
            return value
        else:
            # Nodo de azar: promedio equiprobable de todos los hijos
            total = 0.0
            for move in moves:
                nb     = apply_move(board, move[0], move[1], current)
                total += self._expectimax(nb, depth-1, True, root_player)
            return total / len(moves)

# MCTS — Monte Carlo Tree Search con UCT y control interno de tiempo

class _MCTSNode:
    __slots__ = ['board', 'player', 'parent', 'move', 'children',
                 'wins', 'visits', 'untried_moves']

    def __init__(self, board: Board, player: int,
                 parent: '_MCTSNode | None' = None, move: tuple | None = None):
        self.board  = board
        self.parent = parent
        self.move   = move
        self.children:     list[_MCTSNode] = []
        self.wins          = 0.0
        self.visits        = 0
        # Regla de paso: si el jugador actual no tiene movimientos, cambiar al oponente
        moves = get_legal_moves(board, player)
        if not moves and not is_game_over(board):
            player = -player
            moves  = get_legal_moves(board, player)
        self.player        = player
        self.untried_moves: list[tuple] = moves

    def uct_score(self, C: float) -> float:
        if self.visits == 0:
            return INF
        pv = self.parent.visits if self.parent else self.visits
        return (self.wins / self.visits) + C * math.sqrt(math.log(pv) / self.visits)

    def best_child(self, C: float) -> '_MCTSNode':
        return max(self.children, key=lambda n: n.uct_score(C))

    @property
    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    @property
    def is_terminal(self) -> bool:
        return is_game_over(self.board)


class MCTS:
    def __init__(self, iterations: int = 600, C: float = math.sqrt(2)):
        self.iterations     = iterations
        self.C              = C
        self.nodes_explored = 0

    def search(self, board: Board, player: int,
               time_limit: float = INF) -> tuple[tuple | None, float]:
        deadline            = time.perf_counter() + time_limit
        self.nodes_explored = 0
        root = _MCTSNode(board, player)

        for i in range(self.iterations):
            # Verificar tiempo cada 20 iteraciones
            if i % 20 == 0 and time.perf_counter() > deadline:
                break
            self.nodes_explored += 1
            node = self._select(root)
            if not node.is_terminal:
                node = self._expand(node)
            result = self._simulate(node)
            self._backpropagate(node, result, player)

        if not root.children:
            fallback = get_legal_moves(board, player)
            return (random.choice(fallback) if fallback else None), 0.0

        best  = max(root.children, key=lambda n: n.visits)
        score = best.wins / best.visits if best.visits else 0.0
        return best.move, score

    def _select(self, node: _MCTSNode) -> _MCTSNode:
        while not node.is_terminal:
            if not node.is_fully_expanded:
                return node
            if not node.children:  # nodo completamente expandido sin hijos — tratar como terminal
                return node
            node = node.best_child(self.C)
        return node

    def _expand(self, node: _MCTSNode) -> _MCTSNode:
        idx  = random.randrange(len(node.untried_moves))
        move = node.untried_moves.pop(idx)
        nb   = apply_move(node.board, move[0], move[1], node.player)
        child = _MCTSNode(nb, -node.player, parent=node, move=move)
        node.children.append(child)
        return child

    def _simulate(self, node: _MCTSNode) -> int | None:
        board   = node.board.copy()
        current = node.player
        while True:
            moves = get_legal_moves(board, current)
            if moves:
                move  = random.choice(moves)
                board = apply_move(board, move[0], move[1], current)
                current = -current
            else:
                if get_legal_moves(board, -current):
                    current = -current
                else:
                    return get_winner(board)

    def _backpropagate(self, node: _MCTSNode, result: int | None, root_player: int):
        while node is not None:
            node.visits += 1
            if result == root_player:
                node.wins += 1.0
            elif result is None:
                node.wins += 0.5
            node = node.parent