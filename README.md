# Proyecto No. 3 — Juegos Adversarios: Othello

**Curso:** Inteligencia Artificial — CC3085, Sección 20  
**Universidad:** Universidad del Valle de Guatemala

**Integrantes:**

- Javier Linares — 231135
- Luis Pedro Lira — 23669
- Cindy Gualim — 21226

---

## Descripción General

Implementación completa de un agente inteligente para el juego **Othello (Reversi)** en un tablero de 8×8. El proyecto incluye un motor de juego puro sin dependencias visuales, tres algoritmos de búsqueda adversarial (Alpha-Beta con profundización iterativa, Expectimax y MCTS), una función heurística por fases de juego, una interfaz gráfica en Pygame y un módulo de análisis de rendimiento con gráficas reproducibles.

El diseño sigue una **separación total entre lógica de decisión e interfaz visual**, tal como lo exige el enunciado del proyecto. El módulo `core/` puede ejecutarse de forma completamente independiente sin inicializar Pygame.

---

## Estructura del Repositorio

```
proyecto3_ia/
│
├── core/                       # Motor del juego (GameEngine)
│   ├── __init__.py
│   ├── board.py                # Representación del tablero 8×8
│   ├── rules.py                # get_legal_moves(), apply_move(), flips
│   ├── heuristics.py           # evaluate() por fase: apertura / medio / cierre
│   ├── algorithms.py           # Minimax, AlphaBeta, Expectimax, MCTS
│   └── game_engine.py          # Clase GameEngine — orquesta todo el juego
│
├── ai/                         # Agentes y torneo
│   ├── __init__.py
│   ├── agent.py                # OthelloAgent — control de tiempo y dificultad
│   └── tournament.py           # Duelo IA vs IA (20 partidas, paralelo/secuencial)
│
├── ui/                         # Interfaz visual
│   ├── __init__.py
│   ├── app.py                  # Escenas: menú, selección, juego, torneo, benchmark
│   ├── visualizer.py           # GameVisualizer — renderizado Pygame a 60 FPS
│   └── assets/                 # Sprites, fuentes e imágenes
│
├── analysis/                   # Análisis de rendimiento
│   ├── __init__.py
│   ├── benchmark.py            # Minimax vs Alpha-Beta — genera results.csv
│   ├── metrics.py              # EBF, eficiencia de poda, speedup
│   ├── plots.py                # Gráficas Matplotlib → analysis/graphs/
│   └── graphs/                 # Imágenes generadas (para el reporte PDF)
│
├── main.py                     # Punto de entrada principal
├── requirements.txt            # Dependencias Python
└── README.md
```

---


***Desde el menú principal se puede acceder a:***

| Opción | Descripción |
|--------|-------------|
| **Humano vs Humano** | Dos jugadores en el mismo teclado/mouse |
| **Humano vs IA** | El jugador elige su color y la dificultad del agente |
| **IA vs IA** | Alpha-Beta (hard) contra MCTS — se puede observar en tiempo real |
| **Torneo** | 20 partidas automáticas Alpha-Beta vs MCTS con estadísticas |
| **Benchmark** | Comparación Minimax puro vs Alpha-Beta con gráficas en vivo |


---

## Algoritmos Implementados

### Alpha-Beta con Profundización Iterativa (`AlphaBeta`)

Extiende Minimax con poda α-β y profundización iterativa: busca a profundidad 1, luego 2, hasta llegar a `max_depth` o agotar el tiempo. Siempre retorna el mejor movimiento del último nivel completo, garantizando el límite de 2 segundos. Profundidad máxima configurada en 6. Es el algoritmo principal del agente en dificultad `hard`.

### Minimax puro (`Minimax`)

Implementación sin poda, incluida exclusivamente para la comparación en el benchmark (explosión combinatoria). No se usa en partidas reales. Tiene un límite de tiempo configurable para evitar que bloquee el análisis en profundidades altas.

### Expectimax (`Expectimax`)

Variante de Minimax donde los nodos del oponente son **nodos de azar**: en lugar de minimizar, calculan el promedio equiprobable de todos los movimientos posibles. Modela un oponente subóptimo o con comportamiento impredecible. Disponible como dificultad `expectimax`.

### MCTS con UCT (`MCTS`)

Monte Carlo Tree Search guiado por la fórmula UCT:

```
Score = (wins / visits) + C × sqrt(ln(ParentVisits) / NodeVisits)
```

Con `C = √2` por defecto. El árbol crece iteración a iteración; cada iteración ejecuta selección, expansión, simulación aleatoria hasta el final y retropropagación. El presupuesto por defecto es 600 iteraciones, limitadas al tiempo disponible. Disponible como dificultad `mcts`.

---

## Heurística por Fases (`evaluate`)

La función `evaluate(board, player)` devuelve un valor en el rango `[-100, 100]` combinando cuatro métricas normalizadas:

| Métrica | Qué mide |
|---------|----------|
| **Movilidad** | Diferencia relativa de movimientos legales disponibles |
| **Control de esquinas** | Diferencia relativa de esquinas ocupadas |
| **Puntuación posicional** | Tabla de pesos fijos (esquinas = 100, X-squares = −50) |
| **Estabilidad** | Fichas ancladas desde esquinas capturadas |
| **Conteo de fichas** | Solo en el cierre — fichas propias vs oponente |

Los pesos varían según la **fase del juego**, determinada por el total de fichas en el tablero:

| Fase | Piezas en tablero | Estrategia |
|------|-------------------|------------|
| Apertura | < 20 | Movilidad 50 % · Esquinas 30 % · Posición 20 % |
| Medio juego | 20–49 | Esquinas 40 % · Movilidad 30 % · Estabilidad 15 % · Posición 15 % |
| Cierre | ≥ 50 | Conteo 50 % · Estabilidad 30 % · Esquinas 20 % |

---

## Niveles de Dificultad del Agente

| Nivel | Algoritmo | Profundidad / Iteraciones |
|-------|-----------|--------------------------|
| `easy` | Alpha-Beta | profundidad 2 |
| `medium` | Alpha-Beta | profundidad 4 |
| `hard` | Alpha-Beta | profundidad 6 |
| `mcts` | MCTS | 600 iteraciones |
| `expectimax` | Expectimax | profundidad 4 |

Todos los niveles respetan el **límite estricto de 2 segundos por jugada**.

---

## Torneo IA vs IA

El módulo `ai/tournament.py` enfrenta al Agente A (Alpha-Beta, `hard`) contra el Agente B (MCTS) en 20 partidas. Los colores se alternan cada partida para neutralizar la ventaja de las negras. Soporta ejecución **paralela** con `ProcessPoolExecutor` para reducir el tiempo total del torneo.

Métricas reportadas:
- Victorias, derrotas y empates por agente
- Longitud promedio de partida (número de movimientos)
- Distribución de puntuaciones finales

---

## Análisis de Rendimiento

El módulo `analysis/` mide la **explosión combinatoria** comparando Minimax puro vs Alpha-Beta a profundidades fijas 1–6, sobre 3 posiciones de medio juego generadas con semilla fija (`RANDOM_SEED = 42`).

### Métricas calculadas (`analysis/metrics.py`)

**Factor de Ramificación Efectivo (EBF):** resuelve `b + b² + ... + bᵈ = nodos` numéricamente (método de Newton).

**Eficiencia de poda:** porcentaje de nodos que Alpha-Beta evita explorar respecto a Minimax.

**Speedup:** cuántas veces más rápido es Alpha-Beta en tiempo de pared.

### Gráficas generadas (`analysis/graphs/`)

| Archivo | Contenido |
|---------|-----------|
| `nodes_vs_depth.png` | Nodos explorados por profundidad — escala exponencial visible |
| `time_vs_depth.png` | Tiempo de ejecución (ms) por profundidad |
| `ebf_comparison.png` | EBF comparado por profundidad (barras agrupadas) |
| `pruning_efficiency.png` | Porcentaje de nodos podados por Alpha-Beta por profundidad |

---

## Interfaz Gráfica

Implementada en Pygame a **60 FPS**. Incluye:

- Tablero con tablero a colores alternados y piezas con sombra y gradiente
- Indicadores de movimientos legales disponibles (pistas en amarillo semitransparente)
- Panel lateral con: marcador, turno actual, indicadores de IA (nodos explorados, tiempo de jugada, valoración del tablero)
- Botón para volver al menú en cualquier momento
- Escena de torneo con barra de progreso en vivo y tarjetas de resultado
- Escena de benchmark con progreso en tiempo real e integración directa con las gráficas

---

## Video de Demostración

<a href="https://www.youtube.com/watch?v=lOs5BeRPy_g">
  <img src="https://img.youtube.com/vi/lOs5BeRPy_g/maxresdefault.jpg" width="480" alt="Video de demostración — Othello IA CC3085">
</a>

El video de 3 minutos muestra:
1. Modo **Humano vs Humano** — turno alternado, pistas y volteo de fichas
2. Modo **Humano vs IA** — el agente responde dentro del límite de 2 s con indicadores visibles
3. Modo **IA vs IA** — partida completa Alpha-Beta vs MCTS
4. Pantalla de **Torneo** — progreso de las 20 partidas y resultados finales
5. Pantalla de **Benchmark** — gráficas generadas en vivo






---

*Fecha de presentación: Jueves 4 de junio de 2026*
