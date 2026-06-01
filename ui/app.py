from __future__ import annotations
import pygame
import sys
import os
import threading
import time

from core.board import BLACK, WHITE
from core.game_engine import GameEngine


def _n_workers(n_jobs: int, per_job_mb: int = 80) -> int:
    """
    Calcula el número seguro de workers para ProcessPoolExecutor según la máquina actual.
    - Escala con los núcleos disponibles (maneja None de cpu_count).
    - Limitado por n_jobs: no tiene sentido más workers que tareas.
    - Limitado por RAM: evita saturar máquinas con poca memoria.
    """
    import multiprocessing, os
    n_cpu = multiprocessing.cpu_count() or 1

    # Estimar límite de RAM disponible (opcional, solo en plataformas compatibles)
    try:
        import psutil
        free_mb = psutil.virtual_memory().available // (1024 * 1024)
        ram_cap = max(1, int(free_mb * 0.75 / per_job_mb))
    except Exception:
        ram_cap = n_cpu  # fallback: confiar en el número de núcleos

    return max(1, min(n_cpu, n_jobs, ram_cap))

# Ventana
W, H = 1020, 700

# Paleta de colores
BG         = (12, 18, 30)
PANEL      = (20, 30, 46)
CARD       = (26, 38, 56)
ACCENT     = (0, 200, 130)
GOLD       = (255, 200, 50)
WHITE_C    = (220, 230, 245)
GRAY       = (110, 128, 152)
MID_GRAY   = (55, 70, 90)
RED_C      = (210, 65, 65)
GREEN_D    = (0, 115, 55)
GREEN_L    = (0, 155, 75)
BTN_N      = (32, 46, 66)
BTN_H      = (46, 66, 96)
BTN_SEL    = (0, 150, 90)
BTN_DNG    = (130, 38, 38)
SHADOW     = (6, 10, 16)


def _font(size: int, bold: bool = False) -> pygame.font.Font:
    for name in ('Segoe UI', 'Arial', 'DejaVu Sans', None):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)


# Widget de botón

class Button:
    def __init__(self, text: str, rect: pygame.Rect,
                 color=BTN_N, hover=BTN_H, selected_color=BTN_SEL,
                 fg=WHITE_C, font: pygame.font.Font | None = None,
                 selected: bool = False, danger: bool = False):
        self.text    = text
        self.rect    = rect
        self._color  = color
        self._hover  = hover
        self._selc   = selected_color
        self._fg     = fg
        self._font   = font
        self.selected = selected
        self.danger   = danger
        self._over    = False

    def update(self, mouse: tuple[int, int]):
        self._over = self.rect.collidepoint(mouse)

    def draw(self, surf: pygame.Surface):
        if self.selected:
            bg = self._selc
            border = ACCENT
        elif self.danger and self._over:
            bg = BTN_DNG
            border = RED_C
        elif self._over:
            bg = self._hover
            border = ACCENT
        else:
            bg = self._color
            border = MID_GRAY

        pygame.draw.rect(surf, SHADOW, self.rect.move(3, 3), border_radius=9)
        pygame.draw.rect(surf, bg, self.rect, border_radius=9)
        pygame.draw.rect(surf, border, self.rect, 2, border_radius=9)
        if self._font:
            txt = self._font.render(self.text, True, self._fg)
            surf.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event: pygame.event.Event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# Funciones auxiliares

def _text(surf: pygame.Surface, msg: str, x: int, y: int,
          font: pygame.font.Font, color=WHITE_C, center: bool = False):
    s = font.render(msg, True, color)
    if center:
        surf.blit(s, s.get_rect(centerx=x, y=y))
    else:
        surf.blit(s, (x, y))


def _draw_board_bg(surf: pygame.Surface):
    """Patrón de tablero de ajedrez como fondo de pantalla."""
    tile = 34
    for r in range(H // tile + 1):
        for c in range(W // tile + 1):
            col = (20, 30, 44) if (r + c) % 2 == 0 else (16, 24, 36)
            pygame.draw.rect(surf, col, (c * tile, r * tile, tile, tile))


def _progress_bar(surf: pygame.Surface, x: int, y: int, w: int, h: int,
                  pct: float, color=ACCENT, bg=MID_GRAY):
    pygame.draw.rect(surf, bg, (x, y, w, h), border_radius=h // 2)
    fill = int(w * min(max(pct, 0), 1))
    if fill > 0:
        pygame.draw.rect(surf, color, (x, y, fill, h), border_radius=h // 2)


# ═════════════════════════════════════════════════════════════════════════════
# Menú principal
# ═════════════════════════════════════════════════════════════════════════════

class MainMenu:
    def __init__(self, app: 'App'):
        self.app   = app
        self.screen = app.screen
        self.clock  = app.clock
        f_xl  = _font(52, bold=True)
        f_sm  = _font(14)
        f_btn = _font(20, bold=True)

        cx = W // 2
        bw, bh, gap = 380, 54, 14
        by = 240

        labels = [
            "Humano  vs  Humano",
            "Humano  vs  IA",
            "IA  vs  IA  (Torneo 20 partidas)",
            "Benchmark  (Minimax vs Alpha-Beta)",
            "Ver Graficas",
            "Salir",
        ]
        self.buttons = [
            Button(lbl, pygame.Rect(cx - bw // 2, by + i * (bh + gap), bw, bh),
                   font=f_btn,
                   danger=(lbl == "Salir"))
            for i, lbl in enumerate(labels)
        ]
        self._f_xl   = f_xl
        self._f_sub  = _font(17)
        self._f_foot = f_sm

    def run(self) -> tuple[str, dict]:
        while True:
            dt = self.clock.tick(60)
            mouse = pygame.mouse.get_pos()

            for btn in self.buttons:
                btn.update(mouse)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit', {}
                for i, btn in enumerate(self.buttons):
                    if btn.clicked(event):
                        scenes = ['hvh', 'mode_select', 'tournament',
                                  'benchmark', 'plots', 'quit']
                        return scenes[i], {}

            self._draw()
            pygame.display.flip()

    def _draw(self):
        _draw_board_bg(self.screen)
        cx = W // 2

        # Tarjeta de título
        card_rect = pygame.Rect(cx - 240, 60, 480, 150)
        pygame.draw.rect(self.screen, CARD, card_rect, border_radius=18)
        pygame.draw.rect(self.screen, ACCENT, card_rect, 2, border_radius=18)
        _text(self.screen, "OTHELLO", cx, 90, self._f_xl, GOLD, center=True)
        _text(self.screen, "Inteligencia Artificial  —  CC3085", cx, 158,
              self._f_sub, GRAY, center=True)

        for btn in self.buttons:
            btn.draw(self.screen)

        _text(self.screen,
              "Universidad del Valle de Guatemala  |  Linares · Lira · Gualim",
              cx, H - 26, self._f_foot, MID_GRAY, center=True)


# ═════════════════════════════════════════════════════════════════════════════
# Selección de modo  (Humano vs IA)
# ═════════════════════════════════════════════════════════════════════════════

class ModeSelect:
    _DIFFS  = ['easy', 'medium', 'hard', 'mcts', 'expectimax']
    _LABELS = ['Facil', 'Medium', 'Dificil', 'MCTS', 'Expectimax']

    def __init__(self, app: 'App'):
        self.app    = app
        self.screen = app.screen
        self.clock  = app.clock
        self.diff   = 'medium'
        self.color  = 'black'   # which color the human plays

        f_title = _font(34, bold=True)
        f_sec   = _font(20, bold=True)
        f_btn   = _font(19, bold=True)
        f_sm    = _font(17)

        cx = W // 2

        # Botones de dificultad (fila)
        total_w  = len(self._DIFFS) * 130 + (len(self._DIFFS) - 1) * 12
        start_x  = cx - total_w // 2
        self._diff_btns = [
            Button(lbl, pygame.Rect(start_x + i * 142, 260, 130, 44),
                   font=f_btn,
                   selected=(self._DIFFS[i] == self.diff))
            for i, lbl in enumerate(self._LABELS)
        ]

        # Botones de selección de color
        self._color_btns = [
            Button("Jugar Negro", pygame.Rect(cx - 210, 370, 190, 50), font=f_btn, selected=True),
            Button("Jugar Blanco", pygame.Rect(cx + 20,  370, 190, 50), font=f_btn),
        ]

        self._start_btn = Button("Iniciar Partida",
                                 pygame.Rect(cx - 155, 460, 200, 54),
                                 color=BTN_SEL, hover=ACCENT, font=_font(21, bold=True))
        self._back_btn  = Button("Volver",
                                 pygame.Rect(cx - 155 + 210, 460, 130, 54),
                                 font=f_btn)

        self._f_title = f_title
        self._f_sec   = f_sec

    def run(self) -> tuple[str, dict]:
        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()
            for b in self._diff_btns + self._color_btns + [self._start_btn, self._back_btn]:
                b.update(mouse)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit', {}
                if self._back_btn.clicked(event):
                    return 'main_menu', {}
                if self._start_btn.clicked(event):
                    return 'hva', {'difficulty': self.diff, 'human_color': self.color}

                for i, btn in enumerate(self._diff_btns):
                    if btn.clicked(event):
                        self.diff = self._DIFFS[i]
                        for j, b in enumerate(self._diff_btns):
                            b.selected = (j == i)

                for i, btn in enumerate(self._color_btns):
                    if btn.clicked(event):
                        self.color = 'black' if i == 0 else 'white'
                        for j, b in enumerate(self._color_btns):
                            b.selected = (j == i)

            self._draw()
            pygame.display.flip()

    def _draw(self):
        _draw_board_bg(self.screen)
        cx = W // 2
        _text(self.screen, "Humano vs IA", cx, 80, self._f_title, GOLD, center=True)
        _text(self.screen, "Dificultad:", cx - 240, 210, self._f_sec, GRAY)
        _text(self.screen, "Tu color:", cx - 240, 330, self._f_sec, GRAY)
        for b in self._diff_btns + self._color_btns + [self._start_btn, self._back_btn]:
            b.draw(self.screen)


# ═════════════════════════════════════════════════════════════════════════════
# Pantalla de juego  (envuelve el visualizador, usa superficie compartida)
# ═════════════════════════════════════════════════════════════════════════════

class GameScreen:
    def __init__(self, app: 'App', mode: str = 'hvh',
                 difficulty: str = 'medium', human_color: str = 'black'):
        from ai.agent import OthelloAgent
        from ui.visualizer import GameVisualizer

        self.app    = app
        self.screen = app.screen
        self.clock  = app.clock

        engine = GameEngine()

        black_agent = white_agent = None
        if mode == 'hva':
            if human_color == 'black':
                white_agent = OthelloAgent(WHITE, difficulty)
            else:
                black_agent = OthelloAgent(BLACK, difficulty)
        elif mode == 'ava':
            black_agent = OthelloAgent(BLACK, 'hard')
            white_agent = OthelloAgent(WHITE, 'mcts')

        self._vis = GameVisualizer(
            self.screen, self.clock, engine,
            mode=mode,
            black_agent=black_agent,
            white_agent=white_agent,
        )

    def run(self) -> tuple[str, dict]:
        self._vis.run()
        return 'main_menu', {}


# ═════════════════════════════════════════════════════════════════════════════
# Pantalla de torneo
# ═════════════════════════════════════════════════════════════════════════════

class TournamentScreen:
    def __init__(self, app: 'App'):
        self.app    = app
        self.screen = app.screen
        self.clock  = app.clock

        self._state   = 'running'   # 'running' | 'done'
        self._results = {'agent_a_wins': 0, 'agent_b_wins': 0, 'draws': 0,
                         'game_lengths': [], 'scores': []}
        self._current_game  = 0
        self._total_games   = 20
        self._game_log: list[str] = []
        self._lock    = threading.Lock()

        self._f_title = _font(30, bold=True)
        self._f_med   = _font(19, bold=True)
        self._f_sm    = _font(16)
        self._f_xs    = _font(14)

        cx = W // 2
        self._back_btn = Button("Volver al Menu",
                                pygame.Rect(cx - 110, H - 80, 220, 50),
                                font=_font(18, bold=True))

        self._thread = threading.Thread(target=self._run_tournament, daemon=True)
        self._thread.start()

    def _run_tournament(self):
        import concurrent.futures
        from ai.tournament import _game_worker

        n_workers = _n_workers(self._total_games, per_job_mb=60)
        self._n_workers = n_workers
        args = [(n, 'hard', 'mcts') for n in range(self._total_games)]

        with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as exe:
            future_map = {exe.submit(_game_worker, a): a[0] for a in args}
            for future in concurrent.futures.as_completed(future_map):
                try:
                    r = future.result()
                except Exception:
                    with self._lock:
                        self._current_game += 1
                    continue

                with self._lock:
                    self._current_game += 1
                    if r['a_won']:
                        self._results['agent_a_wins'] += 1
                        wl = 'A (Alpha-Beta)'
                    elif r['b_won']:
                        self._results['agent_b_wins'] += 1
                        wl = 'B (MCTS)'
                    else:
                        self._results['draws'] += 1
                        wl = 'Empate'
                    score = r['score']
                    self._results['game_lengths'].append(r['length'])
                    self._results['scores'].append(score)
                    self._game_log.append(
                        f"P{r['game_num']+1:2d}: {wl:<18}  {score[0]}-{score[1]}"
                    )

        with self._lock:
            self._state = 'done'

    def run(self) -> tuple[str, dict]:
        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()
            self._back_btn.update(mouse)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit', {}
                if self._back_btn.clicked(event) and self._state == 'done':
                    return 'main_menu', {}

            self._draw()
            pygame.display.flip()

    def _draw(self):
        _draw_board_bg(self.screen)
        cx = W // 2
        _text(self.screen, "Torneo  IA vs IA", cx, 40, self._f_title, GOLD, center=True)
        nw = getattr(self, '_n_workers', '?')
        _text(self.screen,
              f"Alpha-Beta (ID)  vs  MCTS (600 iter)  |  {nw} worker(s) en paralelo",
              cx, 82, self._f_sm, GRAY, center=True)

        with self._lock:
            current = self._current_game
            state   = self._state
            a_wins  = self._results['agent_a_wins']
            b_wins  = self._results['agent_b_wins']
            draws   = self._results['draws']
            log     = list(self._game_log[-14:])
            lengths = list(self._results['game_lengths'])

        # Barra de progreso
        pct = current / self._total_games
        _text(self.screen,
              f"Partida {current} / {self._total_games}" if state == 'running' else "Torneo finalizado",
              cx, 118, self._f_med,
              ACCENT if state == 'running' else GOLD, center=True)
        _progress_bar(self.screen, cx - 300, 150, 600, 16, pct)

        # Tarjetas de puntuación
        self._score_card(cx - 340, 185, "Agente A", "Alpha-Beta ID", a_wins, GREEN_D)
        self._score_card(cx - 100, 185, "Empates", "", draws, MID_GRAY)
        self._score_card(cx + 100, 185, "Agente B", "MCTS 600", b_wins, (100, 60, 180))

        # Historial de partidas
        log_x, log_y = 60, 290
        _text(self.screen, "Historial de partidas:", log_x, log_y - 24,
              self._f_sm, GRAY)
        for i, line in enumerate(log):
            col = WHITE_C if i == len(log) - 1 else GRAY
            _text(self.screen, line, log_x, log_y + i * 22, self._f_xs, col)

        # Longitud promedio de partidas
        if lengths:
            avg = sum(lengths) / len(lengths)
            _text(self.screen,
                  f"Promedio de movimientos por partida: {avg:.1f}",
                  cx, H - 110, self._f_sm, GRAY, center=True)

        if state == 'done':
            self._back_btn.draw(self.screen)
        else:
            _text(self.screen, "Calculando... por favor espere",
                  cx, H - 65, self._f_sm, MID_GRAY, center=True)

    def _score_card(self, x: int, y: int, title: str, sub: str,
                    value: int, accent_col):
        r = pygame.Rect(x, y, 190, 80)
        pygame.draw.rect(self.screen, CARD, r, border_radius=12)
        pygame.draw.rect(self.screen, accent_col, r, 2, border_radius=12)
        _text(self.screen, title, x + r.w // 2, y + 10,
              _font(15, bold=True), WHITE_C, center=True)
        if sub:
            _text(self.screen, sub, x + r.w // 2, y + 30,
                  _font(13), GRAY, center=True)
        score_font = _font(28, bold=True)
        sv = score_font.render(str(value), True, accent_col)
        self.screen.blit(sv, sv.get_rect(centerx=x + r.w // 2, y=y + 44))


# ═════════════════════════════════════════════════════════════════════════════
# Pantalla de benchmark
# ═════════════════════════════════════════════════════════════════════════════

class BenchmarkScreen:
    def __init__(self, app: 'App'):
        self.app    = app
        self.screen = app.screen
        self.clock  = app.clock

        self._state   = 'running'
        self._rows: list[dict]  = []
        self._current_depth     = 0
        self._max_depth         = 6
        self._lock = threading.Lock()

        self._f_title = _font(30, bold=True)
        self._f_med   = _font(18, bold=True)
        self._f_sm    = _font(15)
        self._f_xs    = _font(13)

        cx = W // 2
        self._back_btn = Button("Volver al Menu",
                                pygame.Rect(cx - 110, H - 75, 220, 46),
                                font=_font(17, bold=True))

        self._thread = threading.Thread(target=self._run_bench, daemon=True)
        self._thread.start()

    def _run_bench(self):
        import concurrent.futures, multiprocessing, collections
        from analysis.benchmark import (
            _position_worker, _sample_positions, _write_csv, MAX_DEPTH, MM_TIME_CAP
        )
        from analysis.metrics import effective_branching_factor

        positions = _sample_positions(3)   # 3 mid-game positions
        n_workers = _n_workers(3 * MAX_DEPTH, per_job_mb=50)
        self._n_workers = n_workers

        depth_data: dict = collections.defaultdict(list)
        rows: list[dict] = []

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

                depth = r['depth']
                with self._lock:
                    depth_data[depth].append(r)
                    self._current_depth = max(depth_data.keys())

                    # Reconstruir filas con todos los datos completados
                    rows = []
                    for d in sorted(depth_data.keys()):
                        items = depth_data[d]
                        if not items:
                            continue
                        mm_n = sum(i['mm_nodes'] for i in items) // len(items)
                        ab_n = sum(i['ab_nodes'] for i in items) // len(items)
                        mm_t = sum(i['mm_time'] for i in items) / len(items)
                        ab_t = sum(i['ab_time'] for i in items) / len(items)
                        rows.extend([
                            {'depth': d, 'algorithm': 'Minimax',
                             'nodes': mm_n,
                             'time_ms': round(mm_t * 1000, 1),
                             'ebf': effective_branching_factor(mm_n, d)},
                            {'depth': d, 'algorithm': 'AlphaBeta',
                             'nodes': ab_n,
                             'time_ms': round(ab_t * 1000, 1),
                             'ebf': effective_branching_factor(ab_n, d)},
                        ])
                    self._rows = rows

        with self._lock:
            _write_csv(rows)
            self._state = 'done'

    def run(self) -> tuple[str, dict]:
        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()
            self._back_btn.update(mouse)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit', {}
                if self._back_btn.clicked(event) and self._state == 'done':
                    return 'main_menu', {}

            self._draw()
            pygame.display.flip()

    def _draw(self):
        _draw_board_bg(self.screen)
        cx = W // 2

        _text(self.screen, "Benchmark", cx, 35, self._f_title, GOLD, center=True)
        nw = getattr(self, '_n_workers', '?')
        _text(self.screen,
              f"Minimax  vs  Alpha-Beta  |  3 posiciones  |  {nw} worker(s) en paralelo",
              cx, 78, self._f_xs, GRAY, center=True)

        with self._lock:
            depth   = self._current_depth
            state   = self._state
            rows    = list(self._rows)

        pct = (depth - 1) / self._max_depth if state == 'running' else 1.0
        label = (f"Calculando profundidad {depth} / {self._max_depth}..."
                 if state == 'running' else "Completado — results.csv guardado")
        _text(self.screen, label, cx, 110, self._f_sm,
              ACCENT if state == 'running' else GOLD, center=True)
        _progress_bar(self.screen, cx - 340, 138, 680, 14, pct)

        # Tabla de resultados
        tx, ty = 60, 175
        headers = ["Depth", "Algoritmo", "Nodos", "Tiempo (ms)", "EBF", "Poda %"]
        widths  = [60, 130, 110, 120, 80, 90]
        col_x   = [tx + sum(widths[:i]) + i * 14 for i in range(len(widths))]

        # Fila de encabezados
        header_rect = pygame.Rect(tx - 6, ty - 4, sum(widths) + (len(widths)-1)*14 + 12, 28)
        pygame.draw.rect(self.screen, PANEL, header_rect, border_radius=6)
        for i, h in enumerate(headers):
            _text(self.screen, h, col_x[i], ty, self._f_xs, ACCENT)
        ty += 32

        # Filas por par de algoritmos
        from analysis.metrics import pruning_efficiency
        paired: list[tuple[dict, dict]] = []
        mm_rows  = [r for r in rows if r['algorithm'] == 'Minimax']
        ab_rows  = [r for r in rows if r['algorithm'] == 'AlphaBeta']
        for mm, ab in zip(mm_rows, ab_rows):
            paired.append((mm, ab))

        for mm, ab in paired:
            prun = pruning_efficiency(mm['nodes'], ab['nodes'])
            row_col = (22, 34, 50)
            row_rect = pygame.Rect(tx - 6, ty - 2, header_rect.w, 46)
            pygame.draw.rect(self.screen, row_col, row_rect, border_radius=4)

            vals_mm = [str(mm['depth']), 'Minimax',
                       f"{mm['nodes']:,}", f"{mm['time_ms']:.1f}", f"{mm['ebf']:.2f}", '—']
            vals_ab = ['', 'AlphaBeta',
                       f"{ab['nodes']:,}", f"{ab['time_ms']:.1f}", f"{ab['ebf']:.2f}",
                       f"{prun:.1f}%"]

            for i, (vm, va) in enumerate(zip(vals_mm, vals_ab)):
                _text(self.screen, vm, col_x[i], ty,      self._f_xs, WHITE_C)
                _text(self.screen, va, col_x[i], ty + 22, self._f_xs,
                      (100, 220, 160) if i in (4, 5) else GRAY)
            ty += 50

        if state == 'done':
            self._back_btn.draw(self.screen)
        else:
            _text(self.screen, "Esto puede tardar varios minutos...",
                  cx, H - 55, self._f_xs, MID_GRAY, center=True)


# ═════════════════════════════════════════════════════════════════════════════
# Pantalla de gráficas
# ═════════════════════════════════════════════════════════════════════════════

class PlotsScreen:
    _FILES = [
        ('nodes_vs_depth.png',     'Nodos explorados vs Profundidad'),
        ('time_vs_depth.png',      'Tiempo de ejecucion vs Profundidad'),
        ('ebf_comparison.png',     'Factor de Ramificacion Efectivo (EBF)'),
        ('pruning_efficiency.png', 'Eficiencia de la poda Alpha-Beta'),
    ]

    def __init__(self, app: 'App'):
        self.app    = app
        self.screen = app.screen
        self.clock  = app.clock
        self._idx   = 0

        graphs_dir = os.path.join('analysis', 'graphs')
        self._images: list[pygame.Surface | None] = []
        self._titles: list[str] = []

        for fname, title in self._FILES:
            path = os.path.join(graphs_dir, fname)
            self._titles.append(title)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert()
                    self._images.append(img)
                except Exception:
                    self._images.append(None)
            else:
                self._images.append(None)

        f_btn = _font(17, bold=True)
        cx    = W // 2
        self._prev_btn = Button("< Anterior",
                                pygame.Rect(cx - 480, H - 68, 148, 42), font=f_btn)
        self._next_btn = Button("Siguiente >",
                                pygame.Rect(cx + 332, H - 68, 148, 42), font=f_btn)
        self._gen_btn  = Button("Regenerar Graficas",
                                pygame.Rect(cx - 160, H - 68, 200, 42),
                                font=f_btn, color=BTN_SEL, hover=ACCENT)
        self._back_btn = Button("Volver al Menu",
                                pygame.Rect(cx + 50, H - 68, 170, 42), font=f_btn)

        self._f_title = _font(20, bold=True)
        self._f_sm    = _font(15)
        self._f_xs    = _font(13)
        self._status  = ''
        self._has_any = any(img is not None for img in self._images)

    def run(self) -> tuple[str, dict]:
        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()
            for b in [self._prev_btn, self._next_btn, self._back_btn, self._gen_btn]:
                b.update(mouse)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit', {}
                if self._back_btn.clicked(event):
                    return 'main_menu', {}
                if self._prev_btn.clicked(event):
                    self._idx = (self._idx - 1) % len(self._images)
                if self._next_btn.clicked(event):
                    self._idx = (self._idx + 1) % len(self._images)
                if self._gen_btn.clicked(event):
                    self._regenerate()

            self._draw()
            pygame.display.flip()

    def _regenerate(self):
        csv_path = os.path.join('analysis', 'results.csv')
        if not os.path.exists(csv_path):
            self._status = 'Primero ejecuta el Benchmark (desde el menu principal)'
            return
        try:
            from analysis.plots import generate_plots
            generate_plots()
            graphs_dir = os.path.join('analysis', 'graphs')
            for i, (fname, _) in enumerate(self._FILES):
                path = os.path.join(graphs_dir, fname)
                if os.path.exists(path):
                    self._images[i] = pygame.image.load(path).convert()
            self._has_any = True
            self._status = 'Graficas actualizadas.'
        except Exception as e:
            self._status = f'Error: {e}'

    def _draw(self):
        _draw_board_bg(self.screen)
        cx, cy = W // 2, H // 2

        _text(self.screen, "Graficas de Rendimiento", cx, 18,
              self._f_title, GOLD, center=True)

        # Pestañas de miniaturas
        tab_w = 200
        total_tab = len(self._FILES) * tab_w + (len(self._FILES) - 1) * 8
        tx0 = cx - total_tab // 2
        for i, (_, title) in enumerate(self._FILES):
            tab_rect = pygame.Rect(tx0 + i * (tab_w + 8), 50, tab_w, 30)
            col  = BTN_SEL if i == self._idx else BTN_N
            pygame.draw.rect(self.screen, col, tab_rect, border_radius=6)
            short = title[:28] + '…' if len(title) > 28 else title
            ts = self._f_xs.render(short, True, WHITE_C if i == self._idx else GRAY)
            self.screen.blit(ts, ts.get_rect(center=tab_rect.center))

        # Área de imagen
        img_area = pygame.Rect(30, 88, W - 60, H - 185)
        pygame.draw.rect(self.screen, PANEL, img_area, border_radius=12)
        pygame.draw.rect(self.screen, MID_GRAY, img_area, 1, border_radius=12)

        img = self._images[self._idx] if self._idx < len(self._images) else None
        if img:
            scale = min(img_area.w / img.get_width(),
                        img_area.h / img.get_height())
            nw = int(img.get_width() * scale)
            nh = int(img.get_height() * scale)
            scaled = pygame.transform.smoothscale(img, (nw, nh))
            self.screen.blit(scaled, scaled.get_rect(center=img_area.center))
        else:
            msg1 = 'No hay graficas disponibles.'
            msg2 = 'Ejecuta el Benchmark desde el menu principal primero.'
            _text(self.screen, msg1, cx, cy - 20, self._f_sm, GRAY, center=True)
            _text(self.screen, msg2, cx, cy + 10, self._f_xs, MID_GRAY, center=True)

        _text(self.screen, self._titles[self._idx] if self._titles else '',
              cx, H - 105, self._f_sm, GRAY, center=True)

        if self._status:
            _text(self.screen, self._status, cx, H - 88,
                  self._f_xs, ACCENT, center=True)

        self._prev_btn.draw(self.screen)
        self._next_btn.draw(self.screen)
        self._gen_btn.draw(self.screen)
        self._back_btn.draw(self.screen)


# ═════════════════════════════════════════════════════════════════════════════
# App  — gestor de pantallas
# ═════════════════════════════════════════════════════════════════════════════

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Othello  —  Inteligencia Artificial CC3085")
        self.clock  = pygame.time.Clock()

    def run(self):
        scene  = 'main_menu'
        params: dict = {}

        while scene != 'quit':
            if scene == 'main_menu':
                scene, params = MainMenu(self).run()

            elif scene == 'mode_select':
                scene, params = ModeSelect(self).run()

            elif scene == 'hvh':
                scene, params = GameScreen(self, mode='hvh').run()

            elif scene == 'hva':
                scene, params = GameScreen(
                    self, mode='hva',
                    difficulty=params.get('difficulty', 'medium'),
                    human_color=params.get('human_color', 'black')
                ).run()

            elif scene == 'tournament':
                scene, params = TournamentScreen(self).run()

            elif scene == 'benchmark':
                scene, params = BenchmarkScreen(self).run()

            elif scene == 'plots':
                scene, params = PlotsScreen(self).run()

            else:
                scene = 'quit'

        pygame.quit()
        sys.exit(0)