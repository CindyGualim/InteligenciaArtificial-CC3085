# ***Proyecto No. 3 — Juegos Adversarios Othello***

**Curso:** Inteligencia Artificial — CC3085, Sección 20  
**Universidad:** Universidad del Valle de Guatemala  

**Integrantes:**

- Javier Linares — 231135
- Luis Pedro Lira — 23669
- Cindy Gualim — 21226

---

### Descripción General



---

### Estructura del Repositorio

```
/proyecto3_ia
│
├── core/                           # ===== GAME ENGINE =====
│   │
│   ├── game_engine.py              # Clase GameEngine
│   │
│   ├── board.py                    # Estado del tablero 8x8
│   │
│   ├── rules.py                    # get_legal_moves(), reglas, flips
│   │
│   ├── heuristics.py               # evaluate()
│   │                                # mobility, corners, stability
│   │
│   └── algorithms.py               # minimax, alpha-beta,
│                                    # expectimax, mcts
│
│
├── ai/                             # ===== AGENTES =====
│   │
│   ├── agent.py                    # OthelloAgent
│   │                                # controla tiempo y dificultad
│   │
│   └── tournament.py               # IA vs IA (20 partidas)
│
│
├── ui/                             # ===== GAME VISUALIZER =====
│   │
│   ├── visualizer.py               # Clase GameVisualizer
│   │
│   └── assets/                     # imágenes, sprites, fuentes
│
│
├── analysis/                       # ===== RENDIMIENTO =====
│   │
│   ├── benchmark.py                # minimax vs alpha-beta
│   │
│   ├── metrics.py                  # branching factor
│   │
│   ├── plots.py                    # gráficas
│   │
│   ├── results.csv                 # resultados experimentales
│   │
│   └── graphs/                     # imágenes de gráficas
│
│
│
│
│
├── main.py                         # menú principal
│                                    # H vs H
│                                    # H vs IA
│                                    # IA vs IA
│
│
│
└── README.md                       # documentación GitHub

```




---


*Fecha de entrega: lunes 1 de junio de 2026*
