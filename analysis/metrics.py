from __future__ import annotations
import math


def effective_branching_factor(nodes: int, depth: int) -> float:
    """
    Aproxima el Factor de Ramificación Efectivo (EBF) resolviendo:
    b + b^2 + ... + b^d = nodes  mediante el método de Newton.
    """
    if depth == 0 or nodes <= 1:
        return 1.0
    b = max(1.0, nodes ** (1.0 / depth))
    for _ in range(200):
        f  = sum(b ** i for i in range(1, depth + 1)) - nodes
        df = sum(i * b ** (i - 1) for i in range(1, depth + 1))
        if df == 0:
            break
        b_new = b - f / df
        if abs(b_new - b) < 1e-8:
            b = b_new
            break
        b = max(1.0, b_new)
    return round(b, 4)


def pruning_efficiency(minimax_nodes: int, ab_nodes: int) -> float:
    """Porcentaje de nodos podados por Alpha-Beta respecto al Minimax puro."""
    if minimax_nodes == 0:
        return 0.0
    return round(100.0 * (1.0 - ab_nodes / minimax_nodes), 2)


def speedup_factor(mm_time_ms: float, ab_time_ms: float) -> float:
    """Cuántas veces más rápido es Alpha-Beta respecto al Minimax puro."""
    if ab_time_ms == 0:
        return float('inf')
    return round(mm_time_ms / ab_time_ms, 2)


def summarize(results: list[dict]) -> dict:
    """
    Calcula estadísticas agregadas a partir de las filas del benchmark.
    Cada fila tiene: depth, algorithm, nodes, time_ms, ebf.
    """
    mm  = [r for r in results if r['algorithm'] == 'Minimax']
    ab  = [r for r in results if r['algorithm'] == 'AlphaBeta']
    out = {}
    for depth_row_mm, depth_row_ab in zip(mm, ab):
        d = depth_row_mm['depth']
        out[d] = {
            'mm_nodes':  depth_row_mm['nodes'],
            'ab_nodes':  depth_row_ab['nodes'],
            'mm_time':   depth_row_mm['time_ms'],
            'ab_time':   depth_row_ab['time_ms'],
            'pruning':   pruning_efficiency(depth_row_mm['nodes'], depth_row_ab['nodes']),
            'speedup':   speedup_factor(depth_row_mm['time_ms'], depth_row_ab['time_ms']),
            'mm_ebf':    depth_row_mm['ebf'],
            'ab_ebf':    depth_row_ab['ebf'],
        }
    return out