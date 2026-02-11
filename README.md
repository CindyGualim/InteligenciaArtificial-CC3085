# Laboratorio 01

**Curso:** Inteligencia Artificial  
**Sección.:** 20


Integrantes:
- Cindy Gualim – 21226
- Javier Linares – 231135
- Luis Pedro Lira – 23669


## Descripción
Este repositorio contiene la solución al Laboratorio 01. El objetivo principal es implementar desde cero el algoritmo K-Means y compararlo con soluciones de librería (`scikit-learn`), además de explorar el Clustering Jerárquico y aplicar estos métodos a diversos problemas (datasets reales, datos sintéticos y cuantización de color).

## Tecnologías Utilizadas
* **Python 3.x**
* **Jupyter Notebook**
* **Librerías:**
    * `NumPy`: Cálculos matemáticos y matriciales.
    * `Pandas`: Manipulación de datasets.
    * `Matplotlib` & `Seaborn`: Visualización de datos.
    * `Scikit-learn`: Algoritmos de clustering y datasets de prueba.
    * `SciPy`: Generación de dendrogramas.
    * `Pillow (PIL)`: Procesamiento de imágenes.
    * `OpenPyXL`: Lectura de archivos Excel.

## Estructura del Laboratorio

1.  **Implementación Manual de K-Means:**
    * Desarrollo del algoritmo sin librerías de clustering.
    * Input: Matriz $n \times d$ y número de clusters $k$.
    * Output: Etiquetas y centroides.

2.  **Evaluación con Datasets:**
    * Pruebas con **Iris**, **Penguins** y **Wine Quality**.
    * Comparación de resultados: Implementación Manual vs. `scikit-learn`.

3.  **Agrupamiento Jerárquico:**
    * Análisis del dataset `countries_binary.xlsx`.
    * Comparación de métodos (Simple, Completo, Promedio, Ward) y métricas (Euclidiana, Hamming).

4.  **Análisis Comparativo:**
    * Contraste entre K-Means y Jerárquico para datos binarios.

5.  **Datos Sintéticos (Problemas No Convexos):**
    * Prueba con `make_moons`.
    * Análisis de por qué K-Means falla en formas no lineales y ventajas del Enlace Simple.

6.  **Cuantización de Color:**
    * Aplicación de K-Means para reducir los colores de imágenes RGB.

## Instrucciones de Ejecución

1.  **Instalar dependencias:**
    ```bash
    pip install numpy pandas matplotlib seaborn scikit-learn scipy pillow openpyxl
    ```

2.  **Archivos necesarios:**
    * `countries_binary.xlsx` (Debe estar en la misma carpeta).
    * Imágenes para el inciso 6 (Debe estar en la misma carpeta).

3.  **Ejecutar:**
    Abrir `Lab01_Solucion.ipynb` y ejecutar todas las celdas.

##  Ejecución Recomendada: Google Colab

Para evitar problemas de instalación de librerías locales o conflictos de versiones, se recomienda fuertemente ejecutar este laboratorio en **Google Colab**.

**Ventajas:**
* Todas las librerías necesarias (`scikit-learn`, `pandas`, `numpy`, `seaborn`) vienen preinstaladas.
* No requiere configuración del entorno local.

**Instrucciones para Colab:**
1.  Sube el archivo `Lab01_Solucion.ipynb` a [Google Colab](https://colab.research.google.com/).
2.  **Importante:** Antes de ejecutar el código, abre el panel de archivos (icono de carpeta en la barra lateral izquierda) y sube:
    * El archivo de datos `countries_binary.xlsx`.
    * Las imágenes para el inciso 6 (si tienes imágenes propias).
3.  Ejecuta todas las celdas (Menú *Entorno de ejecución* > *Ejecutar todas*).

---
