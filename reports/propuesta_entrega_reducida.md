# Propuesta de entrega académica reducida

Fecha: 26/10/2026. **Propuesta para aprobación; no implementada.** No existe todavía la carpeta `entrega_profesor` ni se ha construido el notebook único. El proyecto recuperado y el respaldo independiente se conservan completos.

## Paquete propuesto: cuatro archivos

Ruta futura: `C:\Users\panio\Documents\Curso\DataScience\proyecto_machineLearning\entrega_profesor`.

```text
entrega_profesor/
    cancelaciones_hoteleras.ipynb
    hotel_bookings.csv
    presentacion_cancelaciones.pptx
    README.md
```

| Archivo que recibiría el profesor | Contenido y justificación | Origen / trabajo pendiente |
|---|---|---|
| `cancelaciones_hoteleras.ipynb` | Único documento ejecutable con proceso, comentarios, gráficos, SHAP y conclusiones | Nuevo archivo por construir después de aprobar; no concatenación |
| `hotel_bookings.csv` | Datos necesarios para ejecutar sin red; 16.855.599 bytes | Copia exacta de `data/raw/hotel_bookings.csv`, SHA-256 `7c2ae42a7353905ea136e5c2287f17c92c5435826598bfbb8491c6f0c7b1fc06` |
| `presentacion_cancelaciones.pptx` | Presentación académica con notas | Copia revisada de `entrega_final/presentacion_final.pptx`; requiere ROC y explicación del ganador |
| `README.md` | Versiones, instalación, ejecución, origen/hash de datos, alcance retrospectivo y significado de métricas | Nuevo texto corto; también contiene la lista de dependencias para evitar un quinto archivo |

Son cuatro archivos propuestos, **no cuatro archivos actuales ya listos para enviar**. Dos entregables son los exigidos (notebook y presentación); CSV y README tienen función de ejecución y trazabilidad. Si el profesor exige un `requirements.txt` separado, pasaría a ser un quinto archivo justificado. No es necesario añadirlo si las instrucciones exactas están en README. El vídeo se añadiría únicamente si no se realiza la exposición en clase; no se cuenta por defecto.

No se enviarán `.venv`, `.git`, cachés, diez notebooks originales, código duplicado, backups, históricos, informes intermedios, generadores editoriales, renders, joblib o predicciones auxiliares en este paquete mínimo. Permanecen en el proyecto de desarrollo. La memoria PDF se conserva, pero no se añade al paquete por defecto porque los requisitos transcritos no la exigen.

## Cuánto se reduce y qué se conserva

El proyecto recuperado tiene 537 archivos y 106.424.483 bytes. El objetivo es una entrega de cuatro archivos, una reducción de 533 nombres (99,26%). No es una reducción exacta de bytes: el nuevo notebook y la presentación revisada aún no existen. El CSV aporta unos 16,86 MB decimales; el tamaño final y tiempo de ejecución deben medirse después. No se eliminan los originales ni los duplicados, y una coincidencia de contenido no convierte un respaldo histórico en prescindible.

El conjunto completo queda donde estaba, con fases v1/v2/v3, evidencias y modelos. El respaldo independiente está en `C:\Users\panio\Documents\Curso\DataScience\respaldo_ml_original_20261026`, con pares `$R/$I`, correspondencia original y verificación de recuperación. No debe confundirse con la futura entrega ni enviarse al profesor.

## Arquitectura del notebook único

El archivo debe abrirse desde `entrega_profesor` y depender solo de bibliotecas instaladas y del CSV situado junto a él. Incluirá funciones pequeñas dentro del propio notebook para preparación, partición, pipelines, política y gráficos. No importará `src` ni leerá `reports`, `models`, `data/processed` o rutas absolutas del autor. Los gráficos estarán generados e incorporados en las salidas; no requerirán PNG externos. La lista de predictores será cerrada, nunca `drop(target)`.

| Sección propuesta | Reutilización | Cambio necesario |
|---|---|---|
| 1. Problema y objetivo | Memoria y diapositivas 2–3 | Resumen en términos de riesgo y seguimiento |
| 2. Datos y carga | EDA, inspección y CSV original | Ruta relativa, hash, tipos/nulos; explicar Excel sin modificarlo |
| 3. EDA | Celdas 15, 18, 21 y 30 de EDA | Cinco preguntas obligatorias; media ADR visible; evitar 13 gráficos indiscriminados |
| 4. Acciones por EDA | Interpretaciones existentes | Una acción prudente por sección, vinculada a Revenue Management |
| 5. Limpieza | `cleaning.clean` | Conservar filas y política de nulos/anomalías; sin aprender estadísticas globales |
| 6. Features | `features.build_features` | `total_nights` y `children_missing`, cada una con una o dos frases de negocio |
| 7. Leakage | Lista `FEATURES` y auditoría de disponibilidad | Separar X, y y metadatos; declarar snapshots inciertos |
| 8. Tiempo | Regla pura de `temporal_split_v3` | Tabla de cinco bloques, embargos, controles y alcance retrospectivo |
| 9. Baseline | Fábrica de logística | Ajuste solo train, umbral 0,5 para validación, referencia trivial |
| 10. Comparación | Logística/XGBoost iniciales de v3 | Misma población, preprocesamiento por modelo y métricas comparables |
| 11. Optimización | Evidencia y diseño de fase 6 | Distinguir demostración histórica v2 de la selección v3; decisión pendiente descrita abajo |
| 12. Desbalanceo | Prevalencias, AP/PR y política | Justificar expresamente no ponderar o aprobar un estudio train-only |
| 13. Evaluación | Resultados congelados v3 y política | Métricas bien etiquetadas, FP/FN, ROC/PR; no retocar decisiones tras test |
| 14. SHAP | Concepto y nomenclatura, no valores de XGBoost v2 | Explicar logística v3, summary y dos waterfall, preferiblemente en validación |
| 15. Conclusiones finales | Fase 9 y memoria | Última celda Markdown con detección, cobertura, límites y siguientes pasos |

Las secciones 3 y 4 pueden intercalarse para que cada gráfico termine en su decisión. Las limitaciones no necesitan reproducir la cronología completa de auditorías. Bastará explicar por qué se descartó v2 y cómo limita eso la evidencia histórica.

## Punto que requiere decidir antes de implementarlo

El mínimo de cuatro archivos **no puede reproducir el recibo histórico de una inferencia única leyendo archivos que se han excluido**. Tampoco sería honesto presentar tablas pegadas como si acabaran de entrenarse. Debe distinguirse una nueva ejecución académica de la reproducción exacta de artefactos históricos.

Recomiendo un notebook de proceso autónomo, que, en una futura fase autorizada, ajuste de nuevo modelos solo para verificar su ejecución en copia aislada y contraste los resultados con referencias históricas incorporadas y etiquetadas. Eso requeriría autorización expresa para entrenar y, si debe evaluar test de nuevo, para inferir en esa copia. La ejecución no reescribiría el modelo, scores, métricas ni recibos originales; el resultado v3 histórico seguiría siendo la referencia. Una ejecución nueva puede presentar pequeñas diferencias numéricas y no obtiene independencia prospectiva por volver a correr.

Si se mantiene la prohibición de cualquier nueva inferencia incluso en el futuro notebook, solo puede prepararse una modalidad de revisión desde artefactos congelados. Esa modalidad necesitaría añadir al menos scores y etiquetas de test, y el modelo para SHAP, y **no equivaldría a reproducir el proceso completo desde cero con cuatro archivos**. No la recomiendo como sustituto silencioso del requisito académico.

Para la optimización hay evidencia real v2 reutilizable sin modificar resultados. Primera opción conservadora: sección histórica expresamente identificada, con diseño, parámetros y resultados, dejando claro que el protocolo fue descartado y que no optimizó el ganador. Su suficiencia depende de que el docente acepte una demostración de optimización histórica. Si se exige una búsqueda ejecutable coherente con v3, propongo solicitar autorización específica para una demostración limitada con folds temporales solo dentro de train v3, sin usar validación/test para escoger decisiones nuevas. Se registraría como trabajo académico adicional posterior, **no como origen retrospectivo de la decisión congelada**, y no cambiaría el ganador ni su política. No se ha ejecutado ninguna de estas opciones.

Esta decisión tiene que resolverse antes de afirmar que el nuevo notebook cubre por completo la rúbrica. No hace falta ampliar a cinco algoritmos v3, ejecutar decenas de experimentos o crear un nuevo proyecto para resolverla.

## Dependencias y entorno

El README propuesto incluirá las versiones directas verificadas existentes: pandas 3.0.3, NumPy 2.4.6, matplotlib 3.11.0, seaborn 0.13.2, scikit-learn 1.9.0, XGBoost 3.4.1 y SHAP 0.54.1; Python histórico 3.14.5. LightGBM 4.7.0 solo resulta necesario si se incorpora su búsqueda histórica ejecutable. nbformat 5.11.1, nbclient 0.11.0 e ipykernel 7.4.0 son las herramientas existentes de ejecución/validación; la interfaz Jupyter elegida debe quedar documentada aparte, sin inventar una versión no comprobada.

No se requiere openpyxl si se entrega el CSV, ni ReportLab, Artifact Tool o Node para ejecutar el notebook o abrir el PowerPoint final. El notebook básico del profesor importa Optuna y DALEX, pero nuestro código no los necesita para usar su propia búsqueda/SHAP. No se añadirán por copiar importaciones del ejemplo docente. Las dependencias transitivas no están bloqueadas: instalación y ejecución limpias siguen pendientes de prueba.

## Presentación reducida

Partir de las 15 diapositivas actuales y sus notas; conservar problema, objetivos, datos, preparación, calendario, ganador, política, resultados y límites. Reutilizar espacio de la comparación histórica para mostrar la curva ROC v3 y otro espacio para la importancia del ganador. Asegurar cinco insights EDA en el notebook y una selección clara para exposición. Mostrar 1.224 FP y 7.796 FN, capacidad hipotética y próximos pasos. No es necesario ampliar el número de diapositivas. Completar autoría antes del envío.

SHAP del ganador y cambios editoriales todavía requieren trabajo autorizado. No se copiará simplemente el PowerPoint actual con otro nombre afirmando que ya cubre las carencias.

## Condiciones para aceptar la futura entrega

1. Aprobar estructura y resolver la modalidad de ejecución/optimización anterior.
2. Construir en archivos nuevos, sin modificar el proyecto recuperado.
3. Confirmar que el paquete contiene un solo `.ipynb` y que ningún recurso del desarrollo es necesario para ejecutarlo.
4. Comprobar los cinco EDA con acciones, las dos features justificadas, la partición temporal, pipelines, comparación y gestión del desbalanceo.
5. Verificar summary y dos waterfall de logística v3 con base y salida consistentes; mantener XGBoost v2 rotulado como histórico si se menciona.
6. Ejecutar desde cero en entorno aislado autorizado y verificar cada salida, las dependencias y tiempos. Si no se hace, rotular reproducibilidad como no verificada.
7. Verificar que memoria, presentación y resultados históricos originales mantienen hashes; comparar las cifras del futuro notebook sin imponer coincidencias inventadas ni corregir silenciosamente valores.
8. Revisar la presentación y confirmar exposición o vídeo.

## Estado al cerrar esta fase

Únicamente se han recuperado los originales y elaborado los tres informes solicitados. No se ha simplificado el árbol, eliminado duplicados, construido el notebook único, creado `entrega_profesor`, modificado la presentación ni repetido entrenamiento/inferencia. Se espera aprobación del usuario sobre esta propuesta.
