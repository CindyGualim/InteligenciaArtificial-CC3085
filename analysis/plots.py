from __future__ import annotations
import csv
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

RESULTS_CSV = os.path.join(os.path.dirname(__file__), 'results.csv')
GRAPHS_DIR  = os.path.join(os.path.dirname(__file__), 'graphs')

_DARK_STYLE = {
    'figure.facecolor': '#1e2530',
    'axes.facecolor':   '#252e3d',
    'axes.edgecolor':   '#4a5568',
    'text.color':       '#e2e8f0',
    'axes.labelcolor':  '#e2e8f0',
    'xtick.color':      '#a0aec0',
    'ytick.color':      '#a0aec0',
    'grid.color':       '#2d3748',
    'grid.linestyle':   '--',
    'grid.alpha':       0.6,
    'legend.facecolor': '#1e2530',
    'legend.edgecolor': '#4a5568',
}

MM_COLOR = '#fc8181'
AB_COLOR = '#68d391'


def _load() -> dict:
    data: dict = {'Minimax': {}, 'AlphaBeta': {}}
    with open(RESULTS_CSV, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            algo = row['algorithm']
            if algo not in data:
                continue
            d = data[algo]
            d.setdefault('depth',   []).append(int(row['depth']))
            d.setdefault('nodes',   []).append(int(row['nodes']))
            d.setdefault('time_ms', []).append(float(row['time_ms']))
            d.setdefault('ebf',     []).append(float(row['ebf']))
    return data


def _apply_style():
    plt.rcParams.update(_DARK_STYLE)


def generate_plots():
    os.makedirs(GRAPHS_DIR, exist_ok=True)
    _apply_style()
    data = _load()
    mm, ab = data['Minimax'], data['AlphaBeta']

    # 1. Nodos vs Profundidad
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(mm['depth'], mm['nodes'], 'o-', color=MM_COLOR, label='Minimax',    lw=2, ms=7)
    ax.plot(ab['depth'], ab['nodes'], 's-', color=AB_COLOR, label='Alpha-Beta', lw=2, ms=7)
    ax.set_xlabel('Profundidad', fontsize=12)
    ax.set_ylabel('Nodos explorados', fontsize=12)
    ax.set_title('Nodos explorados vs Profundidad', fontsize=14, pad=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.legend(fontsize=11)
    ax.grid(True)
    fig.tight_layout()
    _save(fig, 'nodes_vs_depth.png')

    # 2. Tiempo vs Profundidad
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(mm['depth'], mm['time_ms'], 'o-', color=MM_COLOR, label='Minimax',    lw=2, ms=7)
    ax.plot(ab['depth'], ab['time_ms'], 's-', color=AB_COLOR, label='Alpha-Beta', lw=2, ms=7)
    ax.set_xlabel('Profundidad', fontsize=12)
    ax.set_ylabel('Tiempo (ms)', fontsize=12)
    ax.set_title('Tiempo de ejecución vs Profundidad', fontsize=14, pad=12)
    ax.legend(fontsize=11)
    ax.grid(True)
    fig.tight_layout()
    _save(fig, 'time_vs_depth.png')

    # 3. EBF comparado 
    n  = len(mm['depth'])
    xs = list(range(n))
    w  = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([x - w/2 for x in xs], mm['ebf'], w, label='Minimax',    color=MM_COLOR, alpha=0.85)
    ax.bar([x + w/2 for x in xs], ab['ebf'], w, label='Alpha-Beta', color=AB_COLOR, alpha=0.85)
    ax.set_xlabel('Profundidad', fontsize=12)
    ax.set_ylabel('Factor de Ramificación Efectivo (EBF)', fontsize=12)
    ax.set_title('EBF: Minimax vs Alpha-Beta', fontsize=14, pad=12)
    ax.set_xticks(xs)
    ax.set_xticklabels(mm['depth'])
    ax.legend(fontsize=11)
    ax.grid(True, axis='y')
    fig.tight_layout()
    _save(fig, 'ebf_comparison.png')

    # 4. Eficiencia de poda Alpha-Beta
    from analysis.metrics import pruning_efficiency
    pruning = [pruning_efficiency(mn, an)
               for mn, an in zip(mm['nodes'], ab['nodes'])]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(mm['depth'], pruning, color='#63b3ed', alpha=0.85)
    for bar, val in zip(bars, pruning):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.8,
                f'{val:.1f}%', ha='center', va='bottom',
                fontsize=10, color='#e2e8f0')
    ax.set_xlabel('Profundidad', fontsize=12)
    ax.set_ylabel('Nodos podados (%)', fontsize=12)
    ax.set_title('Eficiencia de la poda Alpha-Beta', fontsize=14, pad=12)
    ax.set_ylim(0, 105)
    ax.grid(True, axis='y')
    fig.tight_layout()
    _save(fig, 'pruning_efficiency.png')

    print(f"\n  4 graficas guardadas en: {GRAPHS_DIR}")


def _save(fig, name: str):
    path = os.path.join(GRAPHS_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  OK: {path}")