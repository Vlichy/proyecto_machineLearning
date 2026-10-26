# Auditoría del proyecto recuperado frente al enunciado de Machine Learning

Fecha: 26/10/2026. Alcance: recuperación verificada y revisión estática de datos, código, diez notebooks y salidas guardadas, tablas, gráficos, registros y entregables. No se han entrenado modelos, cargado el joblib para ejecutarlo, repetido inferencias de test, ejecutado notebooks ni alterado resultados.

## Dictamen

El proyecto original se ha recuperado íntegramente respecto a sus inventarios comprobados. Hay trabajo reutilizable suficiente para preparar la entrega, pero **la entrega actual no cumple todavía todo el formato y contenido solicitados**. Los bloqueos principales son: notebook único inexistente; ejecución limpia no comprobada y con obstáculos estáticos; dos waterfall ausentes; SHAP únicamente histórico de XGBoost v2; acciones de negocio insuficientemente explícitas por sección del EDA; curva ROC ausente del PowerPoint aunque existe en la memoria y como PNG.

La comparación y la búsqueda de hiperparámetros existen, pero la búsqueda corresponde a v2, protocolo descartado para la decisión final. Eso acredita trabajo de optimización histórico, no una optimización del modelo ganador v3. No se deben mezclar ambas evidencias.

## Fuentes y criterio

Los requisitos se toman del texto aportado por el usuario, que transcribe el enunciado oficial, y de la solicitud actual. No se ha aportado aquí un documento oficial independiente para autenticar la transcripción. El notebook básico del profesor es material de referencia, no una rúbrica ni una solución completa. La plantilla de presentación es opcional; el vídeo solo procede si no hay exposición en clase. La memoria PDF no es un requisito obligatorio en los textos facilitados.

Estados: **Cumple** significa evidencia observable del punto concreto; **Parcial** significa contenido existente con una carencia identificada; **Falta** significa ausencia localizada; **No verificado** significa que no se realizó la comprobación necesaria. No se equipara una salida guardada a una nueva ejecución correcta.

## Matriz de cumplimiento

| Requisito | Estado | Evidencia real y límite | Acción propuesta, no ejecutada |
|---|---|---|---|
| Problema y objetivos de negocio | Cumple | README; memoria, secciones 1–2; PowerPoint, diapositivas 2–3 | Reutilizar narrativa abreviada |
| Dataset y carga | Cumple en proyecto | `data/raw/hotel_bookings.csv`, 119.390 × 32; notebook EDA | Usar CSV original y explicar diferencia de Excel |
| Cancelaciones por hotel | Cumple análisis | `notebooks/eda.ipynb`, celda 15; `reports/figures/02_objetivo_hoteles.png`; tasas y volúmenes | Añadir acción explícita y responsable |
| Cancelaciones por mes | Cumple análisis | EDA, celda 30; `08_evolucion_temporal.png` y `09_estacionalidad.png`; mes de llegada, cobertura parcial 2015/2017 | Añadir decisión de planificación y advertencia de cobertura |
| Cancelaciones por canal | Cumple análisis | EDA, celda 21; `05_distribution_channel.png`; agrupación con denominador por canal | Formular acción de seguimiento comercial |
| Lead time y cancelación | Cumple análisis | EDA, celda 18; `04_tasas_antelacion.png`; bandas y tasas | Convertir asociación en hipótesis operativa comprobable |
| ADR medio canceladas/no canceladas | Cumple cálculo; presentación parcial | EDA, celda 18: `groupby(is_canceled)[[lead_time, adr]].agg(...)` incluye media; `03_antelacion_adr.png` compara distribuciones, no medias | Mostrar las dos medias directamente y una conclusión propia |
| Una conclusión accionable por sección EDA | Parcial | Hay interpretaciones y conclusiones globales, pero varias se limitan a asociaciones, cautelas y decisiones técnicas | Redactar acción concreta por cada uno de los cinco apartados |
| Limpieza y nulos | Cumple diseño | `src/cleaning.py`, `src/preparation.py`; cuatro niños desconocidos, país y IDs ausentes; no se eliminan filas indiscriminadamente | Explicar brevemente en el notebook único |
| Feature engineering justificado | Parcial documental | `src/features.py`: `total_nights` y `children_missing`; fase 3 justifica simplificación y desconocidos | Expresar una o dos frases de negocio por cada variable; no inventar features obligatorias |
| Exclusión de leakage directo | Cumple implementación estática | Lista cerrada de 14 predictores; `reservation_status` y fecha solo en auditoría/metadatos | Conservar separación explícita |
| Disponibilidad al reservar | Limitación declarada | Se excluyen 12 campos inciertos; los 14 admitidos siguen bajo supuesto de snapshot inicial no acreditado | Mantener limitación, no certificar ausencia absoluta de leakage histórico |
| Pipelines y fit solo train | Cumple código y evidencia guardada | `src/preprocessing.py`, `baseline.py`, `comparison.py`: imputación, OHE, escala en logística y comprobación contra train | Reutilizar fábricas puras sin las entradas históricas que escriben resultados |
| Partición temporal | Cumple como retrospectiva | `src/splitting.py`, `temporal_split_v3`; manifiesto y tablas v3; embargos | Presentar límites y fechas en tabla compacta |
| Baseline logístico | Cumple | Código y resultados v1/v2/v3; v3 en `protocolo_7_1_metricas.csv` | Usar v3 como referencia del relato principal |
| Comparación de algoritmos | Cumple con ámbitos distintos | Cinco algoritmos en v2; logística y XGBoost iniciales en v3 | Comparar solo poblaciones comunes; v2 como historia |
| Optimización de hiperparámetros | Cumple históricamente; parcial para relato final | `src/optimization.py`, `RandomizedSearchCV`, 54 ajustes internos y dos ajustes finales; solo v2 | Etiquetar protocolo descartado; decidir antes de construir si basta esta demostración o se autoriza un ejercicio adicional en train v3 |
| Gestión del desbalanceo | Parcial | Prevalencias, AP/PR, precision/recall, costes ilustrativos y capacidad mensual; logística `class_weight=None`; no consta comparación de pesos/remuestreo | Justificar expresamente la estrategia sin balanceo o autorizar estudio solo train; no exigir SMOTE como si figurara en el enunciado |
| ROC-AUC, F1, precision, recall en test | Cumple para política definida | `evaluacion_9_metricas.json`: AUC con score; precision/recall/F1 con prioridad mensual | Mantener etiquetas “política”; no presentarlos como umbral 0,5 |
| Clasificación a umbral fijo en test | No localizada como tabla final separada | Hay métricas a 0,5 en validación v3; test final informa la política top-k | Solo añadir si se acuerda necesario, calculando desde scores guardados sin nueva inferencia; no es un umbral exigido expresamente en el texto |
| FP y FN | Cumple | Fase 9: 1.224 FP, 7.796 FN; interpretación como seguimiento innecesario/cancelación sin prioridad | Incluir ambos visiblemente en la presentación |
| ROC y precision-recall de test | Cumple en proyecto/memoria | `entrega_final/figuras/04_curvas.png`; constructor editorial usa scores y etiquetas congelados | Incorporar ROC al notebook y PowerPoint |
| Calibración, meses y hoteles | Cumple análisis descriptivo | Brier/bins, tablas por mes y hotel; no hay calibrador final | Mantener alcance descriptivo |
| SHAP summary | Cumple solo histórico | `explicabilidad_7_shap_resumen.png`, XGBoost v2 | No atribuir a logística; falta equivalente del ganador |
| Dos SHAP waterfall | Falta | Cuatro casos en `explicabilidad_7_casos.csv`; `explicabilidad_7_locales.png` usa `ax.barh`, no waterfall | Crear dos waterfall del modelo final, con autorización posterior |
| Perfil de mayor riesgo del modelo ganador | Parcial | Perfil descriptivo y explicación XGBoost v2, sin SHAP de logística v3 | Explicar el ganador con su transformador y train v3 |
| Correspondencia SHAP/modelo | Cumple honestidad documental | README, memoria y diapositiva 8 diferencian expresamente XGBoost v2 de logística final | Conservar esa distinción |
| Notebook único | Falta | Diez notebooks originales; no hay notebook integral de entrega | Construir solo después de aprobar propuesta |
| Ejecución limpia de arriba abajo | No verificada; obstáculos detectados | Diez esquemas válidos y 64 celdas de código con ejecución guardada sin errores; hashes históricos impiden reejecución directa de algunas entradas actuales | Verificar en copia aislada del futuro paquete, con autorización |
| Comentarios explicativos | Cumple en fuentes existentes | Registro integrado: 454 comentarios y 64 celdas Markdown; fuentes recuperadas coinciden con hashes registrados | Seleccionar explicaciones pertinentes, sin trasladar toda la cronología |
| Celda final de conclusiones integral | Falta en notebook único | Hay conclusiones por fase, memoria y presentación; no existe el notebook solicitado | Última celda Markdown con conclusiones y próximos pasos |
| PowerPoint | Parcial | 15 diapositivas, 15 notas; problema, objetivos, modelo, acción, límites y futuro | Añadir ROC y variables del ganador, reforzar FN/insights |
| Vídeo | Condicional | Solo si no se presenta en clase; situación no acreditada | No producir ni incluir por defecto |

## Datos originales y Excel del profesor

Se compararon todas las filas y columnas por nombre y posición de fila. Ambos archivos tienen 119.390 filas y 32 columnas; el orden físico de columnas difiere (`agent` y `company` aparecen en otra posición en Excel). Se normalizaron solo en memoria números almacenados como texto, ausencias y fechas Excel; tolerancia numérica absoluta 1e-10, sin tolerancia relativa. No se guardó un dataset normalizado.

**Única columna con diferencias de valores: ADR, en 230 filas.** Coinciden con las 230 celdas Excel numéricas con formato de fecha `d.m`/`dd.mm`. Ejemplos:

| Celda Excel | ID de fila del CSV, base cero | ADR original | Valor almacenado en Excel |
|---|---:|---:|---:|
| AB2847 | 2845 | 24,8 | 46258 |
| AB2873 | 2871 | 26,1 | 46048 |
| AB2876 | 2874 | 22,5 | 46164 |

El CSV original tiene ADR entre −6,38 y 5.400. Su media bruta es **99,987693** en no canceladas y **104,964333** en canceladas. Son descriptivos del archivo completo: incluyen el negativo y extremos, no implican causalidad ni son resultados del modelo. El EDA original ya muestra esas medias en tabla, aunque no las destaca en un gráfico específico.

Coinciden target (75.166/44.224), ausencias (children 4, country 488, agent 16.340, company 112.593) y duplicados adicionales (31.994). El CSV conserva SHA-256 `7c2ae42a7353905ea136e5c2287f17c92c5435826598bfbb8491c6f0c7b1fc06`. No se reemplazó por el Excel. Los datos apoyan equivalencia del contenido salvo esas conversiones, no una cadena de procedencia o licencia certificada.

## Temporalidad: qué se corrigió y qué sigue limitado

V1 separaba por llegada menos lead time y madurez basada en máximo de salida prevista/estado final más un día; producía selección condicionada al seguimiento y no cerraba adecuadamente test. V2 usa estado final más un día y un cierre supuesto, pero aún selecciona por disponibilidad del desenlace: cambia el tipo de reserva elegible. La auditoría v3 identifica ese sesgo y pasa a cohortes completas de llegada, con controles comunes por bloque.

| Partición v3 | Llegadas | Filas |
|---|---|---:|
| Train | 01/07/2015–30/06/2016 | 49.157 |
| Embargo | 01/07/2016–31/08/2016 | 9.635 |
| Validación | 01/09/2016–31/12/2016 | 19.911 |
| Embargo | 01/01/2017–28/02/2017 | 7.858 |
| Test | 01/03/2017–31/08/2017 | 32.829 |

Se comprobó por lectura y unión uno-a-uno del manifiesto con metadatos: 119.390 IDs únicos, los tamaños anteriores y **cero grupos de duplicados exactos cruzando particiones**. El código v3 asigna por llegada sin consultar target ni fecha de estado por fila. El seguimiento de train/validación se audita a nivel de bloque; no se rescatan o retiran filas según su resultado.

Los embargos dejan al menos 43/45 días respecto al proxy máximo de disponibilidad de train/validación, según las tablas guardadas. No prueban disponibilidad real de PMS. El cierre de test 01/12/2018 es supuesto; no hay snapshots iniciales ni creación observada. Los proxies de creación se solapan entre cohortes. Train contiene un año; validación cuatro meses y test seis, con mezcla y temporada distintas. Por ello **no es validación prospectiva al reservar**.

Test v3 tuvo exposición previa: la tabla `protocolo_7_1_exposicion_prueba.csv` identifica 319 filas de train v2 y 2.718 de validación v2, además del EDA global. Son **3.037 filas previamente usadas en desarrollo v2**, no todo el test ni una prueba totalmente independiente. Declarar esta limitación es necesario; no puede corregirse renombrando archivos o prometiendo una ejecución limpia.

## Comparación, optimización y selección final

Cinco algoritmos se compararon sobre la misma población v2: logística, árbol de decisión, Random Forest, XGBoost y LightGBM. AUC de validación: 0,820718; 0,786223; 0,841311; 0,858927; 0,848655, respectivamente. La búsqueda de XGBoost y LightGBM usó nueve configuraciones por familia —referencia inicial y ocho muestras— y tres folds temporales internos, con preprocesamiento ajustado por fold. La selección interna se hizo por AP media y AUC para desempate. No mejoró la validación externa v2: XGBoost optimizado AUC 0,855129; LightGBM optimizado 0,843851. Todo ello es histórico y comparte el problema de población de v2.

En validación v3 se comparan únicamente logística y XGBoost iniciales: AUC 0,794590 frente a 0,830592. La logística final **no gana por AUC**. A la capacidad hipotética común del 20% mensual obtiene 3.407 TP frente a 3.375, con 3.980 prioridades para ambos; se añade menor complejidad. Es una diferencia pequeña de 32 detecciones, dependiente de la capacidad, no superioridad estadística demostrada ni beneficio económico medido.

El desbalanceo es moderado (37,04% global), no obliga automáticamente a remuestrear. Hay métricas apropiadas y priorización por capacidad, pero falta una justificación explícita y compacta de por qué se mantiene `class_weight=None` y qué consecuencias tiene. La política top-k gestiona recursos; no equivale a balancear el entrenamiento.

## Resultados finales preservados

| Concepto | Valor definitivo v3 |
|---|---:|
| Modelo | Regresión logística inicial congelada |
| Test | 32.829 |
| Priorizadas | 6.564 |
| TP / FP / FN / TN | 5.340 / 1.224 / 7.796 / 18.469 |
| Precision de política | 81,352834% |
| Recall de política | 40,651644% |
| F1 de política | 0,542132 |
| ROC-AUC del score | 0,780186 |
| Average Precision | 0,741601 |
| Brier | 0,185340 |

La cuota es `n_mes*20//100`, ambos hoteles juntos; usa score descendente y desempates SHA256 de `42|ID`, luego ID. Requiere lote mensual completo, no una cola online. La matriz evalúa prioridad, no clasificación a 0,5. Las cifras se leyeron de resultados guardados y se verificaron sus hashes; no se repitió inferencia ni se generaron nuevos resultados de test.

## Interpretabilidad y presentación

Se inspeccionaron el summary SHAP y el gráfico de cuatro casos. El primero es un beeswarm real sobre columnas transformadas de XGBoost v2, con mayor peso de país/antelación; el segundo son barras horizontales de contribución respecto a cero. Que haya cuatro explicaciones locales no cumple el formato de dos waterfall. No aparece llamada a waterfall en el constructor. Tampoco hay SHAP de logística v3.

Para explicar el ganador se necesitaría una futura implementación SHAP apropiada para su clasificador lineal, usando exactamente su preprocesamiento y nombres transformados, con referencia obtenida solo de train v3; summary y al menos dos waterfall con base, contribuciones y salida en unidades declaradas. Preferir reservas de validación evita volver a tocar test. No se generan aquí explicaciones nuevas ni se atribuye al ganador el perfil histórico de XGBoost.

Se revisó el XML de las 15 diapositivas y sus notas, y una lámina de las 15 vistas finales guardadas. El PowerPoint tiene problema, objetivos, EDA breve, preparación, protocolo, comparación, ganador, política, métricas, variación, límites y conclusiones. **No contiene una curva ROC**, aunque `04_curvas.png` y la página 11 de la memoria sí la contienen. La diapositiva 9 presenta barras de AUC/AP, que no sustituyen a la curva. La importancia de variables se menciona como SHAP histórico en diapositiva 8; falta una explicación visible del ganador. FN figura en notas de diapositiva 12 y en conclusiones/notas, pero conviene mostrar explícitamente las 7.796 cancelaciones no priorizadas.

La memoria tiene 15 páginas, con texto extraíble y vistas guardadas revisadas en conjunto. No se reexportaron PDF/PPTX ni se hizo apertura interactiva en PowerPoint. Esta inspección no equivale a una nueva revisión tipográfica exhaustiva a escala completa ni autentica por sí sola el vínculo entre cada vista histórica y el archivo; sus bytes y los entregables sí coinciden con registros de recuperación.

## Reproducibilidad y dependencias

Los diez notebooks tienen esquemas nbformat válidos y, en total, 64 celdas de código con contador y sin salidas de error guardadas. Esto acredita estructura y evidencia de ejecuciones anteriores, **no ejecución actual completa**. Las once dependencias directas de `requirements.txt` coinciden con las instaladas en `.venv` (Python 3.14.5); no existe un lock completo de transitivas. No se probó instalación limpia ni disponibilidad futura de esas versiones.

Hay bloqueos concretos: `final_evaluation.preflight` comprueba hashes de fuentes originales; cinco fuentes actuales (`decision_policy.py`, `baseline.py`, `features.py`, `preprocessing.py`, `comparison.py`) difieren porque se añadieron comentarios. Sus respaldos y registro documental sí coinciden. Además, el recibo comprueba el hash del código ejecutado. Reejecutar directamente `evaluacion_final.ipynb` con fuentes comentadas encuentra esas protecciones; no debe desactivarlas ni reescribir el recibo. `seleccion_final.ipynb` vuelve a ajustar modelos de desarrollo; otros notebooks descubren toda la batería de pruebas, algunas con entrenamiento y escrituras.

Los notebooks dependen de `src/`, CSV preparado, informes, manifiestos, imágenes y artefactos que no acompañarían a un único archivo copiado. Varias entradas escriben informes/resultados y enlazan referencias externas del curso. Concatenarlos conservaría esas dependencias y mezclaría protocolos. La futura entrega debe tener funciones autónomas y eliminar dependencias del historial, sin modificar los originales.

## Prioridades antes de entregar

1. Aprobar la propuesta de cuatro archivos y el alcance de cualquier nuevo cálculo futuro; preservar recuperación y originales.
2. Construir el notebook único en un área separada, con narrativa v3 y conclusiones por EDA, comentarios y celda final.
3. Resolver la demostración de optimización y desbalanceo sin reutilizar test para seleccionar decisiones; no afirmar que v3 ya fue optimizado.
4. Añadir SHAP del ganador y dos waterfall; las barras históricas no sustituyen el requisito.
5. Preparar una copia de la presentación con ROC, importancia del ganador, FP/FN e insights accionables; mantener originales intactos.
6. Ejecutar el futuro paquete en entorno limpio aislado solo con autorización para entrenamiento/evaluación requeridos; verificar que no depende del árbol de desarrollo y documentar tiempos/versiones. Hasta entonces, reproducibilidad no verificada.
7. Confirmar autoría académica y exposición/vídeo; retirar únicamente en la futura copia de entrega los avisos obsoletos de “enunciado no localizado”. No modificar ahora README, memoria o presentación histórica.

No se ha construido `entrega_profesor`, no se han corregido las carencias ni iniciado nuevos experimentos. Véase [propuesta_entrega_reducida.md](propuesta_entrega_reducida.md).
