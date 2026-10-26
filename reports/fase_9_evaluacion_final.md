# Fase 9 — Evaluación final de la especificación congelada sobre prueba v3

Se completa exclusivamente fase 9. Modelo: regresión logística inicial congelada en fase 8, sin refit, optimización o recalibración. Política: top 20% por mes de llegada, City y Resort conjuntamente; k=n_mes*20//100, scores descendentes, hash SHA256 de `42|ID` y después ID numérico para empates exactos. No es un umbral fijo de probabilidad. El modelo, la política y el protocolo no se cambian tras ver resultados.

**Resultado final:** 6564 prioridades de 32829 reservas, precision 81.35%, recall 40.65%, F1 0.5421, ROC-AUC 0.7802 y AP 0.7416. El rendimiento es inferior al de validación; modelo y política permanecen sin cambios.

## 1. Verificaciones antes de etiquetas y predicciones

Se revisaron informe/especificación/plan de fase 8, joblib, manifiesto v3 y decision_policy.py. SHA de especificación y modelo coinciden con las referencias de fase 8; todos los hashes de entradas, fuentes, versiones y modelo son conformes. Se comprueban clase/hiperparámetros, preprocesamiento, 14 entradas, 192 columnas transformadas, clase positiva 1 y scaler ajustado en 49157 filas. Se verifica hash de IDs de entrenamiento y que los 32829 IDs de prueba no cruzan entrenamiento/validación ni grupos exactos.

El preflight se guarda antes de leer etiquetas. La inferencia bloquea fit/fit_transform de pipeline, clasificador y transformadores; se contrasta la huella de parámetros aprendidos antes/después. Una única llamada predict_proba genera scores de prueba con el pipeline ya ajustado. Se aplica la política sin y y se guardan decisiones, scores y SHA antes de acceder a etiquetas. No se recalibra ni se ensayan otros modelos, cuotas, capacidades o umbrales sobre prueba.

El recibo evaluacion_9_recibo.json registra timestamps, versión/código, hashes y una llamada de inferencia. Las reejecuciones verifican esos archivos y presentan resultados congelados sin otra inferencia. No se repite la evaluación para seleccionar un resultado. No se ejecutan tests históricos que entrenan algoritmos: solo pruebas puras de política y evaluación sin entrenamiento.

## 2. Resultado de la política de seguimiento

Reservas evaluadas: **32829**. Priorizadas: **6564 (19.9945%)**, tras floor por cada mes. Canceladas observadas: 13136.

| n | priorizadas | porcentaje_priorizado | precision | recall | f1 | fp | fn | tp | tn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 32829 | 6564 | 19.994517 | 0.813528 | 0.406516 | 0.542132 | 1224 | 7796 | 5340 | 18469 |

Matriz [[TN, FP], [FN, TP]], filas reales y columnas de prioridad [0,1]: **[[18469, 1224], [7796, 5340]]**. Alerta significa seguimiento, no cancelación segura. Precision describe acierto entre prioridades, recall cobertura de cancelaciones; F1 combina ambas sin incorporar costes reales. FP son seguimientos innecesarios y FN cancelaciones no anticipadas; ninguna métrica acredita que un contacto evitaría cancelaciones.

## 3. Métricas globales y calidad probabilística

| roc_auc | average_precision | brier | tasa_cancelacion | probabilidad_media | canceladas | brecha_media |
| --- | --- | --- | --- | --- | --- | --- |
| 0.780186 | 0.741601 | 0.185340 | 0.400134 | 0.352073 | 13136 | -0.048061 |

ROC-AUC y AP se calculan con scores continuos, no con prioridad binaria; AP depende de prevalencia. Brier mide error cuadrático probabilístico y combina calibración/resolución. La probabilidad media se compara con la tasa observada y se dibujan bins descriptivos sin ajustar un calibrador. No se convierte el 20% de recursos en una probabilidad de corte constante.

![Matriz y calibración](figures/evaluacion_9_matriz_calibracion.png)

## 4. Comparación con validación v3

| metrica | validacion_v3 | prueba_v3 | diferencia_prueba_menos_validacion |
| --- | --- | --- | --- |
| precision | 0.856030 | 0.813528 | -0.042502 |
| recall | 0.450066 | 0.406516 | -0.043550 |
| f1 | 0.589957 | 0.542132 | -0.047825 |
| roc_auc | 0.794590 | 0.780186 | -0.014404 |
| average_precision | 0.762161 | 0.741601 | -0.020560 |
| brier | 0.172380 | 0.185340 | 0.012959 |
| tasa_cancelacion | 0.380192 | 0.400134 | 0.019942 |
| probabilidad_media | 0.330992 | 0.352073 | 0.021081 |

Las diferencias son prueba menos validación, sobre la misma política/modelo congelados. La validación sirvió para seleccionar y es optimista respecto a selección; no se afirma independencia total de prueba, que tuvo exposición parcial bajo v2. Variaciones de prevalencia, calendario y mezcla pueden modificar precision/AP y cobertura. Se conserva la especificación aunque algún indicador empeore. No se atribuye causalmente el cambio a una sola variable ni se prueba significación mediante comparar dos intervalos marginales.

Cambios de composición observados, sin filtrar ni reponderar filas:

| variable | categoria | n_validacion | n_prueba | proporcion_validacion | proporcion_prueba |
| --- | --- | --- | --- | --- | --- |
| hotel | City Hotel | 13690 | 22542 | 0.687560 | 0.686649 |
| hotel | Resort Hotel | 6221 | 10287 | 0.312440 | 0.313351 |
| market_segment | Aviation | 60 | 103 | 0.003013 | 0.003137 |
| market_segment | Complementary | 158 | 171 | 0.007935 | 0.005209 |
| market_segment | Corporate | 818 | 1027 | 0.041083 | 0.031283 |
| market_segment | Direct | 1792 | 3549 | 0.090001 | 0.108106 |
| market_segment | Groups | 3044 | 4437 | 0.152880 | 0.135155 |
| market_segment | Offline TA/TO | 4188 | 5010 | 0.210336 | 0.152609 |
| market_segment | Online TA | 9851 | 18532 | 0.494752 | 0.564501 |
| customer_type | Contract | 147 | 635 | 0.007383 | 0.019343 |
| customer_type | Group | 76 | 158 | 0.003817 | 0.004813 |
| customer_type | Transient | 15868 | 27345 | 0.796946 | 0.832953 |
| customer_type | Transient-Party | 3820 | 4691 | 0.191854 | 0.142892 |

Cuantiles de antelación (p10/p50/p90), validación y prueba: **{'validacion': {'0.1': 4.0, '0.5': 66.0, '0.9': 313.0}, 'prueba': {'0.1': 6.0, '0.5': 103.0, '0.9': 264.0}}**. Las distribuciones se describen después de evaluar; no se usan para adaptar pipeline, cuotas o calibración.

<!-- lectura_resultados_fase9 -->
## 4.1. Lectura de los resultados observados, sin reajustes

La precision de seguimiento baja de 85,60% a 81,35% (−4,25 puntos porcentuales), y recall de 45,01% a 40,65% (−4,35 puntos). F1 baja de 0,58996 a 0,54213; ROC-AUC de 0,79459 a 0,78019 y AP de 0,76216 a 0,74160. Brier empeora de 0,17238 a 0,18534. Los indicadores muestran deterioro descriptivo fuera de la validación seleccionada; no se modifica nada para compensarlo.

La prevalencia aumenta de 38,02% a 40,01% (+1,99 puntos). La caída de precision/AP no se explica simplemente por haber menos positivos: hay mayor proporción de cancelaciones, pero también distinta capacidad de ordenación y composición. No se realiza una descomposición causal. La media predicha es 35,21%, unos 4,81 puntos por debajo de la observada; la selección top-k no requiere calibración para ordenar, pero sus scores no deben tratarse como frecuencias fiables. No se ajusta un calibrador con prueba.

Por meses, los volúmenes son de 4925 a 6313 filas: no se trata de fluctuaciones en grupos de unas pocas reservas, pero las observaciones siguen pudiendo estar relacionadas. La precision alcanza 93,90% en mayo, baja a 68,17% en julio y 58,68% en agosto; recall pasa de 47,79% en marzo a 31,83% en agosto. ROC-AUC es 0,833 en abril y cae a 0,674 en agosto. No hay deterioro monótono desde marzo: los últimos meses son especialmente difíciles y coinciden con otra temporada. No se separa el efecto temporal de cambios comerciales o de selección de datos con este diseño.

La mezcla de hoteles cambia poco: City representa 68,76% en validación y 68,66% en prueba. Por tanto, ese reparto agregado por sí solo no explica el deterioro. Sí cambia el mercado: Online TA pasa de 49,48% a 56,45% y Offline TA/TO de 21,03% a 15,26%; Transient sube de 79,69% a 83,30% y Transient-Party baja de 19,19% a 14,29%. La mediana de antelación pasa de 66 a 103 días, mientras su percentil 90 baja de 313 a 264: no es un desplazamiento uniforme de toda la distribución. Son posibles factores asociados, no causas demostradas del cambio.

City recibe 5349 prioridades (23,73% de sus reservas), con precision 82,99% y recall 45,88%. Resort recibe 1215 (11,81%), con precision 74,16% y recall 26,04%. La cuota es conjunta; esta diferencia no es un fallo de cálculo ni se corrige repartiendo alertas después de ver etiquetas. La infrapredicción media es mayor en Resort (8,56 puntos, frente a 3,09 en City). Cualquier política distinta por hotel requeriría otro estudio autorizado, nunca reajustar esta evaluación final.

Los percentiles de remuestreo para precision son aproximadamente 75,47%–88,76%; para recall, 37,24%–43,62%; para AUC, 0,7478–0,8102. Son intervalos descriptivos condicionados a decisiones originales y bloques escogidos, no una garantía de rendimiento futuro ni una prueba formal de diferencia con validación. No cubren incertidumbre de selección/entrenamiento ni sesgos del protocolo.

## 5. Meses de prueba y comprobación exacta de capacidad

| mes_llegada | n | priorizadas | porcentaje_priorizado | precision | recall | f1 | fp | fn | tp | tn | roc_auc | average_precision | brier | tasa_cancelacion | probabilidad_media | canceladas | brecha_media |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-03 | 4970 | 994 | 20.000000 | 0.803823 | 0.477871 | 0.599400 | 195 | 873 | 799 | 3103 | 0.802881 | 0.724756 | 0.159612 | 0.336419 | 0.320714 | 1672 | -0.015705 |
| 2017-04 | 5661 | 1132 | 19.996467 | 0.916961 | 0.421437 | 0.577469 | 94 | 1425 | 1038 | 3104 | 0.832910 | 0.821594 | 0.165374 | 0.435082 | 0.371170 | 2463 | -0.063912 |
| 2017-05 | 6313 | 1262 | 19.990496 | 0.938986 | 0.429037 | 0.588966 | 77 | 1577 | 1185 | 3474 | 0.821128 | 0.826062 | 0.167203 | 0.437510 | 0.372676 | 2762 | -0.064834 |
| 2017-06 | 5647 | 1129 | 19.992917 | 0.899911 | 0.416564 | 0.569507 | 113 | 1423 | 1016 | 3095 | 0.794315 | 0.781416 | 0.181582 | 0.431911 | 0.385825 | 2439 | -0.046086 |
| 2017-07 | 5313 | 1062 | 19.988707 | 0.681733 | 0.364919 | 0.475378 | 338 | 1260 | 724 | 2991 | 0.712358 | 0.632814 | 0.213248 | 0.373424 | 0.297851 | 1984 | -0.075573 |
| 2017-08 | 4925 | 985 | 20.000000 | 0.586802 | 0.318282 | 0.412710 | 407 | 1238 | 578 | 2702 | 0.673913 | 0.545413 | 0.231700 | 0.368731 | 0.355153 | 1816 | -0.013578 |

En los seis meses se verifica exactamente n_priorizadas=n_mes*20//100. No se reaplica cuota separadamente a cada hotel. Los scores de borde y empates están en evaluacion_9_bordes_empates.csv; son resultados de aplicar la regla, no umbrales nuevos para meses siguientes. Las diferencias mensuales son descriptivas, condicionadas a sus tamaños/composición y sin demostrar deterioro uniforme o generalización anual.

![Evolución mensual](figures/evaluacion_9_mensual.png)

## 6. Hoteles bajo una cuota compartida

| hotel | n | priorizadas | porcentaje_priorizado | precision | recall | f1 | fp | fn | tp | tn | roc_auc | average_precision | brier | tasa_cancelacion | probabilidad_media | canceladas | brecha_media |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| City Hotel | 22542 | 5349 | 23.729039 | 0.829875 | 0.458764 | 0.590882 | 910 | 5237 | 4439 | 11956 | 0.788766 | 0.774550 | 0.183007 | 0.429243 | 0.398323 | 9676 | -0.030920 |
| Resort Hotel | 10287 | 1215 | 11.811024 | 0.741564 | 0.260405 | 0.385455 | 314 | 2559 | 901 | 6513 | 0.756181 | 0.635377 | 0.190451 | 0.336347 | 0.250725 | 3460 | -0.085622 |

El porcentaje alertado puede diferir entre hoteles porque compiten por el mismo top-k mensual. Se mantiene esa distribución sin introducir cuotas a posteriori. Prevalencia, tipos de reservas y tamaños explican parte de las diferencias, sin atribuir causalidad o superioridad universal. No hay datos de capacidad real por establecimiento.

## 7. Incertidumbre descriptiva con dependencia temporal

| metrica | estimacion | p2_5 | p97_5 | replicas_validas |
| --- | --- | --- | --- | --- |
| precision | 0.813528 | 0.754685 | 0.887610 | 500 |
| recall | 0.406516 | 0.372366 | 0.436153 | 500 |
| f1 | 0.542132 | 0.501230 | 0.581212 | 500 |
| roc_auc | 0.780186 | 0.747773 | 0.810234 | 500 |
| average_precision | 0.741601 | 0.693102 | 0.797401 | 500 |
| brier | 0.185340 | 0.171857 | 0.200392 | 500 |
| tasa_cancelacion | 0.400134 | 0.381513 | 0.424930 | 500 |
| probabilidad_media | 0.352073 | 0.335346 | 0.371569 | 500 |

500 réplicas, seed 42, bloques móviles no circulares de 14 días de llegada; se arrastran juntas todas las reservas de cada día y ambos hoteles, preservando también duplicados exactos de ese día. Se sortean bloques con reemplazo hasta tantos días como el calendario original, truncando el último. La longitud/semilla/número se fijaron en el plan antes de acceder a resultados. Como referencia para remuestrear bloques en datos dependientes: [Künsch (1989), versión del autor](https://www.researchgate.net/publication/2355926_The_Jackknife_and_the_Bootstrap_for_General_Stationary_Observations).

Scores y prioridades originales permanecen fijos: no se repriorizan réplicas, no se predice de nuevo y no se ajusta nada. Los porcentajes alertados pueden cambiar en la réplica al remuestrear días. Estos percentiles describen incertidumbre condicional de las decisiones observadas, no la de volver a ejecutar una cuota en un futuro lote completo ni la selección/entrenamiento del modelo. Las observaciones no se tratan como filas independientes.

La dependencia más allá de 14 días, clientes/grupos sin ID, la estacionalidad y solo seis meses limitan supuestos de estacionariedad e intercambiabilidad local de bloques. No se garantiza cobertura frecuentista del 95%, independencia de bloques reales o extrapolación prospectiva. Son intervalos de remuestreo ilustrativos, no una certificación de producción. Las réplicas y su tamaño se exportan, sin elegir las favorables.

## 8. Seguimiento, trazabilidad y limitaciones

Auditoría de metadatos posterior a congelar decisiones: **{'cierre_asumido_exclusivo': '2018-12-01', 'cierre_operativo_acreditado': None, 'max_disponibilidad_proxy': '2017-09-15', 'estados_proxy_no_anteriores_cierre': 0, 'filas_retiradas': 0, 'no_garantiza_integridad_real': True}**. El último estado + un día frente al cierre asumido puede comprobar coherencia del archivo, pero no acredita cuándo se conoció/ingirió cada resultado ni ausencia de reservas o actualizaciones faltantes. No se retiran filas ni se modifica v3 por esa auditoría.

Se declaran expresamente: (1) v3 retrospectivo por llegada, con altas aproximadas solapadas; (2) ausencia de snapshots iniciales acreditados de los 14 predictores; (3) alta=llegada−lead_time y disponibilidad=último estado+un día son aproximaciones; (4) no hay cierre operativo PMS documentado, y 01/12/2018 es supuesto; (5) exposición previa de parte de prueba al desarrollo v2 y al EDA global; (6) selección de modelo/política con validación reutilizada; (7) costes/capacidad reales y eficacia de contacto desconocidos; (8) necesidad del lote mensual completo para priorizar, sin simulación de atención al alta o cola online. Se conservan duplicados y no hay ID real de reserva/cliente, lo que también limita incertidumbre y unidades operativas.

No se presenta como validación prospectiva real, rentabilidad, efecto causal o autorización de despliegue. Priorizar no significa cancelar, penalizar o tratar adversamente de forma automática. El resultado corresponde a la especificación académica congelada y población observada; no generaliza sin evidencia adicional.

## 9. Archivos y reproducción sin nueva evaluación

Nuevos: src/final_evaluation.py, tests/test_final_evaluation.py, notebooks/evaluacion_final.ipynb y este informe. Evidencia evaluacion_9_*: plan, preflight, copia/hash del código ejecutado, recibo, scores/decisiones congelados sin etiqueta, etiquetas en archivo separado, métricas, comparación, meses, hoteles, composición, bins, réplicas e intervalos y verificación. Se generan dos figuras. Solo se muestran agregados en informe/notebook; CSV de reproducción usa IDs técnicos, sin nombres/contactos personales.

Se actualizan README y ejecutor; no hay nuevas dependencias ni cambios en archivos congelados de fase 8, datos originales o manifiesto v3. Las pruebas comprueban separación, bloqueo de fit, cuota mensual/desempate, coherencia de métricas y bloques completos, sin entrenar modelos. La reejecución del notebook valida checkpoints y reproduce presentación desde scores/resultados guardados; no vuelve a llamar predict_proba sobre prueba.

La especificación/modelo congelados siguen con SHA **e9ad0d974e4bfc4a7f377a1b3a5163468f87a8441a7dd23bd978e9d2b65721c6** / **460183467c6c0d783e8e05efe4b560ffce61aadf16fe272e4205b9f615b7867a**. No se decide ningún ajuste con los resultados. Se espera revisión antes de cualquier fase posterior, sin preparar presentación final.

**Fin exclusivo de fase 9. No se avanza a fase 10 sin autorización.**
