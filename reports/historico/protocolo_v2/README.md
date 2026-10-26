# Predicción de cancelaciones hoteleras

Proyecto académico para ayudar al responsable de revenue management a identificar reservas con riesgo de cancelación. Objetivo: `is_canceled` (1: cancelada; 0: no cancelada), utilizando datos disponibles al crear la reserva.

**Estado:** fases 1–4.1 completadas; fase 4.2 aplicada y pendiente de revisión. El protocolo activo es **v2_estado_fechado_aproximado**. La disponibilidad se aproxima por fecha del estado + un día y se aplica también a prueba, con cierre retrospectivo asumido declarado. No hay cierre PMS ni snapshots iniciales acreditados: este es un benchmark académico aproximado, no una validación estricta de uso al crear la reserva. No se ha comenzado fase 5.

## Estructura

```text
proyecto_machineLearning/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   ├── raw/hotel_bookings.csv
│   └── processed/hotel_bookings_prepared.csv
├── notebooks/
│   ├── eda.ipynb                     # Análisis y salidas de fase 2
│   ├── preparacion.ipynb             # Ejecutado, con verificaciones de fase 3
│   ├── baseline.ipynb                # Histórico v1; reejecuciones aisladas
│   └── protocolo_temporal.ipynb      # Ejecutado: protocolo y baseline v2
├── src/
│   ├── __init__.py
│   ├── inspection.py
│   ├── run_notebook.py
│   ├── cleaning.py
│   ├── features.py
│   ├── preprocessing.py
│   ├── preparation.py
│   ├── splitting.py
│   ├── baseline.py
│   ├── audit_baseline.py
│   └── temporal_protocol.py
├── tests/
│   ├── test_preparation.py
│   ├── test_baseline.py
│   ├── test_audit_baseline.py
│   └── test_temporal_protocol.py
└── reports/
    ├── fase_1_inspeccion.md
    ├── inspeccion_dataset.json
    ├── verificacion_referencias.json
    ├── fase_2_eda.md
    ├── eda_resumen.json
    ├── eda_auditoria_leakage.csv
    ├── eda_verificacion.json
    ├── fase_3_preparacion.md
    ├── preparacion_resumen.json
    ├── preparacion_verificacion.json
    ├── preparacion_auditoria_variables.csv
    ├── fase_4_baseline.md
    ├── division_temporal.json
    ├── particiones_temporales.csv
    ├── baseline_resultados.json
    ├── baseline_predicciones_validacion.csv
    ├── baseline_verificacion.json
    ├── fase_4_1_auditoria.md
    ├── fase_4_2_protocolo_temporal.md
    ├── protocolo_4_2_config.json
    ├── protocolo_4_2_verificacion.json
    ├── estado_protocolo.json
    ├── historico/protocolo_v1/        # Manifiesto/resultados v1 congelados
    └── figures/                      # EDA, baseline y auditorías
```

Se conservan las convenciones de los proyectos Python y Estadística: datos separados, notebooks narrativos en español y funciones auxiliares sencillas. `data/raw/` contiene el CSV íntegro extraído; el ZIP original permanece en su ubicación de origen. No se guarda una segunda copia del ZIP en el proyecto.

## Entorno y ejecución

Entorno comprobado: **Python 3.14.5**. Desde la raíz:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.inspection
python -m src.run_notebook
```

Si el alias global de Windows `python` no funciona, usar un intérprete Python instalado y accesible para crear el entorno. En esta sesión se creó `.venv` dentro del proyecto y se instalaron allí las dependencias, incluyendo scikit-learn en fase 3; no se modificó el entorno compartido de los proyectos anteriores. `requirements.txt` fija las versiones directas utilizadas; las dependencias transitivas quedan resueltas por pip, por lo que no es un bloqueo exhaustivo del entorno.

Para abrirlo de forma interactiva, usar `notebooks/eda.ipynb` en Jupyter o VS Code y seleccionar el intérprete `.venv/Scripts/python.exe`. El entorno incluye ipykernel y ejecución programática; no instala un servidor/interfaz de Jupyter adicional.

El ejecutor usa nbclient con un kernel local temporal del Python actual, sin registrar kernels globales, y guarda tablas y gráficos dentro del notebook. Crea `.jupyter_runtime/` para configuración/caché local (ignorada por Git). El acceso local entre ejecutor y kernel puede requerir permiso del entorno de ejecución. Se han comprobado ambas rutas:

```powershell
.venv\Scripts\python.exe -m src.run_notebook
.venv\Scripts\python.exe -m src.run_notebook --cwd notebooks
```

También se puede ejecutar manualmente desde la raíz o desde `notebooks/`. El notebook EDA resuelve la ruta relativa a los datos y solo exporta resúmenes, auditoría y figuras a `reports/`. `df` no se modifica; las columnas auxiliares se crean en una copia en memoria. Los cuatro totales de huéspedes desconocidos se mantienen como desconocidos.

La comprobación de referencias utiliza el manifiesto histórico de fase 1: en este equipo se verificaron 105 archivos sin cambios. En otro equipo, los archivos externos no disponibles se informarán como no verificables; no se confunden con comprobaciones satisfactorias. El dataset se verifica siempre por SHA-256.

## Resultados y límites del EDA

119.390 registros y 32 columnas; 44.224 cancelaciones (37,04%). Tasas: City Hotel 41,73%; Resort Hotel 27,76%. Los hallazgos son asociaciones descriptivas. No se deducen causas ni rendimiento de un modelo. Se conservan duplicados, ausencias y anomalías. Faltan el enunciado oficial, prácticas específicas de ML, diccionario temporal y documentación original de descarga/licencia.

La fecha de llegada no es creación ni cancelación. Solo 2016 incluye todos los meses. Como el EDA ha explorado todo este archivo, una futura prueba obtenida de él no será totalmente ajena a la exploración; se deberá documentar y buscar validación externa/prospectiva.

Consultar [informe de fase 1](reports/fase_1_inspeccion.md), [informe de fase 2](reports/fase_2_eda.md), [resumen numérico](reports/eda_resumen.json), [auditoría temporal](reports/eda_auditoria_leakage.csv) y [verificación de ejecución](reports/eda_verificacion.json).

## Preparación de fase 3

Consultar [informe de preparación](reports/fase_3_preparacion.md), [notebook ejecutado](notebooks/preparacion.ipynb), [resumen](reports/preparacion_resumen.json) y [auditoría de variables](reports/preparacion_auditoria_variables.csv).

Desde la raíz, con el entorno local activado:

```powershell
python -m src.preparation
python -m unittest discover -s tests -v
python -m src.run_notebook --notebook preparacion.ipynb
python -m src.run_notebook --notebook preparacion.ipynb --cwd notebooks
```

El CSV preparado conserva 119.390 filas, incluidas 31.994 repeticiones adicionales: 14 predictores, etiqueta y 10 metadatos. Solo se exporta esa versión. Los 4 nulos de niños y 488 de país siguen sin imputar. Estado final y fecha, así como 12 variables inciertas (depósito, ADR, historial, solicitudes, etc.), quedan fuera de X. Se conservan ceros y anomalías con trazabilidad; el ADR negativo se marca como desconocido en memoria y solo su flag se exporta, pues ADR no es predictor.

Para obtener entradas del modelo, **no eliminar solo la etiqueta del CSV**:

```python
import pandas as pd
from src.features import separate_model_data
from src.preprocessing import build_preprocessor

prepared = pd.read_csv("data/processed/hotel_bookings_prepared.csv")
X, y, metadata = separate_model_data(prepared)
preprocessor = build_preprocessor(scale_numeric=True)  # Nuevo, sin ajustar
# No llamar a fit(X) aquí. En fases posteriores, fit solo con X_train,
# dentro del Pipeline del modelo y de cada partición de validación.
```

Los metadatos incluyen información final usada únicamente para auditoría/madurez de etiquetas; están excluidos de X por lista explícita. El conjunto conservador presupone que los campos del plan/origen reflejan su valor inicial, cosa que el archivo no certifica. No se afirma ausencia total de fuga temporal sin documentación.

Propuesta histórica de fase 3: ordenar por llegada − lead_time (proxy, no creación exacta), iniciar validación el 01/07/2016 y prueba el 01/01/2017, exigir madurez de etiquetas antes de cada corte y comprobar duplicados entre conjuntos. La regla de madurez y sus limitaciones están en el informe. La implementación y sus limitaciones se documentan en la fase 4, sin reescribir los resultados históricos de preparación.

El EDA conserva sus resultados históricos; solo se adaptó la última comprobación para que su futura ejecución permita datos preparados ya existentes. No se ha repetido el análisis exploratorio. La integridad actual se verifica en preparación. Los notebooks solo generan sus entregables de fase correspondientes; el de preparación exporta el CSV determinista y sus informes, sin matrices codificadas, modelos o splits.

## División temporal y baseline de fase 4 (histórico v1)

Esta sección conserva los resultados anteriores. Sus métricas no son la referencia para comparar modelos del protocolo v2. Las reejecuciones se escriben en `reports/historico/protocolo_v1/reproduccion/`, sin modificar el archivo congelado ni los resultados activos.

Consultar [informe de baseline](reports/fase_4_baseline.md), [notebook ejecutado](notebooks/baseline.ipynb), [particiones y auditoría v1](reports/historico/protocolo_v1/division_temporal.json) y [resultados completos v1](reports/historico/protocolo_v1/baseline_resultados.json).

```powershell
python -m src.run_notebook --notebook baseline.ipynb
python -m src.run_notebook --notebook baseline.ipynb --cwd notebooks
python -m unittest discover -s tests -v
```

Las fechas teóricas siguen el proxy llegada − lead_time: entrenamiento anterior al 01/07/2016, validación desde entonces hasta antes del 01/01/2017 y prueba desde enero de 2017. Se exige la madurez de la etiqueta en cada corte. El entrenamiento tiene doce meses de llegada representados en ambos hoteles, con junio parcial.

- Entrenamiento: 48.428 reservas (35,81% canceladas).
- Validación elegible: 14.011 (26,17%).
- Prueba reservada: 26.565 (31,63%); solo auditoría de clases/fechas y transformación, sin predicciones ni evaluación.
- Otras 30.386 reservas permanecen en dos grupos sin madurez al corte correspondiente, dentro del CSV original/preparado y el manifiesto. No se borran ni se desplazan para entrenar con resultados futuros.

El manifiesto `particiones_temporales.csv` guarda únicamente fila técnica y grupo; no duplica X en tres archivos. Los cortes y asignaciones se guardan antes de entrenar. Se verifican cobertura exhaustiva, ausencia de cruces y grupos duplicados separados.

Pipeline: preprocesamiento de fase 3 + LogisticRegression(C=1, solver='lbfgs', max_iter=2000, random_state=42, class_weight=None). Medianas, medias y categorías se aprenden solo con entrenamiento; los parámetros no cambian al transformar validación/prueba. Umbral fijo 0,5, sin optimización. max_iter es un límite de convergencia previo, no una búsqueda.

En validación, el trivial tiene accuracy 73,83%, recall 0 y ROC-AUC 0,5. La logística obtiene accuracy 74,43%, precision 53,36%, recall 18,41%, F1 0,2737 y ROC-AUC 0,7004. Detecta 675 cancelaciones, deja 2.992 sin detectar y genera 590 falsas alertas. La mejora de accuracy es pequeña y el recall bajo: estos resultados no justifican declarar el sistema listo para negocio.

Los resultados se refieren al subconjunto con etiquetas maduras y favorecen reservas de menor antelación; no estiman el rendimiento sobre todas las reservas del semestre. Se mantienen las limitaciones de proxy, snapshots iniciales inciertos, duplicados y exposición previa del archivo durante el EDA. Se requiere seguimiento suficiente antes de evaluar prueba. No se ha elegido otro umbral, calibrado probabilidades o entrenado modelos avanzados.

El modelo permanece en memoria y se reproduce con el notebook; no se exporta un artefacto serializado. Los informes de fases anteriores describen sus resultados históricos: que en fase 3 no hubiera splits o modelos sigue siendo cierto para aquella entrega. Las próximas comparaciones requieren autorización.

## Auditoría metodológica de fase 4.1 (histórico de v1)

Consultar [dictamen y corrección propuesta](reports/fase_4_1_auditoria.md), [tabla de umbrales de validación](reports/auditoria_4_1_umbrales_validacion.csv), [resultados y huellas de integridad](reports/auditoria_4_1_resultados.json) y [verificación](reports/auditoria_4_1_verificacion.json).

```powershell
python -m src.audit_baseline
python -m unittest discover -s tests -v
```

Se reproduce la misma logística de fase 4 exclusivamente con su entrenamiento original para auditar probabilidades internas y de validación; no se entrena otro algoritmo, cambia la configuración ni reemplaza el baseline. No se usa el ejecutor de fase 4 para evitar transformar prueba. Durante esta auditoría, prueba solo se inspecciona en metadatos de fechas necesarios para comprobar madurez; no recibe transformación, predicción o evaluación.

Hallazgos: mediana de antelación de 24 días en validación frente a 161 en su grupo apartado; probabilidades medias de 19,01% frente a una tasa observada de 26,17%; prueba carece de filtro por cierre global documentado. Si se supusiera cierre al terminar agosto de 2017, 652 registros no cumplirían la regla vigente de madurez y 368 tienen fecha de estado en septiembre. El máximo de fechas no certifica la fecha de extracción ni disponibilidad real.

El pipeline está correctamente implementado, pero el diseño solo es defendible como benchmark retrospectivo condicionado. Se documenta la propuesta para revisar población, seguimiento y as_of_date **antes de cambiar particiones**. No se aplicó: original, preparado, manifiesto y entregables de fases anteriores siguen intactos. No se recomienda una comparación formal hasta acordar ese protocolo; no se ha iniciado fase 5.

La curva precision-recall y la rejilla de umbrales usan únicamente validación. El umbral 0,10 daría recall 76,17% y 4.923 falsos positivos, frente a 18,41% y 590 a 0,50. Esto ilustra el intercambio de errores, no selecciona una política definitiva. Los escenarios FP=1 y FN=1/3/10 son unidades abstractas de penalización, no costes económicos estimados. No se ajusta ningún calibrador.

Entregables nuevos: src/audit_baseline.py, tests/test_audit_baseline.py, informe, JSON de resultados y verificación, nueve CSV descriptivos y cuatro figuras auditoria_4_1_*.png en reports/figures. Las doce pruebas ejecutadas pasaron. El análisis reproducible genera los resultados/informe; el registro de verificación recoge además la revisión visual y las comprobaciones externas de esta entrega.

## Protocolo temporal vigente — Fase 4.2

Consultar [informe completo](reports/fase_4_2_protocolo_temporal.md), [notebook ejecutado](notebooks/protocolo_temporal.ipynb), [configuración y supuestos](reports/protocolo_4_2_config.json), [fuentes](reports/protocolo_4_2_fuentes.md), [particiones vigentes](reports/division_temporal.json), [baseline vigente](reports/baseline_resultados.json) y [registro de versión activa](reports/estado_protocolo.json).

```powershell
python -m src.temporal_protocol
python -m src.run_notebook --notebook protocolo_temporal.ipynb
python -m src.run_notebook --notebook protocolo_temporal.ipynb --cwd notebooks
python -m unittest discover -s tests -v
```

La fecha de alta aproximada sigue siendo llegada menos lead_time. V2 sustituye la espera hasta la salida prevista por `reservation_status_date + 1 día` como **proxy de disponibilidad**, nunca predictor. Entrenamiento y validación solo usan etiquetas cuyo proxy precede a su corte:

| Conjunto | Corte del proxy de alta | Registros | Canceladas |
|---|---|---:|---:|
| Entrenamiento | Antes del 01/07/2016 | 54.164 | 23.074 (42,60%) |
| Validación | 01/07/2016 a antes del 01/01/2017 | 18.097 | 7.753 (42,84%) |
| Prueba reservada | Desde el 01/01/2017 | 26.565 | 8.402 (31,63%) |
| Pendientes al corte de entrenamiento | Sin mover a otro periodo | 12.089 | 2.743 |
| Pendientes al corte de validación | Sin mover a otro periodo | 8.475 | 2.252 |

**Cierre asumido de prueba: 01/12/2018 exclusivo**, inicio del mes siguiente a la fecha de publicación de la referencia. No es un cierre de extracción acreditado ni se deduce del último estado observado. El último estado observado sigue siendo 14/09/2017; el cierre real del PMS/local es desconocido. Todas las filas actuales de prueba pasan la regla asumida, pero esto no garantiza integridad del seguimiento o de valores iniciales. Los IDs de prueba son exactamente los mismos de v1 y no se reutiliza ninguno para desarrollo.

Se reincorporan 9.822 de las 30.386 apartadas (32,32%): 5.736 a entrenamiento y 4.086 a validación. Quedan 20.564 pendientes. Las añadidas a validación son cancelaciones registradas antes de su llegada: la población cambia y **permanece sesgo de observación**. No se borran reservas ni se limita artificialmente la antelación para mejorar métricas.

Mismo pipeline y parámetros, umbral 0,5: logística en validación v2 obtiene accuracy 74,71%, precision 80,76%, recall 53,77%, F1 0,6456 y ROC-AUC 0,8207. Trivial mayoritario: accuracy 57,16%, recall/F1 cero y ROC-AUC 0,5. Matriz logística `[[9351, 993], [3584, 4169]]`, filas reales/columnas predichas. **Las diferencias respecto a v1 no son una mejora atribuible al algoritmo**: también cambia la prevalencia del 26,17% al 42,84% en validación. Prueba no se transforma, predice ni evalúa en fase 4.2.

La [fuente primaria](https://pmc.ncbi.nlm.nih.gov/articles/PMC6297060/) permite revisar la semántica temporal, pero no certifica disponibilidad inicial de todos los campos del CSV. Se conservan los 14 predictores, su selección conservadora y los datos originales/preparados intactos; no se afirma ausencia total de fuga temporal. La validación estricta al alta sigue requiriendo logs/snapshots y cierre acreditado.

Para trabajos posteriores, el punto de entrada de datos vigente es `src.temporal_protocol.build_protocol`; `src.splitting.temporal_split` exige el proxy de disponibilidad v2 y aplica cierre a prueba. `src.baseline.load_baseline_data` y el notebook baseline.ipynb reproducen exclusivamente v1 para trazabilidad; no deben usarse como entrada del protocolo activo.

Los cinco archivos originales de manifiesto, división, métricas, predicciones y verificación v1 están congelados en `reports/historico/protocolo_v1/` con registro de hashes. Los nombres raíz de manifiesto y baseline apuntan a v2. Los informes de fases 4 y 4.1 conservan su carácter histórico, y sus métricas/umbrales no sirven como comparación actual.

Han pasado 18 pruebas, además de verificaciones de alineación, no solapamiento, grupos, madurez aproximada y estadísticas aprendidas solo con entrenamiento. El notebook v2 conserva sus salidas y dos figuras. Consultar `protocolo_4_2_verificacion.json`.

**La fase 5 no se ha iniciado.** Podrá autorizarse como comparación académica exploratoria bajo este contrato aproximado. No se presenta este protocolo como evaluación de producción al crear una reserva.

## Fases

1. Inspección y organización (validada).
2. EDA (completada).
3. Limpieza y preparación (completada).
4. División temporal y baseline (completada).

Auditoría intermedia 4.1 completada; corrección 4.2 aplicada con alcance aproximado, pendiente de revisión antes de autorizar comparación de modelos.

Siguientes tareas previstas, sujetas a la fase que autorice el usuario: comparación de modelos, optimización y evaluación final, explicabilidad, conclusiones de negocio y revisión de entregables. La petición actual integra el baseline en fase 4.

Cada fase requiere autorización antes de continuar. No se prepara todavía la presentación.


## Fase 5 — Comparación exploratoria completada

La referencia vigente sigue siendo el protocolo v2, sin cambios de cortes, IDs ni madurez. Se comparan logística, árbol, Random Forest, XGBoost y LightGBM exclusivamente en las 18.097 reservas de validación, tras fit en las 54.164 de entrenamiento. Umbral 0,5, semillas 42 y una configuración inicial por algoritmo. Prueba reservada sin transformar ni evaluar.

Resultados y parámetros: [informe de fase 5](reports/fase_5_comparacion_modelos.md), [notebook ejecutado](notebooks/comparacion_modelos.ipynb), `reports/comparacion_5_metricas.csv` y `reports/comparacion_5_verificacion.json`. XGBoost y LightGBM son candidatos para futura optimización, sin modelo definitivo. Persisten las limitaciones de disponibilidad histórica, selección por madurez y duplicados del protocolo aproximado.

Reproducir desde la raíz con el entorno de requirements.txt:

```powershell
.\.venv\Scripts\python.exe -m src.run_notebook --notebook comparacion_modelos.ipynb --cwd root
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

La ejecución solo escribe artefactos `comparacion_5_*` y el informe de fase 5; verifica que los datos y reportes previos conservan sus hashes. XGBoost 3.4.1 y LightGBM 4.7.0 se incorporan al entorno. La fase 6 queda pendiente de autorización.


## Fase 6 — Optimización y umbrales completados

Se mantiene el protocolo temporal v2 y la prueba reservada. Una búsqueda RandomizedSearchCV de nueve configuraciones por algoritmo (ocho muestras y la referencia inicial), tres ventanas temporales internas y 54 ajustes se realizó solo dentro de entrenamiento. Se seleccionaron parámetros por Average Precision interna, con ROC-AUC como desempate, antes de las dos predicciones externas nuevas.

La optimización no mejora ROC-AUC/AP externos. Se conserva **XGBoost inicial de fase 5** como candidato principal provisional, con logística como referencia. Su calibración infravalora cancelaciones y los folds internos muestran inestabilidad. Se estudian umbrales de 0,1 a 0,9 sin elegir uno operativo, y escenarios de contacto con costes relativos expresamente hipotéticos. No se ajusta calibrador, se utiliza prueba ni se inicia SHAP.

- [Informe de fase 6](reports/fase_6_optimizacion.md): parámetros, resultados, calibración, escenarios y límites.
- [Notebook ejecutado](notebooks/optimizacion.ipynb), `src/optimization.py` y `tests/test_optimization.py`.
- Evidencia `reports/optimizacion_6_*`: plan, selección previa a evaluación, 18 candidatos, folds/IDs, métricas, scores de validación, umbrales, calibración y verificaciones.

```powershell
.\.venv\Scripts\python.exe -m src.run_notebook --notebook optimizacion.ipynb --cwd root
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

La reejecución verifica y presenta los resultados congelados sin repetir ajustes ni predicciones externas. El entrenamiento original terminó; se recuperó el registro final tras corregir la exportación JSON de un default NaN de XGBoost. El informe detalla esta incidencia. El código de búsqueda y el plan permiten reproducción desde cero en una copia de trabajo que conserve la evidencia actual. No se instalaron dependencias nuevas. La siguiente fase requiere autorización.


## Fase 7 — Explicabilidad y errores completados

Se analiza exactamente XGBoost inicial de fase 5, reconstruido solo con entrenamiento y contrastado con las probabilidades congeladas. No se modifica v2, no se optimizan parámetros ni se ajusta calibrador o umbral operativo. Prueba continúa reservada.

[Informe de fase 7](reports/fase_7_explicabilidad.md), [notebook ejecutado](notebooks/explicabilidad.ipynb), `src/explainability.py` y `tests/test_explainability.py`. Se incorpora SHAP 0.54.1, compatible en este entorno con XGBoost 3.4.1. TreeExplainer exacto sobre CSR explica log-odds en una muestra reproducible de 3000 reservas de validación; el mapeo de 196 columnas permite agregar contribuciones por las 14 variables originales. Se exportan atribuciones, casos, segmentos, calibración y seis figuras en `reports/explicabilidad_7_*`.

País y antelación dominan SHAP/gain, junto con cliente y mercado; son explicaciones del modelo, sin causalidad. Resort tiene mayor proporción de cancelaciones omitidas y mayor infrapredicción. Las cohortes futuras de llegada presentes en validación son de una sola clase por selección de resultados disponibles: esta limitación condiciona considerablemente las métricas agregadas. El informe detalla la auditoría, los casos TP/TN/FP/FN y la semántica heredada de ceros dispersos. No se autoriza uso operacional.

```powershell
.\.venv\Scripts\python.exe -m src.run_notebook --notebook explicabilidad.ipynb --cwd root
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

La ejecución reconstruye la misma configuración, verifica estadísticas aprendidas solo de train, reproduce scores, muestra y atribuciones, y protege las huellas de artefactos anteriores. No predice prueba. Las recomendaciones para calibración/evaluación final requieren autorización posterior.
