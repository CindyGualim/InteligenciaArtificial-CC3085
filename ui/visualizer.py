from __future__ import annotations
import time
import pygame
from core.board import Board, BLACK, WHITE, EMPTY
from core.game_engine import GameEngine

# Constantes de diseño
CELL_SIZE = 70
BOARD_OX  = 20
BOARD_OY  = 20
BOARD_PX  = CELL_SIZE * 8
PANEL_X   = BOARD_OX + BOARD_PX + 20
PANEL_W   = 300
WINDOW_W  = PANEL_X + PANEL_W + 20
WINDOW_H  = BOARD_OY + BOARD_PX + 20

# Paleta de colores
BG        = (12, 18, 30)
PANEL_BG  = (18, 26, 40)
CELL_A    = (0,  115, 55)
CELL_B    = (0,  155, 75)
GRID_LINE = (0,   75, 35)
BORDER    = (55,  65, 80)
PIECE_B   = (18,  18, 18)
PIECE_W   = (235, 238, 245)
SHADOW_C  = (8,   8,   8)
HINT_RGBA = (255, 220, 0, 80)
GOLD      = (255, 200, 50)
RED_C     = (210, 65,  65)
GRAY      = (110, 128, 152)
DARK_GRAY = (45,  58,  75)
BLUE_L    = (140, 195, 255)
WHITE_C   = (220, 230, 245)
ACCENT    = (0,   200, 130)
BTN_N     = (30,  44,  64)
BTN_H     = (44,  64,  94)


def _font(size: int, bold: bool = False) -> pygame.font.Font:
    for name in ('Segoe UI', 'Arial', None):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)


class _Button:
    def __init__(self, text: str, rect: pygame.Rect, font: pygame.font.Font,
                 color=BTN_N, hover=BTN_H, fg=WHITE_C):
        self.text  = text
        self.rect  = rect
        self._col  = color
        self._hov  = hover
        self._fg   = fg
        self._font = font
        self._over = False

    def update(self, mouse):
        self._over = self.rect.collidepoint(mouse)

    def draw(self, surf):
        col = self._hov if self._over else self._col
        pygame.draw.rect(surf, col, self.rect, border_radius=8)
        pygame.draw.rect(surf, ACCENT if self._over else DARK_GRAY,
                         self.rect, 2, border_radius=8)
        s = self._font.render(self.text, True, self._fg)
        surf.blit(s, s.get_rect(center=self.rect.center))

    def clicked(self, event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


class GameVisualizer:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock,
                 engine: GameEngine, mode: str = 'hvh',
                 black_agent=None, white_agent=None):
        self.screen = screen
        self.clock  = clock
        self.engine = engine
        self.mode   = mode
        self.black_agent = black_agent
        self.white_agent = white_agent

        self._font_lg = _font(26, bold=True)
        self._font_md = _font(19)
        self._font_sm = _font(15)
        self._font_xs = _font(13)

        self._hint_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self._hint_surf, HINT_RGBA,
                           (CELL_SIZE // 2, CELL_SIZE // 2), 13)

        px = PANEL_X + 12
        self._back_btn = _Button(
            "Volver al Menu",
            pygame.Rect(px, WINDOW_H - 52, PANEL_W - 24, 40),
            font=_font(15, bold=True),
        )

        self._status  = "Turno: Negro"
        self._ai_timer = 0
        self._ai_delay = 380   # ms de retraso antes de que la IA juegue

    # Bucle principal de pygame

    def run(self):
        while True:
            dt = self.clock.tick(60)
            mouse = pygame.mouse.get_pos()
            self._back_btn.update(mouse)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys; sys.exit(0)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
                if self._back_btn.clicked(event):
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)

            if not self.engine.game_over:
                agent = self._current_agent()
                if agent is not None:
                    self._ai_timer += dt
                    if self._ai_timer >= self._ai_delay:
                        self._ai_timer = 0
                        self._do_ai_move(agent)

            self._draw()
            pygame.display.flip()

    # Manejadores de eventos

    def _handle_click(self, pos):
        if self.engine.game_over or self._current_agent() is not None:
            return
        col = (pos[0] - BOARD_OX) // CELL_SIZE
        row = (pos[1] - BOARD_OY) // CELL_SIZE
        if 0 <= row < 8 and 0 <= col < 8:
            if self.engine.make_move(row, col):
                self._refresh_status()

    def _do_ai_move(self, agent):
        self._status = "IA calculando..."
        self._draw()
        pygame.display.flip()
        t0 = time.perf_counter()
        move, score = agent.choose_move(self.engine.board)
        elapsed = time.perf_counter() - t0
        if move:
            self.engine.make_move(move[0], move[1])
        else:
            self.engine._advance_turn()
        self.engine.last_nodes = agent.nodes_explored
        self.engine.last_time  = elapsed
        self.engine.last_eval  = score
        self._refresh_status()

    def _refresh_status(self):
        if self.engine.game_over:
            w = self.engine.winner
            self._status = ("Negro gana!" if w == BLACK
                            else "Blanco gana!" if w == WHITE
                            else "Empate!")
        else:
            p = "Negro" if self.engine.current_player == BLACK else "Blanco"
            self._status = (f"IA ({p})..." if self._current_agent()
                            else f"Turno: {p}")

    def _current_agent(self):
        if self.engine.game_over:
            return None
        return (self.black_agent if self.engine.current_player == BLACK
                else self.white_agent)

    # Métodos de renderizado

    def _draw(self):
        self.screen.fill(BG)
        self._draw_board()
        self._draw_pieces()
        if not self.engine.game_over:
            self._draw_hints()
        self._draw_panel()

    def _draw_board(self):
        for r in range(8):
            for c in range(8):
                x = BOARD_OX + c * CELL_SIZE
                y = BOARD_OY + r * CELL_SIZE
                col = CELL_A if (r + c) % 2 == 0 else CELL_B
                pygame.draw.rect(self.screen, col, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, GRID_LINE, (x, y, CELL_SIZE, CELL_SIZE), 1)
        pygame.draw.rect(self.screen, BORDER,
                         (BOARD_OX - 2, BOARD_OY - 2, BOARD_PX + 4, BOARD_PX + 4), 2)
        # Etiquetas de filas/columnas
        for i in range(8):
            s = self._font_xs.render(str(i), True, DARK_GRAY)
            self.screen.blit(s, (BOARD_OX + i * CELL_SIZE + CELL_SIZE // 2 - 4,
                                 BOARD_OY + BOARD_PX + 4))
            self.screen.blit(s, (BOARD_OX - 16,
                                 BOARD_OY + i * CELL_SIZE + CELL_SIZE // 2 - 7))

    def _draw_pieces(self):
        radius = CELL_SIZE // 2 - 7
        for r in range(8):
            for c in range(8):
                val = self.engine.board.get(r, c)
                if val == EMPTY:
                    continue
                cx = BOARD_OX + c * CELL_SIZE + CELL_SIZE // 2
                cy = BOARD_OY + r * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(self.screen, SHADOW_C, (cx + 3, cy + 3), radius)
                pygame.draw.circle(self.screen, PIECE_B if val == BLACK else PIECE_W,
                                   (cx, cy), radius)

    def _draw_hints(self):
        for r, c in self.engine.get_legal_moves():
            self.screen.blit(self._hint_surf,
                             (BOARD_OX + c * CELL_SIZE, BOARD_OY + r * CELL_SIZE))

    def _draw_panel(self):
        pygame.draw.rect(self.screen, PANEL_BG,
                         (PANEL_X, 0, PANEL_W + 20, WINDOW_H))
        px = PANEL_X + 12
        y  = 18

        self._txt("OTHELLO", px, y, self._font_lg, GOLD)
        y += 36

        b_score, w_score = self.engine.get_score()
        self._txt(f"  Negro  : {b_score:2d}", px, y, self._font_md, WHITE_C)
        y += 24
        self._txt(f"  Blanco : {w_score:2d}", px, y, self._font_md, WHITE_C)
        y += 30

        self._sep(px, y);  y += 14

        # Estado del juego
        col = RED_C if self.engine.game_over else (GOLD if "IA" in self._status else ACCENT)
        self._txt(self._status, px, y, self._font_md, col)
        y += 34

        self._sep(px, y);  y += 14

        # Métricas de la IA
        self._txt("Metricas IA", px, y, self._font_sm, GRAY)
        y += 24
        self._txt(f"Nodos  : {self.engine.last_nodes:,}", px, y, self._font_xs, BLUE_L)
        y += 20
        self._txt(f"Tiempo : {self.engine.last_time * 1000:.1f} ms", px, y, self._font_xs, BLUE_L)
        y += 20
        self._txt(f"Eval   : {self.engine.last_eval:.2f}", px, y, self._font_xs, BLUE_L)
        y += 28

        # Fase del juego
        from core.heuristics import get_phase
        phase = get_phase(self.engine.board)
        phase_col = {
            'opening': (100, 210, 110),
            'midgame': GOLD,
            'endgame': RED_C,
        }.get(phase, GRAY)
        self._txt(f"Fase   : {phase.capitalize()}", px, y, self._font_xs, phase_col)
        y += 24

        # Contador de movimientos
        self._txt(f"Turno  : {len(self.engine.move_history) + 1}", px, y, self._font_xs, GRAY)
        y += 28

        self._sep(px, y);  y += 14

        # Controles
        self._txt("[Click] Colocar ficha", px, y, self._font_xs, DARK_GRAY);  y += 18
        self._txt("[ESC]   Volver al menu", px, y, self._font_xs, DARK_GRAY)

        # Botón de regreso
        self._back_btn.draw(self.screen)

    def _txt(self, msg, x, y, font, color):
        self.screen.blit(font.render(msg, True, color), (x, y))

    def _sep(self, px, y):
        pygame.draw.line(self.screen, DARK_GRAY,
                         (px, y), (px + PANEL_W - 24, y))