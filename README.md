# ***Proyecto No. 2 — Algoritmos de Búsqueda***

**Curso:** Inteligencia Artificial — CC3085, Sección 20  
**Universidad:** Universidad del Valle de Guatemala  

**Integrantes:**

- Javier Linares — 231135
- Luis Pedro Lira — 23669
- Cindy Gualim — 21226

---

### Descripción General

Este proyecto implementa y compara algoritmos de búsqueda para resolver laberintos generados de forma aleatoria. Se abordan tres problemas principales:

1. **Generación aleatoria de laberintos** mediante algoritmos de Árbol de Expansión Mínima (Prim y División Recursiva).
2. **Solución de un laberinto 60×80** con A* (heurística Manhattan), visualizando celdas exploradas y ruta encontrada.
3. **Benchmark comparativo** de BFS, DFS, Dijkstra y A* en K=25 laberintos aleatorios de tamaño 45×55.

---

### Estructura del Repositorio

```
/
│
├── Proyecto2.ipynb          # Notebook principal con toda la implementación
└── README.md                # Este archivo
```

---



### Librerías utilizadas

| Librería | Uso |
|----------|-----|
| `numpy` | Representación del laberinto como array 2D |
| `matplotlib` | Visualizaciones y animaciones |
| `pandas` | Tablas de resultados del benchmark |
| `heapq` | Cola de prioridad para Dijkstra y A* |
| `collections.deque` | Cola FIFO para BFS |
| `random`, `time` | Aleatoriedad y medición de tiempos |


---

### Representación del Laberinto

El laberinto se representa como un **array NumPy 2D** (`filas × columnas`) con valores enteros:

| Valor | Significado | Color de visualización |
|-------|-------------|----------------------|
| `0` | Pared | Negro |
| `1` | Camino libre | Blanco |
| `2` | Celda explorada | Azul claro (`#90CAF9`) |
| `3` | Ruta óptima | Amarillo (`#FFD600`) |
| `4` | Inicio | Verde (`#00E676`) |
| `5` | Fin | Rojo (`#FF1744`) |

### Parámetros Globales

| Constante | Valor | Uso |
|-----------|-------|-----|
| `FILAS_P1, COLS_P1` | 31 × 41 | Demo de generación |
| `FILAS_P2, COLS_P2` | 61 × 81 | Problema 2 (60×80 → impar) |
| `FILAS_P3, COLS_P3` | 45 × 55 | Benchmark |
| `K_SIMULACIONES` | 25 | Número de escenarios |
| Inicio | `(1, 1)` | Punto de entrada fijo |
| Fin | `(filas-2, cols-2)` | Punto de salida fijo |

---

### Problema 1 — Generación de Laberintos

Se implementaron dos algoritmos de spanning tree que generan **laberintos perfectos** (existe exactamente un camino entre cualquier par de celdas).

### ***Algoritmo de Prim (`generar_prim`)***

Crece un Árbol de Expansión Mínima (MST) desde un punto inicial aleatorio.

**Proceso:**
1. Se parte de una celda inicial aleatoria en posición impar `(start_r, start_c)`.
2. Se mantiene una lista de paredes candidatas (celdas adyacentes no visitadas).
3. En cada iteración se elige una pared al azar; si el otro lado no fue visitado, se elimina la pared y se agrega la celda.
4. Se repite hasta que no quedan paredes candidatas.

**Características del laberinto resultante:**
- Patrón orgánico y radial
- Alta densidad de ramificaciones y callejones sin salida
- Pasillos cortos y curvos
- Alta complejidad visual

**Impacto en búsqueda:** Fuerza a BFS y DFS a explorar gran cantidad de nodos. A* aprovecha su heurística para descartar callejones eficientemente.

---

### ***Algoritmo de División Recursiva (`generar_division_recursiva`)***

Parte de un espacio completamente abierto y lo subdivide recursivamente con paredes que tienen una sola apertura.

**Proceso:**
1. Se inicializa la cuadrícula como espacio abierto (valor `1`) con bordes de pared (valor `0`).
2. `dividir(rmin, rmax, cmin, cmax)` decide si cortar horizontal o verticalmente según el aspecto de la región.
3. Se dibuja la pared con un hueco aleatorio en posición impar.
4. Se llama recursivamente a ambas sub-regiones hasta que no quedan regiones divisibles.

**Características del laberinto resultante:**
- Diseño rectilíneo y geométrico (tipo bloques)
- Pocas ramificaciones
- Pasillos largos y rectos
- Complejidad visual media

**Impacto en búsqueda:** Los corredores largos favorecen a DFS, que puede recorrer un corredor directamente hacia la meta.

---

### ***Comparación Estructural: Prim vs División Recursiva***

| Característica | Prim | División Recursiva |
|----------------|------|--------------------|
| Patrón visual | Orgánico y radial | Rectilíneo y geométrico |
| Ramificaciones | Muchas | Pocas |
| Callejones sin salida | Alta densidad | Baja densidad |
| Longitud de pasillos | Cortos y curvos | Largos y rectos |
| Complejidad visual | Alta | Media |
| Algoritmo favorecido | A* | DFS |

---

### Problema 2 — Solución de un Laberinto Aleatorio

Se generaron dos laberintos de tamaño **61×81** (uno Prim, uno División Recursiva) y se resolvieron con **A\***.

### ***Función: `resolver_astar`***

- **Estructura:** `heapq` (cola de prioridad), clave = `f(n) = g(n) + h(n)`
- **Heurística:** Distancia Manhattan `h(n) = |fila_n − fila_fin| + |col_n − col_fin|`
- **Admisibilidad:** La distancia Manhattan nunca sobreestima en grids 4-conectados → A* garantiza optimalidad
- **Salida:** `(camino, nodos_explorados, tiempo_segundos)`

### ***Resultados Problema 2***

| Laberinto | Longitud camino | Nodos explorados | Tiempo (s)* |
|-----------|----------------|-----------------|-------------|
| Prim (61×81) | 153 pasos | 423 | 0.2804 |
| División Recursiva (61×81) | 449 pasos | 2,143 | 2.0335 |

> *Tiempos incluyen animación; no son representativos del costo algorítmico puro.

**Observaciones:**
- División Recursiva exploró 5.1× más nodos que Prim en esta ejecución.
- La diferencia en longitud de camino es específica a cada ejecución aleatoria, no una regla general.

---

### Problema 3 — Comparación de Algoritmos de Búsqueda

### ***Algoritmos Implementados***

#### ***BFS — Breadth-First Search (`resolver_bfs`)***
- **Estructura:** `deque` (cola FIFO)
- **Garantía:** Camino óptimo en grafos con costo uniforme
- **Complejidad:** O(V + E) tiempo y espacio
- **Detalle:** Marca visitados al agregar a la cola (no al expandir), evitando duplicados

#### ***DFS — Depth-First Search (`resolver_dfs`)***
- **Estructura:** Lista como pila (LIFO)
- **Garantía:** Ninguna sobre optimalidad en grafos generales
- **Complejidad:** O(V + E) tiempo, O(profundidad) espacio
- **Nota:** En laberintos perfectos (árbol), existe un único camino, por lo que la longitud coincide con los demás algoritmos

#### ***Dijkstra / Cost Uniform Search (`resolver_dijkstra`)***
- **Estructura:** `heapq` (cola de prioridad mínima), clave = costo acumulado `g(n)`
- **Garantía:** Camino óptimo en grafos con costos no negativos
- **Complejidad:** O((V + E) log V)
- **Equivalencia:** En grids de costo uniforme (peso=1), explora los mismos nodos que BFS pero con overhead del heap

#### ***A\* con Heurística Manhattan (`resolver_astar`)***
- **Estructura:** `heapq`, clave = `f(n) = g(n) + h(n)`
- **Heurística:** Distancia Manhattan (admisible en grids 4-conectados)
- **Garantía:** Camino óptimo con heurística admisible
- **Complejidad:** O(b^d) con factor de ramificación efectivo reducido por h

### ***Selección de Puntos A y B (`puntos_aleatorios`)***

- Selecciona celdas libres (valor = 1) del array NumPy
- Filtra pares con distancia Manhattan **≥ 10 unidades**
- Hasta 2,000 intentos antes de usar fallback

---

### Resultados del Benchmark (K=25, grid 45×55)

### ***Escenarios Representativos***

**Escenario 1 — División Recursiva | A=(25,39), B=(9,45)**

| Algoritmo | Longitud | Nodos Explorados | Tiempo (s) | Rank |
|-----------|----------|-----------------|------------|------|
| **A\*** | 103 | 431 | 0.00135 | 1° |
| DFS | 103 | 603 | 0.00266 | 2° |
| BFS | 103 | 823 | 0.00301 | 3° |
| Dijkstra | 103 | 823 | 0.00308 | 4° |

**Escenario 9 — División Recursiva | A=(13,49), B=(5,1)**

| Algoritmo | Longitud | Nodos Explorados | Tiempo (s) | Rank |
|-----------|----------|-----------------|------------|------|
| **A\*** | 93 | 351 | 0.00110 | 1° |
| BFS | 93 | 812 | 0.00179 | 2° |
| Dijkstra | 93 | 812 | 0.00214 | 3° |
| DFS | 93 | 957 | 0.00213 | 4° |

**Escenario 25 — División Recursiva | A=(34,43), B=(33,24)**

| Algoritmo | Longitud | Nodos Explorados | Tiempo (s) | Rank |
|-----------|----------|-----------------|------------|------|
| **A\*** | 29 | 69 | 0.00022 | 1° |
| DFS | 29 | 90 | 0.00021 | 2° |
| BFS | 29 | 114 | 0.00026 | 3° |
| Dijkstra | 29 | 114 | 0.00031 | 4° |

---

### ***Tabla Resumen Global — Ranking Promedio (K=25)***

| Pos. | Algoritmo | Rank Prom. | Nodos Prom. | Tiempo Prom. (s) | Long. Prom. | Veces #1 | Veces Último |
|------|-----------|------------|-------------|-----------------|-------------|----------|--------------|
| 1 | **A\*** | 1.40 | 417.6 | 0.00130 | 96.1 | 15 | 0 |
| 2 | BFS | 2.52 | 702.1 | 0.00164 | 96.1 | 0 | 0 |
| 3 | DFS | 2.56 | 701.4 | 0.00166 | 96.1 | 10 | 12 |
| 4 | Dijkstra | 3.52 | 702.1 | 0.00191 | 96.1 | 0 | 13 |

**Datos clave:**
- A\* fue el mejor en **15/25 escenarios (60%)**
- DFS fue el mejor en **10/25 escenarios (40%)**, pero también el último en 12
- BFS y Dijkstra nunca fueron el mejor algoritmo
- Dijkstra fue el último en 13 de 25 escenarios
- A\* exploró en promedio **40.5% menos nodos** que BFS
- Todos los algoritmos encontraron rutas de **la misma longitud** (96.1 pasos promedio)

---

### **Análisis por Tipo de Laberinto**

| Tipo | n | BFS nodos prom. | DFS nodos prom. | Dijkstra nodos prom. | A\* nodos prom. | Reducción A\* vs BFS |
|------|---|-----------------|-----------------|---------------------|----------------|----------------------|
| Prim | 10 | 649.0 | 897.2 | 649.0 | 281.2 | **56.7%** |
| Div. Recursiva | 15 | 737.5 | 570.8 | 737.5 | 508.5 | **31.0%** |

### **Victorias por Tipo de Laberinto**

| Algoritmo | Gana en Prim | Gana en Div. Recursiva | Total |
|-----------|-------------|----------------------|-------|
| A\* | 9/10 (90%) | 6/15 (40%) | 15/25 (60%) |
| DFS | 1/10 (10%) | 9/15 (60%) | 10/25 (40%) |
| BFS | 0/10 | 0/15 | 0/25 |
| Dijkstra | 0/10 | 0/15 | 0/25 |

---

## ***Conclusiones***

**¿Qué algoritmo fue más rápido en promedio?**  
A\* fue el más eficiente en tiempo y el que menos nodos exploró en la mayoría de escenarios (15/25). La heurística Manhattan le permite priorizar la expansión hacia la meta, descartando regiones sin visitarlas. Su ventaja fue especialmente pronunciada en laberintos Prim, donde la alta ramificación permite que la heurística descarte callejones eficientemente.

**¿Cuál exploró menos nodos?**  
A\* exploró el menor número de nodos en promedio (417.6). Reducción del 56.7% sobre BFS en laberintos Prim y 31.0% en División Recursiva. DFS fue competitivo en División Recursiva (9/15), pero muy irregular: en Prim puede explorar hasta 2.7× más nodos que A\*.

**¿Cuál encontró mejores rutas?**  
Los cuatro algoritmos encontraron rutas de **la misma longitud** en todos los escenarios (promedio 96.1 pasos). Ambos generadores producen laberintos perfectos con un único camino entre cualquier par de celdas, por lo que la longitud de ruta no es criterio diferenciador.

**¿Cómo afecta la estructura del laberinto?**  
- **Prim** favorece a A\*: alta ramificación permite a la heurística descartar ramas irrelevantes (56.7% menos nodos que BFS, victorias en 9/10 escenarios Prim).  
- **División Recursiva** favorece a DFS: los corredores largos y únicos permiten que DFS alcance la meta explorando una fracción del laberinto. A\* pierde efectividad porque las paredes fuerzan rodeos que la heurística Manhattan no anticipa.

**¿En qué casos falla DFS?**  
DFS es el algoritmo de mayor varianza. Falla en laberintos Prim: puede explorar hasta 1,104 nodos frente a los 104 de A\* en el mismo escenario. Fue el peor (rank 4) en 12/25 escenarios globales.

**¿Cuándo A\* supera claramente a los demás?**  
En laberintos Prim y cuando la distancia Manhattan entre inicio y fin es grande. La alta ramificación crea muchas ramas que la heurística descarta eficientemente (reducción 2×–5× respecto a BFS). En División Recursiva la ventaja baja a ~1.4× y DFS pasa a ser dominante.

**Observación BFS vs Dijkstra:**  
En grids de costo uniforme (peso=1), ambos exploran exactamente los mismos nodos. Dijkstra es consistentemente más lento (0.00191s vs 0.00164s) por el overhead del heap. Dijkstra supera a BFS únicamente cuando los costos de movimiento varían entre celdas.

---


*Fecha de entrega: lunes 11 de mayo de 2026*
