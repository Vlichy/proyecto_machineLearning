# Entrega académica final

La explicación dentro del código está en la [edición comentada del proyecto](../codigo_comentado/README.md): módulos, pruebas, diez notebooks y constructores editoriales, con comentarios en español y equivalencia verificada. Es una edición de lectura separada para conservar las fuentes selladas de la evaluación.

Abrir [memoria_final.pdf](memoria_final.pdf) para leer el trabajo y [presentacion_final.pptx](presentacion_final.pptx) para exponerlo. La memoria tiene 15 páginas y la presentación 15 diapositivas con notas incorporadas. También se incluyen [memoria_final.md](memoria_final.md), [resumen_ejecutivo.md](resumen_ejecutivo.md) y [notas_presentacion.md](notas_presentacion.md).

La carpeta figuras contiene siete visualizaciones con fuentes y explicación en la memoria. fuentes contiene los datos editoriales, los constructores y las comprobaciones. No contiene una copia de los datos originales ni del modelo: la entrega documental se acompaña del proyecto completo si se solicita código y evidencia. Mantener la carpeta figuras junto al Markdown.

## Resultado definitivo

Protocolo v3 retrospectivo por llegada. Regresión logística inicial y cupo mensual conjunto del 20%, con redondeo inferior y desempates congelados. Sobre 32.829 reservas: 6.564 prioridades, TP 5.340, FP 1.224, FN 7.796, TN 18.469. Precision 81,35%, recall 40,65%, F1 0,5421, ROC-AUC 0,7802, AP 0,7416 y Brier 0,18534. Ningún resultado se ha reajustado en fase 10.

Las métricas v2 se identifican como históricas y no se comparan directamente con v3. SHAP corresponde a XGBoost v2, no a la logística final. La capacidad del 20% es hipotética y exige el lote mensual completo. No se acredita evaluación prospectiva, calibración perfecta, ahorro o efecto de intervención.

## Comprobación sin entrenar ni inferir

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe entrega_final/fuentes/auditar_entrega.py
```

El auditor usa la biblioteca estándar, contrasta huellas y cifras, inspecciona los notebooks guardados y comprueba estructura del PowerPoint, enlaces y manifestación de archivos. No importa estimadores, no carga joblib y no ejecuta notebooks. El recibo de fase 9 conserva una sola inferencia. No utilizar un descubrimiento general de tests ni ejecutar notebooks históricos para revisar esta entrega: algunas entradas entrenan algoritmos. Las salidas históricas se conservan y los informes documentan sus contextos.

## Construcción editorial

El entorno de modelado está documentado en ../requirements.txt y la especificación de fase 8 registra versiones. Python 3.14.5, scikit-learn 1.9.0, SciPy 1.18.1 y joblib 1.6.0 forman parte del entorno final comprobado. requirements.txt fija dependencias directas, no todas las transitivas; no se declara un lock completo.

Los gráficos nuevos se construyen exclusivamente desde estadísticas y scores ya guardados:

```powershell
.\.venv\Scripts\python.exe entrega_final/fuentes/preparar_entrega.py
```

Este comando no recalcula predicciones de prueba. Solo calcula coordenadas descriptivas de las curvas desde scores y etiquetas congelados. El PDF se genera con fuentes/exportar_pdf.py, usando ReportLab y Arial; la presentación con fuentes/crear_presentacion.mjs, usando Node.js y @oai/artifact-tool 2.8.99 del runtime editorial. Los paths del runtime local están explícitos en ese constructor y deben adaptarse en otro equipo. Estas herramientas editoriales están separadas del entorno de ML y no se han añadido a requirements.txt. Poppler se utilizó para renderizar el PDF y revisar las 15 páginas. Las 15 diapositivas también se renderizaron y revisaron. No se afirma una apertura o prueba interactiva en Microsoft PowerPoint.

Para exportar el PowerPoint de nuevo, elegir una ruta de salida nueva en el constructor: el finalizador protege la salida existente contra sobrescritura. El PDF se reconstruye a partir del Markdown, que debe actualizarse primero si se corrige autoría. Los ajustes editoriales no autorizan ninguna modificación del modelo o la política.

## Documentación de apoyo

- [Especificación congelada](../reports/seleccion_8_especificacion_congelada.json).
- [Informe de evaluación final](../reports/fase_9_evaluacion_final.md).
- [Recibo de inferencia única](../reports/evaluacion_9_recibo.json).
- [Revisión de fase 10](../reports/fase_10_entrega_final.md).
- [Verificación de entrega](verificacion_entrega.json).
- [Inventario con SHA-256](manifest_entrega.json).

El README principal distingue el protocolo activo de las fases históricas. Los datos, informes y artefactos anteriores se conservan. El antiguo README se archiva sin modificarlo en reports/historico/README_antes_fase10.md.

## Pendiente antes del envío institucional

No se ha encontrado el enunciado oficial. Confirmar nombre de autoría, institución y docente, rúbrica, extensión exigida, duración de exposición y formato o canal de envío. La memoria y portada señalan la ausencia de autoría confirmada; no se ha inventado un nombre. La presentación cubre la estructura solicitada por el usuario y debe contrastarse con los requisitos reales del profesor.
