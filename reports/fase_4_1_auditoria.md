# Fase 4.1 — Auditoría metodológica del baseline

Fecha: 18 de octubre de 2026. Alcance exclusivo de auditoría. Separador decimal de tablas: punto; miles: coma. No se modifican datos, particiones, umbral histórico, parámetros o entregables de fases anteriores. No se usan predicciones de prueba ni se entrena ningún algoritmo nuevo.

## 1. Dictamen

**La implementación del pipeline de regresión logística es correcta respecto a la separación de transformaciones, pero la división temporal solo es defendible como benchmark retrospectivo condicionado a su población elegible. No demuestra una simulación de producción completa.** La selección por madurez sesga antelación y composición. Además, prueba no incorpora una fecha global de cierre ni filtro de madurez. La disponibilidad real de las etiquetas no puede garantizarse con los archivos disponibles.

**No recomiendo pasar todavía a una comparación formal de modelos.** Primero se debe acordar población objetivo, seguimiento y cierre verificable, y aprobar el protocolo corregido. Una comparación académica exploratoria en la validación actual sería posible si se declara expresamente su alcance restringido; no se ha realizado en esta auditoría. No se selecciona un umbral definitivo.

## 2. Qué fechas representan los datos

| Concepto | Representación utilizada | Lo que no demuestra |
|---|---|---|
| Creación de reserva | Llegada prevista menos lead_time, a precisión de día | No hay marca de creación exacta, hora o historial de cambios. |
| Llegada | Reconstruida con año, mes y día previstos | No es alta ni cancelación y puede haber sido modificada. |
| Estado final fechado | reservation_status_date, exclusivamente como metadato | No es necesariamente primera disponibilidad del desenlace ni log de ingestión/publicación. |
| Madurez aproximada | max(llegada + noches, fecha_estado_final) + 1 día | Es una cota artificial conservadora, no conocimiento real demostrado. |
| Cierre de observación de resultados | No está documentado | No se puede inferir un cierre certificado del último día de llegada ni del máximo estado observado. |

Se reprodujeron las fórmulas y se verificó el manifiesto contra temporal_split sin escribirlo. Entrenamiento exige proxy y madurez anteriores al 01/07/2016. Validación exige proxy desde esa fecha hasta antes del 01/01/2017, y madurez anterior al 01/01/2017. Ambos usan desigualdad estricta. Esto añade un margen diario conservador y retrasa también cancelaciones que ya tienen un estado fechado antes de la salida prevista.

No hay un as_of_date global en src/splitting.py. Prueba se asigna únicamente por proxy >= 01/01/2017. Por tanto, no existe un filtro que garantice que su resultado estuviera disponible al cierre. La regla no se ha modificado.

## 3. Reservas apartadas y sesgo de selección

Las 30.386 reservas siguen en el dataset y en el manifiesto: 17.825 pertenecen al periodo de entrenamiento pero no pasan su madurez, y 12.561 al de validación pero no pasan la suya. No son necesariamente etiquetas desconocidas realmente; son **no elegibles bajo la regla implementada**. No se desplazaron a periodos posteriores ni se borraron.

| grupo | registros | tasa_cancelacion | lead_time_media | lead_time_mediana | lead_time_p90 | noches_media | fraccion_city | estado_final_fechado_antes_corte |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| entrenamiento | 48,428 | 35.81% | 88.2953 | 55.0000 | 256.0000 | 3.2310 | 64.37% | 48,428 |
| no_madura_entrenamiento | 17,825 | 47.56% | 226.8871 | 200.0000 | 407.0000 | 4.0121 | 71.42% | 5,868 |
| validacion | 14,011 | 26.17% | 32.7977 | 24.0000 | 80.0000 | 2.8438 | 66.89% | 14,011 |
| no_madura_validacion | 12,561 | 50.46% | 161.7017 | 161.0000 | 277.0000 | 4.2491 | 67.69% | 4,157 |

Las comparaciones se hacen dentro de cada ventana del proxy para no confundir toda la diferencia con el cambio de semestre. Hay un sesgo claro hacia menor antelación: mediana 24 días en validación frente a 161 en su grupo apartado; también cambia duración, segmento y tasa de cancelación. En entrenamiento las medianas son 55 frente a 200 días. Las reservas apartadas no son una muestra aleatoria.

Gráfico: [distribuciones acumuladas de antelación](figures/auditoria_4_1_01_sesgo_antelacion.png).

En la validación incluida, Online TA representa aproximadamente 60.04% y Groups 5.07%; en su grupo apartado son 53.19% y 26.89%. El perfil categórico completo está en el CSV auxiliar. El descenso de la tasa entre entrenamiento y validación no puede interpretarse solo como cambio temporal genuino: selección y composición también intervienen.

Hay **5.868** apartadas del periodo de entrenamiento y **4.157** del de validación cuyo estado final está fechado antes de su corte. La regla las retrasa igualmente por la salida prevista o el margen diario. Eso prueba que “apartada por madurez” no equivale a “no hay una fecha de estado anterior”; no prueba que el hotel tuviera efectivamente publicada la etiqueta. No se incorporan automáticamente: hacerlo requiere definir la disponibilidad y revisar el sesgo de observar antes cancelaciones que no cancelaciones.

La extracción está acotada por llegadas. Al clasificar por creación aproximada, faltan además reservas creadas en esas ventanas con llegadas fuera de la cobertura; no basta con recuperar las filas apartadas para reconstruir todas las altas. El proxy anterior a julio de 2015 no implica un histórico completo desde 2013.

## 4. Prueba y cierre del periodo

Última llegada observada: 2017-08-31. Máxima fecha de estado global y de prueba: 2017-09-14. Máxima cota artificial de madurez en prueba: 2017-09-15.

La inspección de prueba en esta auditoría se limita a estas fechas y las comparaciones de elegibilidad. No se analizan sus puntuaciones, calibración, clases para elegir umbral ni métricas predictivas.

| escenario_no_verificado | corte_exclusivo | registros_prueba | fecha_estado_en_o_despues_del_corte | no_cumple_regla_madurez | cumple_regla_madurez |
| --- | --- | --- | --- | --- | --- |
| cierre_hipotetico_ultimo_dia_llegadas | 2017-09-01 | 26,565 | 368 | 652 | 25,913 |
| dia_siguiente_al_maximo_estado_no_es_cierre_documentado | 2017-09-15 | 26,565 | 0 | 2 | 26,563 |
| corte_posterior_al_maximo_de_cota_no_verificado | 2017-09-16 | 26,565 | 0 | 0 | 26,565 |

Los cortes son exclusivos. Si se toma hipotéticamente el cierre del último día de llegadas (31/08/2017; corte 01/09/2017), **368** registros de prueba tienen estado fechado en septiembre y **652** no pasan la regla actual de madurez. No se puede afirmar que toda prueba fuera conocida al acabar agosto. Con corte 15/09 quedan dos registros sin pasar la cota; con 16/09 todos pasarían matemáticamente. **No se elige 16/09 como cierre:** derivarlo del máximo observado sería circular y no certifica seguimiento, ausencia de retrasos o integridad de extracción. Los máximos observados no documentan un as_of_date.

En consecuencia, **la madurez real de todas las etiquetas de prueba no está garantizada**. No se eliminó ninguna de esas filas, ni se modificó el manifiesto o la prueba.

## 5. Auditoría del pipeline y reproducción controlada

El baseline no estaba serializado. Para obtener probabilidades de entrenamiento se reprodujo exclusivamente la misma logística con los mismos parámetros, las mismas 48.428 filas y semilla 42. No se usó fit_and_validate, porque esa función transformaría también prueba; la nueva función solo recibe X_train, y_train y X_valid. No se sustituyó ni persistió el modelo original.

Las probabilidades reproducidas de validación coinciden con el CSV de fase 4 con diferencia máxima 1.11e-16. Se verificaron medianas numéricas, medias/escalas y categorías contra entrenamiento, así como las 191 columnas transformadas registradas en fase 4. El fit convergió en 131 iteraciones. No se cambió C, class_weight, solver, max_iter o el umbral histórico 0.5.

Se mantienen seis numéricas (lead_time, total_nights, adults, children, babies, children_missing) y ocho categóricas (hotel, arrival_date_month, meal, country, market_segment, distribution_channel, reserved_room_type, customer_type). La lista explícita del ColumnTransformer excluye etiqueta, estados, otros campos dudosos y todos los metadatos. No se detectó fuga por ajuste de preprocesamiento con validación o prueba. **Eso no certifica snapshots iniciales de los predictores:** esa limitación semántica continúa.

OneHotEncoder usa handle_unknown='ignore': una categoría inédita se transforma en un bloque de ceros, sin aprender su efecto. El imputador categórico usa Desconocido; no es necesariamente equivalente a una categoría inédita.

| variable | registros_validacion_categoria_no_vista | porcentaje | n_categorias_no_vistas |
| --- | --- | --- | --- |
| hotel | 0 | 0.0000 | 0 |
| arrival_date_month | 0 | 0.0000 | 0 |
| meal | 0 | 0.0000 | 0 |
| country | 19 | 0.1356 | 10 |
| market_segment | 0 | 0.0000 | 0 |
| distribution_channel | 0 | 0.0000 | 0 |
| reserved_room_type | 0 | 0.0000 | 0 |
| customer_type | 0 | 0.0000 | 0 |

## 6. Entrenamiento frente a validación y distribución probabilística

| grupo | registros | accuracy | precision | recall | f1 | roc_auc | brier | log_loss | average_precision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| entrenamiento_ajuste_interno | 48,428 | 0.8048 | 0.7633 | 0.6593 | 0.7075 | 0.8746 | 0.1331 | 0.4144 | 0.8233 |
| validacion | 14,011 | 0.7443 | 0.5336 | 0.1841 | 0.2737 | 0.7004 | 0.1824 | 0.5678 | 0.4578 |

Las cifras de entrenamiento son **de ajuste interno, optimistas**, no una validación independiente. El descenso de métricas puede reflejar sobreajuste, cambio temporal, composición y censura; estas cifras no permiten atribuirlo a una única causa.

| grupo | tasa_observada | probabilidad_media | probabilidad_mediana | p10 | p90 | p95 | fraccion_alertas_05 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| entrenamiento_ajuste_interno | 35.81% | 35.80% | 0.2485 | 0.0360 | 0.8865 | 0.9305 | 30.93% |
| validacion | 26.17% | 19.01% | 0.1154 | 0.0242 | 0.4777 | 0.6060 | 9.03% |

En validación la probabilidad media es 19.01% frente a 26.17% observado: infrapredicción media de 7.16 puntos porcentuales. La mediana es 0.1154; solo 9.03% supera o iguala 0.5. El umbral histórico queda por encima de la mayor parte de las puntuaciones. Los histogramas y la fiabilidad se generan exclusivamente con entrenamiento/validación.

Gráfico: [distribución de probabilidades](figures/auditoria_4_1_02_distribucion_probabilidades.png).

## 7. Calibración: indicios y límites

| banda | registros | probabilidad_media | tasa_observada | cancelaciones | desviacion_observada_menos_predicha |
| --- | --- | --- | --- | --- | --- |
| (-0.001, 0.1] | 6,295 | 0.0513 | 0.1388 | 874 | 0.0876 |
| (0.1, 0.2] | 3,047 | 0.1416 | 0.2717 | 828 | 0.1302 |
| (0.2, 0.3] | 1,535 | 0.2448 | 0.3251 | 499 | 0.0803 |
| (0.3, 0.4] | 1,075 | 0.3466 | 0.3721 | 400 | 0.0255 |
| (0.4, 0.5] | 794 | 0.4466 | 0.4924 | 391 | 0.0458 |
| (0.5, 0.6] | 531 | 0.5472 | 0.4350 | 231 | -0.1121 |
| (0.6, 0.7] | 426 | 0.6474 | 0.5399 | 230 | -0.1075 |
| (0.7, 0.8] | 208 | 0.7475 | 0.6394 | 133 | -0.1081 |
| (0.8, 0.9] | 95 | 0.8401 | 0.8105 | 77 | -0.0295 |
| (0.9, 1.0] | 5 | 0.9338 | 0.8000 | 4 | -0.1338 |

Las diez bandas son fijas. Se compara probabilidad media con tasa observada y soporte; bandas altas con pocos casos son inestables. La desviación media y el diagrama indican infrapredicción en esta población. El error absoluto de calibración agrupado (ECE descriptivo, dependiente de bandas) es 0.0904; no es una prueba formal ni una corrección.

La infrapredicción no es uniforme: por debajo de 0.5 las tasas observadas superan generalmente las probabilidades medias, mientras que varias bandas superiores a 0.5 sobreestiman el riesgo. La banda 0.9–1.0 contiene solo cinco reservas. El parecido de la media predicha y observada en entrenamiento no acredita calibración fuera de muestra.

Gráfico: [fiabilidad y soporte de bandas](figures/auditoria_4_1_03_calibracion_validacion.png).

Brier/log-loss de la logística están en la tabla de diagnósticos. Como referencia probabilística legítima se usa la prevalencia de entrenamiento (0.3581) constante, sin aprender de validación: Brier 0.2025 y log-loss 0.5961. No se usa la prevalencia de validación para ajustar esa referencia. Brier y log-loss mezclan discriminación y calibración; una mejora frente a una constante no demostraría buena calibración.

No se ajustó calibración isotónica, sigmoide ni otro algoritmo. Cualquier calibración futura requiere datos de desarrollo separados o predicciones fuera de muestra, sin contaminar la prueba final. Los duplicados/dependencias impiden asumir observaciones independientes sin justificación; no se añadieron intervalos de confianza con esa premisa.

## 8. Umbrales: margen de mejora sin selección definitiva

Regla: alerta si p >= umbral. Rejilla descriptiva fijada en código, sin búsqueda continua, sin máximo F1 elegido y sin acceder a prueba. Precision sin alertas se representa como cero, no como un valor estimable entre alertas inexistentes.

| umbral | precision | recall | f1 | falsos_positivos | falsos_negativos | alertas |
| --- | --- | --- | --- | --- | --- | --- |
| 0.0000 | 26.17% | 100.00% | 0.4149 | 10,344 | 0 | 14,011 |
| 0.0500 | 30.36% | 91.38% | 0.4558 | 7,687 | 316 | 11,038 |
| 0.1000 | 36.20% | 76.17% | 0.4907 | 4,923 | 874 | 7,716 |
| 0.1500 | 40.04% | 63.79% | 0.4920 | 3,502 | 1,328 | 5,841 |
| 0.2000 | 42.09% | 53.59% | 0.4714 | 2,704 | 1,702 | 4,669 |
| 0.2500 | 43.46% | 44.56% | 0.4400 | 2,126 | 2,033 | 3,760 |
| 0.3000 | 46.78% | 39.98% | 0.4311 | 1,668 | 2,201 | 3,134 |
| 0.3500 | 50.10% | 34.69% | 0.4099 | 1,267 | 2,395 | 2,539 |
| 0.4000 | 51.77% | 29.07% | 0.3723 | 993 | 2,601 | 2,059 |
| 0.4500 | 53.20% | 23.83% | 0.3292 | 769 | 2,793 | 1,643 |
| 0.5000 | 53.36% | 18.41% | 0.2737 | 590 | 2,992 | 1,265 |
| 0.6000 | 60.49% | 12.11% | 0.2018 | 290 | 3,223 | 734 |
| 0.7000 | 69.48% | 5.84% | 0.1077 | 94 | 3,453 | 308 |
| 0.8000 | 81.00% | 2.21% | 0.0430 | 19 | 3,586 | 100 |
| 0.9000 | 80.00% | 0.11% | 0.0022 | 1 | 3,663 | 5 |
| 1.0000 | 0.00% | 0.00% | 0.0000 | 0 | 3,667 | 0 |

El punto histórico 0.50 reproduce FP=590, FN=2,992, precision 53.36% y recall 18.41%. A 0.20 el recall sube a 53.59%, con 2,704 falsas alertas. A 0.10 llega a 76.17%, con 4,923 falsas alertas y precision 36.20%. Frente a 0.50, este último escenario detectaría 2,118 cancelaciones adicionales a costa de 4,333 falsos positivos adicionales y de una mayor carga de seguimiento.

La curva precision-recall tiene average precision de validación 0.4578, con prevalencia 0.2617 como referencia de contexto. AP no es el promedio simple de precision/recall ni demuestra utilidad económica. Cambiar el umbral no altera la ordenación/AUC ni corrige la calibración ni recupera las reservas excluidas; cambia la política de alertas sobre las mismas puntuaciones. Las cifras obtenidas al inspeccionar muchos umbrales en validación deben confirmarse posteriormente; no son una evaluación final independiente.

Gráfico: [curva precision-recall y rejilla de umbrales](figures/auditoria_4_1_04_precision_recall_umbrales.png).

## 9. Consecuencias y escenarios de negocio

Un falso negativo deja sin anticipar una cancelación, con posibles errores en previsiones de ocupación y planificación. Un falso positivo puede provocar seguimiento innecesario o contacto molesto con un cliente que mantiene la reserva. Detectar una cancelación no demuestra que una intervención la evite, ni que toda cancelación suponga una pérdida neta de igual importe.

**Supuestos ilustrativos, no costes reales:** penalización relativa FP=1; FN=1, 3 o 10 unidades abstractas. Se calcula FP + r*FN, sin euros y sin seleccionar el menor valor como política definitiva.

| umbral | falsos_positivos | falsos_negativos | alertas | unidades_relativas_FP_1_FN_1 | unidades_relativas_FP_1_FN_3 | unidades_relativas_FP_1_FN_10 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1000 | 4,923 | 874 | 7,716 | 5,797 | 7,545 | 13,663 |
| 0.2000 | 2,704 | 1,702 | 4,669 | 4,406 | 7,810 | 19,724 |
| 0.3000 | 1,668 | 2,201 | 3,134 | 3,869 | 8,271 | 23,678 |
| 0.5000 | 590 | 2,992 | 1,265 | 3,582 | 9,566 | 30,510 |
| 0.7000 | 94 | 3,453 | 308 | 3,547 | 10,453 | 34,624 |

Para la comparación específica 0.10 frente a 0.50, bajo este modelo simplificado el menor umbral compensa la penalización adicional de falsos positivos solo si FN pesa más de 2.046 veces FP. Esta cuenta es retrospectiva sobre validación, no un coste estimado ni garantía futura. Falta coste de actuar incluso sobre verdaderos positivos, capacidad de seguimiento, eficacia de la intervención y diferencias entre reservas. No puede fijarse un umbral solo por F1 ni convertir probabilidades mal calibradas en una decisión económica exacta.

## 10. Corrección propuesta ANTES de cualquier modificación

1. Obtener fecha de extracción/cierre de resultados documentada y, si existen, logs de creación, cambios de predictores y disponibilidad de etiquetas. No inferir cierre del máximo observado. Mantener prueba congelada hasta aprobar este contrato temporal.
2. Definir la población: todas las altas o solo reservas con horizonte operativo acotado. Si se mantiene una población acotada, justificar un horizonte/capacidad de seguimiento con negocio antes de comparar algoritmos; no elegirlo por métricas.
3. Construir cohortes completas con seguimiento suficiente. La elegibilidad debería depender de reglas operativas conocidas al predecir y un seguimiento prefijado, no de conservar solo los desenlaces ya observados de una cohorte incompleta. Recuperar datos de llegadas fuera de la extracción si se pretende representar todas las altas.
4. Verificar disponibilidad de etiquetas de entrenamiento antes del primer corte, y de validación antes de cualquier decisión que preceda a prueba. Añadir a validación las 12.561 apartadas usando desenlaces posteriores y mantener prueba desde enero de 2017 **no sería una corrección válida** para seleccionar modelos en enero: emplearía resultados futuros. Harían falta ventanas de validación más tempranas, prueba posterior, un horizonte operativo previo o más datos, con la nueva política explícitamente aprobada.
5. Establecer un as_of_date para prueba y su regla de madurez/seguimiento antes de evaluar. Si un escenario exige excluir filas, registrar el cambio y los motivos; los conteos de esta auditoría son hipotéticos, no un nuevo conjunto. No excluir automáticamente las 652 del escenario de agosto ni adoptar septiembre como cierre por conveniencia.
6. Si no se consigue la documentación, reformular el alcance como benchmark retrospectivo de una cohorte de llegadas y declarar que no reproduce todas las nuevas reservas en tiempo real. Cambiar solo a cortes por llegada cambia el objetivo de evaluación y no prueba disponibilidad al crear la reserva.

**No se aplica ninguna corrección de particiones en esta fase.** Tampoco se cambia el modelo o su umbral histórico. Esta auditoría distingue corrección técnica del pipeline de validez del diseño poblacional/temporal.

## 11. Entregables y verificación

Se crean src/audit_baseline.py, tests/test_audit_baseline.py, este informe, auditoria_4_1_resultados.json, nueve CSV auxiliares y cuatro figuras auditoria_4_1_*.png. README solo añade el enlace y el dictamen de auditoría. Los entregables de fases anteriores, original, preparado y manifiesto se comprueban por SHA-256 y se mantienen intactos. El registro completo de huellas está en el JSON de resultados.

La reproducción usa el mismo algoritmo y parámetros, no alternativas ni optimización. Las predicciones de validación coinciden con las guardadas. Los tests auxiliares comprueban conteos/fronteras de umbral, bandas de calibración y escenarios temporales sin modificación de sus entradas. Prueba no recibe predict, predict_proba, transform, calibración ni análisis de umbral durante esta auditoría: solo se examinan sus metadatos de fechas necesarios para la pregunta temporal.

Reproducción desde la raíz: `.venv\Scripts\python.exe -m src.audit_baseline`. Las salidas son exclusivamente de auditoría. La comparación de algoritmos requiere aprobación posterior y no se ha iniciado.

**Fin de fase 4.1. Detenerse y presentar el dictamen para revisión.**
