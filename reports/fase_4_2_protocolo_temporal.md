# Fase 4.2 — Corrección del protocolo temporal y validación de datos

Fecha: 18 de octubre de 2026. Versión activa: **v2_estado_fechado_aproximado**. Se termina exclusivamente la fase 4.2. Las tablas generadas usan punto decimal y coma de miles. No se entrenan algoritmos avanzados, optimizan parámetros ni selecciona umbral final.

## 1. Alcance y problemas del protocolo v1

Se revisaron fase_3_preparacion.md, fase_4_baseline.md, fase_4_1_auditoria.md, splitting.py, baseline.py y audit_baseline.py. V1 mezclaba una cota basada en salida prevista y estado final, que retrasaba cancelaciones ya fechadas, con prueba sin cierre global. Sus 30.386 apartadas tenían composición y antelación distintas. La selección por seguimiento limitaba la interpretación de métricas y faltaba una fecha de observación de resultados explícita.

La corrección reduce una exclusión innecesaria y hace explícita la protección de prueba. **No transforma este archivo en una evaluación temporal estricta:** siguen faltando logs de alta, versiones iniciales e ingestión. La modalidad seleccionada es una simulación retrospectiva de disponibilidad registrada, bajo supuestos expresos.

## 2. Cuatro fechas y evidencia

| Concepto | Uso |
|---|---|
| Alta aproximada | llegada prevista − lead_time. Se usa para ordenar cohortes, sin hora ni historial del alta. |
| Llegada prevista | calendario del viaje, distinto del alta y del resultado. Puede ser posterior al corte aun si ya se registró cancelación. |
| Disponibilidad aproximada de resultado | fecha del último estado + un día de margen. No acredita cuándo se conoció/publicó realmente el resultado. |
| Cortes de decisión/observación | 01/07/2016 para fit; 01/01/2017 para validación previa a prueba; 01/12/2018 como cierre retrospectivo asumido de prueba. |

La semántica y la limitación de snapshots se contrastaron en la [fuente primaria](https://pmc.ncbi.nlm.nih.gov/articles/PMC6297060/). El estado fechado solo se usa como metadato: no es predictor, ni se codifica o imputa en X. La fuente no permite certificar que los 14 campos sean valores del instante inicial. Consultar [nota de fuentes](protocolo_4_2_fuentes.md).

**Tres conceptos de cierre que no deben confundirse:**

- Máximos observados del CSV: llegada 2017-08-31, último estado 2017-09-14, proxy de disponibilidad 2017-09-15.
- Cierre asumido: corte exclusivo **01/12/2018**, anclado al mes siguiente a la publicación de la referencia (29/11/2018), no elegido por métricas o por el último caso de prueba.
- Cierre realmente acreditado del PMS/local: **desconocido**. Publicación y máximo de fechas no acreditan integridad del seguimiento, ingestión o extracción.

La fecha asumida no se presenta como histórica del hotel. Permite un escenario retrospectivo reproducible con margen posterior a los estados observados. El hecho de pasar su comprobación matemática no garantiza que no falten reservas o actualizaciones.

## 3. Alternativas consideradas antes de ajustar el baseline

| Alternativa | Valoración |
|---|---|
| Mantener max(salida prevista, estado)+1 | Retrasa incluso cancelaciones anteriores; no resuelve cierre de prueba. Se conserva solo para historia. |
| Añadir todas las apartadas y usar sus resultados finales en cada corte | Rechazada: incorporaría etiquetas posteriores a decisiones de entrenamiento/selección. |
| Dividir solo por llegada | No reproduce predicción al alta: puede entrenar con resultados posteriores al proxy de reservas evaluadas. Cambiaría el objetivo de evaluación. |
| Limitar lead_time para conseguir cohortes cerradas | Podría servir con un horizonte real de negocio y seguimiento prefijado. No se impone ahora un horizonte arbitrario que retire reservas difíciles. |
| Cohortes completas por alta con seguimiento acreditado | Preferible para validación estricta, pero requiere logs/fechas de cierre y datos adicionales; algunas cohortes observadas tienen estados hasta 2017. |
| Estado fechado + margen, con cierre declarado y pendientes explícitas | Seleccionada como aproximación disponible, manteniendo cortes y prueba; se reconoce selección por resultados registrados y riesgo de instantánea. |

No se tomó la decisión mirando métricas del nuevo baseline o de prueba. Las reglas, manifestación de supuestos y asignaciones se guardaron primero.

## 4. Reglas definitivas para este ejercicio aproximado

`meta_label_available_proxy = reservation_status_date + 1 día`. El margen fijo no se aprende ni se ajusta. `meta_label_available_after` del CSV preparado conserva la cota v1 como metadato histórico y **no dirige la división v2**.

- Entrenamiento: proxy de alta < 01/07/2016 y disponibilidad proxy < 01/07/2016.
- Validación: 01/07/2016 <= proxy de alta < 01/01/2017 y disponibilidad proxy < 01/01/2017.
- Prueba reservada: proxy de alta >= 01/01/2017 y disponibilidad proxy < 01/12/2018 asumido.
- Si una fila no cumple disponibilidad al corte que le corresponde, se asigna a no_madura_entrenamiento, no_madura_validacion o no_madura_prueba. Estos nombres significan no elegible según el proxy, no desconocimiento real demostrado.

Las desigualdades son estrictas. Un estado del día inmediatamente anterior al corte puede seguir pendiente por el margen, deliberadamente conservador. No se añaden a entrenamiento etiquetas fechadas después del corte. No se desplazan pendientes a otros periodos para aprovechar sus resultados futuros. No se permite solapamiento de IDs o grupos exactos. Las fechas de llegada sí pueden superponerse, porque una reserva para una llegada futura puede haberse cancelado antes de entrenar.

## 5. Tamaños, fechas reales y clases

| particion | registros | no_canceladas | canceladas | tasa_cancelacion | lead_time_mediana |
| --- | --- | --- | --- | --- | --- |
| entrenamiento | 54,164 | 31,090 | 23,074 | 42.60% | 68.0000 |
| validacion | 18,097 | 10,344 | 7,753 | 42.84% | 37.0000 |
| prueba_reservada | 26,565 | 18,163 | 8,402 | 31.63% | 40.0000 |
| no_madura_entrenamiento | 12,089 | 9,346 | 2,743 | 22.69% | 185.0000 |
| no_madura_validacion | 8,475 | 6,223 | 2,252 | 26.57% | 163.0000 |
| no_madura_prueba | 0 | 0 | 0 | nan% | nan |

| particion | proxy_min | proxy_max | llegada_min | llegada_max | disponibilidad_proxy_max |
| --- | --- | --- | --- | --- | --- |
| entrenamiento | 2013-06-24 | 2016-06-29 | 2015-07-01 | 2017-05-31 | 2016-06-30 |
| validacion | 2016-07-01 | 2016-12-30 | 2016-07-01 | 2017-08-28 | 2016-12-31 |
| prueba_reservada | 2017-01-01 | 2017-08-31 | 2017-01-01 | 2017-08-31 | 2017-09-15 |
| no_madura_entrenamiento | 2015-02-20 | 2016-06-30 | 2016-06-14 | 2017-08-29 | 2017-08-31 |
| no_madura_validacion | 2016-07-01 | 2016-12-31 | 2016-12-13 | 2017-08-31 | 2017-09-11 |
| no_madura_prueba | nan | nan | nan | nan | nan |

Se conservan **119.390 filas**, sin modificar ni original ni preparado. Entrenamiento representa los doce meses de llegada en ambos hoteles, aunque no es una muestra completa de todas las altas. El intervalo de proxy anterior a 2015 no representa cobertura íntegra de ese periodo: el archivo está seleccionado por llegadas.

Prueba mantiene exactamente los **26.565 IDs** de v1. Ninguno pasa a desarrollo. La regla de cierre se aplica aunque, con el supuesto elegido, no quede ningún caso pendiente en prueba. Esto no autoriza una evaluación de prueba todavía; aquí solo se auditan tamaños, fechas y clases permitidas.

## 6. Qué ocurre con las 30.386 apartadas

Se reincorporan **9,822 (32.32%)** y permanecen pendientes **20,564**. El desglose es:

| destino | reincorporadas | canceladas | no_canceladas | lead_time_mediana |
| --- | --- | --- | --- | --- |
| entrenamiento | 5,736 | 5,734 | 2 | 250.0000 |
| validacion | 4,086 | 4,086 | 0 | 158.0000 |

El resto es 12.089 del periodo de entrenamiento y 8.475 del de validación. La tabla de transición completa está en protocolo_4_2_transicion.csv. La distribución mensual de las apartadas está en protocolo_4_2_apartadas_por_mes.csv; resumen por trimestre:

| grupo_v1 | trimestre_proxy | reservas | reincorporadas | pendientes |
| --- | --- | --- | --- | --- |
| no_madura_entrenamiento | 2015Q1 | 60 | 0 | 60 |
| no_madura_entrenamiento | 2015Q2 | 27 | 2 | 25 |
| no_madura_entrenamiento | 2015Q3 | 1,622 | 1,234 | 388 |
| no_madura_entrenamiento | 2015Q4 | 2,283 | 714 | 1,569 |
| no_madura_entrenamiento | 2016Q1 | 6,842 | 2,509 | 4,333 |
| no_madura_entrenamiento | 2016Q2 | 6,991 | 1,277 | 5,714 |
| no_madura_validacion | 2016Q3 | 2,843 | 1,009 | 1,834 |
| no_madura_validacion | 2016Q4 | 9,718 | 3,077 | 6,641 |

V1 había apartado reservas con mediana de antelación 200 días frente a 55 en entrenamiento, y 161 frente a 24 en validación. En v2 las medianas de las incluidas son 68 y 37, mientras las pendientes siguen en 185 y 163 días. **El sesgo no desaparece.** La nueva inclusión favorece cancelaciones registradas pronto: las 4.086 añadidas a validación son canceladas, y casi todas las añadidas a entrenamiento también. Por tanto, la prevalencia de validación cambia del 26.17% al 42.84%, no por el algoritmo sino por población/disponibilidad.

La regla de observación es más coherente con un sistema que solo puede aprender resultados registrados, pero la población con resultado observado a tiempo no es la cohorte completa de reservas. Cancelaciones tempranas y estancias aún abiertas tienen mecanismos de disponibilidad diferentes. No se afirma haber corregido toda censura/supervivencia; ni se interpretará una mejora de métricas como utilidad de negocio recuperada.

## 7. Comprobaciones de disponibilidad y cierre

Cada resultado usado en fit o selección cumple la fecha proxy antes de su corte. Se verifica también disponibilidad posterior al proxy de alta, fechas válidas, alineación de filas, unicidad de asignación y grupos, y condición de prueba. Eso valida la regla implementada, no la disponibilidad real sin logs.

Sensibilidad de prueba usando solo metadatos, sin cambiar la regla seleccionada por esos conteos:

| corte_exclusivo_escenario | cumplen_proxy | no_cumplen_proxy | acreditado | seleccionado |
| --- | --- | --- | --- | --- |
| 2017-09-01 | 26,129 | 436 | False | False |
| 2017-09-15 | 26,563 | 2 | False | False |
| 2018-12-01 | 26,565 | 0 | False | True |

Estas cifras se refieren a estado+1, no a salida prevista+estado de la auditoría anterior. No se convierten máximos o escenarios en cierre acreditado. La instantánea de predictores puede ser posterior al alta; la referencia primaria refuerza esta advertencia. La semilla o el aislamiento de preprocesadores no resuelven esa limitación de datos.

## 8. Baseline recalculado únicamente en validación v2

Mismo pipeline, 14 predictores y configuración: mediana, escalado, categoría de ausencia y OneHotEncoder con desconocidas ignoradas; LogisticRegression(C=1, solver=lbfgs, max_iter=2000, class_weight=None, random_state=42), umbral 0.5. No se optimizan hiperparámetros ni umbral. La reproducción verifica estadísticas, vocabularios y número de filas de fit exclusivamente contra entrenamiento.

Fit: 54,164 filas. Validación: 18,097. Iteraciones hasta converger: 111. Prueba no se transforma, predice o evalúa en esta ejecución. No se serializan modelos.

| protocolo | modelo | accuracy | precision | recall | f1 | roc_auc |
| --- | --- | --- | --- | --- | --- | --- |
| v1_historia_no_comparable_como_ranking | mayoritario | 0.7383 | 0.0000 | 0.0000 | 0.0000 | 0.5000 |
| v1_historia_no_comparable_como_ranking | regresion_logistica | 0.7443 | 0.5336 | 0.1841 | 0.2737 | 0.7004 |
| v2_vigente | mayoritario | 0.5716 | 0.0000 | 0.0000 | 0.0000 | 0.5000 |
| v2_vigente | regresion_logistica | 0.7471 | 0.8076 | 0.5377 | 0.6456 | 0.8207 |

**La tabla es una comparación descriptiva de protocolos, no un ranking de algoritmos. Las métricas v1 quedan obsoletas para comparar modelos sobre v2.** Cambian entrenamiento, prevalencia y población evaluada, mientras el algoritmo permanece fijo. Los umbrales explorados en 4.1 tampoco se trasladan como decisiones al protocolo nuevo.

Matriz de logística v2, filas reales y columnas predichas:

| Real / predicción | No cancela | Cancela |
|---|---:|---:|
| No cancela | 9,351 | 993 |
| Cancela | 3,584 | 4,169 |

Precision 80.76%, recall 53.77% y ROC-AUC 0.8207 se refieren exclusivamente a la validación elegible de esta aproximación. No certifican capacidad al alta ni calibración, rentabilidad o efecto causal de acciones. [Matrices de validación](figures/protocolo_4_2_confusion_validacion.png) y [destino de apartadas](figures/protocolo_4_2_reincorporacion.png).

## 9. Trazabilidad, cambios y pruebas

- splitting.py contiene el protocolo v2 vigente y temporal_split_legacy explícito para reproducir v1.
- temporal_protocol.py implementa/reproduce fase 4.2; tests/test_temporal_protocol.py añade pruebas de fronteras, margen, cierre de prueba, grupos, alineación, errores y no mutación.
- reports/particiones_temporales.csv y division_temporal.json son v2; estado_protocolo.json identifica la versión vigente.
- Cinco archivos de resultados/manifiesto v1 y sus hashes están en reports/historico/protocolo_v1. Los informes de fases anteriores conservan su contenido histórico. Métricas y predicciones v2 ocupan los nombres activos, con versión explícita en JSON.
- baseline.py comparte fábrica y fit, pero la carga/reporte del notebook histórico usa v1. Sus reejecuciones se escriben en historico/protocolo_v1/reproduccion, preservando los cinco archivos congelados y sus huellas. audit_baseline.py lee el histórico para mantener reproducible 4.1. El notebook baseline.ipynb conserva salidas históricas y se anota su versión; su código de rutas se adapta sin reejecutar el análisis anterior.
- El nuevo notebook protocolo_temporal.ipynb presenta y ejecuta v2; README documenta resultados, límites y reproducción. No se modifican las dependencias ni el CSV preparado.

Se ejecutan pruebas automatizadas de v1 y v2, verificaciones de integridad y de fit solo en entrenamiento. El registro técnico está en protocolo_4_2_verificacion.json y baseline_verificacion.json. La fuente externa se documenta separadamente, sin copiar datos o código del artículo.

## 10. Limitaciones pendientes y autorización de fase 5

1. No hay cierre operativo acreditado ni primera disponibilidad de resultados. El cierre público asumido permite un ejercicio retrospectivo, no una garantía de exhaustividad del PMS.
2. El alta es aproximada y no hay historial de valores iniciales. La preparación de la fuente no certifica la disponibilidad de los 14 predictores al alta. Mantenerlos conserva comparabilidad de diseño, pero no convierte el modelo en desplegable.
3. Quedan 20.564 pendientes de decisión temporal; la evaluación observada está condicionada a disponibilidad y contiene sesgo. No se reconstruyen reservas con llegadas fuera de la extracción ni IDs reales de cliente/reserva.
4. El EDA previo vio el archivo completo; los duplicados pueden sobreponderar patrones aunque no crucen conjuntos. No se afirma evaluación independiente ni ausencia total de fuga temporal.

**Puede plantearse fase 5 solo como comparación académica exploratoria bajo este contrato aproximado, con estas mismas particiones y evaluación en validación, si el usuario la autoriza.** Para afirmar validez operacional al crear una reserva se requieren datos iniciales y seguimiento acreditado; eso sigue pendiente y no se suple con mejores métricas. Se deja prueba protegida para una evaluación final autorizada, sujeta a esas limitaciones.

**Fin de fase 4.2. No se avanza a fase 5.**
