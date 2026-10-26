# Decisión metodológica previa a entrenamiento v3

Se fija la estrategia antes de calcular métricas v3 o consultar etiquetas de prueba. No se comparan modelos entre alternativas.

**A — Cohortes por alta aproximada con seguimiento común.** Es más cercana a predecir al crear reservas. Sin embargo, el CSV está delimitado por llegada, no por alta: no acredita cohortes completas de altas ni incluye reservas con llegadas fuera de julio de 2015–agosto de 2017. Extender el seguimiento hasta 2018 para todas las altas evita el filtro individual por resultado, pero no permitiría afirmar que los resultados de entrenamiento estaban disponibles al alta de las reservas de validación. Conservar los cortes de altas de v2 y exigir cohortes completamente resueltas antes de ellos no es viable sin retirar cohortes enteras o disponer de más historia/logs. Un horizonte fijo de antelación cambiaría la población y no se impone para mejorar resultados. No se selecciona A con estos datos para simular el alta.

**B — Cohortes completas por llegada con embargo. Seleccionada.** La extracción cubre ese calendario y permite incluir todas las filas de cada bloque, sin rescatar cancelaciones tempranas. Se conserva un ciclo anual de llegadas para entrenamiento y se deja un margen de dos meses de calendario para seguimiento, en vez de filtrar filas por su fecha de estado:

- Entrenamiento: llegadas 2015-07-01 ≤ fecha < 2016-07-01; cierre proxy común exclusivo 2016-09-01.
- Embargo entre ajuste y validación: julio–agosto de 2016.
- Validación: llegadas 2016-09-01 ≤ fecha < 2017-01-01; cierre proxy común exclusivo 2017-03-01.
- Embargo entre validación y prueba: enero–febrero de 2017.
- Prueba reservada: llegadas 2017-03-01 ≤ fecha < 2017-09-01. No se usan sus etiquetas, scores o métricas. El cierre retrospectivo asumido 2018-12-01 queda para una futura auditoría autorizada; no está acreditado por el PMS.

Los dos meses son un margen de calendario fijado antes de métricas, no un plazo universal de madurez validado. La auditoría previa de metadatos de los bloques train/validación contrasta salida prevista + un día y último estado + un día contra su cierre. Si alguna fila incumple, se bloquea la ejecución de todo el bloque: no se elimina la fila ni se aceptan solo cancelaciones tempranas. La comprobación no garantiza ausencia de actualizaciones faltantes o el momento real de ingestión.

Esta alternativa cambia expresamente el objeto evaluado a generalización retrospectiva entre cohortes de llegada. Las altas aproximadas pueden solaparse entre bloques y algunas reservas se crearon antes de entrenar: no es una simulación al alta ni al primer contacto. La falta de snapshots iniciales permanece.

Los IDs de prueba v1/v2 quedan en prueba v3 o en su embargo; nunca pasan a entrenamiento o validación. Parte de la nueva prueba ya participó en desarrollo v2: se documentará por IDs, sin utilizar sus etiquetas, y no se llamará holdout independiente. No se recupera independencia de todas las decisiones metodológicas redefiniendo particiones. Los apartados por embargo permanecen en el dataset y manifiesto.

V3 sustituirá el protocolo activo. V1 y v2 se conservan con hashes, fuentes, informes y notebooks históricos. Las métricas v2 no serán un ranking contra las de v3. Se reentrenarán únicamente logística inicial y XGBoost inicial, con umbral diagnóstico 0,5, sin tuning, calibración ni evaluación de prueba.
