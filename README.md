# Laboratorio 02
23 . febrero . 2026

En este laboratorio vamos a implementar varios métodos de aprendizaje supervisado y aplicarlos a conjuntos de datos.

**Curso:** Inteligencia Artificial  
**Sección.:** 20


Integrantes:
- Cindy Gualim – 21226
- Javier Linares – 231135
- Luis Pedro Lira – 23669



### 1. 
Para los siguientes datos: Construir el clasificador bayesiano óptimo. Indicar la regla de clasificación. Hallar el error de este clasificador.

|       | X = 1 | X = 2 | X = 3 | X = 4 |
|-------|-------|-------|-------|-------|
| Y = 0 | 0.09  | 0.16  | 0.17  | 0.05  |
| Y = 1 | 0.15  | 0.07  | 0.10  | 0.21  |


El objetivo es construir un clasificador que minimice la probabilidad de error. Según la teoría de decisión de Bayes, esto se logra seleccionando la clase con la mayor probabilidad posterior:
$$\hat{y} = \arg \max_{y} P(Y=y | X=x)$$

En términos de implementación en Python (`pandas` y `numpy`), seguimos estos pasos:

1.  **Carga de Datos:** Representamos la tabla en un `DataFrame`.
2.  **Regla de Decisión:** Usamos la función `.idxmax(axis=0)`. Dado que $P(Y|X) \propto P(X, Y)$, elegir el valor máximo de la probabilidad conjunta por cada columna $X$ nos da la predicción óptima.
3.  **Cálculo del Error:** El error de Bayes es la suma de las probabilidades de los eventos que el clasificador **no** eligió (las probabilidades mínimas por columna).


### Regla de Clasificación
Tras ejecutar el algoritmo, la regla de decisión óptima queda definida de la siguiente manera:

| Valor de $X$ | Clase Predicha ($\hat{Y}$) | Probabilidad Asociada |
| :--- | :---: | :--- |
| **$X = 1$** | $Y = 1$ | $0.15$ |
| **$X = 2$** | $Y = 0$ | $0.16$ |
| **$X = 3$** | $Y = 0$ | $0.17$ |
| **$X = 4$** | $Y = 1$ | $0.21$ |

### Análisis del Error
El error total del clasificador se calcula sumando las probabilidades de las clases descartadas:

* **Error en $X=1$**: $0.09$
* **Error en $X=2$**: $0.07$
* **Error en $X=3$**: $0.10$
* **Error en $X=4$**: $0.05$

**Error Total del Clasificador:** $$Error = 0.09 + 0.07 + 0.10 + 0.05 = \mathbf{0.31}$$


## Conclusión
El clasificador bayesiano óptimo ha sido implementado correctamente. El error del **31%** representa la cota inferior de error posible para este conjunto de datos (Error de Bayes); ningún otro clasificador puede obtener un desempeño superior basándose únicamente en esta distribución de probabilidad.

---


### 3.

La siguiente tabla de datos muestra información de la decisión de jugar o no jugar golf, en función de varios factores como el tipo de clima, temperatura, humedad, o si hay viento, para 14 observaciones diferentes.

| Obs | Outlook   | Temperature | Humidity | Windy | Play Golf? |
|-----|-----------|------------|----------|-------|------------|
| 0   | Rainy     | Hot        | High     | False | No         |
| 1   | Rainy     | Hot        | High     | True  | No         |
| 2   | Overcast  | Hot        | High     | False | Yes        |
| 3   | Sunny     | Mild       | High     | False | Yes        |
| 4   | Sunny     | Cool       | Normal   | False | Yes        |
| 5   | Sunny     | Cool       | Normal   | True  | No         |
| 6   | Overcast  | Cool       | Normal   | True  | Yes        |
| 7   | Rainy     | Mild       | High     | False | No         |
| 8   | Rainy     | Cool       | Normal   | False | Yes        |
| 9   | Sunny     | Mild       | Normal   | False | Yes        |
| 10  | Rainy     | Mild       | Normal   | True  | Yes        |
| 11  | Overcast  | Mild       | High     | True  | Yes        |
| 12  | Overcast  | Hot        | Normal   | False | Yes        |
| 13  | Sunny     | Mild       | High     | True  | No         |

Las variables son:

- $X_1$ = Outlook  
- $X_2$ = Temperature  
- $X_3$ = Humidity  
- $X_4$ = Windy  

Con base en la evidencia de la tabla, construya **dos** de los siguientes clasificadores:

- (a) KNN  
- (b) Naive Bayes  
- (c) Regresión logística  

para determinar si se debe o no jugar golf en los siguientes casos:

- $x = (\text{Rainy}, \text{Hot}, \text{High}, \text{False})$
- $x = (\text{Sunny}, \text{Hot}, \text{Normal}, \text{False})$

---

Compare el desempeño de sus dos clasificadores e indique con cuál se obtienen mejores resultados.  
Utilice métricas como:

- Accuracy  
- Precision  
- Recall  
- $F_1$ Score  
- ROC AUC  

para validar su argumento.

---

Responda la siguiente pregunta:

**¿Cómo construir un clasificador bueno, con tan pocos datos?**


## Análisis de Clasificadores: Caso "Play Golf"

Comparativa de desempeño entre **Categorical Naïve Bayes** y **Regresión Logística** sobre un dataset de 14 observaciones.

## Justificación de Modelos
* **Naïve Bayes:** Elegido por su alta eficiencia en datos **categóricos** y su robustez ante muestras pequeñas al calcular probabilidades condicionales independientes.
* **Regresión Logística:** Seleccionada por su capacidad de devolver **probabilidades continuas**, facilitando la evaluación mediante la métrica ROC AUC.

## Comparativa de Métricas

| Métrica | Naïve Bayes | Regresión Logística |
| :--- | :---: | :---: |
| **Accuracy** | 0.8571 | 0.8571 |
| **Precision** | **0.8889** | 0.8182 |
| **Recall** | 0.8889 | **1.0000** |
| **F1 Score** | 0.8889 | **0.9000** |
| **ROC AUC** | 0.8889 | **0.9778** |

### Resultados de Predicción
Ambos modelos coinciden en los casos de prueba:
1.  `(Rainy, Hot, High, False)` → **No Jugar**
2.  `(Sunny, Hot, Normal, False)` → **Sí Jugar**



## Conclusiones
La **Regresión Logística** resulta ser el modelo superior para este caso, ya que alcanza un **ROC AUC de 0.9778** y un **Recall de 1.0**, demostrando una capacidad casi perfecta para separar las clases y no omitir ningún caso positivo ("Yes").

## ¿Cómo clasificar con pocos datos?
Para construir modelos confiables con muestras mínimas (N=14):
1.  **Simplicidad:** Usar modelos con "fuerte sesgo" (como los probados) que evitan el sobreajuste (overfitting).
2.  **Codificación:** Transformar variables categóricas correctamente (One-Hot Encoding).
3.  **Métricas Robustas:** No fiarse solo del Accuracy; priorizar F1-Score y ROC AUC para entender la capacidad real de distinción del modelo.
