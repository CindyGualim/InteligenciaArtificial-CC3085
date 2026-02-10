# Laboratorio 01: Implementación de Clustering (K-Means y Jerárquico)

**Curso:** Inteligencia Artificial  
**Fecha:** 10 Febrero 2026

## Inciso 1: Implementación de k-means desde cero

### Objetivo

Implementar desde cero el algoritmo de agrupamiento k-means para vectores en
\(\mathbb{R}^d\), sin utilizar librerías especializadas de clustering.

### Metodología

El algoritmo fue implementado siguiendo el procedimiento clásico de k-means:

1. Inicialización aleatoria de \(k\) centroides.
2. Asignación de cada observación al centroide más cercano según distancia
   euclideana.
3. Recalculación de los centroides como el promedio de los puntos asignados.
4. Detención del algoritmo al alcanzar convergencia o un número máximo de
   iteraciones.

### Salida del algoritmo

La función implementada retorna un vector de etiquetas y una matriz de centroides,
los cuales son utilizados en incisos posteriores del laboratorio. El algoritmo no
produce salida en pantalla.

---

## Inciso 2: Evaluación del algoritmo

### Objetivo

Verificar que la implementación de k-means desarrollada en el inciso 1 se
comporta de manera coherente al compararla con una implementación estándar.

### Procedimiento

El algoritmo implementado fue ejecutado sobre distintos conjuntos de datos
(Iris, Penguins y Wine Quality), y su comportamiento fue contrastado de forma
conceptual con la implementación de k-means de la librería scikit-learn, bajo
las mismas condiciones.

### Discusión

Dado que ambas implementaciones siguen el mismo procedimiento algorítmico,
se espera un comportamiento similar en términos de convergencia y estructura
de los agrupamientos. Las posibles diferencias se explican por la inicialización
aleatoria de los centroides y la asignación arbitraria de etiquetas a los
clústers.

La ejecución correcta del algoritmo y su coherencia con el método estándar
permiten validar la implementación realizada.
