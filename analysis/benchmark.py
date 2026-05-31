from __future__ import annotations
import csv
import os
import random
import time

from core.game_engine import GameEngine
from core.rules import get_legal_moves
from core.algorithms import Minimax, AlphaBeta
from analysis.metrics import effective_branching_factor

RESULTS_CSV = os.path.join(os.path.dirname(__file__), 'results.csv')
MAX_DEPTH   = 6
POSITIONS   = 3    # tableros de medio juego por ejecución
RANDOM_SEED = 42
MM_TIME_CAP = 30.0  # límite de tiempo por posición para Minimax (segundos)

# Función a nivel de módulo — requerida para serialización con ProcessPoolExecutor

def _position_worker(args: tuple) -> dict | None:
    """
    Ejecuta el benchmark para una combinación (profundidad, tablero).
    Usa profundidad fija para comparación justa entre Minimax y Alpha-Beta.
    Llamada por ProcessPoolExecutor.
    """
    depth, grid, player, mm_cap = args

    from core.board import Board
    from core.algorithms import Minimax, AlphaBeta
    from core.rules import get_legal_moves as glm

    board = Board.__new__(Board)
    board.grid = [row[:] for row in grid]

    if not glm(board, player):
        return None

    # Minimax a profundidad fija
    mm = Minimax(max_depth=depth)
    t0 = time.perf_counter()
    mm.search(board, player, time_limit=mm_cap)
    mm_time = time.perf_counter() - t0

    # Alpha-Beta a la misma profundidad fija (sin profundizacion iterativa — comparación justa)
    ab = AlphaBeta(max_depth=depth)
    t0 = time.perf_counter()
    ab.search_fixed(board, player, depth=depth, time_limit=mm_cap)
    ab_time = time.perf_counter() - t0

    return {
        'depth':    depth,
        'mm_nodes': mm.nodes_explored,
        'mm_time':  mm_time,
        'ab_nodes': ab.nodes_explored,
        'ab_time':  ab_time,
    }

# Funciones auxiliares

def _sample_positions(n: int) -> list[tuple]:
    """Genera n tableros de medio juego usando movimientos aleatorios."""
    random.seed(RANDOM_SEED)
    positions = []
    for _ in range(n):
        engine = GameEngine()
        for _ in range(30):
            moves = engine.get_legal_moves()
            if moves and not engine.game_over:
                engine.make_move(*random.choice(moves))
            else:
                break
        positions.append((engine.board.copy(), engine.current_player))
    return positions


def _write_csv(rows: list[dict]):
    """Escribe los resultados en results.csv. Solo este archivo puede hacerlo."""
    os.makedirs(os.path.dirname(RESULTS_CSV) or '.', exist_ok=True)
    with open(RESULTS_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['depth', 'algorithm', 'nodes', 'time_ms', 'ebf'])
        w.writeheader()
        w.writerows(rows)


def _build_rows(depth: int, mm_n: int, mm_t: float, ab_n: int, ab_t: float) -> list[dict]:
    return [
        {'depth': depth, 'algorithm': 'Minimax',
         'nodes': mm_n, 'time_ms': round(mm_t * 1000, 1),
         'ebf': effective_branching_factor(mm_n, depth)},
        {'depth': depth, 'algorithm': 'AlphaBeta',
         'nodes': ab_n, 'time_ms': round(ab_t * 1000, 1),
         'ebf': effective_branching_factor(ab_n, depth)},
    ]

# API pública

def run_benchmark(progress_cb=None) -> list[dict]:
    """Benchmark secuencial — Minimax vs AlphaBeta a profundidades fijas 1-MAX_DEPTH."""
    positions = _sample_positions(POSITIONS)
    rows: list[dict] = []

    for depth in range(1, MAX_DEPTH + 1):
        mm_n = ab_n = mm_t = ab_t = valid = 0

        for board, player in positions:
            if not get_legal_moves(board, player):
                continue
            valid += 1

            mm = Minimax(max_depth=depth)
            t0 = time.perf_counter()
            mm.search(board, player, time_limit=MM_TIME_CAP)
            mm_t += time.perf_counter() - t0
            mm_n += mm.nodes_explored

            ab = AlphaBeta(max_depth=depth)
            t0 = time.perf_counter()
            ab.search_fixed(board, player, depth=depth, time_limit=MM_TIME_CAP)
            ab_t += time.perf_counter() - t0
            ab_n += ab.nodes_explored

        if not valid:
            continue

        mm_avg_n = mm_n // valid;  ab_avg_n = ab_n // valid
        mm_avg_t = mm_t / valid;   ab_avg_t = ab_t / valid

        rows.extend(_build_rows(depth, mm_avg_n, mm_avg_t, ab_avg_n, ab_avg_t))
        if progress_cb:
            progress_cb(depth, mm_avg_n, mm_avg_t, ab_avg_n, ab_avg_t)

    _write_csv(rows)
    return rows


def run_parallel_benchmark(progress_cb=None,
                           max_workers: int | None = None) -> list[dict]:
    """Benchmark paralelo usando ProcessPoolExecutor."""
    import concurrent.futures, multiprocessing, collections

    positions = _sample_positions(POSITIONS)
    n_cpu     = multiprocessing.cpu_count() or 1
    n_workers = max_workers or max(1, min(n_cpu, POSITIONS * MAX_DEPTH))
    depth_data: dict[int, list[dict]] = collections.defaultdict(list)

    args = [
        (depth, board.grid, player, MM_TIME_CAP)
        for depth in range(1, MAX_DEPTH + 1)
        for board, player in positions
    ]

    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as exe:
        future_map = {exe.submit(_position_worker, a): a[0] for a in args}
        for future in concurrent.futures.as_completed(future_map):
            try:
                r = future.result()
            except Exception:
                continue
            if r is None:
                continue
            depth_data[r['depth']].append(r)

    rows: list[dict] = []
    for depth in range(1, MAX_DEPTH + 1):
        items = depth_data.get(depth, [])
        if not items:
            continue
        mm_n = sum(i['mm_nodes'] for i in items) // len(items)
        ab_n = sum(i['ab_nodes'] for i in items) // len(items)
        mm_t = sum(i['mm_time']  for i in items) / len(items)
        ab_t = sum(i['ab_time']  for i in items) / len(items)
        rows.extend(_build_rows(depth, mm_n, mm_t, ab_n, ab_t))
        if progress_cb:
            progress_cb(depth, mm_n, mm_t, ab_n, ab_t)

    _write_csv(rows)
    return rows