# Comentarios integrados en los archivos principales

## Alcance

Se han documentado directamente los archivos principales, utilizando codigo_comentado como referencia y revisando las explicaciones para evitar comentarios triviales o repetitivos:

- 32 archivos Python de src/, tests/ y entrega_final/fuentes/.
- 2 JavaScript de construcción y revisión editorial.
- Los 10 notebooks originales, con comentarios en código y 64 celdas Markdown antes de sus bloques.

Las explicaciones cubren la finalidad de cada fase, limpieza y ausentes, separación de predictores/objetivo/metadatos, prevención de leakage, ajuste del preprocesamiento solo con train, algoritmos, validación temporal, métricas, SHAP histórico, política mensual, desempates, integridad y limitaciones. Los experimentos v1/v2 se identifican como históricos; v3 y la evaluación final conservan su alcance retrospectivo.

Además se actualizan los dos README y el manifiesto de entrega para identificar las fuentes documentadas y el auditor vigente. En total se modifican 47 archivos preexistentes: 44 de código/notebooks y 3 de documentación o integridad. Las nuevas herramientas y evidencias de esta revisión son adicionales a ese recuento.

## Respaldo anterior a la modificación

Antes de modificar cualquier archivo se copió y verificó cada uno de los 47 archivos afectados en [historico/documentacion_pre_integracion](historico/documentacion_pre_integracion). Su registro_previo.json guarda los hashes de las copias y una captura de integridad de los demás archivos del proyecto.

La carpeta codigo_comentado permanece intacta como referencia anterior. No se han modificado los archivos históricos v1/v2 ni la copia del código de inferencia guardada con los resultados de fase 9.

## Integridad documental e histórica

El [registro de revisión](documentacion_integrada_registro.json) enlaza los hashes anteriores, los respaldos y los hashes actuales. El [resultado de auditoría](documentacion_integrada_verificacion.json) clasifica los cambios y contrasta la estructura ejecutable. El manifiesto de entrega contiene los hashes actuales de README y constructores editoriales; la versión anterior también está respaldada.

Los recibos históricos y la especificación de fase 8 no se reescriben. Sus SHA-256 identifican exactamente los bytes utilizados entonces, por lo que añadir comentarios cambia las huellas de las fuentes actuales. Las comprobaciones históricas estrictas deben contrastarse con el respaldo de aquella fuente; no se hace pasar la nueva huella por la de ejecución ni se desactiva ninguna protección.

La auditoría vigente comprueba simultáneamente: integridad de los bytes históricos respaldados, integridad de la versión documental registrada, igualdad de instrucciones y conservación exacta de los artefactos ML. Este criterio documental solo se aplica al código y las celdas admitidos por el registro. Datos, modelos, especificación, manifiesto de particiones, scores y métricas siguen exigiendo sus hashes exactos.

## Comprobaciones estáticas

Desde la raíz:

```powershell
.\.venv\Scripts\python.exe herramientas/auditar_documentacion_integrada.py
```

El auditor utiliza biblioteca estándar y no importa módulos de modelado. Comprueba:

1. SHA-256 del respaldo, de cada fuente antes/después y de los archivos ajenos a la revisión.
2. Diff de Python/JavaScript limitado a inserciones de comentarios, con conservación del código previo.
3. AST de Python y de cada celda de notebook idéntico, incluyendo literales y docstrings. La compilación se realiza en memoria sin ejecutar código ni generar pyc.
4. Tokens de código idénticos: nombres, operadores, literales, sangrías y líneas mágicas de IPython. Las magias solo se sustituyen temporalmente para el parseo AST, nunca en el notebook.
5. Las 64 celdas nuevas son exclusivamente Markdown. Al retirarlas para comparar, las celdas originales mantienen su orden e identificadores; las salidas, contadores y metadatos son idénticos.
6. Modelo, datos, particiones, especificación y resultados finales intactos, incluyendo el recibo de una sola inferencia.
7. Integridad de los 105 archivos de referencia del curso y del inventario actualizado de entrega.

También se valida el formato nbformat de los diez notebooks y la sintaxis de los dos JavaScript mediante node --check. No se ejecuta ningún notebook, prueba de entrenamiento o experimento. La auditoría antigua de bytes se conserva como evidencia de su versión y no sustituye a la verificación documental vigente.

El [registro estático complementario](documentacion_integrada_estatica.json) documenta los diez esquemas nbformat válidos, la compilación en memoria de los 36 Python principales y auxiliares, y las dos comprobaciones de sintaxis JavaScript.

## Resultado

No hay diferencias en el código ejecutable respecto a la versión anterior. Se conservan parámetros, predictores, particiones, modelos, scores y resultados. El aumento de líneas cambia ubicaciones de errores y hashes de fuentes, como corresponde a una revisión documental; no cambia las operaciones de cálculo. Las salidas existentes pertenecen a la ejecución anterior y no se presentan como una ejecución nueva.

No se han reentrenado modelos, recalibrado scores o repetido predicciones de prueba. La memoria, el PDF, la presentación, los gráficos y las métricas finales permanecen intactos.
