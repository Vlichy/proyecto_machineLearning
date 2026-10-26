# Informe de fase 2 — Análisis exploratorio

Fecha: 18 de octubre de 2026. Estado: completada, pendiente de revisión del usuario. Alcance limitado al EDA, sin limpieza definitiva, selección final de variables, división ni entrenamiento.

## Archivos creados o modificados

Creados:

- `notebooks/eda.ipynb`: 29 celdas, 14 de código, 13 figuras incorporadas y salidas conservadas. Las interpretaciones se generan con los resultados reales de las tablas; el texto que aparece tras cada bloque forma parte de la salida guardada.
- `src/run_notebook.py`: ejecuta y guarda el notebook usando el Python actual. Admite raíz o `notebooks/` como directorio de ejecución, no registra un kernel global y cierra el kernel al terminar.
- `reports/eda_resumen.json`: resultados numéricos de calidad, objetivo, grupos, tiempo y correlaciones.
- `reports/eda_auditoria_leakage.csv`: clasificación razonada por disponibilidad temporal (no es un dataset preparado).
- `reports/eda_verificacion.json`: comprobación de celdas, errores, imágenes, integridad y rutas.
- `reports/figures/`: 13 PNG que reproducen los gráficos incorporados al notebook.
- Este informe.

Modificados: README, dependencias directas en `requirements.txt` y `.gitignore` (añade el directorio de configuración/caché local de Jupyter). Se creó un entorno local `.venv/` y `.jupyter_runtime/`, ambos excluidos de Git. No se modificaron el CSV, ZIP original, informes de fase 1 ni archivos de los proyectos anteriores.

## Ejecución y comprobaciones

Se ejecutó el notebook completo con Python 3.14.5, pandas 3.0.3, NumPy 2.4.6, matplotlib 3.11.0, seaborn 0.13.2, nbformat 5.11.1, nbclient 0.11.0 e ipykernel 7.4.0. Las versiones directas constan en requirements; no se afirma que se hayan bloqueado todas las transitivas. `pip check` no encontró dependencias incompatibles.

Se comprobaron ejecuciones completas desde la raíz y desde `notebooks/`. Las 14 celdas de código tienen número de ejecución; no hay salidas de error ni advertencias en las celdas de la entrega. Las 13 imágenes PNG incorporadas y los 13 archivos exportados se decodifican correctamente. Se revisó visualmente una lámina de los gráficos y las figuras de mayor densidad por separado para comprobar etiquetas, escalas y legibilidad.

La ejecución inicial dentro de las restricciones no arrancó el kernel; se autorizó su ejecución local fuera de ese bloqueo. Una primera ejecución detectó un error al exportar a JSON la etiqueta de huéspedes desconocidos: se corrigió la etiqueta de presentación, sin imputar datos, y se volvió a ejecutar todo. El lanzador puede emitir advertencias de su entorno sobre la ubicación original de Python o el transporte TCP del kernel; no son errores de las celdas.

El CSV mantiene la huella SHA-256 `7c2ae42a7353905ea136e5c2287f17c92c5435826598bfbb8491c6f0c7b1fc06`; `df` mantiene su huella de contenido y sus 119.390 filas/32 columnas. Los 105 archivos de referencia conservan sus hashes. `data/processed/` sigue vacía. La suma de los grupos de huéspedes (incluyendo desconocidos) y de los meses reproduce el total del dataset.

## Principales resultados numéricos

| Grupo | Reservas | Cancelaciones | Tasa |
|---|---:|---:|---:|
| Total | 119.390 | 44.224 | 37,04 % |
| City Hotel | 79.330 | 33.102 | 41,73 % |
| Resort Hotel | 40.060 | 11.122 | 27,76 % |
| Antelación cero | 6.345 | 430 | 6,78 % |
| Antelación >365 días | 3.148 | 2.130 | 67,66 % |
| Non Refund | 14.587 | 14.494 | 99,36 % |
| Groups (segmento) | 19.811 | 12.097 | 61,06 % |
| Online TA | 56.477 | 20.739 | 36,72 % |
| Huéspedes repetidos | 3.810 | 552 | 14,49 % |
| Sin solicitudes especiales | 70.318 | 33.556 | 47,72 % |
| Con una solicitud | 33.226 | 7.318 | 22,02 % |
| Con aparcamiento solicitado | 7.416 | 0 | 0,00 % |

Con antecedentes de cancelación la tasa es 91,64% (6.484 reservas), frente a 33,91% sin ellos. Con reservas previas no canceladas es 5,52% (3.620), frente a 38,03% sin ellas. El cómputo temporal de esos antecedentes necesita verificarse.

ADR tiene mediana 94,575, mínimo −6,38 y máximo 5.400; su P99 es 252. Las tasas entre 50 y 300 se sitúan aproximadamente entre 37,96% y 38,94%, sin una relación simplemente creciente. Las estancias de 2–3 noches tienen tasa 42,97%, frente a 35,90% en 4–7; no se interpreta como efecto causal de duración.

Cobertura de llegadas: 01/07/2015–31/08/2017. Solo 2016 incluye enero–diciembre. La tasa mensual agregada oscila entre 20,77% (noviembre de 2015) y 45,35% (julio de 2015). Las curvas muestran volumen, cancelaciones por llegada prevista y tasas por hotel. No representan fechas de creación o cancelación. Las diferencias de cobertura impiden comparar sin cautela totales anuales o meses del año agregados.

En la selección de magnitudes numéricas, las mayores correlaciones absolutas de Pearson con la etiqueta son `lead_time` (0,293), solicitudes (−0,235) y aparcamiento (−0,195). Spearman complementa la lectura; no se usa ninguna correlación como filtro de variables ni como evidencia causal.

## Hallazgos e interpretación de negocio

City presenta una tasa 13,96 puntos superior a Resort, pero no se ha aislado la composición por calendario o canal. Antelación, historial, solicitudes, segmento y depósito ofrecen hipótesis para investigar, no efectos independientes. El volumen de cancelaciones de Online TA es mayor que el de Groups aunque su tasa sea menor: las dos métricas responden preguntas diferentes. Grupos pequeños como `Undefined` no permiten conclusiones estables.

Las asociaciones extremas de Non Refund y aparcamiento exigen estudiar definición, proceso de registro y composición antes de usarlas. No son prueba automática de fuga ni justificación para cambiar políticas de depósito. No se recomiendan penalizaciones o sobreventa basadas solo en este EDA. El valor operativo se validaría mediante un piloto tras desarrollar y evaluar el modelo.

## Calidad de datos

- Nulos: `children` 4 (0,0034%); `country` 488 (0,4087%); `agent` 16.340 (13,6862%); `company` 112.593 (94,3069%). El notebook muestra porcentajes por hotel, etiqueta y patrones conjuntos.
- La ausencia de agente es 10,25% en City y 20,49% en Resort; en país, 0,03% y 1,16%. No es homogénea por hotel y no se presume un mecanismo aleatorio.
- Duplicados adicionales: 31.994; registros que pertenecen a grupos repetidos: 40.165. Sin identificador único no se acredita duplicación técnica. Se conserva todo y se compara su perfil por hotel/etiqueta.
- ADR negativo: 1; ADR cero: 1.959. Estancias de cero noches: 715. Registros con cero huéspedes conocidos: 180. Totales de huéspedes desconocidos: 4; no se trataron como cero.
- Se revisan grandes grupos, conteos negativos, componentes de llegada, fechas de estado, categorías `Undefined` y extremos mediante IQR. Las comprobaciones pueden solaparse y no deben sumarse. IQR cero en conteos raros no justifica eliminar sus valores positivos. Ceros o extremos no son automáticamente errores.

## Auditoría de fuga de información

| Clasificación | Variables / criterio |
|---|---|
| No utilizables como predictores | `reservation_status`, `reservation_status_date`: estado final y fecha de actualización/desenlace. `is_canceled` es exclusivamente la etiqueta. |
| Disponibilidad por verificar | Asignación de habitación; cambios acumulados; espera; depósito; ADR; aparcamiento y solicitudes; historial y repetición. |
| Potencialmente utilizables | Hotel, antelación/calendario previstos, estancia, huéspedes, habitación reservada y datos comerciales/origen, siempre en su versión inicial. |

`booking_changes` final registra cambios futuros respecto a la creación. La espera depende del instante: al entrar en lista se desconoce su duración; al confirmar podría conocerse. `deposit_type` puede ser una política inicial legítima: debe acreditarse, sin diagnosticar fuga solo por su asociación. La asignación puede existir al principio o modificarse después. Historial válido significa hechos anteriores y conocidos, sin sumar el resultado actual ni futuras reservas. Se recomienda excluir del futuro modelado cualquier campo cuyo valor inicial no pueda verificarse para este escenario.

La fecha de llegada menos `lead_time` sería una aproximación a creación, pendiente de semántica y estabilidad; no hay fecha exacta observada. Una futura validación temporal debe considerar cuándo están disponibles predictores y etiquetas.

## Decisiones pendientes para la fase 3

1. Acordar unidad de observación y política justificada sobre duplicados; evitar contaminación entre conjuntos por reservas equivalentes.
2. Distinguir ausencia estructural de dato desconocido, especialmente empresa/agente; valorar categorías, indicadores e imputación aprendida solo en entrenamiento.
3. Investigar ADR negativo/extremo, ceros, noches/huéspedes y categorías ambiguas sin borrado automático; documentar trazabilidad.
4. Confirmar disponibilidad inicial, tipos semánticos y exclusiones por fuga; decidir codificación/escalado cuando se seleccionen algoritmos.
5. Planificar la división cronológica para fase 4; no implementarla todavía.
6. Obtener diccionario temporal, enunciado y prácticas específicas de ML para contrastar todas las decisiones.

## Limitaciones

Archivo observacional de dos hoteles y poco más de dos años, sin ID único ni documentación local de muestreo, costes de errores o descarga/licencia. Las reservas pueden depender entre sí; no se construyen intervalos suponiendo independencia sin justificarla. Asociaciones agregadas pueden reflejar confusión por hotel, segmento o temporada. No se estiman efectos causales ni rendimiento de modelos.

Todo el archivo ha sido explorado por el alcance solicitado. Una futura prueba extraída de él no será completamente ajena al EDA: documentar esa exposición y buscar datos nuevos para validación externa o prospectiva. No se ha afirmado una evaluación independiente inexistente.

**Fin de fase 2. Esperar autorización antes de iniciar fase 3.**
