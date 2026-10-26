# Informe de fase 3 — Limpieza y preparación

Fecha: 18 de octubre de 2026. Fases 1 y 2 completadas por indicación del usuario. Esta entrega completa exclusivamente la fase 3; la fase 4 requiere autorización.

## 1. Revisión y alcance

Antes de editar se revisaron `notebooks/eda.ipynb`, los informes de fases 1 y 2, README, el notebook y módulos de limpieza/validación del proyecto Python y la organización del proyecto Estadística. Se conservaron las convenciones: carpetas separadas, funciones en snake_case, variables originales descriptivas, rutas con pathlib, comentarios y documentación en español y un notebook narrativo. No se copió la eliminación de duplicados o precios negativos de Online Retail: sus decisiones se apoyaban en evidencias propias de aquel problema.

Se ha creado una preparación determinista sin ajustar estadísticas sobre el conjunto completo. No hay split, modelos, optimización ni comparación de métricas predictivas. La inspección de anomalías fue dirigida a los casos ya detectados; no se repitió el EDA completo.

## 2. Registros conservados y duplicados

**119.390 registros conservados; 0 excluidos.** Se mantienen las 31.994 repeticiones adicionales y los 40.165 registros participantes en grupos idénticos. No existe identificador único de reserva y no puede probarse que sean duplicaciones técnicas; podrían ser reservas distintas con las mismas características.

El impacto se cuantificó mediante restas de recuentos, sin construir otro dataset:

| Escenario descriptivo | Registros | Cancelaciones | Tasa |
|---|---:|---:|---:|
| Conservar todos (adoptado) | 119.390 | 44.224 | 37,04 % |
| Quitar repeticiones (hipotético) | 87.396 | 24.025 | 27,49 % |

La diferencia ilustra que eliminar no sería neutral. Conservar mantiene el peso observado, pero si hay duplicación técnica puede sobreponderar ciertos patrones e inflar el tamaño efectivo. Las métricas futuras deberán reconocer esta limitación.

`meta_row_id` permite volver a la posición de fila del CSV original, numerada desde cero; no identifica una reserva real. `meta_duplicate_group` es una huella técnica de las 32 columnas originales, independiente del índice. Incluye etiqueta y estados únicamente para reconocer repeticiones en auditoría, y queda fuera de X. Se comprobó que produce las mismas 31.994 repeticiones adicionales en este archivo. La huella de 64 bits tiene riesgo teórico de colisión; una aplicación operativa necesitaría un ID real y verificar los grupos. En fase 4 se comprobará que no haya cruces de duplicados entre conjuntos; las repeticiones exactas también comparten proxy de creación.

## 3. Estrategias para valores ausentes y tipos

| Variable | Ausentes originales | Decisión |
|---|---:|---|
| children | 4 | Mantener desconocido como Int64 nullable en memoria; children_missing=1. Mediana solo cuando se ajuste el preprocesador con entrenamiento. |
| country | 488 | Mantener nulo en el CSV; categoría constante Desconocido al ajustar/aplicar el pipeline. No usar moda. |
| agent | 16.340 | ID como cadena anulable, sin sufijo .0; no crear ID cero. Fuera de X por incertidumbre de versión inicial. |
| company | 112.593 | Mismo tratamiento de ID; no asumir que ausencia equivale a no aplicable. Fuera de X. |

En agente/empresa no se distingue “sin intermediario/empresa” de “no informado”; por tanto, no se inventa una semántica. La normalización de IDs se realiza en la copia limpia en memoria y no se exportan como predictores. Los nulos de niños y país permanecen en el CSV preparado; su manejo estadístico/categórico se delega al entrenamiento. Los tipos numéricos de X son float64 para expresar np.nan y facilitar scikit-learn; eso no convierte los conteos en magnitudes conceptualmente continuas. Se preservan las categorías `Undefined`, sin fusionarlas con nulos.

## 4. Tratamiento de anomalías

| Problema | Registros | Interpretación y tratamiento |
|---|---:|---|
| ADR negativo (−6,38) | 1 | Posible ajuste o error, no probado. Se convierte a NaN solo en la copia limpia; no se adivina una tarifa positiva. Se conserva fila, original y flag meta_adr_negative. ADR no entra en X. |
| ADR cero | 1.959 | Puede representar cortesía/acuerdo u otra situación, pero falta evidencia. Conservar cero y fila; flag meta_adr_zero. |
| Cero noches | 715 | Podría ser uso diurno, registro administrativo o error. Conservar total_nights=0; flag meta_zero_nights. |
| Cero huéspedes conocidos | 180 | Podría ser un registro administrativo o inconsistencia. Conservar componentes y flag meta_zero_guests; no inventar huéspedes. |
| Total de huéspedes desconocido | 4 | No contar niños ausentes como cero. Flag meta_guests_unknown; children_missing también identifica este caso. |

Las anomalías se solapan y no se suman para contar exclusiones. No se recortan ADR extremo o tamaños grandes por IQR/rareza. Los flags de calidad son metadatos de auditoría, no predictores seleccionados. La versión de ADR marcada como desconocida no se guarda en otro dataset porque ADR se excluye de la selección conservadora: raw conserva su valor y el CSV preparado guarda el indicador. Esta es una corrección de fiabilidad en la copia de trabajo, no recuperación de un dato verdadero.

## 5. Auditoría temporal y exclusiones

La auditoría de las 32 columnas está en `reports/preparacion_auditoria_variables.csv`. Distingue disponibilidad conceptual en el proceso, evidencia disponible y decisión de inclusión.

**No disponibles como predictores:** `reservation_status` y `reservation_status_date`, obligatoriamente excluidas por revelar estado final y su actualización. `is_canceled` se separa como etiqueta futura.

**Disponibilidad incierta; excluidas del conjunto conservador:**

- `assigned_room_type`: no distingue asignación inicial de cambios posteriores.
- `booking_changes`: el total final puede acumular modificaciones futuras.
- `days_in_waiting_list`: depende de pre-reserva frente a confirmación; la duración futura no se sabe al entrar en espera.
- `deposit_type`: una política inicial podría ser legítima, pero no se acredita su versión; la tasa extrema del EDA no demuestra fuga por sí sola.
- `adr`: no se sabe si es tarifa inicial o promedio actualizado.
- `total_of_special_requests` y `required_car_parking_spaces`: peticiones que podrían haberse añadido después.
- `previous_cancellations`, `previous_bookings_not_canceled`, `is_repeated_guest`: falta acreditar cómputo estrictamente anterior, sin resultado actual o reservas futuras.
- `agent` y `company`: origen posiblemente inicial, pero sin prueba de versión temporal y con ausencia ambigua; se dejan fuera como decisión conservadora.

**Disponibles en la operación inicial por definición del escenario:** hotel, calendario previsto, noches previstas, composición de huéspedes, habitación reservada, régimen y origen/segmentación comercial. Se utilizan sus valores como supuesto explícito de información inicial. El archivo no demuestra que no hayan sido modificados antes de la extracción; si se acredita una actualización, deberán excluirse o recuperarse sus versiones originales. La selección reduce riesgos identificados; **no certifica ausencia total de leakage histórico**.

## 6. Características seleccionadas

**6 numéricas:** `lead_time`, `total_nights`, `adults`, `children`, `babies`, `children_missing`.

**8 categóricas:** `hotel`, `arrival_date_month`, `meal`, `country`, `market_segment`, `distribution_channel`, `reserved_room_type`, `customer_type`.

`total_nights` sustituye las dos clases de noches para simplificar sin duplicar el total. `children_missing` identifica desconocidos sin aprender del dataset. No se incluye total_guests para no duplicar componentes ni tener que imputar niños durante su construcción.

Año, semana y día de llegada se excluyen de X para simplificar el calendario y no añadir códigos/años redundantes. La fecha completa se conserva como metadato para auditoría y estrategia temporal; el mes previsto sí es una categoría admisible bajo el supuesto inicial. No se eligieron variables por correlación ni por métricas de clasificación.

## 7. Transformaciones propuestas, sin fit sobre reservas reales

`src/preprocessing.py` devuelve un ColumnTransformer nuevo en cada llamada:

- Numéricas: Pipeline de SimpleImputer(strategy='median', keep_empty_features=True) y, cuando corresponda, StandardScaler. Se admite scale_numeric=False para algoritmos que no lo necesiten.
- Categóricas: Pipeline de SimpleImputer(strategy='constant', fill_value='Desconocido', keep_empty_features=True) y OneHotEncoder(handle_unknown='ignore', sparse_output=True).
- Resto de columnas: remainder='drop'. La lista cerrada de columnas excluye etiqueta, metadatos y entradas adicionales aunque estén presentes en el DataFrame.

La mediana es una aproximación aprendida, no el número verdadero de niños. Si una columna numérica fuera completamente ausente en entrenamiento, keep_empty_features conservaría la columna mediante el relleno cero interno de scikit-learn, sin mediana disponible; este caso deberá revisarse en fase 4. Para children existe un indicador explícito que evita confundir ausencia con cero declarado.

Una categoría nueva se codifica con ceros en su bloque: permite transformar sin error, pero no implica que se conozca su efecto. Si la categoría Desconocido no se vio en entrenamiento, también puede ser desconocida para el codificador. No se garantiza rendimiento por manejar categorías nuevas.

No se ha ajustado ni persistido ningún transformador de reservas reales ni se ha guardado una matriz codificada. En la fase de modelado, este preprocesador deberá ir dentro del Pipeline del modelo y ajustarse solo en el entrenamiento de cada partición/fold. Validación/prueba usarán transform. Las pruebas con fit de esta entrega utilizan exclusivamente registros inventados.

## 8. Único dataset preparado y separación

`data/processed/hotel_bookings_prepared.csv`: **119.390 filas y 25 columnas**, distribuidas en 14 predictores, etiqueta y 10 metadatos:

`meta_row_id`, `meta_duplicate_group`, `meta_arrival_date`, `meta_booking_date_proxy`, `meta_label_available_after`, `meta_adr_negative`, `meta_adr_zero`, `meta_zero_nights`, `meta_zero_guests`, `meta_guests_unknown`.

No se exportan las columnas originales excluidas. Algunos metadatos se calculan con información posterior, únicamente para auditoría retrospectiva o elegibilidad de etiquetas: **no son características**. Para cargar X se debe usar `separate_model_data`, nunca eliminar solo la etiqueta del CSV. Esa función usa FEATURES explícitamente y restaura los tipos después de leer CSV.

Se verificó igualdad de X e y antes/después de exportar y leer, orden de filas, alineación de etiqueta, duplicados y sumas de indicadores. CLI y notebook reprodujeron el mismo SHA-256 del CSV preparado: `2718ad6c88b52da2914b54e5f6eccb51815a2ff3c59100793c093292f900c60c`.

## 9. Estrategia de división temporal propuesta

**No se han creado particiones.** Las reglas están definidas en TEMPORAL_PLAN de `src/preparation.py` y se implementarán/revisarán en fase 4.

- Orden: proxy de creación = llegada prevista − lead_time. Rango observado de este proxy: 24/06/2013–31/08/2017. No es una fecha exacta de creación y puede alterarse si llegada/antelación fueron actualizadas.
- Cortes propuestos: **01/07/2016** para comenzar validación y **01/01/2017** para comenzar prueba. Se busca permitir un ciclo anual de llegadas antes del primer corte, pues los datos comienzan en julio de 2015. Son fronteras de calendario, no seleccionadas por métricas. Sus tamaños y cobertura deben revisarse antes de adoptarlas.
- Entrenamiento: proxy anterior al primer corte y etiqueta madura antes de ese corte.
- Validación: proxy entre ambos cortes y etiqueta madura antes del segundo, para simular decisiones de selección anteriores a prueba.
- Prueba: proxy desde el segundo corte, con seguimiento suficiente para conocer etiquetas en el momento de evaluación.
- Madurez propuesta: `max(llegada + total_nights, fecha_estado_final) + 1 día < corte`. La fecha del estado final se usa solo para restringir elegibilidad retrospectiva de la etiqueta, nunca para X ni para ajustar transformaciones. Es una cota offline conservadora, no disponibilidad histórica demostrada; puede retrasar reservas cuya cancelación ya se conocía antes de la salida prevista.
- Mantener fechas iguales juntas; verificar que ningún grupo duplicado cruce conjuntos. Registrar reservas temporalmente no elegibles por falta de madurez sin eliminarlas del dataset preparado.

La regla evita asumir que una reserva antigua ya tiene un resultado conocido, pero no puede garantizar una simulación de producción fiel sin logs de creación, versiones y publicación de etiquetas. Llegadas por sí solas solo medirían generalización por cohortes de llegada. Las fechas/proxies de corte quedan fuera de X.

Todo el archivo fue explorado en fase 2. Una prueba posterior obtenida de él no será completamente ajena al EDA. Documentar la exposición y buscar datos externos/prospectivos para una evaluación independiente.

## 10. Archivos creados/modificados y ejecución

Creados:

- `notebooks/preparacion.ipynb`, con resultados conservados.
- `src/cleaning.py`, `src/features.py`, `src/preprocessing.py`, `src/preparation.py`.
- `tests/test_preparation.py`, con cinco pruebas de integridad y prevención de fuga.
- El CSV preparado único, `reports/preparacion_resumen.json`, `reports/preparacion_verificacion.json`, `reports/preparacion_auditoria_variables.csv` y este informe.

Modificados:

- README y requirements; se añadió scikit-learn 1.9.0 únicamente al entorno local .venv del proyecto. pip check confirmó dependencias compatibles.
- `src/run_notebook.py`: admite elegir eda.ipynb o preparacion.ipynb, manteniendo el EDA como valor predeterminado.
- `notebooks/eda.ipynb`: ajuste mínimo en su última comprobación para aceptar archivos preparados preexistentes de fases posteriores, sin exigir una carpeta processed vacía. Se conservan las salidas históricas; no se repitieron EDA, tablas ni gráficos. El código modificado se validó sintácticamente y la integridad actual se verificó en preparación; `reports/eda_verificacion.json` conserva su huella histórica y añade el registro de mantenimiento y la huella del notebook actual; no se afirma haber reejecutado todo el EDA actualizado.

El notebook de preparación tiene 20 celdas, 9 de código. Se ejecutó completo desde raíz y notebooks/ sin errores ni advertencias en las celdas. Las salidas de la versión final conservan el último recorrido desde raíz; se incluye la propuesta temporal final en el informe y resumen. El lanzador local puede emitir avisos sobre ubicación original de Python o transporte del kernel; no son errores de las celdas.

## 11. Verificaciones ejecutadas

Cinco pruebas con datos sintéticos verificaron:

1. Todas las filas y duplicados se conservan, entrada sin mutación y dos preparaciones iguales.
2. ADR negativo pasa a desconocido; ceros y ausencia de niños/agente se mantienen; flags no confunden cero con desconocido.
3. Modificar etiqueta, estado final, fecha final, depósito, ADR y cambios no altera X.
4. Mediana y media aprendidas únicamente con entrenamiento sintético; transform de datos posteriores no cambia estadísticas; categorías inéditas no fallan y columnas adicionales/metadatos no llegan a la salida.
5. Variante sin escalado y metadatos temporales coherentes.

Además, se verificaron X e y tras el round-trip CSV, lista de predictores, preprocesador real sin fit, integridad del CSV original, conservación de 105 archivos de referencia y reproducibilidad del CSV preparado. Las pruebas de transformadores no son evaluación predictiva. El registro técnico de celdas y rutas está en `preparacion_verificacion.json`.

## 12. Limitaciones y próximos pasos

Pendientes: enunciado y prácticas específicas de ML, diccionario temporal, IDs reales, significado de ausencias, casos anómalos y snapshots iniciales. Las exclusiones conservadoras pueden reducir capacidad predictiva, pero no se relajarán por observar mejores métricas sin acreditar disponibilidad.

Antes de modelar: autorizar fase 4, revisar los supuestos, comprobar cobertura/tamaños y madurez de etiquetas en los cortes, fijar particiones con grupos y registrar elegibilidad. Solo después ajustar el preprocesador con entrenamiento y comenzar un baseline en la fase correspondiente.

**Fin exclusivo de fase 3. No se continúa a fase 4 sin autorización.**
