# Fase 10: memoria, presentación y entrega

Fecha: 18/10/2026. Se completa exclusivamente la preparación editorial y revisión de la entrega. No se entrenan modelos, recalibran probabilidades o recalculan predicciones de prueba. Los documentos utilizan la selección cerrada de fase 8 y los resultados guardados de fase 9.

## Materiales revisados

Se revisaron informes de fases 1-9 y auditorías intermedias, README, estructura y salidas de los diez notebooks, datos de los gráficos, especificación congelada, recibo de inferencia, métricas y tablas mensuales y por hotel. Se contrastaron convenciones con los README de proyecto_python y proyecto_estadistica y la revisión inicial de sus notebooks. Curso/MachineLearning contiene el ZIP de datos, sin enunciado local de la práctica. Los materiales disponibles no acreditan una rúbrica o requisitos del profesor. La referencia adicional de Kaggle no se considera un enunciado.

Se verificaron referencias científicas y documentación oficial del dataset, métricas, prevención de leakage, calibración y TreeExplainer. La memoria distingue procedencia científica de trazabilidad del ZIP local y documenta las versiones del experimento frente a la documentación web consultada.

## Entregables

Carpeta entrega_final:

- memoria_final.md y memoria_final.pdf: memoria integrada, 15 páginas PDF.
- presentacion_final.pptx: 15 diapositivas editables, 3 gráficos con libros de datos incorporados y 4 tablas nativas.
- notas_presentacion.md: guion breve, también incorporado en cada diapositiva.
- resumen_ejecutivo.md y README.md: síntesis y guía de lectura/reproducción.
- figuras: siete visualizaciones seleccionadas o derivadas de datos ya guardados.
- fuentes: constructores editoriales, datos de gráficos y auditorías de integridad/notebooks.
- manifest_entrega.json y verificacion_entrega.json: inventario SHA-256 y comprobaciones reproducibles.

La memoria sigue problema, objetivos, datos, EDA, preparación, metodología, comparación, optimización/explicabilidad, selección, política, evaluación, limitaciones, conclusiones y referencias. Evita convertir la exposición en una cronología técnica.

Se actualiza README principal para identificar v3 y la evaluación completada sin avisos contradictorios de fases antiguas. El README anterior se conserva íntegro en reports/historico/README_antes_fase10.md. Ningún archivo histórico previo se elimina o sobrescribe.

## Coherencia de resultados

Los cinco algoritmos, búsqueda de hiperparámetros y SHAP se documentan como experimentos históricos v2. Sus métricas no se comparan directamente con v3. SHAP de XGBoost no se atribuye a logística. La decisión v3 sigue siendo logística inicial y top mensual del 20%, capacidad hipotética conjunta para ambos hoteles. Los scores originales permanecen sin recalibrar.

Se contrastan las cifras finales: N 32.829, cancelaciones 13.136, prioridades 6.564, TP 5.340, FP 1.224, FN 7.796, TN 18.469. Precision 81,35%, recall 40,65%, F1 0,5421, ROC-AUC 0,7802, AP 0,7416 y Brier 0,18534. La evaluación es retrospectiva, con exposición previa parcial y snapshots/cierre inciertos; no acredita causalidad, rentabilidad o validación prospectiva. Se explica la caída respecto a validación y la variación entre meses y hoteles sin reajustes.

## Revisión y reproducción

Las 15 páginas PDF se renderizaron con Poppler y se inspeccionaron. El PowerPoint final se importó con Artifact Tool, se renderizaron e inspeccionaron sus 15 diapositivas y se comprobaron geometría, tipografía, paquete, tablas y datos de gráficos con cero incidencias finales del validador. No se afirma apertura interactiva en Microsoft PowerPoint. Los gráficos editables usan valores redondeados a seis decimales por compatibilidad del libro de datos; no se alteran los CSV, métricas o scores originales.

Los diez notebooks tienen todas sus celdas de código ejecutadas y salidas guardadas sin errores. Su revisión fue de lectura, sin ejecutar entradas históricas. La entrega incorpora un auditor de biblioteca estándar que contrasta huellas, cifras, cupos, enlaces y estructura de documentos. Las dependencias ML permanecen intactas; las herramientas editoriales usan el runtime separado, documentado en el README de entrega.

Las verificaciones finales se guardan en entrega_final/verificacion_entrega.json. Los hashes capturados antes de componer la entrega permiten acreditar datos, artefactos, código, notebooks e informes previos sin cambios. También se comprueban los 105 archivos de referencia del curso. El recibo original conserva una sola inferencia y cero reentrenamientos o recalibraciones. Los intermedios de renderizado están en tmp/fase10, fuera de la carpeta de entrega.

## Pendientes administrativos

Confirmar nombre académico de autoría, institución/docente, enunciado, rúbrica, extensión, duración y canal de entrega. Se han señalado los datos de autoría no confirmados, sin atribuir un nombre a partir de las rutas del sistema. Estos pendientes no se sustituyen por requisitos inventados. Los documentos quedan preparados para revisión del usuario antes de su envío institucional.
