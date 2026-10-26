# Informe de fase 4 — División temporal y modelo baseline

Fecha: 18 de octubre de 2026. Resultado de una ejecución real, con los valores completos guardados en baseline_resultados.json. Clase positiva: is_canceled=1. Separador decimal de las tablas generadas: punto; miles: coma. Se completa exclusivamente la fase 4 solicitada: división y regresión logística, sin optimización ni modelos avanzados.

## 1. Revisión de preparación

Se revisaron los informes de fases 1–3, preparacion.ipynb y todos los módulos existentes de src. Se conservan 119.390 registros, sus 31.994 duplicados adicionales y los 14 predictores seleccionados. No se modifican original, CSV preparado, reglas de limpieza ni supuestos de disponibilidad inicial.

X contiene seis numéricas (lead_time, total_nights, adults, children, babies, children_missing) y ocho categóricas (hotel, arrival_date_month, meal, country, market_segment, distribution_channel, reserved_room_type, customer_type). is_canceled es únicamente y. Los diez metadatos, estados finales y las doce variables inciertas excluidas en fase 3 no llegan a X ni a la salida del ColumnTransformer. Se construyó un pipeline nuevo sin ajustar; no se reutilizaron transformadores entrenados sobre todo el archivo.

Se contrastaron las huellas SHA-256 de original y preparado con fase 3, y se verificó la integridad posterior. No se ha regenerado otro dataset de características por partición: el manifiesto guarda solo ID técnico y asignación.

## 2. Cortes y madurez temporal

Se mantienen los cortes propuestos, fijados antes de entrenar:

- Entrenamiento: proxy de creación < 2016-07-01 y madurez < 2016-07-01.
- Validación: 2016-07-01 <= proxy < 2017-01-01 y madurez < 2017-01-01.
- Prueba reservada: proxy >= 2017-01-01. No se evalúa aquí.
- Dos grupos aparte: reservas del periodo de entrenamiento/validación cuya etiqueta no había madurado al corte correspondiente. Permanecen en el dataset y en el manifiesto, sin desplazarlas a un periodo posterior.

El proxy es llegada prevista menos lead_time. La cota de madurez es max(llegada + noches, fecha_estado_final) + 1 día, con desigualdad estricta respecto al corte. La fecha final solo interviene en elegibilidad retrospectiva de etiquetas, nunca como predictor. Es una aproximación conservadora a disponibilidad, no un registro histórico demostrado; puede retrasar una cancelación ya conocida antes de la salida prevista.

| Partición | Reservas | No canceladas | Canceladas | Tasa de cancelación |
|---|---:|---:|---:|---:|
| entrenamiento | 48,428 | 31,088 | 17,340 | 35.81% |
| validacion | 14,011 | 10,344 | 3,667 | 26.17% |
| prueba_reservada | 26,565 | 18,163 | 8,402 | 31.63% |
| no_madura_entrenamiento | 17,825 | 9,348 | 8,477 | 47.56% |
| no_madura_validacion | 12,561 | 6,223 | 6,338 | 50.46% |

| Partición | Rango observado del proxy | Rango observado de llegada | Máxima cota de madurez |
|---|---|---|---|
| entrenamiento | 2013-06-24 a 2016-06-29 | 2015-07-01 a 2016-06-29 | 2016-06-30 |
| validacion | 2016-07-01 a 2016-12-30 | 2016-07-01 a 2016-12-30 | 2016-12-31 |
| prueba_reservada | 2017-01-01 a 2017-08-31 | 2017-01-01 a 2017-08-31 | 2017-09-15 |
| no_madura_entrenamiento | 2015-02-20 a 2016-06-30 | 2016-06-14 a 2017-08-29 | 2017-08-31 |
| no_madura_validacion | 2016-07-01 a 2016-12-31 | 2016-12-13 a 2017-08-31 | 2017-09-12 |

Los límites teóricos y los rangos observados son distintos: por ejemplo, entrenamiento termina el 29/06/2016 en proxy/llegada por la restricción de madurez. La tabla evita describir junio como un mes completo.

Todas las filas se asignan exactamente a un grupo; no hay cruces de filas ni de huellas de duplicados. Entrenamiento incluye julio de 2015–junio de 2016 y los doce meses están representados en ambos hoteles, con junio parcial. El proxy se extiende desde junio de 2013, pero la extracción solo contiene llegadas desde julio de 2015: no hay cobertura completa de todas las altas desde 2013.

### Limitación detectada antes del ajuste y tratamiento

Las 30.386 reservas no elegibles por madurez no son una pérdida de datos ni una muestra aleatoria. Se hizo explícita su asignación en vez de eliminarlas o incorporarlas al entrenamiento con información futura. La validación resultante favorece menor antelación/llegadas cercanas, y sus métricas no describen todas las reservas creadas durante el semestre. Las tasas de los grupos apartados reflejan esa diferencia de composición. Esta solución mantiene la cronología propuesta, pero no resuelve la censura ni hace representativo el subconjunto.

No se modificaron cortes tras observar métricas. En prueba se describieron clases y fechas únicamente como auditoría requerida. Su cota de madurez máxima es septiembre de 2017: antes de la futura evaluación habrá que justificar seguimiento suficiente y fecha de extracción. No se ha supuesto una fecha exacta de creación ni una disponibilidad operacional certificada.

## 3. Pipeline ajustado exclusivamente con entrenamiento

Pipeline: ColumnTransformer de fase 3 seguido de LogisticRegression.

- Numéricas: SimpleImputer(strategy='median', keep_empty_features=True) y StandardScaler.
- Categóricas: categoría constante Desconocido y OneHotEncoder(handle_unknown='ignore').
- Resto de columnas: drop por lista explícita. La etiqueta/metadatos quedan separados antes de fit.
- Regresión logística: C=1.0, solver=lbfgs, class_weight=None, random_state=42, tol=0.0001, max_iter=2000. Umbral fijado a 0.5.

max_iter es un límite numérico fijado antes de evaluar; no se buscaron hiperparámetros. El modelo convergió en 131 iteraciones, sin advertencias de fit. La representación resultante tiene 191 columnas. Las medianas, medias y categorías aprendidas se verificaron contra las 48,428 filas de entrenamiento y no cambiaron al transformar validación ni prueba. No hay columnas numéricas completamente ausentes en entrenamiento.

La prueba se transformó solo para comprobar que se usan parámetros aprendidos de entrenamiento y que la salida es finita. No se ejecutó predict ni predict_proba del clasificador sobre prueba, ni se calcularon métricas allí. Los desconocidos se toleran por la regla establecida en fase 3, sin aprender categorías de validación/prueba.

La logística se elige por sencillez, reproducibilidad y carácter de primera referencia de clasificación probabilística. Impone linealidad/aditividad en log-odds y no captura automáticamente todas las interacciones. No se presupone calibración de probabilidades.

## 4. Comparación en validación

El trivial es DummyClassifier(strategy='most_frequent'), entrenado solo con y_train: siempre predice clase 0. Usa una entrada constante porque ignora los predictores. No se eligió su clase a partir de validación.

| Clasificador | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| mayoritario | 0.738277 | 0.000000 | 0.000000 | 0.000000 | 0.500000 |
| regresion_logistica | 0.744344 | 0.533597 | 0.184074 | 0.273723 | 0.700440 |

Precision/F1 sin positivos predichos del trivial se consignan como cero mediante zero_division=0; precision no se puede estimar entre alertas inexistentes. Su puntuación constante no discrimina y da ROC-AUC 0.5. El AUC de la logística usa probabilidad, no etiqueta binaria.

La logística mejora accuracy en 0.6067 puntos porcentuales; detecta algunas cancelaciones frente a ninguna del trivial y tiene mayor AUC. La mejora de accuracy es pequeña y no basta para declarar que el sistema sea bueno o útil. El recall 18.41% indica una detección limitada al umbral fijado.

## 5. Matrices de confusión e interpretación de errores

Filas: realidad [no cancelación, cancelación]. Columnas: predicción [no cancelación, cancelación].

Trivial:

| Real / predicción | No cancelación | Cancelación |
|---|---:|---:|
| No cancelación | 10,344 | 0 |
| Cancelación | 3,667 | 0 |

Regresión logística (0.5):

| Real / predicción | No cancelación | Cancelación |
|---|---:|---:|
| No cancelación | 9,754 | 590 |
| Cancelación | 2,992 | 675 |

Se generan 1,265 alertas: 675 corresponden a cancelaciones y 590 son falsas alarmas. Quedan 2,992 cancelaciones sin detectar (81.59% del total cancelado elegible). Los falsos positivos pueden consumir seguimiento innecesario; los falsos negativos dejan riesgo sin anticipar para la planificación. No se atribuyen importes económicos sin conocer costes y actuaciones.

Precision 53.36% describe acierto entre alertas; recall 18.41%, cobertura de cancelaciones. El umbral 0.5 no es una decisión óptima de negocio demostrada. No se ensayaron otros umbrales, reponderaciones o remuestreos en esta fase. F1 no incorpora costes; ROC-AUC mide ordenación, no calibración, causalidad o rentabilidad. Las gráficas de matrices y ROC son únicamente de validación.

## 6. Desbalance y limitaciones

La clase mayoritaria es no cancelación: el trivial ya alcanza 73.83% en validación. El entrenamiento tiene 35.81% de cancelación frente a 26.17% en validación; precisión y accuracy dependen de esa composición. La logística sin ponderación y a umbral 0.5 puede favorecer la clase mayoritaria. Este resultado no demuestra que ponderar o cambiar el umbral vaya a mejorar la utilidad; deberá investigarse con autorización, sin recurrir a prueba.

Los duplicados siguen pudiendo sobreponderar patrones, aunque no crucen particiones. Las huellas incluyen las columnas finales y no identifican una reserva real: no descartan duplicados parciales, relaciones entre clientes/grupos ni reservas distintas con iguales predictores. No se construyen intervalos de confianza suponiendo independencia sin justificarla.

Los 14 predictores conservan el supuesto de representar datos iniciales; no hay logs para verificar versiones. La partición es una simulación offline basada en proxy de creación y madurez aproximada, no una evaluación de producción certificada. La prueba queda reservada respecto a este baseline, pero el EDA ya exploró todo el archivo y esa exposición previa sigue siendo una limitación. Faltan requisitos académicos oficiales y documentación temporal. Se necesita validación externa/prospectiva para confirmar generalización y utilidad.

## 7. Archivos y comprobaciones

Creados: notebooks/baseline.ipynb; src/splitting.py; src/baseline.py; tests/test_baseline.py; reports/particiones_temporales.csv (solo ID y asignación); reports/division_temporal.json; reports/baseline_resultados.json; reports/baseline_predicciones_validacion.csv; reports/baseline_verificacion.json; este informe y tres PNG baseline_* en reports/figures.

Modificados: README y src/run_notebook.py para permitir el notebook baseline. Las dependencias y decisiones de preparación se mantienen. No se guardan copias de X por partición, transformadores entrenados sobre todo el dataset ni predicciones de prueba. El pipeline entrenado reside en memoria y se reproduce ejecutando el notebook; no se exportó un modelo serializado.

El notebook se ejecutó completo con salidas conservadas. Nueve pruebas comprueban preparación, fronteras temporales, madurez, prohibición de grupos compartidos y orientación de métricas. Se verifican también hashes de datos, estado inicial sin fit, estadísticas aprendidas solo de train, inmutabilidad al transformar y 105 archivos de referencia sin cambios. El detalle de ejecución y rutas se conserva en baseline_verificacion.json. Las figuras se revisan visualmente.

## 8. Recomendación para la siguiente fase

Revisar primero la detección limitada del baseline y la población elegible para validación. Tras autorización, comparar modelos estudiados con estas mismas reglas, manteniendo preprocesamiento dentro de cada ajuste y prueba reservada. Los costes de alertas y cancelaciones no detectadas, la calibración y la posible elección de umbral necesitan una fase posterior autorizada; no se han optimizado ahora. No relajar exclusiones temporales solo para mejorar métricas.

**Fin de fase 4. No se continúa sin confirmación del usuario.**
