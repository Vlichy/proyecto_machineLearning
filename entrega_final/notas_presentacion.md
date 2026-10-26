# Notas para la exposición

## 1. Predicción de cancelaciones hoteleras

Presentar el objetivo académico: clasificar riesgo y priorizar seguimiento. Aclarar que la autoría académica no se ha confirmado. La evaluación es retrospectiva, no un piloto de intervención.

Fuente: Memoria final, 18/10/2026

## 2. Problema de negocio

Una reserva puede cancelar y generar incertidumbre de demanda. El seguimiento consume tiempo. Diferenciar capacidad predictiva de eficacia del contacto. No se estiman ahorros ni se recomiendan penalizaciones.

Fuente: Memoria, introducción y alcance

## 3. Objetivos del proyecto

Describir calidad y asociaciones, construir pipelines sin ajuste global, contrastar algoritmos y cerrar una decisión antes de prueba. El enunciado oficial no se ha localizado.

Fuente: Informes de fases 1 a 9

## 4. Dataset y calidad

Archivo local compatible con Hotel Booking Demand, sin cadena de descarga acreditada. La publicación describe 31 variables por hotel y el archivo combinado añade hotel. Conservar duplicados evita asumir errores sin un ID real.

Fuente: Fases 1 y 2. António et al., 2019, DOI 10.1016/j.dib.2018.11.126

## 5. Análisis exploratorio

La tasa City supera la de Resort en el archivo completo. Lead time cero tiene 6,78% y mayor a 365 días 67,66%, grupos seleccionados no exhaustivos. No atribuir causalidad. El EDA utilizó todo el archivo y esa exposición se declara.

Fuente: Fase 2, EDA global. No corresponde a prueba v3

## 6. Preparación de datos

Seis numéricas y ocho categóricas. Numéricas: lead_time, total_nights, adults, children, babies, children_missing. Categóricas: hotel, mes, meal, country, mercado, canal, habitación reservada y tipo de cliente. OHE ignora categorías desconocidas. Solo logística escala.

Fuente: Fase 3 y especificación congelada de fase 8

## 7. Prevención de leakage y protocolo v3

Se excluyen estado final y fecha de estado, además de 12 campos inciertos. V2 seleccionaba por disponibilidad de desenlaces, favoreciendo cancelaciones anticipadas. V3 usa llegada y seguimiento común de bloque. Embargos julio-agosto 2016 y enero-febrero 2017. Train completa un ciclo anual. Cierre de prueba asumido 01/12/2018, sin certificación PMS.

Fuente: Fases 3, 7.1 y manifiesto v3

## 8. Algoritmos comparados

Comparación v2: logística, árbol profundidad 8, bosque 200 árboles, XGBoost 300 y LightGBM 300. La búsqueda v2 tuvo 54 ajustes y no mejoró evaluación externa. TreeExplainer sobre 3.000 filas de XGBoost v2 destacó país y antelación. No explica la logística final ni implica causalidad.

Fuente: Fases 5, 6 y 7. Experimentos históricos v2

## 9. Resultados de modelado en validación v3

Los cinco algoritmos se compararon en v2, una población distinta. En v3 se mantienen los dos iniciales sin optimizar. XGBoost mejora AUC, AP y Brier. Esta diapositiva no compara resultados entre protocolos.

Fuente: seleccion_8_metricas.csv y seleccion_8_calibracion.csv

## 10. Selección de regresión logística

A igual volumen mensual de 3.980 prioridades, logística identifica 32 TP más. Es una ventaja pequeña, descriptiva, sin prueba de superioridad estadística. A 30% gana XGBoost. Se valora también menor complejidad. La capacidad 20% se fijó como supuesto antes del análisis, sin escogerla para favorecer un modelo.

Fuente: Fase 8, capacidad mensual del 20% en validación v3

## 11. Política mensual de priorización

Cada mes reúne ambos hoteles. Se aplica floor del 20% dentro del mes, no del total multimensual. Ante empate exacto: SHA256 UTF-8 de 42|ID ascendente y después ID numérico. Sin redondeo de scores, etiquetas ni cuotas por hotel. Requiere lote completo y revisión humana, sin garantía de evitar cancelaciones.

Fuente: Especificación congelada de fase 8 y src/decision_policy.py

## 12. Evaluación final sobre prueba v3

32.829 reservas, 13.136 cancelaciones, 6.564 prioridades. Matriz TN18469 FP1224 FN7796 TP5340. Una inferencia, scores congelados antes de acceder a objetivos. Comparar con validación sin cambiar el modelo ni política. Precision baja 4,25 puntos y recall 4,35.

Fuente: Fase 9, evaluacion_9_metricas.json

## 13. Variabilidad por mes y hotel

Precision mensual: marzo80,38 abril91,70 mayo93,90 junio89,99 julio68,17 agosto58,68%. City prioriza23,73% con precision82,99 y recall45,88. Resort11,81%, precision74,16 y recall26,04. Son cuotas compartidas. Los cambios de temporada y composición no permiten atribuir causalidad ni concluir una tendencia permanente con seis meses.

Fuente: Fase 9, tablas mensuales y por hotel

## 14. Limitaciones de la evaluación

Faltan snapshots iniciales y cierre operativo acreditado. Fecha de alta aproximada no observada. Parte de prueba estuvo expuesta bajo v2 y al EDA. Validación reutilizada. Scores no calibrados, promedio35,21% frente40,01% observado. Intervalos por bloques descriptivos, sin cobertura garantizada. Sin costes, eficacia de intervención ni ID real.

Fuente: Memoria, limitaciones y fase 9

## 15. Conclusiones

El proyecto integra conocimientos de calidad, pipelines, comparación, búsqueda temporal, SHAP y evaluación. En prueba cubre40,65% de cancelaciones al20% de capacidad y deja7796 sin prioridad. Conservar decisiones congeladas. Trabajo futuro: nuevas reservas con trazabilidad, evaluación externa y piloto humano. Confirmar autoría y rúbrica del profesor antes de entregar.

Fuente: Memoria final y evaluación congelada de fase 9
