# Resumen ejecutivo

## Predicción de cancelaciones hoteleras

Curso de Data Science y Machine Learning. 18 de octubre de 2026.

El proyecto desarrolla una clasificación de cancelaciones sobre 119.390 registros de City Hotel y Resort Hotel. Conserva los datos, separa 14 predictores de etiquetas y metadatos, y aprende imputación, codificación y escalado exclusivamente en entrenamiento.

El protocolo definitivo v3 define cohortes retrospectivas por llegada con embargos: entrenamiento julio 2015-junio 2016, validación septiembre-diciembre 2016 y prueba marzo-agosto 2017. Los experimentos históricos v2 de cinco algoritmos, optimización y SHAP conservan su valor formativo, pero sus resultados no son directamente comparables con v3. SHAP analizó XGBoost v2 y no explica la logística final.

En validación v3 se seleccionó regresión logística inicial. Aunque XGBoost obtuvo mejores métricas globales, logística identificó 32 cancelaciones adicionales al mismo volumen mensual del 20%, con menor complejidad. Esta ventaja es pequeña y descriptiva. El 20% es un supuesto de capacidad, no un recurso real del hotel.

La política ordena ambos hoteles conjuntamente dentro de cada mes por score descendente y prioriza floor(0,20 × n_mes), con desempates deterministas SHA256 de «42|ID» y después ID. Requiere el lote mensual completo y seguimiento humano. No corresponde a un umbral fijo de probabilidad ni implica certeza de cancelación.

La evaluación final única sobre 32.829 reservas contiene 13.136 cancelaciones y 6.564 prioridades. Obtiene 5.340 verdaderos positivos, 1.224 falsos positivos, 7.796 falsos negativos y 18.469 verdaderos negativos. Precision es 81,35%, recall 40,65% y F1 0,5421. ROC-AUC alcanza 0,7802, Average Precision 0,7416 y Brier 0,18534. Los scores medios (35,21%) subestiman la prevalencia (40,01%).

Precision y recall disminuyen 4,25 y 4,35 puntos frente a validación. Julio y agosto presentan un rendimiento inferior. City concentra 23,73% de sus reservas en prioridades y Resort 11,81%, porque comparten el cupo mensual. No se modifica esa distribución tras observar prueba.

El resultado demuestra capacidad retrospectiva de priorización en esta población, pero no valida un uso prospectivo ni ahorro económico. Faltan snapshots iniciales, cierre operativo acreditado, identificadores reales, costes y evidencia del efecto de intervenir. Parte de prueba estuvo expuesta en el desarrollo histórico y en el EDA. Los intervalos por bloques son descriptivos, sin garantía de cobertura o generalización.

Modelo, política, particiones y métricas permanecen congelados. El trabajo futuro requiere datos nuevos con trazabilidad temporal y un piloto de seguimiento evaluado de forma independiente. Antes de la entrega institucional deben confirmarse autoría y requisitos del profesor, cuyo enunciado no se ha localizado.

Fuente de todas las cifras: especificación congelada de fase 8 y evaluación final de fase 9. Detalles y referencias en memoria_final.md.
