# Revisión de comentarios del proyecto

Se añade una edición didáctica en codigo_comentado, independiente de la memoria, que cubre todos los módulos src, las diez pruebas modulares, los diez notebooks y los scripts editoriales. Se incorporan 890 líneas de comentarios en 44 archivos para explicar operaciones, decisiones y comprobaciones.

Los comentarios abordan lectura y calidad, conservación de filas, selección de variables, metadatos, imputación, codificación, escalado, particiones temporales y embargo, entrenamiento histórico, métricas, búsqueda interna, SHAP situado, política de capacidad, desempates y congelación de la evaluación. Los bloques de código de los notebooks reciben comentarios específicos de su objetivo, además de sus explicaciones Markdown originales.

Las fuentes originales vinculadas a los hashes de fases 8 y 9 y a la auditoría de entrega permanecen byte a byte intactas. Las copias comentadas son para lectura y revisión, no una nueva ruta de ejecución: conservan las rutas de las fuentes originales. Las salidas de los notebooks son las ya guardadas y no acreditan una ejecución nueva de esta edición.

La verificación independiente herramientas/verificar_comentarios.py comprueba que los cambios son inserciones de comentarios, que los AST de Python y las celdas coinciden y que las salidas y metadatos de notebooks son idénticos. Los dos JavaScript editoriales reciben comentarios entre líneas y comprobación de sintaxis. No se entrenan modelos, ejecutan notebooks o recalculan predicciones. Las fuentes históricas archivadas v1/v2 conservan sus bytes originales.

La entrada de lectura y el índice por tema están en codigo_comentado/README.md. El manifiesto codigo_comentado/verificacion_comentarios.json registra las dos huellas de cada archivo y los comentarios añadidos. Esto permite distinguir el código ejecutado y sellado de su explicación didáctica sin invalidar la trazabilidad del proyecto.
