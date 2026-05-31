from __future__ import annotations
from core.board import BLACK, WHITE
from core.game_engine import GameEngine
from ai.agent import OthelloAgent

# Función a nivel de módulo — requerida para serialización con ProcessPoolExecutor

def _game_worker(args: tuple) -> dict:
    """Ejecuta una partida completa entre dos agentes. Usada por ProcessPoolExecutor."""
    game_num, a_difficulty, b_difficulty = args

    if game_num % 2 == 0:
        black = OthelloAgent(BLACK, a_difficulty)
        white = OthelloAgent(WHITE, b_difficulty)
        a_is_black = True
    else:
        black = OthelloAgent(BLACK, b_difficulty)
        white = OthelloAgent(WHITE, a_difficulty)
        a_is_black = False

    engine = GameEngine()
    agents = {BLACK: black, WHITE: white}
    moves  = 0

    while not engine.game_over:
        agent = agents[engine.current_player]
        move, _ = agent.choose_move(engine.board)
        if move:
            engine.make_move(*move)
            moves += 1
        else:
            engine._advance_turn()

    winner = engine.winner
    score  = engine.get_score()

    a_color = BLACK if a_is_black else WHITE
    b_color = WHITE if a_is_black else BLACK

    return {
        'game_num':   game_num,
        'a_won':      winner == a_color,
        'b_won':      winner == b_color,
        'draw':       winner is None,
        'length':     moves,
        'score':      score,
        'a_is_black': a_is_black,
    }

# Clase Torneo

class Tournament:
    def __init__(self, agent_a: OthelloAgent, agent_b: OthelloAgent,
                 num_games: int = 20):
        self.agent_a   = agent_a
        self.agent_b   = agent_b
        self.num_games = num_games

    # Ejecución secuencial

    def run(self) -> dict:
        results = {'agent_a_wins': 0, 'agent_b_wins': 0, 'draws': 0,
                   'game_lengths': [], 'scores': []}

        for game_num in range(self.num_games):
            if game_num % 2 == 0:
                black, white = self.agent_a, self.agent_b
            else:
                black, white = self.agent_b, self.agent_a

            black.player = BLACK
            white.player = WHITE

            winner, length, score = self._play_game(black, white)
            results['game_lengths'].append(length)
            results['scores'].append(score)

            a_color = BLACK if game_num % 2 == 0 else WHITE
            if winner == a_color:
                results['agent_a_wins'] += 1
                wl = 'A'
            elif winner is not None:
                results['agent_b_wins'] += 1
                wl = 'B'
            else:
                results['draws'] += 1
                wl = 'Empate'

            print(f"  Partida {game_num+1:2d}: {wl:6s} | "
                  f"Negro {score[0]}-{score[1]} Blanco | {length} mov.")

        return results

    def _play_game(self, black_agent: OthelloAgent, white_agent: OthelloAgent
                   ) -> tuple[int | None, int, tuple[int, int]]:
        engine = GameEngine()
        agents = {BLACK: black_agent, WHITE: white_agent}
        moves  = 0
        while not engine.game_over:
            agent = agents[engine.current_player]
            move, _ = agent.choose_move(engine.board)
            if move:
                engine.make_move(*move)
                moves += 1
            else:
                engine._advance_turn()
        return engine.winner, moves, engine.get_score()

    # Ejecución paralela (ProcessPoolExecutor)

    def run_parallel(self, progress_cb=None, max_workers: int | None = None) -> dict:
        """Ejecuta todas las partidas en paralelo usando ProcessPoolExecutor."""
        import concurrent.futures, multiprocessing

        n_cpu     = multiprocessing.cpu_count() or 1
        n_workers = max_workers or max(1, min(n_cpu, self.num_games))
        a_diff    = self.agent_a.difficulty
        b_diff    = self.agent_b.difficulty

        results = {'agent_a_wins': 0, 'agent_b_wins': 0, 'draws': 0,
                   'game_lengths': [], 'scores': []}

        args = [(n, a_diff, b_diff) for n in range(self.num_games)]

        with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as exe:
            future_map = {exe.submit(_game_worker, a): a[0] for a in args}
            for future in concurrent.futures.as_completed(future_map):
                try:
                    r = future.result()
                except Exception:
                    continue

                results['game_lengths'].append(r['length'])
                results['scores'].append(r['score'])
                if r['a_won']:
                    results['agent_a_wins'] += 1
                elif r['b_won']:
                    results['agent_b_wins'] += 1
                else:
                    results['draws'] += 1

                if progress_cb:
                    progress_cb(r)

        return results