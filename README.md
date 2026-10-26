# Predicción de cancelaciones hoteleras

**Código explicado en los archivos principales:** los módulos de src/, tests/, los constructores editoriales y los diez notebooks incluyen comentarios en español; estos últimos incorporan además 64 celdas Markdown nuevas. El [registro de la revisión documental](reports/documentacion_integrada.md) explica las comprobaciones de equivalencia y el respaldo previo. codigo_comentado/ se conserva como referencia anterior.

Proyecto académico del curso de Data Science y Machine Learning. Fases 1 a 10 completadas. La entrega integra metodología, experimentos y resultados con sus limitaciones.

## Entrega final

- [Guía de entrega](entrega_final/README.md).
- [Memoria PDF, 15 páginas](entrega_final/memoria_final.pdf) y [fuente Markdown](entrega_final/memoria_final.md).
- [Presentación PowerPoint, 15 diapositivas con notas](entrega_final/presentacion_final.pptx).
- [Resumen ejecutivo](entrega_final/resumen_ejecutivo.md) y [notas de exposición](entrega_final/notas_presentacion.md).
- [Revisión de fase 10](reports/fase_10_entrega_final.md).

No se ha localizado el enunciado del profesor. Quedan por confirmar autoría académica, rúbrica, extensión, duración y formato de envío. No se inventan esos requisitos.

## Resultado y alcance vigentes

El protocolo activo es v3, retrospectivo por cohortes de llegada con embargo. Se conservan 119.390 registros y 14 predictores. El objetivo es is_canceled (1=cancelación). No se acredita una simulación prospectiva al crear reservas.

| Bloque | Llegadas | Registros |
|---|---|---:|
| Entrenamiento | Julio 2015 a junio 2016 | 49.157 |
| Embargo | Julio a agosto 2016 | 9.635 |
| Validación | Septiembre a diciembre 2016 | 19.911 |
| Embargo | Enero a febrero 2017 | 7.858 |
| Prueba | Marzo a agosto 2017 | 32.829 |

Modelo congelado: regresión logística inicial ajustada solo con train v3. Política: ambos hoteles juntos dentro de cada mes, k=n_mes*20//100, score descendente, SHA256 de `42|ID` ascendente y después ID numérico. No es un umbral fijo ni una cuota por hotel. Requiere lote mensual completo y capacidad hipotética del 20%.

Prueba se evaluó una sola vez en fase 9: 6.564 prioridades, TP 5.340, FP 1.224, FN 7.796 y TN 18.469. Precision 81,35%, recall 40,65%, F1 0,5421, ROC-AUC 0,7802, Average Precision 0,7416 y Brier 0,18534. En fase 10 no se entrenó, recalibró o predijo de nuevo.

Faltan snapshots iniciales y cierre operativo acreditados. Parte de la prueba tuvo exposición previa y se reutilizó validación para seleccionar. Los scores no tienen calibración acreditada, existe variación mensual y no se han estimado costes o efectos del seguimiento. No se afirma rentabilidad ni validez prospectiva.

## Estructura

- data/raw y data/processed: archivo original y preparación, intactos.
- src: módulos de inspección, preparación, protocolos, experimentos y evaluación.
- notebooks: diez notebooks con salidas guardadas, etiquetados por fase en sus informes.
- reports: informes, manifiestos, métricas y gráficos.
- reports/historico: evidencia v1 y v2 congelada y README anterior conservado.
- models: artefacto congelado de fase 8.
- tests: comprobaciones de las etapas del proyecto.
- entrega_final: documentos, presentación y fuentes editoriales.

## Revisión reproducible sin nuevos ajustes o predicciones

Desde la raíz con Python 3.14.5:

```powershell
.\.venv\Scripts\python.exe herramientas/auditar_documentacion_integrada.py
```

El auditor vigente distingue los bytes de las fuentes históricas de la documentación actual. Comprueba el respaldo previo, hashes antes/después, AST y tokens de Python y celdas, inserciones de Markdown y conservación exacta de salidas, contadores y metadatos. Datos, modelo, particiones, predicciones y métricas siguen exigiendo hashes exactos. No carga joblib ni ejecuta estimadores o notebooks.

Las fuentes de los experimentos se respaldaron, antes de añadir documentación, en reports/historico/documentacion_pre_integracion/. Los recibos y especificación conservan sus hashes de ejecución originales. Sus comprobaciones SHA estrictas rechazan los nuevos bytes documentados: se contrastan con ese respaldo, mientras la auditoría vigente verifica la equivalencia de las fuentes actuales. No se han desactivado esas protecciones ni cambiado la lógica para aceptar otros artefactos.

Esta revisión se comprueba estáticamente. Para una reproducción histórica debe utilizarse una copia aislada con las fuentes respaldadas y los artefactos de aquella ejecución, conservando los originales. No ejecutar el conjunto general de pruebas ni notebooks históricos para revisar la documentación: varias entradas entrenan modelos. Las salidas guardadas permiten revisión sin ejecutar código.

requirements.txt fija las dependencias directas utilizadas. La especificación de fase 8 y los recibos de fase 9 registran versiones y hashes adicionales. No es un lock de todas las transitivas. Consultar entrega_final/README.md para reconstrucción editorial con ReportLab y Artifact Tool, separada del entorno de ML.

## Fuentes de verdad y fases históricas

- [Protocolo v3](reports/fase_7_1_correccion_sesgo_temporal.md) y reports/particiones_temporales.csv.
- [Selección final](reports/fase_8_seleccion_final.md) y [especificación congelada](reports/seleccion_8_especificacion_congelada.json).
- [Evaluación final](reports/fase_9_evaluacion_final.md), [métricas](reports/evaluacion_9_metricas.json) y [recibo de inferencia única](reports/evaluacion_9_recibo.json).
- [Memoria integrada](entrega_final/memoria_final.md), con referencias y resultados históricos identificados.

Los informes de fases 1 a 7 describen el contexto vigente en cada experimento. V1 y v2 están archivados y no son el protocolo activo. Las métricas históricas de cinco algoritmos, optimización y SHAP pertenecen a v2. SHAP de XGBoost no explica la regresión logística final. No deben mezclarse sus poblaciones con v3 ni ejecutar entradas v2 sobre los artefactos activos.

El campo prueba_evaluada=false en el estado de origen de fase 7.1 conserva aquella fotografía histórica. La evidencia vigente de evaluación completada es evaluacion_9_recibo.json. El [README previo](reports/historico/README_antes_fase10.md) conserva íntegra la documentación anterior, incluidos sus avisos históricos de estado.

La fuente científica del dataset es [António et al., Hotel booking demand datasets](https://doi.org/10.1016/j.dib.2018.11.126). El ZIP local no acredita por sí solo su cadena de descarga o licencia. Las referencias completas y sus límites figuran en la memoria.
