# Código y notebooks comentados

Esta edición añade comentarios en español dentro del código de todos los módulos activos, las pruebas, los diez notebooks y los constructores de la entrega. Explica qué se hace, para qué se hace y qué precauciones metodológicas corresponden a cada fase. Es independiente de la memoria final.

Los archivos originales utilizados en los experimentos están vinculados a especificaciones y recibos con hashes. Se conservan exactamente en sus ubicaciones originales para mantener verificable la evaluación. Esta carpeta contiene su edición didáctica comentada: las instrucciones ejecutables son las mismas, pero los bytes cambian por los comentarios. No se han entrenado modelos, recalculado predicciones o ejecutado las copias.

**Uso:** abrir estos archivos para estudiar y revisar el código. Para reproducción se conservan las entradas originales y las instrucciones del README principal. Esta edición no constituye un segundo proyecto ejecutable: las rutas y comprobaciones de integridad pertenecen al proyecto original. Las salidas de los notebooks se conservan de aquella ejecución, y no se presentan como una nueva ejecución del texto comentado.

## Recorrido recomendado

| Parte | Archivos comentados | Qué se explica |
|---|---|---|
| Inspección y EDA | [inspection.py](src/inspection.py), [eda.ipynb](notebooks/eda.ipynb) | Estructura, ausentes, repeticiones, tasas, calendario y asociaciones |
| Limpieza | [cleaning.py](src/cleaning.py), [preparation.py](src/preparation.py), [preparacion.ipynb](notebooks/preparacion.ipynb) | Tipos, copias, anomalías y conservación de filas |
| Variables y transformaciones | [features.py](src/features.py), [preprocessing.py](src/preprocessing.py) | Listas cerradas, exclusiones, X/y/metadatos, imputación, one-hot y escalado |
| Particiones | [splitting.py](src/splitting.py), [temporal_bias_v3.py](src/temporal_bias_v3.py), [correccion_sesgo_temporal.ipynb](notebooks/correccion_sesgo_temporal.ipynb) | Cohortes por llegada, embargo, seguimiento y sesgo temporal |
| Baseline y auditoría histórica | [baseline.py](src/baseline.py), [audit_baseline.py](src/audit_baseline.py), [baseline.ipynb](notebooks/baseline.ipynb) | Ajuste en train, trivial, errores, umbrales y calibración descriptiva |
| Protocolo v2 histórico | [temporal_protocol.py](src/temporal_protocol.py), [protocolo_temporal.ipynb](notebooks/protocolo_temporal.ipynb) | Proxies temporales y limitaciones del experimento anterior |
| Comparación histórica | [comparison.py](src/comparison.py), [comparacion_modelos.ipynb](notebooks/comparacion_modelos.ipynb) | Pipelines independientes, auditoría de estadísticas y cinco algoritmos |
| Optimización histórica | [optimization.py](src/optimization.py), [optimizacion.ipynb](notebooks/optimizacion.ipynb) | Folds internos, búsqueda, selección y checkpoints |
| Explicabilidad histórica | [explainability.py](src/explainability.py), [explicabilidad.ipynb](notebooks/explicabilidad.ipynb) | SHAP de XGBoost v2, contribuciones, segmentos y errores |
| Selección definitiva | [final_selection.py](src/final_selection.py), [seleccion_final.ipynb](notebooks/seleccion_final.ipynb) | Comparación en validación v3, capacidad y congelación |
| Política mensual | [decision_policy.py](src/decision_policy.py) | Cupo por mes, ranking, hash, empates y ausencia de etiquetas |
| Evaluación final | [final_evaluation.py](src/final_evaluation.py), [evaluacion_final.ipynb](notebooks/evaluacion_final.ipynb) | Preflight, inferencia única, congelación anterior a y y métricas |
| Interpretación | [evaluation_narrative.py](src/evaluation_narrative.py) | Lectura de resultados guardados sin volver a evaluar |
| Ejecución de notebooks | [run_notebook.py](src/run_notebook.py) | Rutas, kernel local y bloqueo de entradas históricas |
| Pruebas | [tests](tests) | Contratos, errores esperados, cuota mensual, empates e integridad |
| Construcción editorial | [fuentes](entrega_final/fuentes) | Gráficos desde scores guardados, PDF, PowerPoint y auditoría |

Los nombres y explicaciones identifican los experimentos históricos v1/v2 y el protocolo final v3. Los comentarios no actualizan retroactivamente resultados ni convierten SHAP de XGBoost en una explicación de logística.

## Comprobación de equivalencia

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe herramientas/verificar_comentarios.py
```

La comprobación valida hashes, que el diff solo inserta líneas de comentarios y que el AST de cada Python y celda de notebook coincide con el original. También comprueba que salidas, orden de celdas y contadores de ejecución permanecen idénticos. No ejecuta modelos ni notebooks. Los archivos JavaScript pasan además comprobación de sintaxis con Node.js.

El detalle por archivo está en [verificacion_comentarios.json](verificacion_comentarios.json). El generador reproducible es herramientas/comentar_proyecto.py, en la raíz del proyecto.
