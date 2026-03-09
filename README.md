# Inteligencia Artificial - Lab 03


## ¿Cómo se resolvió? 

### Ejercicio 1: Clasificación de Dígitos
- **Preprocesamiento:** Se normalizaron los valores de los píxeles de las imágenes dividiendo entre 16 para asegurar valores en el rango [0,1]. Además, las etiquetas fueron transformadas usando *One-Hot Encoding*.
- **Arquitectura:** Se diseñó una red con dos capas ocultas (64 y 32 neuronas) usando la función de activación ReLU. La capa de salida utilizó la función Softmax con 10 neuronas para las 10 posibles clases.
- **Entrenamiento:** Se utilizó la función de pérdida `categorical_crossentropy` junto con el optimizador Adam. 
- **Resultados:** Se graficó una matriz de confusión para observar falsos positivos/negativos comunes y se extrajeron métricas de *Accuracy*. Se visualizó directamente qué imágenes fueron bien interpretadas y cuáles confundieron al modelo.

### Ejercicio 2: Regresión de Precios
- **Preprocesamiento:** Para lidiar con la heterogeneidad de los datos demográficos y geográficos, fue estricto el uso de `StandardScaler` ajustado en el set de entrenamiento.
- **Arquitectura:** Se requirió mayor profundidad para el modelado no lineal, usando 3 capas ocultas (64, 32, 16 neuronas, todas con ReLU) y una única neurona de salida con activación lineal (ya que predecimos un valor continuo).
- **Entrenamiento:** Se evaluó con Error Cuadrático Medio (MSE) como función de pérdida, utilizando Adam como optimizador.
- **Resultados:** Las métricas de MSE, MAE y el puntaje $R^2$ mostraron la capacidad del modelo para generalizar. Esto fue respaldado visualmente con un diagrama de dispersión (Scatter Plot) comparando los precios reales vs las predicciones. Finalmente, se realizó una inferencia realística sobre 3 datos sintéticos (simulando casas nuevas).