# Inventario del proyecto recuperado

Fecha: 26/10/2026. Inventario completo de los **537 archivos recuperados**, no de las bibliotecas instaladas en `.venv` ni de objetos internos de `.git`.

## Recuperación e integridad

Raíz restaurada: `C:\Users\panio\Documents\Curso\DataScience\proyecto_machineLearning`.

Respaldo independiente: `C:\Users\panio\Documents\Curso\DataScience\respaldo_ml_original_20261026`. Contiene `papelera_original/` con **537 pares `$R/$I` (1.074 archivos)**, `correspondencia_recuperacion.json` y `verificacion_recuperacion.json`. La correspondencia conserva ruta original, nombre interno, tamaño, SHA-256 del contenido y del metadato y fecha de eliminación. Es una copia de seguridad independiente fuera del proyecto y de la papelera, aunque está en el mismo volumen C: y no protege frente a pérdida física de ese disco.

Antes de copiar se comprobaron 537 contenidos por 106.424.483 bytes, rutas resueltas dentro de la raíz original, ausencia de destinos existentes y espacio libre. Había 135.050.735.616 bytes disponibles, muy por encima de los 317.847.482 bytes requeridos por el control conservador (dos copias de contenido, metadatos y 100 MiB de margen). Se verificó primero el respaldo y solo después se restauró desde él mediante creación exclusiva de archivos. No hubo conflictos ni sobrescrituras. Se conservaron los tiempos de modificación de los contenidos; los tiempos de creación del sistema de archivos restaurado no se presentan como evidencia original: los metadatos originales están en el respaldo.

Resultado: **537/537 restaurados**, 106.424.483 bytes, hashes idénticos a papelera; 432 archivos contrastados con registros documentales actuales, 47 respaldos históricos y 21 entradas del manifiesto editorial conformes. Los conjuntos se solapan. El registro previo también coincide con su hash registrado. Los pares de la papelera permanecen íntegros. No se ejecutó código del proyecto ni se cargó el modelo para inferir.

La desaparición está acreditada por entradas de papelera fechadas el **25/10/2026, 19:24:05–19:24:12, Europe/Madrid**. Se desconoce autor, aplicación o motivo. No se atribuye a sincronización o a otra sesión sin pruebas.

## Clasificación primaria sin doble conteo

Cada archivo tiene una sola categoría primaria. El criterio da prioridad a respaldos/históricos/referencia/temporales sobre la extensión. Por ello un PNG de protocolo v2 se cuenta en histórico y no otra vez en gráficos, y un notebook respaldado no se cuenta como notebook principal. Las categorías combinadas explicitan su contenido. Los duplicados se analizan después como etiqueta transversal.

| Categoría | Archivos | Bytes | Función | Para reproducir | Para entrega académica |
|---|---:|---:|---|---|---|
| Archivos generados temporales | 54 | 4282654 | Borradores, 45 renders, inspecciones y snapshots de gráficos. | No para entrenar; útiles para revisión visual/editorial. | No. |
| Archivos históricos | 148 | 22772989 | Protocolos v1/v2 e informes anteriores congelados. | Necesarios para trazabilidad y reproducir historia; no para v3 puro. | No. |
| Código auxiliar | 9 | 95535 | Herramientas documentales y constructores editoriales. | Necesario solo para regenerar auditorías/documentos. | No. |
| Código auxiliar de referencia | 46 | 5362338 | Árbol codigo_comentado, referencia documental anterior. | No para cálculo ML; evidencia de documentación. | No. |
| Código fuente vigente (incluye entradas históricas) | 19 | 366185 | Módulos de preparación, experimentos, política y evaluación; vigente no implica que todas las entradas sean v3. | Sí para ejecutar las entradas actuales; funciones puras se pueden integrar. | No como archivos separados en propuesta autónoma. |
| Datos originales | 1 | 16855599 | Fuente de 119.390 reservas; preservación exacta del CSV. | Sí, para reproducción desde datos. | Sí: una copia CSV. |
| Datos procesados | 1 | 17849778 | Preparación determinista con features, target y metadatos. | Derivable del original; útil para reproducción histórica exacta. | No, generarlo en memoria. |
| Documentación y configuración | 10 | 60251 | README, requisitos y documentos explicativos fuera de bloques editoriales. | Requisitos y guía sí; resto según tarea. | Un README nuevo con versiones y ejecución. |
| Documentación y entregables editoriales | 11 | 865689 | PDF/Markdown, PowerPoint, notas, datos y manifiestos editoriales. | Documentos finales no son entradas ML; fuentes/datos editoriales para regeneración. | Solo una presentación revisada; PDF no exigido. |
| Gráficos | 48 | 4204029 | PNG de EDA, evaluación, SHAP y documentos, fuera de históricos/temporales. | Regenerables; necesarios para mostrar salidas actuales que los referencian. | Incorporar solo gráficos pertinentes dentro de notebook/PPTX. |
| Informes y evidencias tabulares | 113 | 11543257 | Fases, métricas, planes, particiones, verificaciones y valores SHAP. | Parte necesaria para trazabilidad de entradas históricas; no todo para entrenar desde cero. | No, sintetizar evidencia pertinente en notebook. |
| Modelos entrenados | 1 | 4476 | Un joblib congelado: logística final. | Sí para reproducción sin refit del modelo histórico. | No en modalidad autónoma desde cero; sería necesario en modalidad de artefactos. |
| Notebooks | 10 | 4875833 | Diez fases con fuentes y salidas históricas. | Útiles para revisar/desarrollar, no deben ejecutarse indiscriminadamente. | Sustituir en la futura entrega por uno nuevo; conservar estos diez. |
| Predicciones y copias de referencia | 8 | 11913062 | Scores/decisiones de etapas y copias para igualdad numérica. | Sí para revisión histórica sin inferencia; no todas las copias para recalcular. | No en modalidad autónoma; test scores/etiquetas serían necesarios si se prohíbe nueva inferencia. |
| Pruebas | 10 | 44883 | Diez archivos de comprobaciones de etapas; algunas entrenan. | Útiles para desarrollo; no ejecutadas en esta fase. | No como archivos separados; controles breves en notebook. |
| Respaldos históricos | 48 | 5327925 | 47 archivos previos más registro_previo.json. | Necesarios para contrastar hashes/bytes históricos tras documentar fuentes. | No. |
| **Total recuperado** | **537** | **106424483** | Proyecto original completo respecto a inventarios verificados | Preservar | Seleccionar en copia futura |

Cachés: **0 dentro de los 537 recuperados**. Ya permanecían en la raíz **30 archivos `.pyc` (604393 bytes)**; no se restauraron, borraron ni regeneraron. También quedaban tres auxiliares de `.jupyter_runtime` y el entorno `.venv`. El inventario de recuperación no los mezcla con los 537. Los archivos internos de entorno/Git no son materiales académicos y se excluyen del recuento de entrega.

## Por qué hay tantos archivos

148 históricos + 48 respaldos preintegración + 46 archivos de `codigo_comentado` + 54 temporales/snapshots suman **296 archivos (55,12% de los recuperados)**. No representan 296 experimentos nuevos: son principalmente versiones, referencias y salidas editoriales. Los 54 temporales incluyen 48 archivos de `tmp` y seis snapshots `.chart-data`. Además se guardan resultados detallados, comprobaciones y gráficos por fase, no solo el resultado final. El volumen de 106,42 MB es moderado en almacenamiento; el problema para el profesor es la dispersión del contenido y las dependencias, no una necesidad de borrar trabajo.

Hay **387 contenidos distintos** por SHA-256. Se detectaron **149 grupos de igualdad exacta**, con **150 copias adicionales** que suman **18.168.961 bytes** respecto a conservar un ejemplar por contenido. Esta cifra es descriptiva, no espacio cuya eliminación esté autorizada. Que dos informes, gráficos o predicciones coincidan puede ser intencional para conservar una fase; no son intercambiables sus roles históricos. `codigo_comentado` también puede ser redundante por función aunque sus bytes no coincidan.

## Qué hace falta conservar y entregar

Conservar los 537 originales, los 30 cachés preexistentes y el respaldo, sin limpieza. No hay un número universal de archivos “necesarios” para toda reproducción: la histórica depende de fuentes, hashes, manifiestos y scores de cada protocolo. Para el paquete académico autónomo se proponen **cuatro archivos**, de los cuales dos son los entregables exigidos y dos soportan datos/ejecución. Ese paquete aún no está construido ni validado. Ver [propuesta_entrega_reducida.md](propuesta_entrega_reducida.md).

## Diez notebooks principales: revisión estática

| Notebook | Celdas | Código | Código sin contador | Errores guardados | Imágenes incorporadas |
|---|---:|---:|---:|---:|---:|
| baseline.ipynb | 19 | 6 | 0 | 0 | 3 |
| comparacion_modelos.ipynb | 14 | 4 | 0 | 0 | 3 |
| correccion_sesgo_temporal.ipynb | 20 | 6 | 0 | 0 | 2 |
| eda.ipynb | 43 | 14 | 0 | 0 | 13 |
| evaluacion_final.ipynb | 17 | 5 | 0 | 0 | 2 |
| explicabilidad.ipynb | 19 | 6 | 0 | 0 | 6 |
| optimizacion.ipynb | 17 | 5 | 0 | 0 | 3 |
| preparacion.ipynb | 29 | 9 | 0 | 0 | 0 |
| protocolo_temporal.ipynb | 13 | 4 | 0 | 0 | 2 |
| seleccion_final.ipynb | 16 | 5 | 0 | 0 | 3 |

Los diez esquemas se validaron con nbformat sin ejecutar celdas. En total hay 64 celdas de código ejecutadas según sus contadores guardados. No equivale a reproducción limpia actual: algunas entradas entrenan, escriben resultados o requieren hashes de las fuentes anteriores a la integración documental. No se han ejecutado.

## Grupos duplicados exactos por contenido

Cada grupo muestra su SHA-256 completo, tamaño de un ejemplar y todas las rutas relativas. No se ha eliminado ni fusionado ningún archivo.

### Grupo 1: 2 archivos, 1832872 bytes por ejemplar

`9f246d9e36b75ca29ff9f642aa2a5a6590ed4b5b8b1e0092ff45c8813fdfa719`

- `reports/historico/protocolo_v2/reports/optimizacion_6_ids_folds.csv`
- `reports/optimizacion_6_ids_folds.csv`

### Grupo 2: 2 archivos, 1763048 bytes por ejemplar

`1f668616d7e39c8e5eb478c5cf175ec5c72c01e9c9fb2889842a2638f1973ae6`

- `reports/comparacion_5_predicciones_validacion.csv`
- `reports/historico/protocolo_v2/reports/comparacion_5_predicciones_validacion.csv`

### Grupo 3: 2 archivos, 1763026 bytes por ejemplar

`47c78ded3b64544b028d0c14d6bc99871f83546b3e7e321a8c1a76d6127f21f3`

- `reports/comparacion_5_referencia_reproduccion.csv`
- `reports/historico/protocolo_v2/reports/comparacion_5_referencia_reproduccion.csv`

### Grupo 4: 2 archivos, 1597585 bytes por ejemplar

`b44d29d914cca3320cffdc6e785e12708e89da222e3aab3ba5efcc8bda2ea518`

- `reports/historico/protocolo_v2/reports/optimizacion_6_predicciones_validacion.csv`
- `reports/optimizacion_6_predicciones_validacion.csv`

### Grupo 5: 2 archivos, 1380339 bytes por ejemplar

`795f15aa3ee03b538dffff01cc537f41486034aa9b5c404acf5475f0bade66a3`

- `reports/historico/documentacion_pre_integracion/notebooks/eda.ipynb`
- `reports/historico/protocolo_v2/notebooks/eda.ipynb`

### Grupo 6: 2 archivos, 1122968 bytes por ejemplar

`bcf6af837a5be629f66909360c3524f0a93c0ea48bf031a6d11bf7e315cc1f13`

- `reports/seleccion_8_predicciones_validacion.csv`
- `reports/seleccion_8_referencia_reproduccion.csv`

### Grupo 7: 2 archivos, 1054093 bytes por ejemplar

`849ba306a3cd7be413abc045403367c34672f4726ce33e4e6ac7d28cd84be557`

- `reports/historico/documentacion_pre_integracion/notebooks/explicabilidad.ipynb`
- `reports/historico/protocolo_v2/notebooks/explicabilidad.ipynb`

### Grupo 8: 2 archivos, 869547 bytes por ejemplar

`018f96920bee52a617df27398ca2d18286d8369e213fac0f433f1f027da5a9e6`

- `reports/explicabilidad_7_shap.npz`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_shap.npz`

### Grupo 9: 2 archivos, 669240 bytes por ejemplar

`c55bc6bf16e3cfeb294a0e5018854b2c450de86365dec417bdb65dc086872567`

- `reports/historico/documentacion_pre_integracion/notebooks/optimizacion.ipynb`
- `reports/historico/protocolo_v2/notebooks/optimizacion.ipynb`

### Grupo 10: 2 archivos, 407695 bytes por ejemplar

`dd390d56af8eacfb718942b5262e30863e3c96a2a6743c55436610c47f337f23`

- `reports/historico/documentacion_pre_integracion/notebooks/comparacion_modelos.ipynb`
- `reports/historico/protocolo_v2/notebooks/comparacion_modelos.ipynb`

### Grupo 11: 2 archivos, 361081 bytes por ejemplar

`82ea3ef821b6d3d100c43b6408611402c6ba86968f2f50d3a02fe4f34dbe5364`

- `reports/explicabilidad_7_predicciones_validacion.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_predicciones_validacion.csv`

### Grupo 12: 2 archivos, 223661 bytes por ejemplar

`fff32f5fd46b61c03d5e5e997523f552e9fa3d34dd8820d934fcadd47e6a5902`

- `reports/figures/08_evolucion_temporal.png`
- `reports/historico/protocolo_v2/reports/figures/08_evolucion_temporal.png`

### Grupo 13: 2 archivos, 208501 bytes por ejemplar

`713855e376b70e2e4428be7b17928279bda9e0a50a8ed9b09909611dc61ad554`

- `reports/historico/documentacion_pre_integracion/notebooks/baseline.ipynb`
- `reports/historico/protocolo_v2/notebooks/baseline.ipynb`

### Grupo 14: 2 archivos, 191620 bytes por ejemplar

`3e512c7fcf58fc7b88b092ea18bf63ba9d5343fc618568a1f149021441217432`

- `reports/figures/optimizacion_6_umbrales.png`
- `reports/historico/protocolo_v2/reports/figures/optimizacion_6_umbrales.png`

### Grupo 15: 2 archivos, 175808 bytes por ejemplar

`a88fcfac9fd35ffc8561a51e6f6b42a662e3e6dbed547132ba7948fd58eb832a`

- `reports/figures/optimizacion_6_pr_calibracion.png`
- `reports/historico/protocolo_v2/reports/figures/optimizacion_6_pr_calibracion.png`

### Grupo 16: 2 archivos, 173447 bytes por ejemplar

`fc88d822d224c090e8fb12ae5c583a231cf78e389a662edc2a6a4be30e24be5b`

- `reports/figures/10_correlaciones.png`
- `reports/historico/protocolo_v2/reports/figures/10_correlaciones.png`

### Grupo 17: 2 archivos, 168325 bytes por ejemplar

`611bcff289cffb8cbd9353579dc5be61ecd9ad272bf154eabf5b79b79146661a`

- `reports/figures/comparacion_5_curvas.png`
- `reports/historico/protocolo_v2/reports/figures/comparacion_5_curvas.png`

### Grupo 18: 2 archivos, 166732 bytes por ejemplar

`5ad04ac899fc635639e5a442d3e8fba8c551345355918d3aecd1992adcedd721`

- `reports/figures/explicabilidad_7_shap_resumen.png`
- `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_shap_resumen.png`

### Grupo 19: 2 archivos, 158186 bytes por ejemplar

`f0b1ee4d9661012719f8a9455e16d8f9bc721decbbb5c8a0e8c77046bb9432b2`

- `reports/historico/documentacion_pre_integracion/notebooks/protocolo_temporal.ipynb`
- `reports/historico/protocolo_v2/notebooks/protocolo_temporal.ipynb`

### Grupo 20: 2 archivos, 148958 bytes por ejemplar

`4584db4d82978cb25230455baa299b074b23f476ec29be0d5fbbf79d784a5425`

- `reports/figures/explicabilidad_7_dependencias.png`
- `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_dependencias.png`

### Grupo 21: 2 archivos, 143007 bytes por ejemplar

`fb6254fae92e7dc84b0280c3b5aa96c4ba0c03a867cb3a4e1f633ba801381d4f`

- `reports/figures/explicabilidad_7_calibracion.png`
- `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_calibracion.png`

### Grupo 22: 2 archivos, 130320 bytes por ejemplar

`6ee6ea9bc2e163c4ddb39824f82a748f8a1badf04e7263d99ced2b7bb8a4a24c`

- `reports/figures/explicabilidad_7_locales.png`
- `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_locales.png`

### Grupo 23: 2 archivos, 126399 bytes por ejemplar

`594179bd17315fd4094445ba631cb003a551a10b301db8863c37833c3fbc8b4f`

- `reports/figures/auditoria_4_1_04_precision_recall_umbrales.png`
- `reports/historico/protocolo_v2/reports/figures/auditoria_4_1_04_precision_recall_umbrales.png`

### Grupo 24: 2 archivos, 111377 bytes por ejemplar

`b2ed8b53e7d3b1a0a83ca7e217a592528f9ee790370730c6db1cb5cf65d1eeaa`

- `reports/figures/09_estacionalidad.png`
- `reports/historico/protocolo_v2/reports/figures/09_estacionalidad.png`

### Grupo 25: 2 archivos, 109976 bytes por ejemplar

`8fa26cadee6b044d6aaa13458785dbb4c6faa791b756e81cd7f3a981f299e3b4`

- `reports/figures/03_antelacion_adr.png`
- `reports/historico/protocolo_v2/reports/figures/03_antelacion_adr.png`

### Grupo 26: 2 archivos, 106127 bytes por ejemplar

`0cf3df9531000c4a119b49f9af26c5a6cb42db96d3ed38d55f2d1d14737db5f9`

- `reports/figures/auditoria_4_1_01_sesgo_antelacion.png`
- `reports/historico/protocolo_v2/reports/figures/auditoria_4_1_01_sesgo_antelacion.png`

### Grupo 27: 2 archivos, 100153 bytes por ejemplar

`64f1de722c79e8b4f3dc954354d000781633289a1f0f84269aed32a720e55fc9`

- `reports/historico/documentacion_pre_integracion/notebooks/preparacion.ipynb`
- `reports/historico/protocolo_v2/notebooks/preparacion.ipynb`

### Grupo 28: 2 archivos, 96161 bytes por ejemplar

`019756a7b7283e8ea809da18add09c72d7b56e39cd2fe25bd8727955cbed52bb`

- `reports/figures/auditoria_4_1_03_calibracion_validacion.png`
- `reports/historico/protocolo_v2/reports/figures/auditoria_4_1_03_calibracion_validacion.png`

### Grupo 29: 2 archivos, 86632 bytes por ejemplar

`3a2e917b402cf216b852bf3598cc54871a8716d0800fdc69e5c20be46a7ab363`

- `reports/figures/optimizacion_6_estabilidad.png`
- `reports/historico/protocolo_v2/reports/figures/optimizacion_6_estabilidad.png`

### Grupo 30: 2 archivos, 85437 bytes por ejemplar

`247ddea91f78e37481fedb7ada869984d13d0c6c74969a5c93fd9b01d872f458`

- `entrega_final/figuras/06_mensual.png`
- `reports/figures/evaluacion_9_mensual.png`

### Grupo 31: 2 archivos, 77181 bytes por ejemplar

`51de0dee6f74d1be742c965b9a8fd2b5214965920fdc066914ac55f771ef2a3f`

- `reports/figures/comparacion_5_matrices.png`
- `reports/historico/protocolo_v2/reports/figures/comparacion_5_matrices.png`

### Grupo 32: 2 archivos, 74980 bytes por ejemplar

`7eb999b0143dd228c400f16c1aa2c03b7b531a8a7e4f346184187e2b2372a5dd`

- `.chart-data-2rYvdW/candidate.pptx`
- `entrega_final/presentacion_final.pptx`

### Grupo 33: 2 archivos, 72217 bytes por ejemplar

`c9d10dc2030c06c869bdfd7ef24521ce96d4f3ad33899f22378fe4c01acd8ff2`

- `reports/figures/explicabilidad_7_importancias.png`
- `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_importancias.png`

### Grupo 34: 2 archivos, 70172 bytes por ejemplar

`634260d6324e6921443451395efe7eea817fc2778ed59d4758eef81b46e41ad8`

- `reports/figures/explicabilidad_7_errores.png`
- `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_errores.png`

### Grupo 35: 2 archivos, 67714 bytes por ejemplar

`8be1d7ffe6eaa381eeea21e6ddfb5dd4c54be4f48c4ec49356f50cd49fdd42c2`

- `entrega_final/figuras/05_matriz_calibracion.png`
- `reports/figures/evaluacion_9_matriz_calibracion.png`

### Grupo 36: 2 archivos, 64465 bytes por ejemplar

`e7d21d4a0233825ca8a88df1582a224059e32adc9fb9d227b49c94044b71d2a7`

- `reports/figures/05_market_segment.png`
- `reports/historico/protocolo_v2/reports/figures/05_market_segment.png`

### Grupo 37: 2 archivos, 62870 bytes por ejemplar

`e73746da2350618b27f22a30b9a2c440041a9b3f7f07f980068fc3dc0a645a03`

- `reports/figures/baseline_03_roc_validacion.png`
- `reports/historico/protocolo_v2/reports/figures/baseline_03_roc_validacion.png`

### Grupo 38: 2 archivos, 60514 bytes por ejemplar

`b9e5d2193d4548cfc26acf491225d0e021cf6a21412c77be39044ec9e8b00f26`

- `reports/figures/auditoria_4_1_02_distribucion_probabilidades.png`
- `reports/historico/protocolo_v2/reports/figures/auditoria_4_1_02_distribucion_probabilidades.png`

### Grupo 39: 2 archivos, 57701 bytes por ejemplar

`9f5431f78b42797dbbbdd6fb982204a0144770f3b70acf65caa58ca5bbb5e306`

- `tmp/fase10/diapositiva-15.png`
- `tmp/fase10/final-15.png`

### Grupo 40: 2 archivos, 57015 bytes por ejemplar

`c2812a3ee72499f0ef278fea1255bff1a0fb28420f46e1d73152b383acc97255`

- `tmp/fase10/diapositiva-12.png`
- `tmp/fase10/final-12.png`

### Grupo 41: 2 archivos, 55767 bytes por ejemplar

`33892c7fd3a81f3d488bf95e7b6d4b3667b5a8da5dd3bb093f404be5838310e8`

- `tmp/fase10/diapositiva-07.png`
- `tmp/fase10/final-07.png`

### Grupo 42: 2 archivos, 54726 bytes por ejemplar

`ff959839d025cd7002994f409aa99f41a239fd30f7faa3007eb6cab9099f4b96`

- `reports/figures/baseline_01_particiones.png`
- `reports/historico/protocolo_v2/reports/figures/baseline_01_particiones.png`

### Grupo 43: 2 archivos, 54157 bytes por ejemplar

`2983f7af1fad9dc64bc164996fb45902134d95836ce822e35e94886dd4d20214`

- `reports/figures/baseline_02_confusion_validacion.png`
- `reports/historico/protocolo_v2/reports/figures/baseline_02_confusion_validacion.png`

### Grupo 44: 2 archivos, 53139 bytes por ejemplar

`e064617e4b962774e8d1421dca746d4d61c334e4251b4621414fc92944e18d43`

- `tmp/fase10/diapositiva-04.png`
- `tmp/fase10/final-04.png`

### Grupo 45: 2 archivos, 52940 bytes por ejemplar

`d8ddfd11bd92c693d4ddd1d77131597a30be532b6ea334583fcbbbdadc58f2f3`

- `tmp/fase10/diapositiva-05.png`
- `tmp/fase10/final-05.png`

### Grupo 46: 2 archivos, 52882 bytes por ejemplar

`bd95abafdf91ff4c5af960af2afa68ea3426107561026554512700e03004ae86`

- `tmp/fase10/diapositiva-10.png`
- `tmp/fase10/final-10.png`

### Grupo 47: 2 archivos, 52586 bytes por ejemplar

`d8d31647243caae409a239fab56b82519690e4ba695e01759fc3bcdf34aea60d`

- `reports/figures/04_tasas_antelacion.png`
- `reports/historico/protocolo_v2/reports/figures/04_tasas_antelacion.png`

### Grupo 48: 2 archivos, 50836 bytes por ejemplar

`b8a9bf8479e62589b9829a49fc0e32df4c7157d2eaf1b74692c2c84cad8d11ee`

- `tmp/fase10/diapositiva-11.png`
- `tmp/fase10/final-11.png`

### Grupo 49: 2 archivos, 50793 bytes por ejemplar

`a2bc12484adce21eaa91e5a6a1b3fa005b7853df44b1e4f91b4d702301b4b5ab`

- `reports/figures/protocolo_4_2_confusion_validacion.png`
- `reports/historico/protocolo_v2/reports/figures/protocolo_4_2_confusion_validacion.png`

### Grupo 50: 2 archivos, 50619 bytes por ejemplar

`7944a583b51df877425cbed85c1b79386781aad8332ec2943ce9cdf9efb79b49`

- `reports/figures/01_ausencias.png`
- `reports/historico/protocolo_v2/reports/figures/01_ausencias.png`

### Grupo 51: 2 archivos, 50115 bytes por ejemplar

`d6a465b1d7442d4098e6cad243e5aec28866926fab144ebd6127185b5eeeb1af`

- `tmp/fase10/diapositiva-13.png`
- `tmp/fase10/final-13.png`

### Grupo 52: 2 archivos, 49663 bytes por ejemplar

`5aa722f8f3d0a45dba27829111af5351dac369f756d8c81cadd8ce81644bbf86`

- `reports/figures/comparacion_5_metricas.png`
- `reports/historico/protocolo_v2/reports/figures/comparacion_5_metricas.png`

### Grupo 53: 2 archivos, 49629 bytes por ejemplar

`f744804082242db8c2497466e224e4580f4871b7e1f9c47408e8c21bdec5e9cd`

- `tmp/fase10/diapositiva-08.png`
- `tmp/fase10/final-08.png`

### Grupo 54: 2 archivos, 48778 bytes por ejemplar

`88e5aded3b970d1a3155d8b424f39af12c9f9fa993dcc7606ddbe8dfe20c080e`

- `reports/figures/02_objetivo_hoteles.png`
- `reports/historico/protocolo_v2/reports/figures/02_objetivo_hoteles.png`

### Grupo 55: 2 archivos, 48660 bytes por ejemplar

`d8c169fabe2eb94356eafb98d145495b43cdc27b721a96a51648244d958b9270`

- `reports/figures/06_historial_solicitudes.png`
- `reports/historico/protocolo_v2/reports/figures/06_historial_solicitudes.png`

### Grupo 56: 2 archivos, 47870 bytes por ejemplar

`9fd64799ac04ad804f6276765ce40ac154a753638f7cb3319894d08c752dd7a3`

- `tmp/fase10/diapositiva-06.png`
- `tmp/fase10/final-06.png`

### Grupo 57: 2 archivos, 47720 bytes por ejemplar

`530b4d08197b0c12af3f5ed8e1ba53953ea18379cad706eaa227fbdd79b7e01d`

- `reports/figures/05_distribution_channel.png`
- `reports/historico/protocolo_v2/reports/figures/05_distribution_channel.png`

### Grupo 58: 2 archivos, 47563 bytes por ejemplar

`6e93ae31d0ef7d4f2da731087f08f2835804885b936bda815161abd53ff1b0c7`

- `reports/historico/documentacion_pre_integracion/src/optimization.py`
- `reports/historico/protocolo_v2/src/optimization.py`

### Grupo 59: 2 archivos, 46695 bytes por ejemplar

`fe246aa63e268f178f9635e4f4dada3518022ce707eee86a1922b2d48ea3c705`

- `tmp/fase10/diapositiva-01.png`
- `tmp/fase10/final-01.png`

### Grupo 60: 2 archivos, 46339 bytes por ejemplar

`05ade1426f5362e0a512dc0638396e9818ae22fa6f304580f966c4462af6de79`

- `tmp/fase10/diapositiva-14.png`
- `tmp/fase10/final-14.png`

### Grupo 61: 2 archivos, 44814 bytes por ejemplar

`95f66ebbb0559255e5305d5217f5d832290b6fc7ccabe0b44624e516cbd8a391`

- `reports/figures/05_customer_type.png`
- `reports/historico/protocolo_v2/reports/figures/05_customer_type.png`

### Grupo 62: 2 archivos, 42690 bytes por ejemplar

`ebfc98634ff16939c821d2269a82e1723d1271bc128684196ac20428c564ea25`

- `reports/historico/documentacion_pre_integracion/src/audit_baseline.py`
- `reports/historico/protocolo_v2/src/audit_baseline.py`

### Grupo 63: 2 archivos, 42293 bytes por ejemplar

`b41be3e76e0807190d67d8228884e7ba09c7794f57f6a5e94176724f501be3b7`

- `reports/historico/documentacion_pre_integracion/src/explainability.py`
- `reports/historico/protocolo_v2/src/explainability.py`

### Grupo 64: 2 archivos, 42167 bytes por ejemplar

`8a290ceb7e7d4c739600e386571ca6e1370f54a32d6108dc4d886d4fa871c588`

- `reports/figures/05_deposit_type.png`
- `reports/historico/protocolo_v2/reports/figures/05_deposit_type.png`

### Grupo 65: 2 archivos, 41542 bytes por ejemplar

`6b676813d737aafddbaf70af12b002043bf9b0282e77ae3b470c0ed52c7e2d01`

- `tmp/fase10/diapositiva-03.png`
- `tmp/fase10/final-03.png`

### Grupo 66: 2 archivos, 40048 bytes por ejemplar

`60e0ef353c5755e80ddf68e614e6edb3ff52c22d7141606ce72e9128836cdba9`

- `reports/auditoria_4_1_resultados.json`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_resultados.json`

### Grupo 67: 2 archivos, 39848 bytes por ejemplar

`de1450e08043d9cb1f95020548fff1b8caa26e9d22a44e3a46242792ff224c39`

- `reports/figures/07_estancia_huespedes.png`
- `reports/historico/protocolo_v2/reports/figures/07_estancia_huespedes.png`

### Grupo 68: 2 archivos, 39169 bytes por ejemplar

`795d28abe9273a657a4691ab0764ddfb4c801df7acbd0618d48bbbb1d62b3126`

- `tmp/fase10/diapositiva-09.png`
- `tmp/fase10/final-09.png`

### Grupo 69: 2 archivos, 38477 bytes por ejemplar

`5abad4074fe059dc5f49364ccbd5b2d00b4d6a0c271592b0b5d28d95474ee0cc`

- `tmp/fase10/diapositiva-02.png`
- `tmp/fase10/final-02.png`

### Grupo 70: 2 archivos, 37044 bytes por ejemplar

`729dce34efb471ea8d1b0fa08a689f94ce4e026a08a898253087d18e6cbd2201`

- `reports/baseline_verificacion.json`
- `reports/protocolo_7_1_verificacion.json`

### Grupo 71: 2 archivos, 35231 bytes por ejemplar

`87b28722e8926466734f958a42fac46a71d797244f74c762437e6ba5f116f080`

- `reports/evaluacion_9_fuente_ejecucion.py`
- `reports/historico/documentacion_pre_integracion/src/final_evaluation.py`

### Grupo 72: 2 archivos, 31685 bytes por ejemplar

`d94df3e0995079b5895f1d2a3f9464128ff9e1f8d30216d5d7b1ad8e4a30ad44`

- `reports/figures/protocolo_4_2_reincorporacion.png`
- `reports/historico/protocolo_v2/reports/figures/protocolo_4_2_reincorporacion.png`

### Grupo 73: 2 archivos, 30903 bytes por ejemplar

`f77d101a1ad5e05ae1fa065c096338413ca6bddbcfa902cc147247cd1fd3f1c1`

- `reports/fase_7_explicabilidad.md`
- `reports/historico/protocolo_v2/reports/fase_7_explicabilidad.md`

### Grupo 74: 2 archivos, 25745 bytes por ejemplar

`1cbbaea9a8e12421178d5da4927605e87f5c410cde6689364aeef3d63c94d100`

- `reports/historico/protocolo_v2/reports/optimizacion_6_verificacion.json`
- `reports/optimizacion_6_verificacion.json`

### Grupo 75: 2 archivos, 25364 bytes por ejemplar

`67a852b46d8b7f95b8ff06146c959273006685ab0398319951b2f83021e0adad`

- `reports/fase_6_optimizacion.md`
- `reports/historico/protocolo_v2/reports/fase_6_optimizacion.md`

### Grupo 76: 2 archivos, 24109 bytes por ejemplar

`176d63df132d7279c208ee011cfe3fbc9e8d89a1aa6cd29e48b8e236dcfc04b3`

- `reports/eda_resumen.json`
- `reports/historico/protocolo_v2/reports/eda_resumen.json`

### Grupo 77: 2 archivos, 23510 bytes por ejemplar

`508694e2edc55d9cdf83e7fdae191a945c0ef59f5cae83dec0f03ed685783f42`

- `reports/historico/documentacion_pre_integracion/src/baseline.py`
- `reports/historico/protocolo_v2/src/baseline.py`

### Grupo 78: 2 archivos, 21366 bytes por ejemplar

`744be32ace838f73ded77a68500d4bcbcfa9fb4560e33a2f706811a8f907fa0a`

- `reports/explicabilidad_7_muestra_ids.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_muestra_ids.csv`

### Grupo 79: 2 archivos, 20746 bytes por ejemplar

`5feaf824ea787b3622117a7aa5817e690bb9f6b452b730165ca348f5fbb068b1`

- `reports/fase_4_1_auditoria.md`
- `reports/historico/protocolo_v2/reports/fase_4_1_auditoria.md`

### Grupo 80: 2 archivos, 20127 bytes por ejemplar

`7fd47c800397941b127c6ca4411a96dcf4d705ebdab48810bbd639e9fc13344e`

- `reports/historico/protocolo_v2/reports/optimizacion_6_escenarios.csv`
- `reports/optimizacion_6_escenarios.csv`

### Grupo 81: 2 archivos, 19079 bytes por ejemplar

`0c0ed2c81fa4d49f314121dcea04094efc52acdac7df21791e9400c799f5aff1`

- `reports/historico/protocolo_v2/reports/verificacion_referencias.json`
- `reports/verificacion_referencias.json`

### Grupo 82: 2 archivos, 18850 bytes por ejemplar

`b67698ad4b3e2a8eda7732be2c943079142edad41806c451a9813e12b48bf80d`

- `reports/explicabilidad_7_verificacion.json`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_verificacion.json`

### Grupo 83: 2 archivos, 16852 bytes por ejemplar

`8ee57b577f10d4c2e9b4e26d4a651035c8f351eb0ce8e9e0759d79a7c216d804`

- `reports/fase_3_preparacion.md`
- `reports/historico/protocolo_v2/reports/fase_3_preparacion.md`

### Grupo 84: 2 archivos, 15821 bytes por ejemplar

`3541d2858dfcfa76ef3ba562463c2046ea29855bee902786c7a5d36ab8e6cc4d`

- `reports/fase_4_2_protocolo_temporal.md`
- `reports/historico/protocolo_v2/reports/fase_4_2_protocolo_temporal.md`

### Grupo 85: 2 archivos, 13654 bytes por ejemplar

`65e4b58fc0d9efb9cf9011b07da6b8f53bb397b42f28764ecfa4077f33370ecd`

- `reports/comparacion_5_verificacion.json`
- `reports/historico/protocolo_v2/reports/comparacion_5_verificacion.json`

### Grupo 86: 2 archivos, 12385 bytes por ejemplar

`5c4d4aa720b2b904bd5e275166cf6cfa4bfc29ba74fe718e475b36143f605cff`

- `reports/explicabilidad_7_gain_transformadas.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_gain_transformadas.csv`

### Grupo 87: 2 archivos, 12224 bytes por ejemplar

`ac790bd6c98bf6b24b7998899a430eb3a8b3f5fb20e63c7780cb446608531342`

- `reports/fase_4_baseline.md`
- `reports/historico/protocolo_v2/reports/fase_4_baseline.md`

### Grupo 88: 2 archivos, 10826 bytes por ejemplar

`337e7819b41c133e973fbc334cd807a6a3b055783b574047c8fd01a0f1e7298e`

- `reports/explicabilidad_7_segmentos.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_segmentos.csv`

### Grupo 89: 2 archivos, 10506 bytes por ejemplar

`545c644e1e15dc5323a9f999405059b68f21628fcde755eadbab4bdc70459cb6`

- `reports/fase_5_comparacion_modelos.md`
- `reports/historico/protocolo_v2/reports/fase_5_comparacion_modelos.md`

### Grupo 90: 2 archivos, 10171 bytes por ejemplar

`b2b0d5ea1a7bcbc072c69e8b9ad8537b9e99c6be45a7bfcc98c181fa37b21207`

- `reports/fase_2_eda.md`
- `reports/historico/protocolo_v2/reports/fase_2_eda.md`

### Grupo 91: 2 archivos, 9707 bytes por ejemplar

`0867a3d1c4e26c52eee457092bf6cf15795440ffb312f44ab87e929f5fd16026`

- `reports/explicabilidad_7_shap_transformadas.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_shap_transformadas.csv`

### Grupo 92: 2 archivos, 9197 bytes por ejemplar

`0200d393637fee2924cf79351318b2019aff2077f44f337f24ac12e641a04fad`

- `reports/historico/protocolo_v2/reports/optimizacion_6_busqueda.csv`
- `reports/optimizacion_6_busqueda.csv`

### Grupo 93: 2 archivos, 8955 bytes por ejemplar

`bfd6f6d58eb61411d46417fd6d916db9e4b5e9a36b22edf02e31501805ac8df7`

- `reports/fase_1_inspeccion.md`
- `reports/historico/protocolo_v2/reports/fase_1_inspeccion.md`

### Grupo 94: 2 archivos, 8222 bytes por ejemplar

`55d9a76211e6326f790db6e6b4e7221a54182adc26d337f709f50123656f3739`

- `reports/explicabilidad_7_mapa_caracteristicas.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_mapa_caracteristicas.csv`

### Grupo 95: 2 archivos, 7554 bytes por ejemplar

`58261bbe71e9e8cf8578d1942b6c3ee9d139c8fb658b56e38cc93a555b6033d5`

- `reports/historico/protocolo_v2/reports/optimizacion_6_seleccion_prevalidacion.json`
- `reports/optimizacion_6_seleccion_prevalidacion.json`

### Grupo 96: 2 archivos, 6782 bytes por ejemplar

`c150d2ef7a93d2aba990a926cda1eca746e48011764e4dab8ad60ed3cc620213`

- `reports/historico/documentacion_pre_integracion/src/features.py`
- `reports/historico/protocolo_v2/src/features.py`

### Grupo 97: 2 archivos, 6518 bytes por ejemplar

`a8092aaa00c4020630117d1cf2286e8dd9c66cfcbab1cd43c6007e8935a932bc`

- `reports/historico/documentacion_pre_integracion/tests/test_preparation.py`
- `reports/historico/protocolo_v2/tests/test_preparation.py`

### Grupo 98: 3 archivos, 3258 bytes por ejemplar

`54fca79590344418cd93fdee4b41122b81c0b134f7428f9a289e0987e44bbef6`

- `reports/historico/protocolo_v2/reports/baseline_verificacion.json`
- `reports/historico/protocolo_v2/reports/protocolo_4_2_verificacion.json`
- `reports/protocolo_4_2_verificacion.json`

### Grupo 99: 2 archivos, 6309 bytes por ejemplar

`51fe289fd0af759a25c7c9e8b47e6e9c4d05074bb15098e9364a469314234229`

- `reports/explicabilidad_7_dependencia_perfil.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_dependencia_perfil.csv`

### Grupo 100: 2 archivos, 5484 bytes por ejemplar

`d09536788c45d43a6af6d4daba8ab6b11f6f4ee516ceb3a5ff44ebd35a4bafde`

- `reports/historico/protocolo_v2/reports/optimizacion_6_umbrales.csv`
- `reports/optimizacion_6_umbrales.csv`

### Grupo 101: 2 archivos, 5249 bytes por ejemplar

`aa62e4e62bce731972df2deb7105f283b0d0c3dbd7cbd7019246803e2cb976c6`

- `reports/historico/protocolo_v2/reports/preparacion_auditoria_variables.csv`
- `reports/preparacion_auditoria_variables.csv`

### Grupo 102: 2 archivos, 4718 bytes por ejemplar

`d84c875f314049f77cf4ec4e74b4f5aa98bd16741dee6ab325940487dc340e0d`

- `reports/historico/documentacion_pre_integracion/tests/test_optimization.py`
- `reports/historico/protocolo_v2/tests/test_optimization.py`

### Grupo 103: 2 archivos, 4560 bytes por ejemplar

`5c7aada317829f4991daf7e5161aeab9d2f2b777c537524363503b6f52edf178`

- `reports/auditoria_4_1_perfiles_categoricos.csv`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_perfiles_categoricos.csv`

### Grupo 104: 2 archivos, 4345 bytes por ejemplar

`403f6f45167d319a2841b1843546dda2cfa2f47bc1e662e1ebcd1b4f04210eaa`

- `reports/historico/documentacion_pre_integracion/src/preparation.py`
- `reports/historico/protocolo_v2/src/preparation.py`

### Grupo 105: 2 archivos, 3544 bytes por ejemplar

`20aec08d33019233733f218f0ebb977d227563a8af80629e62e33cbf0433358b`

- `reports/historico/protocolo_v2/reports/optimizacion_6_calibracion_bins.csv`
- `reports/optimizacion_6_calibracion_bins.csv`

### Grupo 106: 2 archivos, 3146 bytes por ejemplar

`c5f80894ad45dcd740528c155cae2009abd6d725db6645446b988af7188b8b77`

- `reports/historico/documentacion_pre_integracion/tests/test_temporal_protocol.py`
- `reports/historico/protocolo_v2/tests/test_temporal_protocol.py`

### Grupo 107: 2 archivos, 2853 bytes por ejemplar

`8164d312108f6d80fe812f350d41cebe630b63a14234438df9c370f4a788a842`

- `reports/historico/documentacion_pre_integracion/tests/test_explainability.py`
- `reports/historico/protocolo_v2/tests/test_explainability.py`

### Grupo 108: 2 archivos, 2650 bytes por ejemplar

`baed84efac99954c7551030aaae2ff2c3cd02c65257f45013b950678cdfc95ef`

- `reports/historico/protocolo_v2/reports/optimizacion_6_estabilidad_mensual.csv`
- `reports/optimizacion_6_estabilidad_mensual.csv`

### Grupo 109: 2 archivos, 2626 bytes por ejemplar

`4cbd6937ea9ff49e343fadfefbe3c5f1bc83fa97f52299897586dc007f9a1ac3`

- `reports/historico/protocolo_v2/reports/optimizacion_6_plan.json`
- `reports/optimizacion_6_plan.json`

### Grupo 110: 2 archivos, 2529 bytes por ejemplar

`b7d52d20481792e7fdfc33156fc9f944f886b40a297882cceffa6bd48e894b95`

- `reports/historico/documentacion_pre_integracion/tests/test_baseline.py`
- `reports/historico/protocolo_v2/tests/test_baseline.py`

### Grupo 111: 2 archivos, 2480 bytes por ejemplar

`eacd7823b2b4cc4aa35ef468677dd2d9cad915f33f2e91799ba89cd4c7912cdd`

- `reports/explicabilidad_7_contribuciones_locales.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_contribuciones_locales.csv`

### Grupo 112: 2 archivos, 2363 bytes por ejemplar

`d18aa575805e54598fa5bb052836c61dc45977ef1425d23e899cdd407583dd29`

- `reports/historico/protocolo_v2/reports/preparacion_resumen.json`
- `reports/preparacion_resumen.json`

### Grupo 113: 2 archivos, 2274 bytes por ejemplar

`52793ede516563751221b92be18ae81850f0fc4802d9b6f4dff27ac15bd49b89`

- `reports/historico/documentacion_pre_integracion/src/cleaning.py`
- `reports/historico/protocolo_v2/src/cleaning.py`

### Grupo 114: 2 archivos, 2143 bytes por ejemplar

`8946c9a5ad6ca07e29163981ce05ecc413a8d1d98e6befc3077413c7807ab606`

- `reports/explicabilidad_7_calibracion_bins.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_calibracion_bins.csv`

### Grupo 115: 2 archivos, 2002 bytes por ejemplar

`a779c9df5e7e836628b593dbe02d52cf7045909cd7581b877f48a27b0eccae0a`

- `reports/historico/documentacion_pre_integracion/tests/test_comparison.py`
- `reports/historico/protocolo_v2/tests/test_comparison.py`

### Grupo 116: 2 archivos, 1923 bytes por ejemplar

`6d891386278cd6b0b2330eefba635ea7bc9d8df1c83daf811bc723c4a2b9c9ba`

- `reports/eda_auditoria_leakage.csv`
- `reports/historico/protocolo_v2/reports/eda_auditoria_leakage.csv`

### Grupo 117: 2 archivos, 1923 bytes por ejemplar

`f89c6b23e95af0912365bd2f2e2d0b29729cc75ead1bddeb5f9f0a8b08aba536`

- `reports/historico/protocolo_v2/reports/inspeccion_dataset.json`
- `reports/inspeccion_dataset.json`

### Grupo 118: 2 archivos, 1881 bytes por ejemplar

`f53cea7a11c44873559f78b36d5d9aaec4f2d3066df32141562af8f85ce67263`

- `reports/historico/documentacion_pre_integracion/tests/test_audit_baseline.py`
- `reports/historico/protocolo_v2/tests/test_audit_baseline.py`

### Grupo 119: 2 archivos, 1879 bytes por ejemplar

`900ecae24e5879cd32d745dd38a3ee01836d87d3506d0b1935e53aa2f78caa74`

- `reports/explicabilidad_7_reproduccion.json`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_reproduccion.json`

### Grupo 120: 2 archivos, 1711 bytes por ejemplar

`5d25bc5ee3ae843940908f973c6f17bfd15d485774742b220db9ffeae588b3c8`

- `reports/auditoria_4_1_umbrales_validacion.csv`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_umbrales_validacion.csv`

### Grupo 121: 2 archivos, 1379 bytes por ejemplar

`5b41fd7480ddc21989fb65b6c2c8190fc14f9f8ea100357d98ce85c3d7aebedc`

- `reports/historico/documentacion_pre_integracion/src/inspection.py`
- `reports/historico/protocolo_v2/src/inspection.py`

### Grupo 122: 2 archivos, 1159 bytes por ejemplar

`c6c89c60777cea68ac92899dd66528c56c8a012cfcd417dd444ff895ce1639a3`

- `reports/historico/protocolo_v2/reports/preparacion_verificacion.json`
- `reports/preparacion_verificacion.json`

### Grupo 123: 2 archivos, 1147 bytes por ejemplar

`f81df0106cf7fdb4c5d169c399c8aca31cee67a234f2d451fb4d1927cc06998b`

- `reports/historico/protocolo_v2/reports/optimizacion_6_metricas.csv`
- `reports/optimizacion_6_metricas.csv`

### Grupo 124: 2 archivos, 1082 bytes por ejemplar

`2877c53e7cefd7d673b4b46500df54ad888c1242af0a783ddd692f45532bae67`

- `reports/historico/documentacion_pre_integracion/src/preprocessing.py`
- `reports/historico/protocolo_v2/src/preprocessing.py`

### Grupo 125: 2 archivos, 1071 bytes por ejemplar

`6e01d970fa641dfdf8fdf867790f22c7dd611eeb3ee130d2c62c2179c794ffbd`

- `reports/historico/protocolo_v2/reports/protocolo_4_2_fuentes.md`
- `reports/protocolo_4_2_fuentes.md`

### Grupo 126: 2 archivos, 1068 bytes por ejemplar

`3ce28cf4858303992e24dbcb39b2c7e4e14bcf3abb8cf9b923593b70fd2289c3`

- `reports/eda_verificacion.json`
- `reports/historico/protocolo_v2/reports/eda_verificacion.json`

### Grupo 127: 2 archivos, 1033 bytes por ejemplar

`7bdb41b2bcb925e089062a5d53d30e196f23a0bf424cf02af74e8c8939cc3af6`

- `reports/comparacion_5_metricas.csv`
- `reports/historico/protocolo_v2/reports/comparacion_5_metricas.csv`

### Grupo 128: 2 archivos, 1029 bytes por ejemplar

`6277f8d2a66785752ffd0dd06b933e20cde412b9aca5f25d431119b2bc0cf9d6`

- `reports/historico/protocolo_v2/reports/protocolo_4_2_apartadas_por_mes.csv`
- `reports/protocolo_4_2_apartadas_por_mes.csv`

### Grupo 129: 2 archivos, 980 bytes por ejemplar

`01b647f5a119f4c2bec692fb85320f5d6105b90c8c36e3beeab1ffc923456f27`

- `reports/auditoria_4_1_verificacion.json`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_verificacion.json`

### Grupo 130: 2 archivos, 935 bytes por ejemplar

`3c0ee5735f0cd453ae95fd75dead66f65cf100b822bd653c5d7be2fed8e1a135`

- `reports/historico/protocolo_v2/reports/optimizacion_6_folds.csv`
- `reports/optimizacion_6_folds.csv`

### Grupo 131: 2 archivos, 898 bytes por ejemplar

`2e07654ac75b06af6bb12e577ee7e6bf5220084b883dc5385374f03aa223d8da`

- `reports/auditoria_4_1_calibracion_validacion.csv`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_calibracion_validacion.csv`

### Grupo 132: 2 archivos, 836 bytes por ejemplar

`3e7f15fb11d59494016bb8a7b097b91b18858c7e1ef0648057e4ae7dd0c20edd`

- `reports/historico/protocolo_v2/reports/protocolo_4_2_particiones.csv`
- `reports/protocolo_4_2_particiones.csv`

### Grupo 133: 2 archivos, 806 bytes por ejemplar

`61366d7cd73dc3fb73805adee2380a7c294e7dfc40f7f0c01e68fa44b774c254`

- `reports/historico/protocolo_v2/reports/protocolo_4_2_config.json`
- `reports/protocolo_4_2_config.json`

### Grupo 134: 2 archivos, 770 bytes por ejemplar

`f36fca9397b39715072a63c74fe7ae31469863580e43f7290ae0dd68fedef8f6`

- `reports/explicabilidad_7_muestra_perfil.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_muestra_perfil.csv`

### Grupo 135: 2 archivos, 728 bytes por ejemplar

`a931f7fd23da33f085f27f47ce7029b11372eb706a2dfc527b5580d61477dd75`

- `reports/explicabilidad_7_gain_originales.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_gain_originales.csv`

### Grupo 136: 2 archivos, 718 bytes por ejemplar

`70859d6a3b7e583d0dabaecbfb465b221d3672419fb8584b0eaa24dadea6f773`

- `reports/explicabilidad_7_shap_global.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_shap_global.csv`

### Grupo 137: 2 archivos, 700 bytes por ejemplar

`3427414e2e9c2e264a822de5c8220957a9e7e3d8dfeeff722547e7c4027a7164`

- `reports/auditoria_4_1_escenarios_coste_relativo.csv`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_escenarios_coste_relativo.csv`

### Grupo 138: 2 archivos, 671 bytes por ejemplar

`2638d3cfbcbbbcb814b61040bc3316b57d1fd5f58ba49e9244212a11185f5b1c`

- `reports/explicabilidad_7_casos.csv`
- `reports/historico/protocolo_v2/reports/explicabilidad_7_casos.csv`

### Grupo 139: 2 archivos, 659 bytes por ejemplar

`510ab20626192e8a12fe8ff37a479c3d62661514ba9ae79f1b60328cc31f04f1`

- `reports/historico/protocolo_v2/reports/optimizacion_6_calibracion.csv`
- `reports/optimizacion_6_calibracion.csv`

### Grupo 140: 2 archivos, 609 bytes por ejemplar

`8a8c71d93e81a75629f601f3e3d26e32c1cd76bd69d0795d9ccd4917a845079a`

- `reports/auditoria_4_1_perfiles_seleccion.csv`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_perfiles_seleccion.csv`

### Grupo 141: 2 archivos, 484 bytes por ejemplar

`dcb890a0f942d8f20f302e4f66f42b1b3847cc8bcafd3942f1bf83b64a9d8d7d`

- `reports/historico/protocolo_v2/reports/protocolo_4_2_comparacion_descriptiva.csv`
- `reports/protocolo_4_2_comparacion_descriptiva.csv`

### Grupo 142: 2 archivos, 449 bytes por ejemplar

`8e6ce7e02d191c1c4288cfb944e843bdc7e3ca909cfc14c2e9be7d391b3d23dd`

- `reports/auditoria_4_1_diagnosticos_train_validacion.csv`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_diagnosticos_train_validacion.csv`

### Grupo 143: 2 archivos, 409 bytes por ejemplar

`b0723c58632f9c6fbe3a6e543fb61d16c395e6114c651386e012ce56eade6759`

- `reports/auditoria_4_1_distribucion_probabilidades.csv`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_distribucion_probabilidades.csv`

### Grupo 144: 2 archivos, 369 bytes por ejemplar

`38ee456e055f58ed447d130f5d9f322e2a351b562204bf743b3ed3fc1034e6a2`

- `reports/auditoria_4_1_cierres_hipoteticos.csv`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_cierres_hipoteticos.csv`

### Grupo 145: 2 archivos, 292 bytes por ejemplar

`c1ce40e5710b31c88d089d5f91ed0f17f05a02b5a19f728858b23fc1f4abc0f1`

- `reports/historico/protocolo_v2/reports/protocolo_4_2_transicion.csv`
- `reports/protocolo_4_2_transicion.csv`

### Grupo 146: 2 archivos, 284 bytes por ejemplar

`e6bb48022891fd0e2084341f000d3e2b2db605e3b2470619a30aa78e44158040`

- `reports/historico/protocolo_v2/requirements.txt`
- `requirements.txt`

### Grupo 147: 2 archivos, 281 bytes por ejemplar

`42187438f5937e1925ccd98533f8362567c2cb7c152ea73dd2533d937bb616b7`

- `reports/auditoria_4_1_categorias_nuevas_validacion.csv`
- `reports/historico/protocolo_v2/reports/auditoria_4_1_categorias_nuevas_validacion.csv`

### Grupo 148: 2 archivos, 130 bytes por ejemplar

`e14dc98b35863402df7c484f0845f48cf1865cc9fc223e60d8c031931048a416`

- `reports/historico/protocolo_v2/reports/protocolo_4_2_reincorporadas_perfil.csv`
- `reports/protocolo_4_2_reincorporadas_perfil.csv`

### Grupo 149: 2 archivos, 69 bytes por ejemplar

`85312e2cd5f7538b0bbe0521faf14f9a28eee7195b50f3c5986d6d5d76008515`

- `reports/historico/documentacion_pre_integracion/src/__init__.py`
- `reports/historico/protocolo_v2/src/__init__.py`

## Anexo: los 537 archivos y su correspondencia de papelera

Rutas relativas a la raíz restaurada. Cada pareja se identifica por el mismo sufijo: el contenido `$R…` y el metadato `$I…` están preservados en `papelera_original` del respaldo. El SHA-256 es del contenido. El manifiesto independiente conserva también el SHA del metadato y las fechas exactas.

| Ruta original relativa | Categoría | Bytes | Contenido / metadato | SHA-256 |
|---|---|---:|---|---|
| `.chart-data-2rYvdW/candidate.pptx` | Archivos generados temporales | 74980 | `$RPS0RW7.pptx` / `$IPS0RW7.pptx` | `7eb999b0143dd228c400f16c1aa2c03b7b531a8a7e4f346184187e2b2372a5dd` |
| `.chart-data-2rYvdW/chart-data-snapshot.json` | Archivos generados temporales | 1532 | `$R8210UK.json` / `$I8210UK.json` | `ba9eeadc7ab22e07fa1d11280e9fb5723a8296e7349c3c2de88e793bf2da1330` |
| `.chart-data-fCYrKC/candidate.pptx` | Archivos generados temporales | 74916 | `$RPTDD2O.pptx` / `$IPTDD2O.pptx` | `c922b85439d49a78e8877ad9fe76904703e8128eb4af008abac9188b3b82322b` |
| `.chart-data-fCYrKC/chart-data-snapshot.json` | Archivos generados temporales | 1532 | `$RZ4Q2KE.json` / `$IZ4Q2KE.json` | `129c559bca07eeecfd9e641a85f448e983a368dfa26301b128018c638b82b96f` |
| `.chart-data-hyCAn5/candidate.pptx` | Archivos generados temporales | 73927 | `$R4ROIEE.pptx` / `$I4ROIEE.pptx` | `02bedb3bda870391996edf8baea5cab09eb224cb2c75bf2d428108042f44f40c` |
| `.chart-data-hyCAn5/chart-data-snapshot.json` | Archivos generados temporales | 1532 | `$RFTOUGN.json` / `$IFTOUGN.json` | `a20039c4efd5d875b59f653bafc1bf95b63e5c82c60c4611af438462814ea447` |
| `.gitignore` | Documentación y configuración | 76 | `$RYVU58X.gitignore` / `$IYVU58X.gitignore` | `a773f1fc2d98f3daedf6f3f91461f03d8379743220f6d5ef2d055471ff7ef3cb` |
| `codigo_comentado/entrega_final/fuentes/auditar_entrega.py` | Código auxiliar de referencia | 9202 | `$RTKRJVA.py` / `$ITKRJVA.py` | `09befab740ab87fa2c43fedce7f576a837247338f91bf7e713c9ce822fecae4c` |
| `codigo_comentado/entrega_final/fuentes/crear_presentacion.mjs` | Código auxiliar de referencia | 17122 | `$R0MQASG.mjs` / `$I0MQASG.mjs` | `dbb244183e199dca88807a847fd76b5a74e3446b5a8d3c2de62a5a6721ebb0b0` |
| `codigo_comentado/entrega_final/fuentes/exportar_pdf.py` | Código auxiliar de referencia | 5413 | `$R1YRFAR.py` / `$I1YRFAR.py` | `da9db4d370892f7ea2fc3a7a1e9c4d51c257c86cdd9015b00848a8c825f96dde` |
| `codigo_comentado/entrega_final/fuentes/preparar_entrega.py` | Código auxiliar de referencia | 7724 | `$RBIJ42D.py` / `$IBIJ42D.py` | `2f1bc905016a9a111b4791e8ab53b87840715fe323db28ce184f97018a1d24ea` |
| `codigo_comentado/entrega_final/fuentes/renderizar_presentacion.mjs` | Código auxiliar de referencia | 1217 | `$R1NGWQG.mjs` / `$I1NGWQG.mjs` | `296e874ac782a6460e3bcadbd1e26cc6719e6dae3a64c81b9b7c4b8232ece803` |
| `codigo_comentado/notebooks/baseline.ipynb` | Código auxiliar de referencia | 212265 | `$R766H90.ipynb` / `$I766H90.ipynb` | `33d92e65581d900a29e3e01f07d6bb7a41877fb8f76fea00807cd9b5f984781a` |
| `codigo_comentado/notebooks/comparacion_modelos.ipynb` | Código auxiliar de referencia | 409145 | `$R6U7C7T.ipynb` / `$I6U7C7T.ipynb` | `b5deba43c7168b850380184268807fdd9fc9985debec13d0d4b8cb13aac10a6c` |
| `codigo_comentado/notebooks/correccion_sesgo_temporal.ipynb` | Código auxiliar de referencia | 202674 | `$RLGC6EH.ipynb` / `$ILGC6EH.ipynb` | `b74d4ca36b2a9848b32a73fb15afdb183ebe31c93ace72431be519c6ac4bef19` |
| `codigo_comentado/notebooks/eda.ipynb` | Código auxiliar de referencia | 1387684 | `$RT3NZBB.ipynb` / `$IT3NZBB.ipynb` | `659b44bec196def59f1687ea27eab25c14af9840c86890a00688646f3c08b525` |
| `codigo_comentado/notebooks/evaluacion_final.ipynb` | Código auxiliar de referencia | 244790 | `$RBVHPBQ.ipynb` / `$IBVHPBQ.ipynb` | `17e65bf8c018294f5281dcfa370ef5ed740696b2566c15c735e6a026941213ca` |
| `codigo_comentado/notebooks/explicabilidad.ipynb` | Código auxiliar de referencia | 1056093 | `$REXRGD0.ipynb` / `$IEXRGD0.ipynb` | `52a315eb74e4d392cb4a2598352808ce46cb96d3f28c13722623d72ae38a1924` |
| `codigo_comentado/notebooks/optimizacion.ipynb` | Código auxiliar de referencia | 671225 | `$RZWXEMH.ipynb` / `$IZWXEMH.ipynb` | `02cbea1363bb86f51fb1e13ec37a26f6506ba9889ddad57dc9329b6fe5156b0d` |
| `codigo_comentado/notebooks/preparacion.ipynb` | Código auxiliar de referencia | 104574 | `$RV49X18.ipynb` / `$IV49X18.ipynb` | `b4bf33a6c005518e7828333d13c6b0982e71507edbbb208ef804563522ef635c` |
| `codigo_comentado/notebooks/protocolo_temporal.ipynb` | Código auxiliar de referencia | 160978 | `$RCK9XA5.ipynb` / `$ICK9XA5.ipynb` | `76ecc35910d0dfe698e0f467f938d89e22a4cf8278952fee190248dc66de3d1b` |
| `codigo_comentado/notebooks/seleccion_final.ipynb` | Código auxiliar de referencia | 419206 | `$RNSWJAJ.ipynb` / `$INSWJAJ.ipynb` | `ecb326580dad99be54b41d9d8b93a7efb7c55a5cf0ba61de5e5137ae586d9ff5` |
| `codigo_comentado/README.md` | Código auxiliar de referencia | 5001 | `$RXZ553O.md` / `$IXZ553O.md` | `d363132127de9cd5cc6c60293a94905ede9d221a51559607e18ae5acbdd1a53c` |
| `codigo_comentado/src/__init__.py` | Código auxiliar de referencia | 310 | `$RBUK2H8.py` / `$IBUK2H8.py` | `7fdf138eb79af54fa2b91277ed0842d5a88364b0fcd5deb66ad02a86eb0d0ac5` |
| `codigo_comentado/src/audit_baseline.py` | Código auxiliar de referencia | 46597 | `$R4G4L97.py` / `$I4G4L97.py` | `b57b62318aecfb095f5653937c86a3c6174e28830a4ffabdde88d1d8446c9bb1` |
| `codigo_comentado/src/baseline.py` | Código auxiliar de referencia | 25058 | `$R3P0A1L.py` / `$I3P0A1L.py` | `1eeec38a98e2cbec9349b3baaabdebd1e75dd487ee999c28df1c58e09daa58dd` |
| `codigo_comentado/src/cleaning.py` | Código auxiliar de referencia | 2705 | `$RHVWZZ8.py` / `$IHVWZZ8.py` | `d26461624419b37f09537b3f22a7aec9901cc28411b67c8a0914c1b1375a6453` |
| `codigo_comentado/src/comparison.py` | Código auxiliar de referencia | 25079 | `$RV8PCW6.py` / `$IV8PCW6.py` | `95d84a309a9b801ca070f584b723add83bbde9bf2df9963a7970b66f0af01b21` |
| `codigo_comentado/src/decision_policy.py` | Código auxiliar de referencia | 4127 | `$R9L5Q2C.py` / `$I9L5Q2C.py` | `55518ce9d3787620972a0705c55b75af2eac6645d4db5047982f957f62011332` |
| `codigo_comentado/src/evaluation_narrative.py` | Código auxiliar de referencia | 4753 | `$RYMSGTY.py` / `$IYMSGTY.py` | `00966e5262b87c0c3bc4522ea8160885d98b800980fc119af6c4df6703f41fda` |
| `codigo_comentado/src/explainability.py` | Código auxiliar de referencia | 44475 | `$RD9YKCK.py` / `$ID9YKCK.py` | `5dcfae135dc30c59a6c485494beaed1cd9f02ac1f3f904e8551a3f088f878361` |
| `codigo_comentado/src/features.py` | Código auxiliar de referencia | 7430 | `$RXFNQZY.py` / `$IXFNQZY.py` | `be08d42b250aeda6dc7272c18539dd5122d5711f3a7cd57483282b62d3de4573` |
| `codigo_comentado/src/final_evaluation.py` | Código auxiliar de referencia | 39143 | `$RDIQ1X3.py` / `$IDIQ1X3.py` | `efd80696a6122d2ae1acbfa21f49f3e806ff8f1a125c15c1580272e6a9aac413` |
| `codigo_comentado/src/final_selection.py` | Código auxiliar de referencia | 35476 | `$RF9K0MR.py` / `$IF9K0MR.py` | `d8baf2ceeeb8ac2d9edaedec951da7b859e60b4381c3f0513f1e16603c6ec3e9` |
| `codigo_comentado/src/inspection.py` | Código auxiliar de referencia | 1885 | `$RJHOF2W.py` / `$IJHOF2W.py` | `7eae210385b9edfdb69e82b3cdc4d7a9e5b9ecd194e7484d292c81271a91f6d2` |
| `codigo_comentado/src/optimization.py` | Código auxiliar de referencia | 52003 | `$RW5BA16.py` / `$IW5BA16.py` | `2ffa1105740d65dab87d1856869c3a5984602be1f7e7cdce3882a1ac4e83d917` |
| `codigo_comentado/src/preparation.py` | Código auxiliar de referencia | 5647 | `$RGIILRZ.py` / `$IGIILRZ.py` | `dc0c97a32f95d49df844df55a78c88678f10e0f2d61e1efd5e85d9b1b96caaa4` |
| `codigo_comentado/src/preprocessing.py` | Código auxiliar de referencia | 1757 | `$RQN0A8N.py` / `$IQN0A8N.py` | `b4104a465431f218f3078b7f85227e6615926f30d5e26737babd0c7cee545a5f` |
| `codigo_comentado/src/run_notebook.py` | Código auxiliar de referencia | 3460 | `$R6RXCR3.py` / `$I6RXCR3.py` | `ce9964a273b6e271c737dcae45530a4063e4155a40b385e1971875b856639e2e` |
| `codigo_comentado/src/splitting.py` | Código auxiliar de referencia | 11536 | `$RMONXGG.py` / `$IMONXGG.py` | `8025c76c71051f18c70daa6fbf21e3d7ddcfac00c9d0f6d54182a2c05626c0dc` |
| `codigo_comentado/src/temporal_bias_v3.py` | Código auxiliar de referencia | 37863 | `$R6V9LTN.py` / `$I6V9LTN.py` | `2b54c0645c75d3e16dfe79a75ee58bf5cd0b11aada783b3a6e236e69c123847c` |
| `codigo_comentado/src/temporal_protocol.py` | Código auxiliar de referencia | 35157 | `$RPUQA7O.py` / `$IPUQA7O.py` | `f160158d5ab51f2028f6cb1807586d80ae6fe9dcd1d7069c0b4f5a7793a5c495` |
| `codigo_comentado/tests/test_audit_baseline.py` | Código auxiliar de referencia | 2587 | `$RKM3O7B.py` / `$IKM3O7B.py` | `7f77e3e724d850a9bfbd6073d58362f6abe449938f813f88f20677427d6d497f` |
| `codigo_comentado/tests/test_baseline.py` | Código auxiliar de referencia | 3327 | `$R55WG6M.py` / `$I55WG6M.py` | `2531b3a7d5de9f1bb2b919c47a63d6600c3a8a7babc928edd2cf87badfd304ef` |
| `codigo_comentado/tests/test_comparison.py` | Código auxiliar de referencia | 2465 | `$RL5170B.py` / `$IL5170B.py` | `7a612de936ec24cd032d143b27ef822eca57685c0c0011845da672f225a0ebb9` |
| `codigo_comentado/tests/test_decision_policy.py` | Código auxiliar de referencia | 3717 | `$RCL4795.py` / `$ICL4795.py` | `af5c1af7b6787082d9aa8b32b70807d844b766c985b2397c28532bcd4ee47cee` |
| `codigo_comentado/tests/test_explainability.py` | Código auxiliar de referencia | 4018 | `$RO3IKR0.py` / `$IO3IKR0.py` | `dce1297a0a55a5c0e15d30571c8efa9a3f43cc542e0e496dfbebfecb6bbf6299` |
| `codigo_comentado/tests/test_final_evaluation.py` | Código auxiliar de referencia | 6098 | `$RXVPN6V.py` / `$IXVPN6V.py` | `05baacd51d0af74489732ea0355248a945ac3a6ae3d01103e109eac9bb535f45` |
| `codigo_comentado/tests/test_optimization.py` | Código auxiliar de referencia | 5918 | `$RMD1MLW.py` / `$IMD1MLW.py` | `cbf7bf0e6add44ed068364dcba3b3de24831253eee95d151969ff30114e70c73` |
| `codigo_comentado/tests/test_preparation.py` | Código auxiliar de referencia | 7613 | `$RILAG7O.py` / `$IILAG7O.py` | `2d8e953f6e4ecadc495b0b02f543607e2f9708f9c045c84a554468197ff1e357` |
| `codigo_comentado/tests/test_temporal_bias_v3.py` | Código auxiliar de referencia | 5788 | `$R022LHU.py` / `$I022LHU.py` | `666ec7913c713ca8adb593e841df0549d305766f8107e4ee21f88ebe1497d29d` |
| `codigo_comentado/tests/test_temporal_protocol.py` | Código auxiliar de referencia | 4221 | `$RJCJMH1.py` / `$IJCJMH1.py` | `75df7cc35c96fb36f4ffda7883d21a329a3ee38b2648b0f6f8551e30268f0ead` |
| `codigo_comentado/verificacion_comentarios.json` | Código auxiliar de referencia | 17812 | `$RSLDN9F.json` / `$ISLDN9F.json` | `2f2097c21fe1568357b9f8ef7384efdb16670e47944edd1478372cf0ffa5beba` |
| `data/processed/hotel_bookings_prepared.csv` | Datos procesados | 17849778 | `$RJSUH9E.csv` / `$IJSUH9E.csv` | `2718ad6c88b52da2914b54e5f6eccb51815a2ff3c59100793c093292f900c60c` |
| `data/raw/hotel_bookings.csv` | Datos originales | 16855599 | `$RH6CDID.csv` / `$IH6CDID.csv` | `7c2ae42a7353905ea136e5c2287f17c92c5435826598bfbb8491c6f0c7b1fc06` |
| `entrega_final/figuras/01_cancelaciones.png` | Gráficos | 43800 | `$R9M9YEF.png` / `$I9M9YEF.png` | `cfdb074cbbca0924b6b7c4fa0489fc9bbf676175ff7f1d5ee8385ad3f264c949` |
| `entrega_final/figuras/02_eda.png` | Gráficos | 69196 | `$R7MGCI5.png` / `$I7MGCI5.png` | `c5ecebe26d60cabce0240dc003d900cd1514871ef46e0ae869a6887d1a6b51e4` |
| `entrega_final/figuras/03_modelos.png` | Gráficos | 71479 | `$RWCYLGF.png` / `$IWCYLGF.png` | `dd5bf285f6abf938f9ed81bbc3f29241a434085e691abdd16b67609eb03554a7` |
| `entrega_final/figuras/04_curvas.png` | Gráficos | 110163 | `$RUJ4V49.png` / `$IUJ4V49.png` | `cc157b2984e552f48bf2aae2239b071b6df10a81fe06078b0ab4e49466b574fc` |
| `entrega_final/figuras/05_matriz_calibracion.png` | Gráficos | 67714 | `$RNOH6DP.png` / `$INOH6DP.png` | `8be1d7ffe6eaa381eeea21e6ddfb5dd4c54be4f48c4ec49356f50cd49fdd42c2` |
| `entrega_final/figuras/06_mensual.png` | Gráficos | 85437 | `$R2DLCQP.png` / `$I2DLCQP.png` | `247ddea91f78e37481fedb7ada869984d13d0c6c74969a5c93fd9b01d872f458` |
| `entrega_final/figuras/07_hoteles.png` | Gráficos | 51690 | `$RWJN00Q.png` / `$IWJN00Q.png` | `f900b99dc9f714d5385c2e07ce3b7e0399d89acd183ac12bc9554512a4bfccde` |
| `entrega_final/fuentes/auditar_entrega.py` | Código auxiliar | 7379 | `$R4LFODD.py` / `$I4LFODD.py` | `8b387fbcb952a9ffc22e065ba31be9de0ced09192a895bb7be283d7ef4dcab4d` |
| `entrega_final/fuentes/crear_presentacion.mjs` | Código auxiliar | 16971 | `$RUV8I9I.mjs` / `$IUV8I9I.mjs` | `2a4c695d3480268f36468f0c8d0ef3ad99434a6a22b28eb6fc839e65a78f2982` |
| `entrega_final/fuentes/datos_presentacion.json` | Documentación y entregables editoriales | 10787 | `$RIRD2OI.json` / `$IIRD2OI.json` | `e9f9de61891563144902a87dcf5838302df8a19a85ae2a04aa123ebfbbbaa122` |
| `entrega_final/fuentes/exportar_pdf.py` | Código auxiliar | 5240 | `$RUMFZUW.py` / `$IUMFZUW.py` | `c5b6832f96b0d0ec9b927f30d6c1debc6a64bcb02f55a0fb2ff1cff55fe0bd62` |
| `entrega_final/fuentes/integridad_previa.json` | Documentación y entregables editoriales | 44898 | `$R5HR1TT.json` / `$I5HR1TT.json` | `601a6308232e032fd0e50aec571eefa45c302cb1bd74e3fa245367903ea7d16e` |
| `entrega_final/fuentes/notebooks_revision.json` | Documentación y entregables editoriales | 1826 | `$RCBSIPA.json` / `$ICBSIPA.json` | `1571546e9f75ab87d3d38f34fbbe306bed819b1e7b603f63b26d7ee61ef8b1f5` |
| `entrega_final/fuentes/preparar_entrega.py` | Código auxiliar | 6713 | `$RVYEWQ6.py` / `$IVYEWQ6.py` | `69c99e87a8fd9cac63e49944844d4b0f44b7a92093956e984f6b4ebaff7b9074` |
| `entrega_final/fuentes/renderizar_presentacion.mjs` | Código auxiliar | 1126 | `$R8CQ9F0.mjs` / `$I8CQ9F0.mjs` | `e22326839f3914b01f1de3f00fe3d19f03666dc808cb325cfa34824439c088bb` |
| `entrega_final/manifest_entrega.json` | Documentación y entregables editoriales | 2407 | `$RGA7RYY.json` / `$IGA7RYY.json` | `9bb296b7818d61c046b9ec73b2cab84e9535e57ac0ffae657448840d5d51bdae` |
| `entrega_final/memoria_final.md` | Documentación y entregables editoriales | 30816 | `$RF57IAJ.md` / `$IF57IAJ.md` | `aebcf33a398d6111ecbf0cd390d9cd479054826e5fedae2c5ac31ea4b24cddec` |
| `entrega_final/memoria_final.pdf` | Documentación y entregables editoriales | 683464 | `$RLSSQ4Q.pdf` / `$ILSSQ4Q.pdf` | `c5ffe534cc543cd06c2581f43ccd5468e0fc08504a1cc88a8bd2446c99dee49b` |
| `entrega_final/notas_presentacion.md` | Documentación y entregables editoriales | 5479 | `$RD4YPIO.md` / `$ID4YPIO.md` | `cf5b846b4a3d714f1b8b79c28a6585d29fb6227f48cac54b4976c2cf5a1cb016` |
| `entrega_final/presentacion_final.pptx` | Documentación y entregables editoriales | 74980 | `$RQSLWKY.pptx` / `$IQSLWKY.pptx` | `7eb999b0143dd228c400f16c1aa2c03b7b531a8a7e4f346184187e2b2372a5dd` |
| `entrega_final/README.md` | Documentación y entregables editoriales | 5512 | `$R85LRJA.md` / `$I85LRJA.md` | `945b90b506571cdae629bcc12c5d31b4578fcffc52f7b993e01d3808fd18405b` |
| `entrega_final/resumen_ejecutivo.md` | Documentación y entregables editoriales | 3022 | `$ROCFAUO.md` / `$IOCFAUO.md` | `7d46889d5a8be8c3706edbcb1027f8257ebe293b3bc94446a8e2c1f229fdfbf2` |
| `entrega_final/verificacion_entrega.json` | Documentación y entregables editoriales | 2498 | `$R01SV9T.json` / `$I01SV9T.json` | `e23aa2cb276cd528e3573e707d495202f1449a7e663f9fc196023c0b3b286921` |
| `herramientas/auditar_documentacion_integrada.py` | Código auxiliar | 9038 | `$RQ0URPI.py` / `$IQ0URPI.py` | `c18890294f36404d474af9f84ab5d054db0a4476e795765f5031b571d0722e06` |
| `herramientas/comentar_proyecto.py` | Código auxiliar | 31940 | `$RSB6MMG.py` / `$ISB6MMG.py` | `a14778411f8ca136c6eeae5280b1260fcf0722592a7e2d2fa6911064dcb70328` |
| `herramientas/integrar_documentacion.py` | Código auxiliar | 13648 | `$RM4F41B.py` / `$IM4F41B.py` | `311d00bb62ed8946287642016d3696c09b68c87e71edf2622c886d2c73484d3a` |
| `herramientas/verificar_comentarios.py` | Código auxiliar | 3480 | `$RCU4G8I.py` / `$ICU4G8I.py` | `0bd58541f297a10724649da2d22c3c1370f2f395a4c2ef9b1f92d827edd40f36` |
| `models/seleccion_8_modelo_congelado.joblib` | Modelos entrenados | 4476 | `$RET2QFW.joblib` / `$IET2QFW.joblib` | `460183467c6c0d783e8e05efe4b560ffce61aadf16fe272e4205b9f615b7867a` |
| `notebooks/baseline.ipynb` | Notebooks | 212094 | `$RXOVHH3.ipynb` / `$IXOVHH3.ipynb` | `63bdbd2b95b556ce82529b1c8484a9ebd5c4387feb9929d216b1dd7183bfce15` |
| `notebooks/comparacion_modelos.ipynb` | Notebooks | 409920 | `$RQ29IJH.ipynb` / `$IQ29IJH.ipynb` | `280a44fd50ca8f09f86903f449c86e30385706e08766f34009171e0b12ae95fb` |
| `notebooks/correccion_sesgo_temporal.ipynb` | Notebooks | 203279 | `$R6KNSZU.ipynb` / `$I6KNSZU.ipynb` | `f9cf92a74f73032cbb8c25cb1815f729a033adbfc4e2633ebb7842885d6020ee` |
| `notebooks/eda.ipynb` | Notebooks | 1388157 | `$RWH1HPY.ipynb` / `$IWH1HPY.ipynb` | `8decf3c2ece8deac9e3bd36eae68784311ef4398a6f5729d13d3102fd4497c2e` |
| `notebooks/evaluacion_final.ipynb` | Notebooks | 246587 | `$RPVF2I1.ipynb` / `$IPVF2I1.ipynb` | `81a3ee79716e9aef913de1fa5e5cdf28f145127031dfde46d2862976a078b8db` |
| `notebooks/explicabilidad.ipynb` | Notebooks | 1056928 | `$R8SCKIM.ipynb` / `$I8SCKIM.ipynb` | `40259d0b1d9ae3b319bf3d803cfc3b8e106b8ab040a20943ae28b84822c3185f` |
| `notebooks/optimizacion.ipynb` | Notebooks | 672246 | `$RK5B4EQ.ipynb` / `$IK5B4EQ.ipynb` | `63224cbfe658531161f36d246729ea9e0459a56e4702d9a82998a959278c2520` |
| `notebooks/preparacion.ipynb` | Notebooks | 105344 | `$RRTO5W4.ipynb` / `$IRTO5W4.ipynb` | `8df6f959209addda593a1cd9f435dbca743c32b992d656a7f05898c537b26711` |
| `notebooks/protocolo_temporal.ipynb` | Notebooks | 160665 | `$RXGO7YZ.ipynb` / `$IXGO7YZ.ipynb` | `7277035cdeca07cbdba073f783e5c1a225894c0af2d6dbd8e8504fa028efcb75` |
| `notebooks/seleccion_final.ipynb` | Notebooks | 420613 | `$R9HOVMZ.ipynb` / `$I9HOVMZ.ipynb` | `b9d60fb1027a3485470ef00906a4074d358de08620236d8f585ae08ebb1416fa` |
| `README.md` | Documentación y configuración | 6661 | `$RGWLQ5R.md` / `$IGWLQ5R.md` | `999a7ad3f3ba344b77469fbd18fb760e99909baceea03e34d42377f7d4bc221c` |
| `reports/auditoria_4_1_calibracion_validacion.csv` | Informes y evidencias tabulares | 898 | `$RLQO2HA.csv` / `$ILQO2HA.csv` | `2e07654ac75b06af6bb12e577ee7e6bf5220084b883dc5385374f03aa223d8da` |
| `reports/auditoria_4_1_categorias_nuevas_validacion.csv` | Informes y evidencias tabulares | 281 | `$R159HDM.csv` / `$I159HDM.csv` | `42187438f5937e1925ccd98533f8362567c2cb7c152ea73dd2533d937bb616b7` |
| `reports/auditoria_4_1_cierres_hipoteticos.csv` | Informes y evidencias tabulares | 369 | `$RRW65T1.csv` / `$IRW65T1.csv` | `38ee456e055f58ed447d130f5d9f322e2a351b562204bf743b3ed3fc1034e6a2` |
| `reports/auditoria_4_1_diagnosticos_train_validacion.csv` | Informes y evidencias tabulares | 449 | `$RXO58EJ.csv` / `$IXO58EJ.csv` | `8e6ce7e02d191c1c4288cfb944e843bdc7e3ca909cfc14c2e9be7d391b3d23dd` |
| `reports/auditoria_4_1_distribucion_probabilidades.csv` | Informes y evidencias tabulares | 409 | `$RH7RQWG.csv` / `$IH7RQWG.csv` | `b0723c58632f9c6fbe3a6e543fb61d16c395e6114c651386e012ce56eade6759` |
| `reports/auditoria_4_1_escenarios_coste_relativo.csv` | Informes y evidencias tabulares | 700 | `$R6LS169.csv` / `$I6LS169.csv` | `3427414e2e9c2e264a822de5c8220957a9e7e3d8dfeeff722547e7c4027a7164` |
| `reports/auditoria_4_1_perfiles_categoricos.csv` | Informes y evidencias tabulares | 4560 | `$RU28ZNY.csv` / `$IU28ZNY.csv` | `5c7aada317829f4991daf7e5161aeab9d2f2b777c537524363503b6f52edf178` |
| `reports/auditoria_4_1_perfiles_seleccion.csv` | Informes y evidencias tabulares | 609 | `$RVHELDD.csv` / `$IVHELDD.csv` | `8a8c71d93e81a75629f601f3e3d26e32c1cd76bd69d0795d9ccd4917a845079a` |
| `reports/auditoria_4_1_resultados.json` | Informes y evidencias tabulares | 40048 | `$RCPSIYP.json` / `$ICPSIYP.json` | `60e0ef353c5755e80ddf68e614e6edb3ff52c22d7141606ce72e9128836cdba9` |
| `reports/auditoria_4_1_umbrales_validacion.csv` | Informes y evidencias tabulares | 1711 | `$RIEQ9ZB.csv` / `$IIEQ9ZB.csv` | `5d25bc5ee3ae843940908f973c6f17bfd15d485774742b220db9ffeae588b3c8` |
| `reports/auditoria_4_1_verificacion.json` | Informes y evidencias tabulares | 980 | `$RBYAH70.json` / `$IBYAH70.json` | `01b647f5a119f4c2bec692fb85320f5d6105b90c8c36e3beeab1ffc923456f27` |
| `reports/baseline_predicciones_validacion.csv` | Predicciones y copias de referencia | 611166 | `$RV7KL17.csv` / `$IV7KL17.csv` | `4525d9eb5fb45777ec0ac9e3835d99c9338982fb16f4f53e2546fe88a2fcc319` |
| `reports/baseline_resultados.json` | Informes y evidencias tabulares | 905 | `$RQ444KQ.json` / `$IQ444KQ.json` | `993ebd38026e07e285e4100d6a4e7ef4c62738486b55082f758a52938289805c` |
| `reports/baseline_verificacion.json` | Informes y evidencias tabulares | 37044 | `$RO5Y9CY.json` / `$IO5Y9CY.json` | `729dce34efb471ea8d1b0fa08a689f94ce4e026a08a898253087d18e6cbd2201` |
| `reports/comparacion_5_metricas.csv` | Informes y evidencias tabulares | 1033 | `$RKO9DLV.csv` / `$IKO9DLV.csv` | `7bdb41b2bcb925e089062a5d53d30e196f23a0bf424cf02af74e8c8939cc3af6` |
| `reports/comparacion_5_predicciones_validacion.csv` | Predicciones y copias de referencia | 1763048 | `$RT4BFC9.csv` / `$IT4BFC9.csv` | `1f668616d7e39c8e5eb478c5cf175ec5c72c01e9c9fb2889842a2638f1973ae6` |
| `reports/comparacion_5_referencia_reproduccion.csv` | Informes y evidencias tabulares | 1763026 | `$R5FGMOR.csv` / `$I5FGMOR.csv` | `47c78ded3b64544b028d0c14d6bc99871f83546b3e7e321a8c1a76d6127f21f3` |
| `reports/comparacion_5_verificacion.json` | Informes y evidencias tabulares | 13654 | `$RCLAP3X.json` / `$ICLAP3X.json` | `65e4b58fc0d9efb9cf9011b07da6b8f53bb397b42f28764ecfa4077f33370ecd` |
| `reports/division_temporal.json` | Informes y evidencias tabulares | 4554 | `$R0F51WT.json` / `$I0F51WT.json` | `c91e3c035a6d5cc7079c45b3fcb977d946394ef408369feddece98010f081376` |
| `reports/documentacion_codigo.md` | Documentación y configuración | 1972 | `$RFRIE3Z.md` / `$IFRIE3Z.md` | `65e7e45ec87e34696ee90766ecc8b80e8a0325c1104a399032c05c4b7980332f` |
| `reports/documentacion_integrada.md` | Documentación y configuración | 5430 | `$R5H40TL.md` / `$I5H40TL.md` | `17bd528ff65993c91c7d1bf9db298e4c21adf8072478ec8882a9675703d6e3e6` |
| `reports/documentacion_integrada_estatica.json` | Informes y evidencias tabulares | 3012 | `$RSI0XNK.json` / `$ISI0XNK.json` | `a4f265f05ae8d2f5305af370857f443573cafa76ab986297d21de9c4edca391f` |
| `reports/documentacion_integrada_registro.json` | Informes y evidencias tabulares | 21966 | `$RI6Z207.json` / `$II6Z207.json` | `4e57856fa4858a30b61663c7d4602e6797728d4b62bdddedcff7ccb6c5357bf5` |
| `reports/documentacion_integrada_verificacion.json` | Informes y evidencias tabulares | 1166 | `$RKRUZRM.json` / `$IKRUZRM.json` | `37795ba4f86e96410c54256567ca0ad1888a34d7d0538ff7491467939050eca4` |
| `reports/eda_auditoria_leakage.csv` | Informes y evidencias tabulares | 1923 | `$ROI01SP.csv` / `$IOI01SP.csv` | `6d891386278cd6b0b2330eefba635ea7bc9d8df1c83daf811bc723c4a2b9c9ba` |
| `reports/eda_resumen.json` | Informes y evidencias tabulares | 24109 | `$RYAEMS2.json` / `$IYAEMS2.json` | `176d63df132d7279c208ee011cfe3fbc9e8d89a1aa6cd29e48b8e236dcfc04b3` |
| `reports/eda_verificacion.json` | Informes y evidencias tabulares | 1068 | `$R7O52K2.json` / `$I7O52K2.json` | `3ce28cf4858303992e24dbcb39b2c7e4e14bcf3abb8cf9b923593b70fd2289c3` |
| `reports/estado_protocolo.json` | Informes y evidencias tabulares | 501 | `$ROQCCNQ.json` / `$IOQCCNQ.json` | `4714df095f56607b833e06037e5d8c65a9e2f0c6fb6ed8ec81fa4d1d27a6b66c` |
| `reports/evaluacion_9_bootstrap_replicas.csv` | Informes y evidencias tabulares | 79031 | `$RQITLU4.csv` / `$IQITLU4.csv` | `611b1afe9c1f7d272ccebf46225692c2ba89edb9257068accb8987c9d73ad49d` |
| `reports/evaluacion_9_bordes_empates.csv` | Informes y evidencias tabulares | 609 | `$R2U7PU6.csv` / `$I2U7PU6.csv` | `39ce65336ce655fb0b266ee850946284c004d37d568144fb9d6baa386e861091` |
| `reports/evaluacion_9_calibracion_bins.csv` | Informes y evidencias tabulares | 496 | `$RI3I6OB.csv` / `$II3I6OB.csv` | `45bf0b597d286e561b0e3100e65e8f55fb3ae2b42cedc3af7950137a48492698` |
| `reports/evaluacion_9_comparacion_validacion.csv` | Informes y evidencias tabulares | 641 | `$RUCPLNU.csv` / `$IUCPLNU.csv` | `1ce921af078f13052299a360091d9b3762ef01b48df22651116db2fa7199a967` |
| `reports/evaluacion_9_composicion.csv` | Informes y evidencias tabulares | 1047 | `$RASE9DS.csv` / `$IASE9DS.csv` | `aa1799dfeaeec5b41f82e4f3f4a59e009471121ed4660210a40b20369375db6f` |
| `reports/evaluacion_9_etiquetas_prueba.csv` | Informes y evidencias tabulares | 308108 | `$RWLXY1N.csv` / `$IWLXY1N.csv` | `f6604f52e764b697dd01a9a48465ea87b8ac0b8c76f7ec43a73702bad6510020` |
| `reports/evaluacion_9_fuente_ejecucion.py` | Documentación y configuración | 35231 | `$RGAAU1W.py` / `$IGAAU1W.py` | `87b28722e8926466734f958a42fac46a71d797244f74c762437e6ba5f116f080` |
| `reports/evaluacion_9_hoteles.csv` | Informes y evidencias tabulares | 652 | `$RY9EX95.csv` / `$IY9EX95.csv` | `fb462559282a21162d6832f88a827bb6444d115aa764c95c4f8658b14eea5b04` |
| `reports/evaluacion_9_intervalos.csv` | Informes y evidencias tabulares | 638 | `$RI95GMR.csv` / `$II95GMR.csv` | `004fd67a22efb2f06a896b52cdc96abacccf2ac5ad52ab39926b666c1bb4c4b6` |
| `reports/evaluacion_9_mensual.csv` | Informes y evidencias tabulares | 1554 | `$RHTB72Y.csv` / `$IHTB72Y.csv` | `e425ea0ac5623f1fef603f6fdac969f176b1316e504704367a0a5702ae6440ff` |
| `reports/evaluacion_9_metricas.json` | Informes y evidencias tabulares | 3811 | `$RCEZASK.json` / `$ICEZASK.json` | `f70c11b67bfc1a128e4995c0100edca2385a14b0f061061b59c8499f0242dfbe` |
| `reports/evaluacion_9_plan_previo.md` | Documentación y configuración | 3077 | `$REPAZV1.md` / `$IEPAZV1.md` | `9a34190f9856975366b2742afc7c0f71f02b82f76d6bb3b0afaf619825e8f657` |
| `reports/evaluacion_9_predicciones_congeladas.csv` | Predicciones y copias de referencia | 4370578 | `$RYLHH5A.csv` / `$IYLHH5A.csv` | `d2473cb9069ca2abdb53eefe1c49c2e2febaf62a3ccba345d63d028f68f6151f` |
| `reports/evaluacion_9_preflight.json` | Informes y evidencias tabulares | 40883 | `$R0V8816.json` / `$I0V8816.json` | `2729f9f381dc18bbe2ec4a4e29e917f5c28e922242c0b170ad5f3027b18131f0` |
| `reports/evaluacion_9_recibo.json` | Informes y evidencias tabulares | 3042 | `$ROMFIGB.json` / `$IOMFIGB.json` | `1c99fb44e298fec001c29f43d23c285b7205083b5ad5c7434be8ff3b8ccb2ba9` |
| `reports/evaluacion_9_verificacion.json` | Informes y evidencias tabulares | 1145 | `$RJ5DULT.json` / `$IJ5DULT.json` | `143e95a0ac267992f00398961413fa30740635b0beb8f4f3c075c6ebaced22a3` |
| `reports/explicabilidad_7_calibracion_bins.csv` | Informes y evidencias tabulares | 2143 | `$RCOBKXH.csv` / `$ICOBKXH.csv` | `8946c9a5ad6ca07e29163981ce05ecc413a8d1d98e6befc3077413c7807ab606` |
| `reports/explicabilidad_7_casos.csv` | Informes y evidencias tabulares | 671 | `$R6SCGJV.csv` / `$I6SCGJV.csv` | `2638d3cfbcbbbcb814b61040bc3316b57d1fd5f58ba49e9244212a11185f5b1c` |
| `reports/explicabilidad_7_contribuciones_locales.csv` | Informes y evidencias tabulares | 2480 | `$RJ1QPQ7.csv` / `$IJ1QPQ7.csv` | `eacd7823b2b4cc4aa35ef468677dd2d9cad915f33f2e91799ba89cd4c7912cdd` |
| `reports/explicabilidad_7_dependencia_perfil.csv` | Informes y evidencias tabulares | 6309 | `$RPNJPI6.csv` / `$IPNJPI6.csv` | `51fe289fd0af759a25c7c9e8b47e6e9c4d05074bb15098e9364a469314234229` |
| `reports/explicabilidad_7_gain_originales.csv` | Informes y evidencias tabulares | 728 | `$R0TOVW0.csv` / `$I0TOVW0.csv` | `a931f7fd23da33f085f27f47ce7029b11372eb706a2dfc527b5580d61477dd75` |
| `reports/explicabilidad_7_gain_transformadas.csv` | Informes y evidencias tabulares | 12385 | `$RWOY7YY.csv` / `$IWOY7YY.csv` | `5c4d4aa720b2b904bd5e275166cf6cfa4bfc29ba74fe718e475b36143f605cff` |
| `reports/explicabilidad_7_mapa_caracteristicas.csv` | Informes y evidencias tabulares | 8222 | `$RUTNECI.csv` / `$IUTNECI.csv` | `55d9a76211e6326f790db6e6b4e7221a54182adc26d337f709f50123656f3739` |
| `reports/explicabilidad_7_muestra_ids.csv` | Informes y evidencias tabulares | 21366 | `$RC7VW55.csv` / `$IC7VW55.csv` | `744be32ace838f73ded77a68500d4bcbcfa9fb4560e33a2f706811a8f907fa0a` |
| `reports/explicabilidad_7_muestra_perfil.csv` | Informes y evidencias tabulares | 770 | `$R166OI6.csv` / `$I166OI6.csv` | `f36fca9397b39715072a63c74fe7ae31469863580e43f7290ae0dd68fedef8f6` |
| `reports/explicabilidad_7_predicciones_validacion.csv` | Predicciones y copias de referencia | 361081 | `$R4L2PSZ.csv` / `$I4L2PSZ.csv` | `82ea3ef821b6d3d100c43b6408611402c6ba86968f2f50d3a02fe4f34dbe5364` |
| `reports/explicabilidad_7_reproduccion.json` | Informes y evidencias tabulares | 1879 | `$RUR3MZO.json` / `$IUR3MZO.json` | `900ecae24e5879cd32d745dd38a3ee01836d87d3506d0b1935e53aa2f78caa74` |
| `reports/explicabilidad_7_segmentos.csv` | Informes y evidencias tabulares | 10826 | `$RG9F32A.csv` / `$IG9F32A.csv` | `337e7819b41c133e973fbc334cd807a6a3b055783b574047c8fd01a0f1e7298e` |
| `reports/explicabilidad_7_shap.npz` | Informes y evidencias tabulares | 869547 | `$R2N9LFC.npz` / `$I2N9LFC.npz` | `018f96920bee52a617df27398ca2d18286d8369e213fac0f433f1f027da5a9e6` |
| `reports/explicabilidad_7_shap_global.csv` | Informes y evidencias tabulares | 718 | `$RQZPGIA.csv` / `$IQZPGIA.csv` | `70859d6a3b7e583d0dabaecbfb465b221d3672419fb8584b0eaa24dadea6f773` |
| `reports/explicabilidad_7_shap_transformadas.csv` | Informes y evidencias tabulares | 9707 | `$RJJJ7DG.csv` / `$IJJJ7DG.csv` | `0867a3d1c4e26c52eee457092bf6cf15795440ffb312f44ab87e929f5fd16026` |
| `reports/explicabilidad_7_verificacion.json` | Informes y evidencias tabulares | 18850 | `$RJHHYTV.json` / `$IJHHYTV.json` | `b67698ad4b3e2a8eda7732be2c943079142edad41806c451a9813e12b48bf80d` |
| `reports/fase_10_entrega_final.md` | Informes y evidencias tabulares | 5182 | `$RZ9EY9B.md` / `$IZ9EY9B.md` | `8f97b76c3cdbc49c692e8a745154b6b76fd679123eccbb84a5995b659be2614b` |
| `reports/fase_1_inspeccion.md` | Informes y evidencias tabulares | 8955 | `$RORZ5MC.md` / `$IORZ5MC.md` | `bfd6f6d58eb61411d46417fd6d916db9e4b5e9a36b22edf02e31501805ac8df7` |
| `reports/fase_2_eda.md` | Informes y evidencias tabulares | 10171 | `$RD7QUAC.md` / `$ID7QUAC.md` | `b2b0d5ea1a7bcbc072c69e8b9ad8537b9e99c6be45a7bfcc98c181fa37b21207` |
| `reports/fase_3_preparacion.md` | Informes y evidencias tabulares | 16852 | `$RZMS3ZM.md` / `$IZMS3ZM.md` | `8ee57b577f10d4c2e9b4e26d4a651035c8f351eb0ce8e9e0759d79a7c216d804` |
| `reports/fase_4_1_auditoria.md` | Informes y evidencias tabulares | 20746 | `$RJ5VUOF.md` / `$IJ5VUOF.md` | `5feaf824ea787b3622117a7aa5817e690bb9f6b452b730165ca348f5fbb068b1` |
| `reports/fase_4_2_protocolo_temporal.md` | Informes y evidencias tabulares | 15821 | `$RG92QB2.md` / `$IG92QB2.md` | `3541d2858dfcfa76ef3ba562463c2046ea29855bee902786c7a5d36ab8e6cc4d` |
| `reports/fase_4_baseline.md` | Informes y evidencias tabulares | 12224 | `$RZNSYX8.md` / `$IZNSYX8.md` | `ac790bd6c98bf6b24b7998899a430eb3a8b3f5fb20e63c7780cb446608531342` |
| `reports/fase_5_comparacion_modelos.md` | Informes y evidencias tabulares | 10506 | `$RB47TBR.md` / `$IB47TBR.md` | `545c644e1e15dc5323a9f999405059b68f21628fcde755eadbab4bdc70459cb6` |
| `reports/fase_6_optimizacion.md` | Informes y evidencias tabulares | 25364 | `$RH225CE.md` / `$IH225CE.md` | `67a852b46d8b7f95b8ff06146c959273006685ab0398319951b2f83021e0adad` |
| `reports/fase_7_1_correccion_sesgo_temporal.md` | Informes y evidencias tabulares | 26847 | `$RJ0ZZWW.md` / `$IJ0ZZWW.md` | `9f29eee062ca69527df0309acd7ed69306c0e3c8466df33db3560f55cd21c478` |
| `reports/fase_7_explicabilidad.md` | Informes y evidencias tabulares | 30903 | `$RRSWTZJ.md` / `$IRSWTZJ.md` | `f77d101a1ad5e05ae1fa065c096338413ca6bddbcfa902cc147247cd1fd3f1c1` |
| `reports/fase_8_seleccion_final.md` | Informes y evidencias tabulares | 23596 | `$RGNHMKA.md` / `$IGNHMKA.md` | `50c45506202ea26709107d114fb3d17062afac695e40081834f18f4ba50a60f0` |
| `reports/fase_9_evaluacion_final.md` | Informes y evidencias tabulares | 17374 | `$R6FZFU5.md` / `$I6FZFU5.md` | `3ddf68e8430b6f908cadd3a31b72b1bc5f9f6803e93959a726b4e698325a0890` |
| `reports/figures/01_ausencias.png` | Gráficos | 50619 | `$RVDSYWH.png` / `$IVDSYWH.png` | `7944a583b51df877425cbed85c1b79386781aad8332ec2943ce9cdf9efb79b49` |
| `reports/figures/02_objetivo_hoteles.png` | Gráficos | 48778 | `$RH7XZGA.png` / `$IH7XZGA.png` | `88e5aded3b970d1a3155d8b424f39af12c9f9fa993dcc7606ddbe8dfe20c080e` |
| `reports/figures/03_antelacion_adr.png` | Gráficos | 109976 | `$RYLGN3A.png` / `$IYLGN3A.png` | `8fa26cadee6b044d6aaa13458785dbb4c6faa791b756e81cd7f3a981f299e3b4` |
| `reports/figures/04_tasas_antelacion.png` | Gráficos | 52586 | `$R1110GX.png` / `$I1110GX.png` | `d8d31647243caae409a239fab56b82519690e4ba695e01759fc3bcdf34aea60d` |
| `reports/figures/05_customer_type.png` | Gráficos | 44814 | `$RLQZG5L.png` / `$ILQZG5L.png` | `95f66ebbb0559255e5305d5217f5d832290b6fc7ccabe0b44624e516cbd8a391` |
| `reports/figures/05_deposit_type.png` | Gráficos | 42167 | `$RCLYXX2.png` / `$ICLYXX2.png` | `8a290ceb7e7d4c739600e386571ca6e1370f54a32d6108dc4d886d4fa871c588` |
| `reports/figures/05_distribution_channel.png` | Gráficos | 47720 | `$R03QXRQ.png` / `$I03QXRQ.png` | `530b4d08197b0c12af3f5ed8e1ba53953ea18379cad706eaa227fbdd79b7e01d` |
| `reports/figures/05_market_segment.png` | Gráficos | 64465 | `$RWQVVVH.png` / `$IWQVVVH.png` | `e7d21d4a0233825ca8a88df1582a224059e32adc9fb9d227b49c94044b71d2a7` |
| `reports/figures/06_historial_solicitudes.png` | Gráficos | 48660 | `$R5S576T.png` / `$I5S576T.png` | `d8c169fabe2eb94356eafb98d145495b43cdc27b721a96a51648244d958b9270` |
| `reports/figures/07_estancia_huespedes.png` | Gráficos | 39848 | `$R4QEYC4.png` / `$I4QEYC4.png` | `de1450e08043d9cb1f95020548fff1b8caa26e9d22a44e3a46242792ff224c39` |
| `reports/figures/08_evolucion_temporal.png` | Gráficos | 223661 | `$RWI0QA8.png` / `$IWI0QA8.png` | `fff32f5fd46b61c03d5e5e997523f552e9fa3d34dd8820d934fcadd47e6a5902` |
| `reports/figures/09_estacionalidad.png` | Gráficos | 111377 | `$RC83X1X.png` / `$IC83X1X.png` | `b2ed8b53e7d3b1a0a83ca7e217a592528f9ee790370730c6db1cb5cf65d1eeaa` |
| `reports/figures/10_correlaciones.png` | Gráficos | 173447 | `$RKREU6D.png` / `$IKREU6D.png` | `fc88d822d224c090e8fb12ae5c583a231cf78e389a662edc2a6a4be30e24be5b` |
| `reports/figures/auditoria_4_1_01_sesgo_antelacion.png` | Gráficos | 106127 | `$R8LU0K9.png` / `$I8LU0K9.png` | `0cf3df9531000c4a119b49f9af26c5a6cb42db96d3ed38d55f2d1d14737db5f9` |
| `reports/figures/auditoria_4_1_02_distribucion_probabilidades.png` | Gráficos | 60514 | `$R07VJTO.png` / `$I07VJTO.png` | `b9e5d2193d4548cfc26acf491225d0e021cf6a21412c77be39044ec9e8b00f26` |
| `reports/figures/auditoria_4_1_03_calibracion_validacion.png` | Gráficos | 96161 | `$RGMYQAH.png` / `$IGMYQAH.png` | `019756a7b7283e8ea809da18add09c72d7b56e39cd2fe25bd8727955cbed52bb` |
| `reports/figures/auditoria_4_1_04_precision_recall_umbrales.png` | Gráficos | 126399 | `$RZRDRLO.png` / `$IZRDRLO.png` | `594179bd17315fd4094445ba631cb003a551a10b301db8863c37833c3fbc8b4f` |
| `reports/figures/baseline_01_particiones.png` | Gráficos | 54726 | `$R6P093C.png` / `$I6P093C.png` | `ff959839d025cd7002994f409aa99f41a239fd30f7faa3007eb6cab9099f4b96` |
| `reports/figures/baseline_02_confusion_validacion.png` | Gráficos | 54157 | `$RJFBB3A.png` / `$IJFBB3A.png` | `2983f7af1fad9dc64bc164996fb45902134d95836ce822e35e94886dd4d20214` |
| `reports/figures/baseline_03_roc_validacion.png` | Gráficos | 62870 | `$RRZZJT1.png` / `$IRZZJT1.png` | `e73746da2350618b27f22a30b9a2c440041a9b3f7f07f980068fc3dc0a645a03` |
| `reports/figures/comparacion_5_curvas.png` | Gráficos | 168325 | `$RE2M8WY.png` / `$IE2M8WY.png` | `611bcff289cffb8cbd9353579dc5be61ecd9ad272bf154eabf5b79b79146661a` |
| `reports/figures/comparacion_5_matrices.png` | Gráficos | 77181 | `$RNB6RHX.png` / `$INB6RHX.png` | `51de0dee6f74d1be742c965b9a8fd2b5214965920fdc066914ac55f771ef2a3f` |
| `reports/figures/comparacion_5_metricas.png` | Gráficos | 49663 | `$ROIP7S7.png` / `$IOIP7S7.png` | `5aa722f8f3d0a45dba27829111af5351dac369f756d8c81cadd8ce81644bbf86` |
| `reports/figures/evaluacion_9_matriz_calibracion.png` | Gráficos | 67714 | `$RP7ZAPN.png` / `$IP7ZAPN.png` | `8be1d7ffe6eaa381eeea21e6ddfb5dd4c54be4f48c4ec49356f50cd49fdd42c2` |
| `reports/figures/evaluacion_9_mensual.png` | Gráficos | 85437 | `$RRLXGIG.png` / `$IRLXGIG.png` | `247ddea91f78e37481fedb7ada869984d13d0c6c74969a5c93fd9b01d872f458` |
| `reports/figures/explicabilidad_7_calibracion.png` | Gráficos | 143007 | `$RJQ2SU3.png` / `$IJQ2SU3.png` | `fb6254fae92e7dc84b0280c3b5aa96c4ba0c03a867cb3a4e1f633ba801381d4f` |
| `reports/figures/explicabilidad_7_dependencias.png` | Gráficos | 148958 | `$RUUS153.png` / `$IUUS153.png` | `4584db4d82978cb25230455baa299b074b23f476ec29be0d5fbbf79d784a5425` |
| `reports/figures/explicabilidad_7_errores.png` | Gráficos | 70172 | `$RBQEMLE.png` / `$IBQEMLE.png` | `634260d6324e6921443451395efe7eea817fc2778ed59d4758eef81b46e41ad8` |
| `reports/figures/explicabilidad_7_importancias.png` | Gráficos | 72217 | `$RLFFK1T.png` / `$ILFFK1T.png` | `c9d10dc2030c06c869bdfd7ef24521ce96d4f3ad33899f22378fe4c01acd8ff2` |
| `reports/figures/explicabilidad_7_locales.png` | Gráficos | 130320 | `$RNP21RK.png` / `$INP21RK.png` | `6ee6ea9bc2e163c4ddb39824f82a748f8a1badf04e7263d99ced2b7bb8a4a24c` |
| `reports/figures/explicabilidad_7_shap_resumen.png` | Gráficos | 166732 | `$RB556O2.png` / `$IB556O2.png` | `5ad04ac899fc635639e5a442d3e8fba8c551345355918d3aecd1992adcedd721` |
| `reports/figures/optimizacion_6_estabilidad.png` | Gráficos | 86632 | `$ROMN428.png` / `$IOMN428.png` | `3a2e917b402cf216b852bf3598cc54871a8716d0800fdc69e5c20be46a7ab363` |
| `reports/figures/optimizacion_6_pr_calibracion.png` | Gráficos | 175808 | `$R39QELS.png` / `$I39QELS.png` | `a88fcfac9fd35ffc8561a51e6f6b42a662e3e6dbed547132ba7948fd58eb832a` |
| `reports/figures/optimizacion_6_umbrales.png` | Gráficos | 191620 | `$R84DOW4.png` / `$I84DOW4.png` | `3e512c7fcf58fc7b88b092ea18bf63ba9d5343fc618568a1f149021441217432` |
| `reports/figures/protocolo_4_2_confusion_validacion.png` | Gráficos | 50793 | `$REA3G4Q.png` / `$IEA3G4Q.png` | `a2bc12484adce21eaa91e5a6a1b3fa005b7853df44b1e4f91b4d702301b4b5ab` |
| `reports/figures/protocolo_4_2_reincorporacion.png` | Gráficos | 31685 | `$RUO2HV4.png` / `$IUO2HV4.png` | `d94df3e0995079b5895f1d2a3f9464128ff9e1f8d30216d5d7b1ad8e4a30ad44` |
| `reports/figures/protocolo_7_1_estabilidad.png` | Gráficos | 70218 | `$RJX9CWP.png` / `$IJX9CWP.png` | `14a11f7b95d225c38e218aeee87469a584c79197c8702ced6100348365d1b59e` |
| `reports/figures/protocolo_7_1_matrices.png` | Gráficos | 33397 | `$R23Z4UP.png` / `$I23Z4UP.png` | `56e7bcf0bd72f52f028ded60a2b119e28128177703d077321185fd258f0f2224` |
| `reports/figures/seleccion_8_calibracion.png` | Gráficos | 89859 | `$RV7HCXH.png` / `$IV7HCXH.png` | `fc66d49d63270409a5516b0c24db087c5220b30efed17f5d12cb971851b44473` |
| `reports/figures/seleccion_8_capacidades.png` | Gráficos | 72332 | `$RKVEJX5.png` / `$IKVEJX5.png` | `c53d8535b7f564857d886fb0f73b5f13e83afcfc148bf3be9b1b255c6660a1e0` |
| `reports/figures/seleccion_8_umbrales.png` | Gráficos | 103408 | `$RNMC5Z0.png` / `$INMC5Z0.png` | `ae82e20b0b450657bf4f755bd8a10fb2bbb82f3b380de1277e002450550481e7` |
| `reports/historico/documentacion_pre_integracion/entrega_final/fuentes/auditar_entrega.py` | Respaldos históricos | 6642 | `$RFGOGOK.py` / `$IFGOGOK.py` | `ed07d3db62741aae19e6a8994d2c7fe7fecdd3d2cd486c4623c304561cc2d4a3` |
| `reports/historico/documentacion_pre_integracion/entrega_final/fuentes/crear_presentacion.mjs` | Respaldos históricos | 14699 | `$RIIMCB7.mjs` / `$IIIMCB7.mjs` | `b3581cfd1e7012add4afd94b9691ba4f4ee9400bfb15a93a44557f65e2853c6f` |
| `reports/historico/documentacion_pre_integracion/entrega_final/fuentes/exportar_pdf.py` | Respaldos históricos | 5002 | `$RVO0RJ3.py` / `$IVO0RJ3.py` | `c955bc3e41a3404e96a9ce416645d052c64f07ee91422990b1f41b4670dd35a1` |
| `reports/historico/documentacion_pre_integracion/entrega_final/fuentes/preparar_entrega.py` | Respaldos históricos | 6368 | `$RZKN0CQ.py` / `$IZKN0CQ.py` | `fbaf76659be7d310ead9dce12961cf53c521f8a37571774157e9cfc72205af57` |
| `reports/historico/documentacion_pre_integracion/entrega_final/fuentes/renderizar_presentacion.mjs` | Respaldos históricos | 881 | `$R9Z8TAG.mjs` / `$I9Z8TAG.mjs` | `daa7bd6f3ef807cc81142a870a00087fbcd4aa5d1f12286059c8bb3a5e03799c` |
| `reports/historico/documentacion_pre_integracion/entrega_final/manifest_entrega.json` | Respaldos históricos | 2274 | `$R3WHJZK.json` / `$I3WHJZK.json` | `809662aabaeb8e0ff20783551edc8da702a88a2d93555c450582b3520c6a97d1` |
| `reports/historico/documentacion_pre_integracion/entrega_final/README.md` | Respaldos históricos | 5197 | `$R05JMOZ.md` / `$I05JMOZ.md` | `c329c35243b90a5abc3fb9f63559698ecaec0cb2ed291143ea65d306fd5203b2` |
| `reports/historico/documentacion_pre_integracion/notebooks/baseline.ipynb` | Respaldos históricos | 208501 | `$R8VCUAI.ipynb` / `$I8VCUAI.ipynb` | `713855e376b70e2e4428be7b17928279bda9e0a50a8ed9b09909611dc61ad554` |
| `reports/historico/documentacion_pre_integracion/notebooks/comparacion_modelos.ipynb` | Respaldos históricos | 407695 | `$RIPQHUY.ipynb` / `$IIPQHUY.ipynb` | `dd390d56af8eacfb718942b5262e30863e3c96a2a6743c55436610c47f337f23` |
| `reports/historico/documentacion_pre_integracion/notebooks/correccion_sesgo_temporal.ipynb` | Respaldos históricos | 200321 | `$RYK5IJJ.ipynb` / `$IYK5IJJ.ipynb` | `d6e00c6d6ec17846220a23f14f17eb4b99dc3867c5c7756ac9ec2148569d697f` |
| `reports/historico/documentacion_pre_integracion/notebooks/eda.ipynb` | Respaldos históricos | 1380339 | `$R86BEY7.ipynb` / `$I86BEY7.ipynb` | `795f15aa3ee03b538dffff01cc537f41486034aa9b5c404acf5475f0bade66a3` |
| `reports/historico/documentacion_pre_integracion/notebooks/evaluacion_final.ipynb` | Respaldos históricos | 242811 | `$R33DHZA.ipynb` / `$I33DHZA.ipynb` | `d042cd55813d444f1868aaae5a30826d5ecd83d2441267c4fd39391a97960bf1` |
| `reports/historico/documentacion_pre_integracion/notebooks/explicabilidad.ipynb` | Respaldos históricos | 1054093 | `$R6VUGPR.ipynb` / `$I6VUGPR.ipynb` | `849ba306a3cd7be413abc045403367c34672f4726ce33e4e6ac7d28cd84be557` |
| `reports/historico/documentacion_pre_integracion/notebooks/optimizacion.ipynb` | Respaldos históricos | 669240 | `$RUU217I.ipynb` / `$IUU217I.ipynb` | `c55bc6bf16e3cfeb294a0e5018854b2c450de86365dec417bdb65dc086872567` |
| `reports/historico/documentacion_pre_integracion/notebooks/preparacion.ipynb` | Respaldos históricos | 100153 | `$RA9ITP9.ipynb` / `$IA9ITP9.ipynb` | `64f1de722c79e8b4f3dc954354d000781633289a1f0f84269aed32a720e55fc9` |
| `reports/historico/documentacion_pre_integracion/notebooks/protocolo_temporal.ipynb` | Respaldos históricos | 158186 | `$RT0JU5Y.ipynb` / `$IT0JU5Y.ipynb` | `f0b1ee4d9661012719f8a9455e16d8f9bc721decbbb5c8a0e8c77046bb9432b2` |
| `reports/historico/documentacion_pre_integracion/notebooks/seleccion_final.ipynb` | Respaldos históricos | 417336 | `$RFWCTBV.ipynb` / `$IFWCTBV.ipynb` | `124dd2e42aea7c4d64776327f49310ef4f5e2898157ed8b683e3475e9ac61a99` |
| `reports/historico/documentacion_pre_integracion/README.md` | Respaldos históricos | 6012 | `$RMJPTPL.md` / `$IMJPTPL.md` | `dcd3863ef3f95b54cb9bedfbe104a5fee7a87204180b677f08132928607c692d` |
| `reports/historico/documentacion_pre_integracion/registro_previo.json` | Respaldos históricos | 58481 | `$RB9XK1F.json` / `$IB9XK1F.json` | `c46f084f4f7b83c915105e094c8cb9ab251fc3d9e876c225f1f6386fc0663b85` |
| `reports/historico/documentacion_pre_integracion/src/__init__.py` | Respaldos históricos | 69 | `$RBB9YCM.py` / `$IBB9YCM.py` | `85312e2cd5f7538b0bbe0521faf14f9a28eee7195b50f3c5986d6d5d76008515` |
| `reports/historico/documentacion_pre_integracion/src/audit_baseline.py` | Respaldos históricos | 42690 | `$RMGOYA4.py` / `$IMGOYA4.py` | `ebfc98634ff16939c821d2269a82e1723d1271bc128684196ac20428c564ea25` |
| `reports/historico/documentacion_pre_integracion/src/baseline.py` | Respaldos históricos | 23510 | `$REIU72R.py` / `$IEIU72R.py` | `508694e2edc55d9cdf83e7fdae191a945c0ef59f5cae83dec0f03ed685783f42` |
| `reports/historico/documentacion_pre_integracion/src/cleaning.py` | Respaldos históricos | 2274 | `$RU5S0GI.py` / `$IU5S0GI.py` | `52793ede516563751221b92be18ae81850f0fc4802d9b6f4dff27ac15bd49b89` |
| `reports/historico/documentacion_pre_integracion/src/comparison.py` | Respaldos históricos | 21024 | `$R8B8R1C.py` / `$I8B8R1C.py` | `3d44658eb5a829e2980257104e61c37d5a7f59971bfeee5e96bf71521f9216fc` |
| `reports/historico/documentacion_pre_integracion/src/decision_policy.py` | Respaldos históricos | 3095 | `$RVUEPR9.py` / `$IVUEPR9.py` | `5b9776ea088e8cb125be7464c0c2579657c600a2750cd8c4e39c90c9b4b1a755` |
| `reports/historico/documentacion_pre_integracion/src/evaluation_narrative.py` | Respaldos históricos | 4311 | `$RSTM5SO.py` / `$ISTM5SO.py` | `87c57c1b7e803c97fe82d9092f8730f99176151c973463f3f66907304c2c2840` |
| `reports/historico/documentacion_pre_integracion/src/explainability.py` | Respaldos históricos | 42293 | `$RH7T3IN.py` / `$IH7T3IN.py` | `b41be3e76e0807190d67d8228884e7ba09c7794f57f6a5e94176724f501be3b7` |
| `reports/historico/documentacion_pre_integracion/src/features.py` | Respaldos históricos | 6782 | `$R2BAHXK.py` / `$I2BAHXK.py` | `c150d2ef7a93d2aba990a926cda1eca746e48011764e4dab8ad60ed3cc620213` |
| `reports/historico/documentacion_pre_integracion/src/final_evaluation.py` | Respaldos históricos | 35231 | `$RXGQ3ZF.py` / `$IXGQ3ZF.py` | `87b28722e8926466734f958a42fac46a71d797244f74c762437e6ba5f116f080` |
| `reports/historico/documentacion_pre_integracion/src/final_selection.py` | Respaldos históricos | 32547 | `$RGM3C97.py` / `$IGM3C97.py` | `7701253463942f9609f77fd658508f6efbd1e8b87c572375b16668a8b3dab786` |
| `reports/historico/documentacion_pre_integracion/src/inspection.py` | Respaldos históricos | 1379 | `$RSZAFYF.py` / `$ISZAFYF.py` | `5b41fd7480ddc21989fb65b6c2c8190fc14f9f8ea100357d98ce85c3d7aebedc` |
| `reports/historico/documentacion_pre_integracion/src/optimization.py` | Respaldos históricos | 47563 | `$RMUJDYL.py` / `$IMUJDYL.py` | `6e93ae31d0ef7d4f2da731087f08f2835804885b936bda815161abd53ff1b0c7` |
| `reports/historico/documentacion_pre_integracion/src/preparation.py` | Respaldos históricos | 4345 | `$RYY0YFP.py` / `$IYY0YFP.py` | `403f6f45167d319a2841b1843546dda2cfa2f47bc1e662e1ebcd1b4f04210eaa` |
| `reports/historico/documentacion_pre_integracion/src/preprocessing.py` | Respaldos históricos | 1082 | `$R770BMM.py` / `$I770BMM.py` | `2877c53e7cefd7d673b4b46500df54ad888c1242af0a783ddd692f45532bae67` |
| `reports/historico/documentacion_pre_integracion/src/run_notebook.py` | Respaldos históricos | 2903 | `$R7R0BEO.py` / `$I7R0BEO.py` | `216f52e479566ce4ce2b08cea97ebed8e664dc9d929cd9084125380907ba96c9` |
| `reports/historico/documentacion_pre_integracion/src/splitting.py` | Respaldos históricos | 11278 | `$RLNYCRA.py` / `$ILNYCRA.py` | `1840c5de0f3124eaa3530a4963a05fbe5878dd5478a999767f2e7a2b9e005fca` |
| `reports/historico/documentacion_pre_integracion/src/temporal_bias_v3.py` | Respaldos históricos | 34871 | `$R8IW2TH.py` / `$I8IW2TH.py` | `17c05fa340c27b7ca6dd1458129175ba62cf58abc32d3f8e974f6ec7bde926bf` |
| `reports/historico/documentacion_pre_integracion/src/temporal_protocol.py` | Respaldos históricos | 31627 | `$RV0ENQM.py` / `$IV0ENQM.py` | `d83cf5d676723907fb67e7273cec9463d78f2ba2af1f89e90202455bb0ce0fa9` |
| `reports/historico/documentacion_pre_integracion/tests/test_audit_baseline.py` | Respaldos históricos | 1881 | `$R42Z1RX.py` / `$I42Z1RX.py` | `f53cea7a11c44873559f78b36d5d9aaec4f2d3066df32141562af8f85ce67263` |
| `reports/historico/documentacion_pre_integracion/tests/test_baseline.py` | Respaldos históricos | 2529 | `$RUJVBDU.py` / `$IUJVBDU.py` | `b7d52d20481792e7fdfc33156fc9f944f886b40a297882cceffa6bd48e894b95` |
| `reports/historico/documentacion_pre_integracion/tests/test_comparison.py` | Respaldos históricos | 2002 | `$RB5KB0P.py` / `$IB5KB0P.py` | `a779c9df5e7e836628b593dbe02d52cf7045909cd7581b877f48a27b0eccae0a` |
| `reports/historico/documentacion_pre_integracion/tests/test_decision_policy.py` | Respaldos históricos | 2818 | `$RAVUHHU.py` / `$IAVUHHU.py` | `63bc16c993f871de0302ac37dbdcb4387c31b4809941f48e39b9b4e0e65e1d9f` |
| `reports/historico/documentacion_pre_integracion/tests/test_explainability.py` | Respaldos históricos | 2853 | `$RDVJYWO.py` / `$IDVJYWO.py` | `8164d312108f6d80fe812f350d41cebe630b63a14234438df9c370f4a788a842` |
| `reports/historico/documentacion_pre_integracion/tests/test_final_evaluation.py` | Respaldos históricos | 4405 | `$RQ8F2AD.py` / `$IQ8F2AD.py` | `a00d61b8182c27a0765bd5ee8eca993dd516d1ba63f4c4bdfb75c380d222b5d2` |
| `reports/historico/documentacion_pre_integracion/tests/test_optimization.py` | Respaldos históricos | 4718 | `$RW8UW1I.py` / `$IW8UW1I.py` | `d84c875f314049f77cf4ec4e74b4f5aa98bd16741dee6ab325940487dc340e0d` |
| `reports/historico/documentacion_pre_integracion/tests/test_preparation.py` | Respaldos históricos | 6518 | `$RFQVCIE.py` / `$IFQVCIE.py` | `a8092aaa00c4020630117d1cf2286e8dd9c66cfcbab1cd43c6007e8935a932bc` |
| `reports/historico/documentacion_pre_integracion/tests/test_temporal_bias_v3.py` | Respaldos históricos | 3950 | `$RU0OJQ5.py` / `$IU0OJQ5.py` | `aeff0c9a9d13bf42f77a19ebef19cdcb5b55d3f3ed9e41f82f08dc9e30964326` |
| `reports/historico/documentacion_pre_integracion/tests/test_temporal_protocol.py` | Respaldos históricos | 3146 | `$RQTJTFO.py` / `$IQTJTFO.py` | `c5f80894ad45dcd740528c155cae2009abd6d725db6645446b988af7188b8b77` |
| `reports/historico/protocolo_v1/baseline_predicciones_validacion.csv` | Archivos históricos | 462195 | `$RX614WK.csv` / `$IX614WK.csv` | `b5da5e5e4c979d6ffdb85028ac301a288c2476121204a708e3babb9ccda556d4` |
| `reports/historico/protocolo_v1/baseline_resultados.json` | Archivos históricos | 11506 | `$RPMCXZ0.json` / `$IPMCXZ0.json` | `fe3b57c6c870c67b5d2386a228f10883837a4f07947f2300cee9831ae231306b` |
| `reports/historico/protocolo_v1/baseline_verificacion.json` | Archivos históricos | 1274 | `$RYODJO4.json` / `$IYODJO4.json` | `692e9a843952ce8b3404eaca7520d78528161b41f43406baa167e9ab73c1808d` |
| `reports/historico/protocolo_v1/division_temporal.json` | Archivos históricos | 3081 | `$RU3USS9.json` / `$IU3USS9.json` | `5b33fe8e0f8885d02b412ab2e181620407728e1c771ab3b617f4bf418e13d374` |
| `reports/historico/protocolo_v1/particiones_temporales.csv` | Archivos históricos | 2819332 | `$RJ9BM9J.csv` / `$IJ9BM9J.csv` | `0bbb709048a34d2843f856c2fc9e0d129e8408a3f3d5ed474a86716bf2362a4a` |
| `reports/historico/protocolo_v1/README.md` | Archivos históricos | 729 | `$RBD34Q0.md` / `$IBD34Q0.md` | `fd5cdd32f61d372681be44dcfe143e1018362bc7a9a162504044a34a3311f965` |
| `reports/historico/protocolo_v1/registro_historico.json` | Archivos históricos | 1097 | `$REX3IJ7.json` / `$IEX3IJ7.json` | `bb83cffe58359f9b223630c976ae3e30b8db7ae738adce05440414cfc9fff713` |
| `reports/historico/protocolo_v2/notebooks/baseline.ipynb` | Archivos históricos | 208501 | `$RPLEYO0.ipynb` / `$IPLEYO0.ipynb` | `713855e376b70e2e4428be7b17928279bda9e0a50a8ed9b09909611dc61ad554` |
| `reports/historico/protocolo_v2/notebooks/comparacion_modelos.ipynb` | Archivos históricos | 407695 | `$RLMFM6Z.ipynb` / `$ILMFM6Z.ipynb` | `dd390d56af8eacfb718942b5262e30863e3c96a2a6743c55436610c47f337f23` |
| `reports/historico/protocolo_v2/notebooks/eda.ipynb` | Archivos históricos | 1380339 | `$RVKGGU0.ipynb` / `$IVKGGU0.ipynb` | `795f15aa3ee03b538dffff01cc537f41486034aa9b5c404acf5475f0bade66a3` |
| `reports/historico/protocolo_v2/notebooks/explicabilidad.ipynb` | Archivos históricos | 1054093 | `$RUCW0CP.ipynb` / `$IUCW0CP.ipynb` | `849ba306a3cd7be413abc045403367c34672f4726ce33e4e6ac7d28cd84be557` |
| `reports/historico/protocolo_v2/notebooks/optimizacion.ipynb` | Archivos históricos | 669240 | `$RQFIKQN.ipynb` / `$IQFIKQN.ipynb` | `c55bc6bf16e3cfeb294a0e5018854b2c450de86365dec417bdb65dc086872567` |
| `reports/historico/protocolo_v2/notebooks/preparacion.ipynb` | Archivos históricos | 100153 | `$RWXFI5M.ipynb` / `$IWXFI5M.ipynb` | `64f1de722c79e8b4f3dc954354d000781633289a1f0f84269aed32a720e55fc9` |
| `reports/historico/protocolo_v2/notebooks/protocolo_temporal.ipynb` | Archivos históricos | 158186 | `$R74YPKY.ipynb` / `$I74YPKY.ipynb` | `f0b1ee4d9661012719f8a9455e16d8f9bc721decbbb5c8a0e8c77046bb9432b2` |
| `reports/historico/protocolo_v2/README.md` | Archivos históricos | 25435 | `$RL7UF4X.md` / `$IL7UF4X.md` | `8412590a60144cc4c1913906c903d7e977bf6c43ddaa5fa7bb58270270850cd1` |
| `reports/historico/protocolo_v2/registro_historico.json` | Archivos históricos | 16221 | `$RFROVI5.json` / `$IFROVI5.json` | `44a33c4219de3da9efc015e3120b2fa3954955b50b242c87d942b2d15e130ccc` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_calibracion_validacion.csv` | Archivos históricos | 898 | `$RXY25H7.csv` / `$IXY25H7.csv` | `2e07654ac75b06af6bb12e577ee7e6bf5220084b883dc5385374f03aa223d8da` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_categorias_nuevas_validacion.csv` | Archivos históricos | 281 | `$RGJCB7M.csv` / `$IGJCB7M.csv` | `42187438f5937e1925ccd98533f8362567c2cb7c152ea73dd2533d937bb616b7` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_cierres_hipoteticos.csv` | Archivos históricos | 369 | `$R1BNKET.csv` / `$I1BNKET.csv` | `38ee456e055f58ed447d130f5d9f322e2a351b562204bf743b3ed3fc1034e6a2` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_diagnosticos_train_validacion.csv` | Archivos históricos | 449 | `$RY8FVP5.csv` / `$IY8FVP5.csv` | `8e6ce7e02d191c1c4288cfb944e843bdc7e3ca909cfc14c2e9be7d391b3d23dd` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_distribucion_probabilidades.csv` | Archivos históricos | 409 | `$RQRECLG.csv` / `$IQRECLG.csv` | `b0723c58632f9c6fbe3a6e543fb61d16c395e6114c651386e012ce56eade6759` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_escenarios_coste_relativo.csv` | Archivos históricos | 700 | `$R1NW9SA.csv` / `$I1NW9SA.csv` | `3427414e2e9c2e264a822de5c8220957a9e7e3d8dfeeff722547e7c4027a7164` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_perfiles_categoricos.csv` | Archivos históricos | 4560 | `$RNCZZLO.csv` / `$INCZZLO.csv` | `5c7aada317829f4991daf7e5161aeab9d2f2b777c537524363503b6f52edf178` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_perfiles_seleccion.csv` | Archivos históricos | 609 | `$RYXA06F.csv` / `$IYXA06F.csv` | `8a8c71d93e81a75629f601f3e3d26e32c1cd76bd69d0795d9ccd4917a845079a` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_resultados.json` | Archivos históricos | 40048 | `$REQNOUK.json` / `$IEQNOUK.json` | `60e0ef353c5755e80ddf68e614e6edb3ff52c22d7141606ce72e9128836cdba9` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_umbrales_validacion.csv` | Archivos históricos | 1711 | `$RAHI0G7.csv` / `$IAHI0G7.csv` | `5d25bc5ee3ae843940908f973c6f17bfd15d485774742b220db9ffeae588b3c8` |
| `reports/historico/protocolo_v2/reports/auditoria_4_1_verificacion.json` | Archivos históricos | 980 | `$RJX9LPZ.json` / `$IJX9LPZ.json` | `01b647f5a119f4c2bec692fb85320f5d6105b90c8c36e3beeab1ffc923456f27` |
| `reports/historico/protocolo_v2/reports/baseline_predicciones_validacion.csv` | Archivos históricos | 590391 | `$R95VVUU.csv` / `$I95VVUU.csv` | `b923479cb550961832b51c8166ecfa16d1345292f5650bab3678c02469199bfb` |
| `reports/historico/protocolo_v2/reports/baseline_resultados.json` | Archivos históricos | 12551 | `$RORK72Q.json` / `$IORK72Q.json` | `d821a3d6772f78da8a9d14188c37da0eeac526c583bd98db0f8e29ce816a62a7` |
| `reports/historico/protocolo_v2/reports/baseline_verificacion.json` | Archivos históricos | 3258 | `$RC9OTN6.json` / `$IC9OTN6.json` | `54fca79590344418cd93fdee4b41122b81c0b134f7428f9a289e0987e44bbef6` |
| `reports/historico/protocolo_v2/reports/comparacion_5_metricas.csv` | Archivos históricos | 1033 | `$R3GPL1L.csv` / `$I3GPL1L.csv` | `7bdb41b2bcb925e089062a5d53d30e196f23a0bf424cf02af74e8c8939cc3af6` |
| `reports/historico/protocolo_v2/reports/comparacion_5_predicciones_validacion.csv` | Archivos históricos | 1763048 | `$RCQB3GK.csv` / `$ICQB3GK.csv` | `1f668616d7e39c8e5eb478c5cf175ec5c72c01e9c9fb2889842a2638f1973ae6` |
| `reports/historico/protocolo_v2/reports/comparacion_5_referencia_reproduccion.csv` | Archivos históricos | 1763026 | `$R12LYFB.csv` / `$I12LYFB.csv` | `47c78ded3b64544b028d0c14d6bc99871f83546b3e7e321a8c1a76d6127f21f3` |
| `reports/historico/protocolo_v2/reports/comparacion_5_verificacion.json` | Archivos históricos | 13654 | `$R92NUJP.json` / `$I92NUJP.json` | `65e4b58fc0d9efb9cf9011b07da6b8f53bb397b42f28764ecfa4077f33370ecd` |
| `reports/historico/protocolo_v2/reports/division_temporal.json` | Archivos históricos | 7219 | `$RVEIHKB.json` / `$IVEIHKB.json` | `506b92d7d9f2adcaddf5192ab50a5b2df9674b9516744a48ae67664f330417d1` |
| `reports/historico/protocolo_v2/reports/eda_auditoria_leakage.csv` | Archivos históricos | 1923 | `$RBFL254.csv` / `$IBFL254.csv` | `6d891386278cd6b0b2330eefba635ea7bc9d8df1c83daf811bc723c4a2b9c9ba` |
| `reports/historico/protocolo_v2/reports/eda_resumen.json` | Archivos históricos | 24109 | `$RTSMQ4R.json` / `$ITSMQ4R.json` | `176d63df132d7279c208ee011cfe3fbc9e8d89a1aa6cd29e48b8e236dcfc04b3` |
| `reports/historico/protocolo_v2/reports/eda_verificacion.json` | Archivos históricos | 1068 | `$RGDTCHK.json` / `$IGDTCHK.json` | `3ce28cf4858303992e24dbcb39b2c7e4e14bcf3abb8cf9b923593b70fd2289c3` |
| `reports/historico/protocolo_v2/reports/estado_protocolo.json` | Archivos históricos | 452 | `$RZ5PN8K.json` / `$IZ5PN8K.json` | `033c1147e1f2a459ce8ceda120564cfe63e65456ea986fdf8bd15db33575395a` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_calibracion_bins.csv` | Archivos históricos | 2143 | `$RBRKTEZ.csv` / `$IBRKTEZ.csv` | `8946c9a5ad6ca07e29163981ce05ecc413a8d1d98e6befc3077413c7807ab606` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_casos.csv` | Archivos históricos | 671 | `$R8FX3YI.csv` / `$I8FX3YI.csv` | `2638d3cfbcbbbcb814b61040bc3316b57d1fd5f58ba49e9244212a11185f5b1c` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_contribuciones_locales.csv` | Archivos históricos | 2480 | `$RU1BYDS.csv` / `$IU1BYDS.csv` | `eacd7823b2b4cc4aa35ef468677dd2d9cad915f33f2e91799ba89cd4c7912cdd` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_dependencia_perfil.csv` | Archivos históricos | 6309 | `$RIJCO5V.csv` / `$IIJCO5V.csv` | `51fe289fd0af759a25c7c9e8b47e6e9c4d05074bb15098e9364a469314234229` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_gain_originales.csv` | Archivos históricos | 728 | `$RFO1QJ6.csv` / `$IFO1QJ6.csv` | `a931f7fd23da33f085f27f47ce7029b11372eb706a2dfc527b5580d61477dd75` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_gain_transformadas.csv` | Archivos históricos | 12385 | `$RU4XJCF.csv` / `$IU4XJCF.csv` | `5c4d4aa720b2b904bd5e275166cf6cfa4bfc29ba74fe718e475b36143f605cff` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_mapa_caracteristicas.csv` | Archivos históricos | 8222 | `$RTPOGVE.csv` / `$ITPOGVE.csv` | `55d9a76211e6326f790db6e6b4e7221a54182adc26d337f709f50123656f3739` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_muestra_ids.csv` | Archivos históricos | 21366 | `$RAQQBDW.csv` / `$IAQQBDW.csv` | `744be32ace838f73ded77a68500d4bcbcfa9fb4560e33a2f706811a8f907fa0a` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_muestra_perfil.csv` | Archivos históricos | 770 | `$RP4S7LN.csv` / `$IP4S7LN.csv` | `f36fca9397b39715072a63c74fe7ae31469863580e43f7290ae0dd68fedef8f6` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_predicciones_validacion.csv` | Archivos históricos | 361081 | `$RRY3X9W.csv` / `$IRY3X9W.csv` | `82ea3ef821b6d3d100c43b6408611402c6ba86968f2f50d3a02fe4f34dbe5364` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_reproduccion.json` | Archivos históricos | 1879 | `$R87LUXC.json` / `$I87LUXC.json` | `900ecae24e5879cd32d745dd38a3ee01836d87d3506d0b1935e53aa2f78caa74` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_segmentos.csv` | Archivos históricos | 10826 | `$R5NEFBK.csv` / `$I5NEFBK.csv` | `337e7819b41c133e973fbc334cd807a6a3b055783b574047c8fd01a0f1e7298e` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_shap.npz` | Archivos históricos | 869547 | `$RLO0DD0.npz` / `$ILO0DD0.npz` | `018f96920bee52a617df27398ca2d18286d8369e213fac0f433f1f027da5a9e6` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_shap_global.csv` | Archivos históricos | 718 | `$RTMHT23.csv` / `$ITMHT23.csv` | `70859d6a3b7e583d0dabaecbfb465b221d3672419fb8584b0eaa24dadea6f773` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_shap_transformadas.csv` | Archivos históricos | 9707 | `$RIPE69Z.csv` / `$IIPE69Z.csv` | `0867a3d1c4e26c52eee457092bf6cf15795440ffb312f44ab87e929f5fd16026` |
| `reports/historico/protocolo_v2/reports/explicabilidad_7_verificacion.json` | Archivos históricos | 18850 | `$RUQZNNJ.json` / `$IUQZNNJ.json` | `b67698ad4b3e2a8eda7732be2c943079142edad41806c451a9813e12b48bf80d` |
| `reports/historico/protocolo_v2/reports/fase_1_inspeccion.md` | Archivos históricos | 8955 | `$RMGW4IW.md` / `$IMGW4IW.md` | `bfd6f6d58eb61411d46417fd6d916db9e4b5e9a36b22edf02e31501805ac8df7` |
| `reports/historico/protocolo_v2/reports/fase_2_eda.md` | Archivos históricos | 10171 | `$RK4W5BH.md` / `$IK4W5BH.md` | `b2b0d5ea1a7bcbc072c69e8b9ad8537b9e99c6be45a7bfcc98c181fa37b21207` |
| `reports/historico/protocolo_v2/reports/fase_3_preparacion.md` | Archivos históricos | 16852 | `$R3TK3RL.md` / `$I3TK3RL.md` | `8ee57b577f10d4c2e9b4e26d4a651035c8f351eb0ce8e9e0759d79a7c216d804` |
| `reports/historico/protocolo_v2/reports/fase_4_1_auditoria.md` | Archivos históricos | 20746 | `$R4JFTNY.md` / `$I4JFTNY.md` | `5feaf824ea787b3622117a7aa5817e690bb9f6b452b730165ca348f5fbb068b1` |
| `reports/historico/protocolo_v2/reports/fase_4_2_protocolo_temporal.md` | Archivos históricos | 15821 | `$RC36AVR.md` / `$IC36AVR.md` | `3541d2858dfcfa76ef3ba562463c2046ea29855bee902786c7a5d36ab8e6cc4d` |
| `reports/historico/protocolo_v2/reports/fase_4_baseline.md` | Archivos históricos | 12224 | `$RPLX3UT.md` / `$IPLX3UT.md` | `ac790bd6c98bf6b24b7998899a430eb3a8b3f5fb20e63c7780cb446608531342` |
| `reports/historico/protocolo_v2/reports/fase_5_comparacion_modelos.md` | Archivos históricos | 10506 | `$RBFH35I.md` / `$IBFH35I.md` | `545c644e1e15dc5323a9f999405059b68f21628fcde755eadbab4bdc70459cb6` |
| `reports/historico/protocolo_v2/reports/fase_6_optimizacion.md` | Archivos históricos | 25364 | `$R6O6TXH.md` / `$I6O6TXH.md` | `67a852b46d8b7f95b8ff06146c959273006685ab0398319951b2f83021e0adad` |
| `reports/historico/protocolo_v2/reports/fase_7_explicabilidad.md` | Archivos históricos | 30903 | `$RO4X63U.md` / `$IO4X63U.md` | `f77d101a1ad5e05ae1fa065c096338413ca6bddbcfa902cc147247cd1fd3f1c1` |
| `reports/historico/protocolo_v2/reports/figures/01_ausencias.png` | Archivos históricos | 50619 | `$RV97NDN.png` / `$IV97NDN.png` | `7944a583b51df877425cbed85c1b79386781aad8332ec2943ce9cdf9efb79b49` |
| `reports/historico/protocolo_v2/reports/figures/02_objetivo_hoteles.png` | Archivos históricos | 48778 | `$RMUEVWQ.png` / `$IMUEVWQ.png` | `88e5aded3b970d1a3155d8b424f39af12c9f9fa993dcc7606ddbe8dfe20c080e` |
| `reports/historico/protocolo_v2/reports/figures/03_antelacion_adr.png` | Archivos históricos | 109976 | `$R0H7FH4.png` / `$I0H7FH4.png` | `8fa26cadee6b044d6aaa13458785dbb4c6faa791b756e81cd7f3a981f299e3b4` |
| `reports/historico/protocolo_v2/reports/figures/04_tasas_antelacion.png` | Archivos históricos | 52586 | `$RR9M7TG.png` / `$IR9M7TG.png` | `d8d31647243caae409a239fab56b82519690e4ba695e01759fc3bcdf34aea60d` |
| `reports/historico/protocolo_v2/reports/figures/05_customer_type.png` | Archivos históricos | 44814 | `$RU68AX0.png` / `$IU68AX0.png` | `95f66ebbb0559255e5305d5217f5d832290b6fc7ccabe0b44624e516cbd8a391` |
| `reports/historico/protocolo_v2/reports/figures/05_deposit_type.png` | Archivos históricos | 42167 | `$RM7CXEF.png` / `$IM7CXEF.png` | `8a290ceb7e7d4c739600e386571ca6e1370f54a32d6108dc4d886d4fa871c588` |
| `reports/historico/protocolo_v2/reports/figures/05_distribution_channel.png` | Archivos históricos | 47720 | `$RZK7CKL.png` / `$IZK7CKL.png` | `530b4d08197b0c12af3f5ed8e1ba53953ea18379cad706eaa227fbdd79b7e01d` |
| `reports/historico/protocolo_v2/reports/figures/05_market_segment.png` | Archivos históricos | 64465 | `$RVDYLR8.png` / `$IVDYLR8.png` | `e7d21d4a0233825ca8a88df1582a224059e32adc9fb9d227b49c94044b71d2a7` |
| `reports/historico/protocolo_v2/reports/figures/06_historial_solicitudes.png` | Archivos históricos | 48660 | `$RIU24R5.png` / `$IIU24R5.png` | `d8c169fabe2eb94356eafb98d145495b43cdc27b721a96a51648244d958b9270` |
| `reports/historico/protocolo_v2/reports/figures/07_estancia_huespedes.png` | Archivos históricos | 39848 | `$RZ45P4M.png` / `$IZ45P4M.png` | `de1450e08043d9cb1f95020548fff1b8caa26e9d22a44e3a46242792ff224c39` |
| `reports/historico/protocolo_v2/reports/figures/08_evolucion_temporal.png` | Archivos históricos | 223661 | `$RK443AK.png` / `$IK443AK.png` | `fff32f5fd46b61c03d5e5e997523f552e9fa3d34dd8820d934fcadd47e6a5902` |
| `reports/historico/protocolo_v2/reports/figures/09_estacionalidad.png` | Archivos históricos | 111377 | `$RHPZY60.png` / `$IHPZY60.png` | `b2ed8b53e7d3b1a0a83ca7e217a592528f9ee790370730c6db1cb5cf65d1eeaa` |
| `reports/historico/protocolo_v2/reports/figures/10_correlaciones.png` | Archivos históricos | 173447 | `$R67RKF2.png` / `$I67RKF2.png` | `fc88d822d224c090e8fb12ae5c583a231cf78e389a662edc2a6a4be30e24be5b` |
| `reports/historico/protocolo_v2/reports/figures/auditoria_4_1_01_sesgo_antelacion.png` | Archivos históricos | 106127 | `$RVPOLGU.png` / `$IVPOLGU.png` | `0cf3df9531000c4a119b49f9af26c5a6cb42db96d3ed38d55f2d1d14737db5f9` |
| `reports/historico/protocolo_v2/reports/figures/auditoria_4_1_02_distribucion_probabilidades.png` | Archivos históricos | 60514 | `$RKOZ1K5.png` / `$IKOZ1K5.png` | `b9e5d2193d4548cfc26acf491225d0e021cf6a21412c77be39044ec9e8b00f26` |
| `reports/historico/protocolo_v2/reports/figures/auditoria_4_1_03_calibracion_validacion.png` | Archivos históricos | 96161 | `$RHB175S.png` / `$IHB175S.png` | `019756a7b7283e8ea809da18add09c72d7b56e39cd2fe25bd8727955cbed52bb` |
| `reports/historico/protocolo_v2/reports/figures/auditoria_4_1_04_precision_recall_umbrales.png` | Archivos históricos | 126399 | `$RD4X9RC.png` / `$ID4X9RC.png` | `594179bd17315fd4094445ba631cb003a551a10b301db8863c37833c3fbc8b4f` |
| `reports/historico/protocolo_v2/reports/figures/baseline_01_particiones.png` | Archivos históricos | 54726 | `$R1OJ060.png` / `$I1OJ060.png` | `ff959839d025cd7002994f409aa99f41a239fd30f7faa3007eb6cab9099f4b96` |
| `reports/historico/protocolo_v2/reports/figures/baseline_02_confusion_validacion.png` | Archivos históricos | 54157 | `$RRRJ26U.png` / `$IRRJ26U.png` | `2983f7af1fad9dc64bc164996fb45902134d95836ce822e35e94886dd4d20214` |
| `reports/historico/protocolo_v2/reports/figures/baseline_03_roc_validacion.png` | Archivos históricos | 62870 | `$RQ3VF12.png` / `$IQ3VF12.png` | `e73746da2350618b27f22a30b9a2c440041a9b3f7f07f980068fc3dc0a645a03` |
| `reports/historico/protocolo_v2/reports/figures/comparacion_5_curvas.png` | Archivos históricos | 168325 | `$RTZXR7X.png` / `$ITZXR7X.png` | `611bcff289cffb8cbd9353579dc5be61ecd9ad272bf154eabf5b79b79146661a` |
| `reports/historico/protocolo_v2/reports/figures/comparacion_5_matrices.png` | Archivos históricos | 77181 | `$RVTDB72.png` / `$IVTDB72.png` | `51de0dee6f74d1be742c965b9a8fd2b5214965920fdc066914ac55f771ef2a3f` |
| `reports/historico/protocolo_v2/reports/figures/comparacion_5_metricas.png` | Archivos históricos | 49663 | `$R0G0T7I.png` / `$I0G0T7I.png` | `5aa722f8f3d0a45dba27829111af5351dac369f756d8c81cadd8ce81644bbf86` |
| `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_calibracion.png` | Archivos históricos | 143007 | `$RR9MUMX.png` / `$IR9MUMX.png` | `fb6254fae92e7dc84b0280c3b5aa96c4ba0c03a867cb3a4e1f633ba801381d4f` |
| `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_dependencias.png` | Archivos históricos | 148958 | `$R0XS4E6.png` / `$I0XS4E6.png` | `4584db4d82978cb25230455baa299b074b23f476ec29be0d5fbbf79d784a5425` |
| `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_errores.png` | Archivos históricos | 70172 | `$RYLSZG6.png` / `$IYLSZG6.png` | `634260d6324e6921443451395efe7eea817fc2778ed59d4758eef81b46e41ad8` |
| `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_importancias.png` | Archivos históricos | 72217 | `$RZUKRBJ.png` / `$IZUKRBJ.png` | `c9d10dc2030c06c869bdfd7ef24521ce96d4f3ad33899f22378fe4c01acd8ff2` |
| `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_locales.png` | Archivos históricos | 130320 | `$RNGI3S3.png` / `$INGI3S3.png` | `6ee6ea9bc2e163c4ddb39824f82a748f8a1badf04e7263d99ced2b7bb8a4a24c` |
| `reports/historico/protocolo_v2/reports/figures/explicabilidad_7_shap_resumen.png` | Archivos históricos | 166732 | `$R3FU3CR.png` / `$I3FU3CR.png` | `5ad04ac899fc635639e5a442d3e8fba8c551345355918d3aecd1992adcedd721` |
| `reports/historico/protocolo_v2/reports/figures/optimizacion_6_estabilidad.png` | Archivos históricos | 86632 | `$RKUKAII.png` / `$IKUKAII.png` | `3a2e917b402cf216b852bf3598cc54871a8716d0800fdc69e5c20be46a7ab363` |
| `reports/historico/protocolo_v2/reports/figures/optimizacion_6_pr_calibracion.png` | Archivos históricos | 175808 | `$RJ18KSD.png` / `$IJ18KSD.png` | `a88fcfac9fd35ffc8561a51e6f6b42a662e3e6dbed547132ba7948fd58eb832a` |
| `reports/historico/protocolo_v2/reports/figures/optimizacion_6_umbrales.png` | Archivos históricos | 191620 | `$R5DN74S.png` / `$I5DN74S.png` | `3e512c7fcf58fc7b88b092ea18bf63ba9d5343fc618568a1f149021441217432` |
| `reports/historico/protocolo_v2/reports/figures/protocolo_4_2_confusion_validacion.png` | Archivos históricos | 50793 | `$RCXGL32.png` / `$ICXGL32.png` | `a2bc12484adce21eaa91e5a6a1b3fa005b7853df44b1e4f91b4d702301b4b5ab` |
| `reports/historico/protocolo_v2/reports/figures/protocolo_4_2_reincorporacion.png` | Archivos históricos | 31685 | `$R1O7FT6.png` / `$I1O7FT6.png` | `d94df3e0995079b5895f1d2a3f9464128ff9e1f8d30216d5d7b1ad8e4a30ad44` |
| `reports/historico/protocolo_v2/reports/inspeccion_dataset.json` | Archivos históricos | 1923 | `$RBCE1L1.json` / `$IBCE1L1.json` | `f89c6b23e95af0912365bd2f2e2d0b29729cc75ead1bddeb5f9f0a8b08aba536` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_busqueda.csv` | Archivos históricos | 9197 | `$RNBV348.csv` / `$INBV348.csv` | `0200d393637fee2924cf79351318b2019aff2077f44f337f24ac12e641a04fad` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_calibracion.csv` | Archivos históricos | 659 | `$REYDRUQ.csv` / `$IEYDRUQ.csv` | `510ab20626192e8a12fe8ff37a479c3d62661514ba9ae79f1b60328cc31f04f1` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_calibracion_bins.csv` | Archivos históricos | 3544 | `$RP3OC7L.csv` / `$IP3OC7L.csv` | `20aec08d33019233733f218f0ebb977d227563a8af80629e62e33cbf0433358b` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_escenarios.csv` | Archivos históricos | 20127 | `$R69VRYF.csv` / `$I69VRYF.csv` | `7fd47c800397941b127c6ca4411a96dcf4d705ebdab48810bbd639e9fc13344e` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_estabilidad_mensual.csv` | Archivos históricos | 2650 | `$RBPWRW8.csv` / `$IBPWRW8.csv` | `baed84efac99954c7551030aaae2ff2c3cd02c65257f45013b950678cdfc95ef` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_folds.csv` | Archivos históricos | 935 | `$R6TNJ77.csv` / `$I6TNJ77.csv` | `3c0ee5735f0cd453ae95fd75dead66f65cf100b822bd653c5d7be2fed8e1a135` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_ids_folds.csv` | Archivos históricos | 1832872 | `$R2AM836.csv` / `$I2AM836.csv` | `9f246d9e36b75ca29ff9f642aa2a5a6590ed4b5b8b1e0092ff45c8813fdfa719` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_metricas.csv` | Archivos históricos | 1147 | `$R0943V6.csv` / `$I0943V6.csv` | `f81df0106cf7fdb4c5d169c399c8aca31cee67a234f2d451fb4d1927cc06998b` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_plan.json` | Archivos históricos | 2626 | `$RZYYIOX.json` / `$IZYYIOX.json` | `4cbd6937ea9ff49e343fadfefbe3c5f1bc83fa97f52299897586dc007f9a1ac3` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_predicciones_validacion.csv` | Archivos históricos | 1597585 | `$RP46KKB.csv` / `$IP46KKB.csv` | `b44d29d914cca3320cffdc6e785e12708e89da222e3aab3ba5efcc8bda2ea518` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_seleccion_prevalidacion.json` | Archivos históricos | 7554 | `$R48Y32S.json` / `$I48Y32S.json` | `58261bbe71e9e8cf8578d1942b6c3ee9d139c8fb658b56e38cc93a555b6033d5` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_umbrales.csv` | Archivos históricos | 5484 | `$R4HVREG.csv` / `$I4HVREG.csv` | `d09536788c45d43a6af6d4daba8ab6b11f6f4ee516ceb3a5ff44ebd35a4bafde` |
| `reports/historico/protocolo_v2/reports/optimizacion_6_verificacion.json` | Archivos históricos | 25745 | `$RMGASM9.json` / `$IMGASM9.json` | `1cbbaea9a8e12421178d5da4927605e87f5c410cde6689364aeef3d63c94d100` |
| `reports/historico/protocolo_v2/reports/particiones_temporales.csv` | Archivos históricos | 2721112 | `$RZCU2RC.csv` / `$IZCU2RC.csv` | `cedadccd48504c1a3bcb97efbbbb3983c4b9b3ede5f39bc8e5a5ca7d2c261778` |
| `reports/historico/protocolo_v2/reports/preparacion_auditoria_variables.csv` | Archivos históricos | 5249 | `$RYHMFU0.csv` / `$IYHMFU0.csv` | `aa62e4e62bce731972df2deb7105f283b0d0c3dbd7cbd7019246803e2cb976c6` |
| `reports/historico/protocolo_v2/reports/preparacion_resumen.json` | Archivos históricos | 2363 | `$R144W44.json` / `$I144W44.json` | `d18aa575805e54598fa5bb052836c61dc45977ef1425d23e899cdd407583dd29` |
| `reports/historico/protocolo_v2/reports/preparacion_verificacion.json` | Archivos históricos | 1159 | `$RWOFX6T.json` / `$IWOFX6T.json` | `c6c89c60777cea68ac92899dd66528c56c8a012cfcd417dd444ff895ce1639a3` |
| `reports/historico/protocolo_v2/reports/protocolo_4_2_apartadas_por_mes.csv` | Archivos históricos | 1029 | `$RFGR7LU.csv` / `$IFGR7LU.csv` | `6277f8d2a66785752ffd0dd06b933e20cde412b9aca5f25d431119b2bc0cf9d6` |
| `reports/historico/protocolo_v2/reports/protocolo_4_2_comparacion_descriptiva.csv` | Archivos históricos | 484 | `$R0JLZ61.csv` / `$I0JLZ61.csv` | `dcb890a0f942d8f20f302e4f66f42b1b3847cc8bcafd3942f1bf83b64a9d8d7d` |
| `reports/historico/protocolo_v2/reports/protocolo_4_2_config.json` | Archivos históricos | 806 | `$RV6UQGG.json` / `$IV6UQGG.json` | `61366d7cd73dc3fb73805adee2380a7c294e7dfc40f7f0c01e68fa44b774c254` |
| `reports/historico/protocolo_v2/reports/protocolo_4_2_fuentes.md` | Archivos históricos | 1071 | `$RFM9P3H.md` / `$IFM9P3H.md` | `6e01d970fa641dfdf8fdf867790f22c7dd611eeb3ee130d2c62c2179c794ffbd` |
| `reports/historico/protocolo_v2/reports/protocolo_4_2_particiones.csv` | Archivos históricos | 836 | `$RUM3KCR.csv` / `$IUM3KCR.csv` | `3e7f15fb11d59494016bb8a7b097b91b18858c7e1ef0648057e4ae7dd0c20edd` |
| `reports/historico/protocolo_v2/reports/protocolo_4_2_reincorporadas_perfil.csv` | Archivos históricos | 130 | `$REOUKXV.csv` / `$IEOUKXV.csv` | `e14dc98b35863402df7c484f0845f48cf1865cc9fc223e60d8c031931048a416` |
| `reports/historico/protocolo_v2/reports/protocolo_4_2_transicion.csv` | Archivos históricos | 292 | `$RWR0T15.csv` / `$IWR0T15.csv` | `c1ce40e5710b31c88d089d5f91ed0f17f05a02b5a19f728858b23fc1f4abc0f1` |
| `reports/historico/protocolo_v2/reports/protocolo_4_2_verificacion.json` | Archivos históricos | 3258 | `$RL4D4AY.json` / `$IL4D4AY.json` | `54fca79590344418cd93fdee4b41122b81c0b134f7428f9a289e0987e44bbef6` |
| `reports/historico/protocolo_v2/reports/verificacion_referencias.json` | Archivos históricos | 19079 | `$RXNSI50.json` / `$IXNSI50.json` | `0c0ed2c81fa4d49f314121dcea04094efc52acdac7df21791e9400c799f5aff1` |
| `reports/historico/protocolo_v2/requirements.txt` | Archivos históricos | 284 | `$RXMWEFV.txt` / `$IXMWEFV.txt` | `e6bb48022891fd0e2084341f000d3e2b2db605e3b2470619a30aa78e44158040` |
| `reports/historico/protocolo_v2/src/__init__.py` | Archivos históricos | 69 | `$RK3NAAR.py` / `$IK3NAAR.py` | `85312e2cd5f7538b0bbe0521faf14f9a28eee7195b50f3c5986d6d5d76008515` |
| `reports/historico/protocolo_v2/src/audit_baseline.py` | Archivos históricos | 42690 | `$RXYPZBC.py` / `$IXYPZBC.py` | `ebfc98634ff16939c821d2269a82e1723d1271bc128684196ac20428c564ea25` |
| `reports/historico/protocolo_v2/src/baseline.py` | Archivos históricos | 23510 | `$RCX0WVB.py` / `$ICX0WVB.py` | `508694e2edc55d9cdf83e7fdae191a945c0ef59f5cae83dec0f03ed685783f42` |
| `reports/historico/protocolo_v2/src/cleaning.py` | Archivos históricos | 2274 | `$R4IBARL.py` / `$I4IBARL.py` | `52793ede516563751221b92be18ae81850f0fc4802d9b6f4dff27ac15bd49b89` |
| `reports/historico/protocolo_v2/src/comparison.py` | Archivos históricos | 20647 | `$RLRK6PS.py` / `$ILRK6PS.py` | `72d58e7add366e5e509fc6a821a6685eaf1f1891e295c55cc29f8ccb93f992b1` |
| `reports/historico/protocolo_v2/src/explainability.py` | Archivos históricos | 42293 | `$RE3END6.py` / `$IE3END6.py` | `b41be3e76e0807190d67d8228884e7ba09c7794f57f6a5e94176724f501be3b7` |
| `reports/historico/protocolo_v2/src/features.py` | Archivos históricos | 6782 | `$RRPJC43.py` / `$IRPJC43.py` | `c150d2ef7a93d2aba990a926cda1eca746e48011764e4dab8ad60ed3cc620213` |
| `reports/historico/protocolo_v2/src/inspection.py` | Archivos históricos | 1379 | `$R5II71H.py` / `$I5II71H.py` | `5b41fd7480ddc21989fb65b6c2c8190fc14f9f8ea100357d98ce85c3d7aebedc` |
| `reports/historico/protocolo_v2/src/optimization.py` | Archivos históricos | 47563 | `$RW8TASX.py` / `$IW8TASX.py` | `6e93ae31d0ef7d4f2da731087f08f2835804885b936bda815161abd53ff1b0c7` |
| `reports/historico/protocolo_v2/src/preparation.py` | Archivos históricos | 4345 | `$RK75RGT.py` / `$IK75RGT.py` | `403f6f45167d319a2841b1843546dda2cfa2f47bc1e662e1ebcd1b4f04210eaa` |
| `reports/historico/protocolo_v2/src/preprocessing.py` | Archivos históricos | 1082 | `$RS2HK5X.py` / `$IS2HK5X.py` | `2877c53e7cefd7d673b4b46500df54ad888c1242af0a783ddd692f45532bae67` |
| `reports/historico/protocolo_v2/src/run_notebook.py` | Archivos históricos | 2271 | `$RUW2P1G.py` / `$IUW2P1G.py` | `d1c74e9d1ca11a2b00d34a8cdc3b193e23106be7c0200a0659212df6ddcaa6cb` |
| `reports/historico/protocolo_v2/src/splitting.py` | Archivos históricos | 6895 | `$RRDA7LO.py` / `$IRDA7LO.py` | `f15a925b930c873089a83aff15f79098935aa8875f95a06d9e89498bacbc3785` |
| `reports/historico/protocolo_v2/src/temporal_protocol.py` | Archivos históricos | 31334 | `$RL81QJ4.py` / `$IL81QJ4.py` | `87b7ab9682515524d8b22416fcf67740d293b0cb32cd5a82b2ad2b17fafd98c3` |
| `reports/historico/protocolo_v2/tests/test_audit_baseline.py` | Archivos históricos | 1881 | `$R88RUZT.py` / `$I88RUZT.py` | `f53cea7a11c44873559f78b36d5d9aaec4f2d3066df32141562af8f85ce67263` |
| `reports/historico/protocolo_v2/tests/test_baseline.py` | Archivos históricos | 2529 | `$R0TZ213.py` / `$I0TZ213.py` | `b7d52d20481792e7fdfc33156fc9f944f886b40a297882cceffa6bd48e894b95` |
| `reports/historico/protocolo_v2/tests/test_comparison.py` | Archivos históricos | 2002 | `$RZQEXL7.py` / `$IZQEXL7.py` | `a779c9df5e7e836628b593dbe02d52cf7045909cd7581b877f48a27b0eccae0a` |
| `reports/historico/protocolo_v2/tests/test_explainability.py` | Archivos históricos | 2853 | `$RS08C0E.py` / `$IS08C0E.py` | `8164d312108f6d80fe812f350d41cebe630b63a14234438df9c370f4a788a842` |
| `reports/historico/protocolo_v2/tests/test_optimization.py` | Archivos históricos | 4718 | `$RSE9IXP.py` / `$ISE9IXP.py` | `d84c875f314049f77cf4ec4e74b4f5aa98bd16741dee6ab325940487dc340e0d` |
| `reports/historico/protocolo_v2/tests/test_preparation.py` | Archivos históricos | 6518 | `$RUEGHG1.py` / `$IUEGHG1.py` | `a8092aaa00c4020630117d1cf2286e8dd9c66cfcbab1cd43c6007e8935a932bc` |
| `reports/historico/protocolo_v2/tests/test_temporal_protocol.py` | Archivos históricos | 3146 | `$RTD4TBK.py` / `$ITD4TBK.py` | `c5f80894ad45dcd740528c155cae2009abd6d725db6645446b988af7188b8b77` |
| `reports/historico/README_antes_fase10.md` | Archivos históricos | 33776 | `$R3ELCWC.md` / `$I3ELCWC.md` | `002ad5abed7921f3f1b2c2f7cfd5917857ea51d6f458b951d1bd2209e521995b` |
| `reports/inspeccion_dataset.json` | Informes y evidencias tabulares | 1923 | `$R8X0HJW.json` / `$I8X0HJW.json` | `f89c6b23e95af0912365bd2f2e2d0b29729cc75ead1bddeb5f9f0a8b08aba536` |
| `reports/optimizacion_6_busqueda.csv` | Informes y evidencias tabulares | 9197 | `$RA9FLDK.csv` / `$IA9FLDK.csv` | `0200d393637fee2924cf79351318b2019aff2077f44f337f24ac12e641a04fad` |
| `reports/optimizacion_6_calibracion.csv` | Informes y evidencias tabulares | 659 | `$RKGT40C.csv` / `$IKGT40C.csv` | `510ab20626192e8a12fe8ff37a479c3d62661514ba9ae79f1b60328cc31f04f1` |
| `reports/optimizacion_6_calibracion_bins.csv` | Informes y evidencias tabulares | 3544 | `$R1EXMN7.csv` / `$I1EXMN7.csv` | `20aec08d33019233733f218f0ebb977d227563a8af80629e62e33cbf0433358b` |
| `reports/optimizacion_6_escenarios.csv` | Informes y evidencias tabulares | 20127 | `$RUK68OA.csv` / `$IUK68OA.csv` | `7fd47c800397941b127c6ca4411a96dcf4d705ebdab48810bbd639e9fc13344e` |
| `reports/optimizacion_6_estabilidad_mensual.csv` | Informes y evidencias tabulares | 2650 | `$RR7AAP2.csv` / `$IR7AAP2.csv` | `baed84efac99954c7551030aaae2ff2c3cd02c65257f45013b950678cdfc95ef` |
| `reports/optimizacion_6_folds.csv` | Informes y evidencias tabulares | 935 | `$R1GZ75N.csv` / `$I1GZ75N.csv` | `3c0ee5735f0cd453ae95fd75dead66f65cf100b822bd653c5d7be2fed8e1a135` |
| `reports/optimizacion_6_ids_folds.csv` | Informes y evidencias tabulares | 1832872 | `$RGNFHK0.csv` / `$IGNFHK0.csv` | `9f246d9e36b75ca29ff9f642aa2a5a6590ed4b5b8b1e0092ff45c8813fdfa719` |
| `reports/optimizacion_6_metricas.csv` | Informes y evidencias tabulares | 1147 | `$RI9ZTLF.csv` / `$II9ZTLF.csv` | `f81df0106cf7fdb4c5d169c399c8aca31cee67a234f2d451fb4d1927cc06998b` |
| `reports/optimizacion_6_plan.json` | Informes y evidencias tabulares | 2626 | `$RF3L7FW.json` / `$IF3L7FW.json` | `4cbd6937ea9ff49e343fadfefbe3c5f1bc83fa97f52299897586dc007f9a1ac3` |
| `reports/optimizacion_6_predicciones_validacion.csv` | Predicciones y copias de referencia | 1597585 | `$RVQVEMI.csv` / `$IVQVEMI.csv` | `b44d29d914cca3320cffdc6e785e12708e89da222e3aab3ba5efcc8bda2ea518` |
| `reports/optimizacion_6_seleccion_prevalidacion.json` | Informes y evidencias tabulares | 7554 | `$RWOU37K.json` / `$IWOU37K.json` | `58261bbe71e9e8cf8578d1942b6c3ee9d139c8fb658b56e38cc93a555b6033d5` |
| `reports/optimizacion_6_umbrales.csv` | Informes y evidencias tabulares | 5484 | `$R570NQW.csv` / `$I570NQW.csv` | `d09536788c45d43a6af6d4daba8ab6b11f6f4ee516ceb3a5ff44ebd35a4bafde` |
| `reports/optimizacion_6_verificacion.json` | Informes y evidencias tabulares | 25745 | `$REA5MQT.json` / `$IEA5MQT.json` | `1cbbaea9a8e12421178d5da4927605e87f5c410cde6689364aeef3d63c94d100` |
| `reports/particiones_temporales.csv` | Informes y evidencias tabulares | 2754528 | `$RJC7395.csv` / `$IJC7395.csv` | `cb6bc1be91d3e71d0d45bb27428d17656170d9fa231a2e13afe284871f309f73` |
| `reports/preparacion_auditoria_variables.csv` | Informes y evidencias tabulares | 5249 | `$RSPBTRT.csv` / `$ISPBTRT.csv` | `aa62e4e62bce731972df2deb7105f283b0d0c3dbd7cbd7019246803e2cb976c6` |
| `reports/preparacion_resumen.json` | Informes y evidencias tabulares | 2363 | `$R5PCGLF.json` / `$I5PCGLF.json` | `d18aa575805e54598fa5bb052836c61dc45977ef1425d23e899cdd407583dd29` |
| `reports/preparacion_verificacion.json` | Informes y evidencias tabulares | 1159 | `$RRCKWUL.json` / `$IRCKWUL.json` | `c6c89c60777cea68ac92899dd66528c56c8a012cfcd417dd444ff895ce1639a3` |
| `reports/protocolo_4_2_apartadas_por_mes.csv` | Informes y evidencias tabulares | 1029 | `$RCPOFL0.csv` / `$ICPOFL0.csv` | `6277f8d2a66785752ffd0dd06b933e20cde412b9aca5f25d431119b2bc0cf9d6` |
| `reports/protocolo_4_2_comparacion_descriptiva.csv` | Informes y evidencias tabulares | 484 | `$R8KOK94.csv` / `$I8KOK94.csv` | `dcb890a0f942d8f20f302e4f66f42b1b3847cc8bcafd3942f1bf83b64a9d8d7d` |
| `reports/protocolo_4_2_config.json` | Informes y evidencias tabulares | 806 | `$RSAUS2B.json` / `$ISAUS2B.json` | `61366d7cd73dc3fb73805adee2380a7c294e7dfc40f7f0c01e68fa44b774c254` |
| `reports/protocolo_4_2_fuentes.md` | Documentación y configuración | 1071 | `$RLNJF4A.md` / `$ILNJF4A.md` | `6e01d970fa641dfdf8fdf867790f22c7dd611eeb3ee130d2c62c2179c794ffbd` |
| `reports/protocolo_4_2_particiones.csv` | Informes y evidencias tabulares | 836 | `$R17XSA7.csv` / `$I17XSA7.csv` | `3e7f15fb11d59494016bb8a7b097b91b18858c7e1ef0648057e4ae7dd0c20edd` |
| `reports/protocolo_4_2_reincorporadas_perfil.csv` | Informes y evidencias tabulares | 130 | `$R951PA4.csv` / `$I951PA4.csv` | `e14dc98b35863402df7c484f0845f48cf1865cc9fc223e60d8c031931048a416` |
| `reports/protocolo_4_2_transicion.csv` | Informes y evidencias tabulares | 292 | `$REFCL3U.csv` / `$IEFCL3U.csv` | `c1ce40e5710b31c88d089d5f91ed0f17f05a02b5a19f728858b23fc1f4abc0f1` |
| `reports/protocolo_4_2_verificacion.json` | Informes y evidencias tabulares | 3258 | `$RWWWCGB.json` / `$IWWWCGB.json` | `54fca79590344418cd93fdee4b41122b81c0b134f7428f9a289e0987e44bbef6` |
| `reports/protocolo_7_1_auditoria_v2.csv` | Informes y evidencias tabulares | 1050 | `$RNQEGC9.csv` / `$INQEGC9.csv` | `b2841dc8ecdc74e5f32f305d4b72277b4930eeece65cde51e651e386d27d28e6` |
| `reports/protocolo_7_1_exposicion_prueba.csv` | Informes y evidencias tabulares | 471 | `$R665OIX.csv` / `$I665OIX.csv` | `e417a0007ad8498d6aca3aadbf3f53f3835f360cb06f4ae315409209cf2491bf` |
| `reports/protocolo_7_1_metricas.csv` | Informes y evidencias tabulares | 481 | `$R4PBR84.csv` / `$I4PBR84.csv` | `b41f5ba3a5c3a3e137b90f1ee6efc6fd46f720a5c7c122bc3a521c86e3cb4d89` |
| `reports/protocolo_7_1_modelos.json` | Informes y evidencias tabulares | 4022 | `$R5RMOQJ.json` / `$I5RMOQJ.json` | `0bdcc1aab909a6f573f35a4c90c18ddcaa68ea226069c9d753727e245d11fede` |
| `reports/protocolo_7_1_particiones.csv` | Informes y evidencias tabulares | 678 | `$RQ06NU2.csv` / `$IQ06NU2.csv` | `977cf092dfd50b3c225e0b08a59e6b63e6ea76a45aa766ea5ac53e9a5ed24db1` |
| `reports/protocolo_7_1_predicciones_validacion.csv` | Predicciones y copias de referencia | 963668 | `$R5YVUR1.csv` / `$I5YVUR1.csv` | `3fe7f707c81b70f4cdd8f7b2b419b3272b2256d0258ec9568a0b328331faeb24` |
| `reports/protocolo_7_1_propuesta_previa.md` | Documentación y configuración | 3480 | `$RMK1HMT.md` / `$IMK1HMT.md` | `489827d65638da5dc8d4422d69fa147bf2f34561be51d811bf2c5ad9b14e04e1` |
| `reports/protocolo_7_1_referencia_reproduccion.csv` | Informes y evidencias tabulares | 933156 | `$R5QOH0F.csv` / `$I5QOH0F.csv` | `e1da187010cbc4da07aba2cda53e4ef239d1066dcffe4a86cd81c89562113ea2` |
| `reports/protocolo_7_1_segmentos.csv` | Informes y evidencias tabulares | 4743 | `$RDDLNW9.csv` / `$IDDLNW9.csv` | `9751576fe13aa69acbc5318f0fd91c7dca5378d28e229213c72f28e98f2a2c73` |
| `reports/protocolo_7_1_seguimiento.csv` | Informes y evidencias tabulares | 339 | `$RTYMUN7.csv` / `$ITYMUN7.csv` | `99e2b58f9e5930bca9dbd858d5e0fd819aaf83a3afa9ab9af39f17103595f876` |
| `reports/protocolo_7_1_seleccion_resultado_v2.csv` | Informes y evidencias tabulares | 143 | `$RT9F98Z.csv` / `$IT9F98Z.csv` | `ace924b92c1894dce9124b01cac885969823acd133268a54459a1778eab1f824` |
| `reports/protocolo_7_1_transicion_v2_v3.csv` | Informes y evidencias tabulares | 301 | `$RT4NP22.csv` / `$IT4NP22.csv` | `00fb0a077a8537f9ad209b26fea9ecc86f2e61ab4f4ec83686fbfc2a3c11ab1f` |
| `reports/protocolo_7_1_verificacion.json` | Informes y evidencias tabulares | 37044 | `$RO8BXOK.json` / `$IO8BXOK.json` | `729dce34efb471ea8d1b0fa08a689f94ce4e026a08a898253087d18e6cbd2201` |
| `reports/seleccion_8_bordes_empates.csv` | Informes y evidencias tabulares | 2368 | `$RS021IZ.csv` / `$IS021IZ.csv` | `53bcc1140cd6887800d5d86c5bcb69813a15481e58400fe664547f2faec25b2f` |
| `reports/seleccion_8_calibracion.csv` | Informes y evidencias tabulares | 317 | `$RIGYKP8.csv` / `$IIGYKP8.csv` | `ff05924a5c644c551c8d0d421e4f434358e9a86ad67efdd2d80d69c364ce1742` |
| `reports/seleccion_8_calibracion_bins.csv` | Informes y evidencias tabulares | 1414 | `$RJTY6XK.csv` / `$IJTY6XK.csv` | `f52f954dce635962ec9e2fbe6fb1ad6bc6423dd15e4136913862ee603145e3c7` |
| `reports/seleccion_8_capacidades.csv` | Informes y evidencias tabulares | 793 | `$RW9OFMG.csv` / `$IW9OFMG.csv` | `627bcf761c6f52324d31afad28693f3145dbe2a3fbac83191a74ca366fef7568` |
| `reports/seleccion_8_especificacion_congelada.json` | Informes y evidencias tabulares | 14176 | `$RN03GHD.json` / `$IN03GHD.json` | `e9ad0d974e4bfc4a7f377a1b3a5163468f87a8441a7dd23bd978e9d2b65721c6` |
| `reports/seleccion_8_hoteles_capacidad_20.csv` | Informes y evidencias tabulares | 691 | `$ROJAYEJ.csv` / `$IOJAYEJ.csv` | `b400f070344ab4d81c1a1bf72ff26aff59d199a47e29883212247d782cf8bfb1` |
| `reports/seleccion_8_mensual_capacidad_20.csv` | Informes y evidencias tabulares | 1238 | `$RLMKCAL.csv` / `$ILMKCAL.csv` | `0c81923048d4fe0c80d96076f44f9234ab057c5cbea1b07eaf599286c71bc13e` |
| `reports/seleccion_8_metricas.csv` | Informes y evidencias tabulares | 483 | `$RQWNQA6.csv` / `$IQWNQA6.csv` | `5a81db7f184aa0acd00d6662d516c6a7dac5795b32d7421ac4c9df127dd8da06` |
| `reports/seleccion_8_plan_previo.md` | Documentación y configuración | 2969 | `$RN6SKQ1.md` / `$IN6SKQ1.md` | `a09b1ecf09f2f9d1cdb86a2a25276a99c2f2ff23040546374dff86835bffa6d8` |
| `reports/seleccion_8_politica_validacion.csv` | Informes y evidencias tabulares | 2235473 | `$R61V2WQ.csv` / `$I61V2WQ.csv` | `b0eb29e421b8d3ce0362d31b44fe61a718f2478d41877df2e0cf2f34e1d606c3` |
| `reports/seleccion_8_predicciones_validacion.csv` | Predicciones y copias de referencia | 1122968 | `$RUTTDW5.csv` / `$IUTTDW5.csv` | `bcf6af837a5be629f66909360c3524f0a93c0ea48bf031a6d11bf7e315cc1f13` |
| `reports/seleccion_8_referencia_reproduccion.csv` | Predicciones y copias de referencia | 1122968 | `$RNMMX59.csv` / `$INMMX59.csv` | `bcf6af837a5be629f66909360c3524f0a93c0ea48bf031a6d11bf7e315cc1f13` |
| `reports/seleccion_8_reproduccion.json` | Informes y evidencias tabulares | 469 | `$REMQNRJ.json` / `$IEMQNRJ.json` | `70900e4d76dfa0527eabcc7b320ef22f7109455a6675daa37c2076035e68ae39` |
| `reports/seleccion_8_umbrales.csv` | Informes y evidencias tabulares | 2223 | `$RQMOK0B.csv` / `$IQMOK0B.csv` | `840cad880f8c64e3e0c8753bef6b90235e9495cf7e15f29218ab41ac0a36c163` |
| `reports/seleccion_8_verificacion.json` | Informes y evidencias tabulares | 39734 | `$R25B1WQ.json` / `$I25B1WQ.json` | `9d4d03cecdb5fd1e63817546f31364532036832aa47a50884fe49ae206d0c024` |
| `reports/verificacion_referencias.json` | Informes y evidencias tabulares | 19079 | `$RYJARUX.json` / `$IYJARUX.json` | `0c0ed2c81fa4d49f314121dcea04094efc52acdac7df21791e9400c799f5aff1` |
| `requirements.txt` | Documentación y configuración | 284 | `$RMAAJD9.txt` / `$IMAAJD9.txt` | `e6bb48022891fd0e2084341f000d3e2b2db605e3b2470619a30aa78e44158040` |
| `src/__init__.py` | Código fuente vigente (incluye entradas históricas) | 137 | `$RPJ61YO.py` / `$IPJ61YO.py` | `fae158363d83f95227aece350947a824e054fa5dc5a424819c4b37d20b39bab3` |
| `src/audit_baseline.py` | Código fuente vigente (incluye entradas históricas) | 44566 | `$RI59DZG.py` / `$II59DZG.py` | `e32b39a6c3d2f2961e4a1684b3ec23d831b917732450d18ccb3035f6b1d163ff` |
| `src/baseline.py` | Código fuente vigente (incluye entradas históricas) | 24181 | `$RG6JVI0.py` / `$IG6JVI0.py` | `59aca443a07d503dd088c3bf0ecef9ad431fc3fe3e80d3a787afb1492ea315d3` |
| `src/cleaning.py` | Código fuente vigente (incluye entradas históricas) | 2532 | `$RWOA1RS.py` / `$IWOA1RS.py` | `b6ae9cc77aff709a2c9ec981541092f739cf54839008a2f39736d240af98a4b7` |
| `src/comparison.py` | Código fuente vigente (incluye entradas históricas) | 22949 | `$RTG2TR0.py` / `$ITG2TR0.py` | `9b1ea395ad88de1cfd4458adda7809cf25b41bea0d04a73995763b14002d546f` |
| `src/decision_policy.py` | Código fuente vigente (incluye entradas históricas) | 3954 | `$RH0UYQP.py` / `$IH0UYQP.py` | `e33a37771b8ca11b31804e9540b41b7de4c5404a99e203752c31979c4e19f603` |
| `src/evaluation_narrative.py` | Código fuente vigente (incluye entradas históricas) | 4476 | `$RF9E2HM.py` / `$IF9E2HM.py` | `7fb90f849f76a2e4bf3100cd9b45802401626f9068680e84c901654e7f95f4b7` |
| `src/explainability.py` | Código fuente vigente (incluye entradas históricas) | 43129 | `$RHSGHFA.py` / `$IHSGHFA.py` | `30eeb6ed15dafe23a2cd32da3c87caa55fafe35a6c9f8a69ce76b765035096f6` |
| `src/features.py` | Código fuente vigente (incluye entradas históricas) | 7257 | `$RC28V7V.py` / `$IC28V7V.py` | `fe93ff6b6292a57ca841f0616da47278658888ddb448e321056450fbc0d5aaca` |
| `src/final_evaluation.py` | Código fuente vigente (incluye entradas históricas) | 37502 | `$RS0AY6E.py` / `$IS0AY6E.py` | `ca9f249cedd128225116b484f5d87902b64dba2ec03c0e47ca38df69ffbf4e89` |
| `src/final_selection.py` | Código fuente vigente (incluye entradas históricas) | 33918 | `$RLAPLDP.py` / `$ILAPLDP.py` | `3ce6348b03b58c307ef2524501f02dde1fb160c1a3177288715889a71aa7015d` |
| `src/inspection.py` | Código fuente vigente (incluye entradas históricas) | 1602 | `$R1QXHYS.py` / `$I1QXHYS.py` | `6c39434686be3770da86bc1f9bc40bcd13f11d47aa6df2c3c7f91f81d0cc89e3` |
| `src/optimization.py` | Código fuente vigente (incluye entradas históricas) | 49733 | `$RJ5LNSM.py` / `$IJ5LNSM.py` | `36bd09cf3e2c1bcbc41573d1b1a890f4cab0e9fbae6aa988dc6a1b56133e76f4` |
| `src/preparation.py` | Código fuente vigente (incluye entradas históricas) | 4888 | `$R2MUPMU.py` / `$I2MUPMU.py` | `311e97b6a7f15cab3d71472f31c4d6119385532e200811cae6d4aa22fd83cb94` |
| `src/preprocessing.py` | Código fuente vigente (incluye entradas históricas) | 1584 | `$RY7AQ8L.py` / `$IY7AQ8L.py` | `2d765493a4573a3c86d88442f22cf2df24ae64426ada563a279e3552e654c4c3` |
| `src/run_notebook.py` | Código fuente vigente (incluye entradas históricas) | 3183 | `$RV3UAQV.py` / `$IV3UAQV.py` | `ba5e0a71c93f312582dd2ceffddfd6c9f8d457f4cb9659576c00f0e25e777c12` |
| `src/splitting.py` | Código fuente vigente (incluye entradas históricas) | 11363 | `$R2JZLNB.py` / `$I2JZLNB.py` | `d263e835fdf1ddfca2751c3e8c8e9ec5a0d7f6f32c2b9d7ca9bc3d956ebd789e` |
| `src/temporal_bias_v3.py` | Código fuente vigente (incluye entradas históricas) | 36241 | `$RYWF7OT.py` / `$IYWF7OT.py` | `1386bc6dc5952e6d5d949123dcdf9aeb0c9be5cc5007ab4ef244efd8a7705e2b` |
| `src/temporal_protocol.py` | Código fuente vigente (incluye entradas históricas) | 32990 | `$RF9KDF1.py` / `$IF9KDF1.py` | `7b6e3ef0e32fcffd324dd1f89587869df7a387762b01e88324a55b29f0eabb4a` |
| `tests/test_audit_baseline.py` | Pruebas | 2435 | `$RAH2ZDJ.py` / `$IAH2ZDJ.py` | `2c276942ff7669c61637e41630e59760a7e54434b96e1360b02b6c04244dbdf4` |
| `tests/test_baseline.py` | Pruebas | 3269 | `$R2O4ZEW.py` / `$I2O4ZEW.py` | `1786eadf2ba9c6e8e627a8a5c060fcc3235b147493922fcbcbc9eeeb6bd21134` |
| `tests/test_comparison.py` | Pruebas | 2477 | `$R0Q9M33.py` / `$I0Q9M33.py` | `ed7a2a1a5d1d9fcc92ec986999a3819dcaa286f47a6bcc539d2505c1324154f1` |
| `tests/test_decision_policy.py` | Pruebas | 3650 | `$RH2OBWI.py` / `$IH2OBWI.py` | `c55661e5d046b6f946499048c9895bc0bbc1bdffe0953756462c2bd7c4e9a500` |
| `tests/test_explainability.py` | Pruebas | 3911 | `$RWBMINC.py` / `$IWBMINC.py` | `6b75dd30dac60242768a50a46b8ad88ac127fbd32e571f776aacca28c1827392` |
| `tests/test_final_evaluation.py` | Pruebas | 5908 | `$RXYCYWY.py` / `$IXYCYWY.py` | `97d2fda597560039176be6862a4cdf67098819f9e4a178a326666fe432fd6d1c` |
| `tests/test_optimization.py` | Pruebas | 5905 | `$RCKFSRD.py` / `$ICKFSRD.py` | `9672cf8a64903c6ee1b61717a106ac8d27f651b0f24eb7a91afc9fd4fb3859a2` |
| `tests/test_preparation.py` | Pruebas | 7619 | `$RZXTFC8.py` / `$IZXTFC8.py` | `918a757ac71dce226c3b6721beb2c1725693a7d6bd276153665e787e1a665cf6` |
| `tests/test_temporal_bias_v3.py` | Pruebas | 5559 | `$RUP9TBQ.py` / `$IUP9TBQ.py` | `4478a59b0448cc3dc64ecd334c0b0da54d0251a46c22f4cf87aeee98f28ee2fc` |
| `tests/test_temporal_protocol.py` | Pruebas | 4150 | `$RFOD7DS.py` / `$IFOD7DS.py` | `80540c8b6ace1f282ab868a7fd6b04520fe3f4875aa9524493ecc8b36aac6b62` |
| `tmp/fase10/borrador.pptx` | Archivos generados temporales | 69956 | `$ROB4R45.pptx` / `$IOB4R45.pptx` | `49e14ce6b93dfc3bf6f0bc5f937eb3c64165cdcc3013e53090c84a68268c1e89` |
| `tmp/fase10/borrador.pptx.inspect.ndjson` | Archivos generados temporales | 33779 | `$RPT9Y6N.ndjson` / `$IPT9Y6N.ndjson` | `30e75c0a2d0b2f8f9a7c9522234a07e1d7dcbcae2bf9b9917d83c5d8158d1048` |
| `tmp/fase10/diapositiva-01.png` | Archivos generados temporales | 46695 | `$RQFMJFQ.png` / `$IQFMJFQ.png` | `fe246aa63e268f178f9635e4f4dada3518022ce707eee86a1922b2d48ea3c705` |
| `tmp/fase10/diapositiva-02.png` | Archivos generados temporales | 38477 | `$RS5ENGR.png` / `$IS5ENGR.png` | `5abad4074fe059dc5f49364ccbd5b2d00b4d6a0c271592b0b5d28d95474ee0cc` |
| `tmp/fase10/diapositiva-03.png` | Archivos generados temporales | 41542 | `$RCQZ96I.png` / `$ICQZ96I.png` | `6b676813d737aafddbaf70af12b002043bf9b0282e77ae3b470c0ed52c7e2d01` |
| `tmp/fase10/diapositiva-04.png` | Archivos generados temporales | 53139 | `$R637SF5.png` / `$I637SF5.png` | `e064617e4b962774e8d1421dca746d4d61c334e4251b4621414fc92944e18d43` |
| `tmp/fase10/diapositiva-05.png` | Archivos generados temporales | 52940 | `$R92L03K.png` / `$I92L03K.png` | `d8ddfd11bd92c693d4ddd1d77131597a30be532b6ea334583fcbbbdadc58f2f3` |
| `tmp/fase10/diapositiva-06.png` | Archivos generados temporales | 47870 | `$RRYW1IE.png` / `$IRYW1IE.png` | `9fd64799ac04ad804f6276765ce40ac154a753638f7cb3319894d08c752dd7a3` |
| `tmp/fase10/diapositiva-07.png` | Archivos generados temporales | 55767 | `$RODL4OP.png` / `$IODL4OP.png` | `33892c7fd3a81f3d488bf95e7b6d4b3667b5a8da5dd3bb093f404be5838310e8` |
| `tmp/fase10/diapositiva-08.png` | Archivos generados temporales | 49629 | `$RNG8IEQ.png` / `$ING8IEQ.png` | `f744804082242db8c2497466e224e4580f4871b7e1f9c47408e8c21bdec5e9cd` |
| `tmp/fase10/diapositiva-09.png` | Archivos generados temporales | 39169 | `$RD5SUC2.png` / `$ID5SUC2.png` | `795d28abe9273a657a4691ab0764ddfb4c801df7acbd0618d48bbbb1d62b3126` |
| `tmp/fase10/diapositiva-10.png` | Archivos generados temporales | 52882 | `$REIA7X7.png` / `$IEIA7X7.png` | `bd95abafdf91ff4c5af960af2afa68ea3426107561026554512700e03004ae86` |
| `tmp/fase10/diapositiva-11.png` | Archivos generados temporales | 50836 | `$ROWL8WV.png` / `$IOWL8WV.png` | `b8a9bf8479e62589b9829a49fc0e32df4c7157d2eaf1b74692c2c84cad8d11ee` |
| `tmp/fase10/diapositiva-12.png` | Archivos generados temporales | 57015 | `$RHFQJ8X.png` / `$IHFQJ8X.png` | `c2812a3ee72499f0ef278fea1255bff1a0fb28420f46e1d73152b383acc97255` |
| `tmp/fase10/diapositiva-13.png` | Archivos generados temporales | 50115 | `$REBZS4E.png` / `$IEBZS4E.png` | `d6a465b1d7442d4098e6cad243e5aec28866926fab144ebd6127185b5eeeb1af` |
| `tmp/fase10/diapositiva-14.png` | Archivos generados temporales | 46339 | `$RWR48LC.png` / `$IWR48LC.png` | `05ade1426f5362e0a512dc0638396e9818ae22fa6f304580f966c4462af6de79` |
| `tmp/fase10/diapositiva-15.png` | Archivos generados temporales | 57701 | `$RJ8TBDU.png` / `$IJ8TBDU.png` | `9f5431f78b42797dbbbdd6fb982204a0144770f3b70acf65caa58ca5bbb5e306` |
| `tmp/fase10/final-01.png` | Archivos generados temporales | 46695 | `$R1KEUQD.png` / `$I1KEUQD.png` | `fe246aa63e268f178f9635e4f4dada3518022ce707eee86a1922b2d48ea3c705` |
| `tmp/fase10/final-02.png` | Archivos generados temporales | 38477 | `$RQIOSKC.png` / `$IQIOSKC.png` | `5abad4074fe059dc5f49364ccbd5b2d00b4d6a0c271592b0b5d28d95474ee0cc` |
| `tmp/fase10/final-03.png` | Archivos generados temporales | 41542 | `$RC96KPR.png` / `$IC96KPR.png` | `6b676813d737aafddbaf70af12b002043bf9b0282e77ae3b470c0ed52c7e2d01` |
| `tmp/fase10/final-04.png` | Archivos generados temporales | 53139 | `$REZHFDL.png` / `$IEZHFDL.png` | `e064617e4b962774e8d1421dca746d4d61c334e4251b4621414fc92944e18d43` |
| `tmp/fase10/final-05.png` | Archivos generados temporales | 52940 | `$R93EFYQ.png` / `$I93EFYQ.png` | `d8ddfd11bd92c693d4ddd1d77131597a30be532b6ea334583fcbbbdadc58f2f3` |
| `tmp/fase10/final-06.png` | Archivos generados temporales | 47870 | `$R6SGW3D.png` / `$I6SGW3D.png` | `9fd64799ac04ad804f6276765ce40ac154a753638f7cb3319894d08c752dd7a3` |
| `tmp/fase10/final-07.png` | Archivos generados temporales | 55767 | `$RU0HVEO.png` / `$IU0HVEO.png` | `33892c7fd3a81f3d488bf95e7b6d4b3667b5a8da5dd3bb093f404be5838310e8` |
| `tmp/fase10/final-08.png` | Archivos generados temporales | 49629 | `$RULLFI7.png` / `$IULLFI7.png` | `f744804082242db8c2497466e224e4580f4871b7e1f9c47408e8c21bdec5e9cd` |
| `tmp/fase10/final-09.png` | Archivos generados temporales | 39169 | `$RG9PYZO.png` / `$IG9PYZO.png` | `795d28abe9273a657a4691ab0764ddfb4c801df7acbd0618d48bbbb1d62b3126` |
| `tmp/fase10/final-10.png` | Archivos generados temporales | 52882 | `$RNHSK7W.png` / `$INHSK7W.png` | `bd95abafdf91ff4c5af960af2afa68ea3426107561026554512700e03004ae86` |
| `tmp/fase10/final-11.png` | Archivos generados temporales | 50836 | `$RMU3IQB.png` / `$IMU3IQB.png` | `b8a9bf8479e62589b9829a49fc0e32df4c7157d2eaf1b74692c2c84cad8d11ee` |
| `tmp/fase10/final-12.png` | Archivos generados temporales | 57015 | `$RDJVE1J.png` / `$IDJVE1J.png` | `c2812a3ee72499f0ef278fea1255bff1a0fb28420f46e1d73152b383acc97255` |
| `tmp/fase10/final-13.png` | Archivos generados temporales | 50115 | `$RO1DCE3.png` / `$IO1DCE3.png` | `d6a465b1d7442d4098e6cad243e5aec28866926fab144ebd6127185b5eeeb1af` |
| `tmp/fase10/final-14.png` | Archivos generados temporales | 46339 | `$R41OBGK.png` / `$I41OBGK.png` | `05ade1426f5362e0a512dc0638396e9818ae22fa6f304580f966c4462af6de79` |
| `tmp/fase10/final-15.png` | Archivos generados temporales | 57701 | `$R8TGVVU.png` / `$I8TGVVU.png` | `9f5431f78b42797dbbbdd6fb982204a0144770f3b70acf65caa58ca5bbb5e306` |
| `tmp/fase10/memoria-01.png` | Archivos generados temporales | 63864 | `$RYL5GIC.png` / `$IYL5GIC.png` | `6396caa66b6d29db62cbffbd6f8a02c5b117a19438d14db2954a1b15d90710fb` |
| `tmp/fase10/memoria-02.png` | Archivos generados temporales | 250233 | `$RY3R73C.png` / `$IY3R73C.png` | `71a78baac6428f0c556f0337e637f90080d4d511662ee440da746b05445643d8` |
| `tmp/fase10/memoria-03.png` | Archivos generados temporales | 162189 | `$RLIO3F5.png` / `$ILIO3F5.png` | `a251732927959c72fcd990b87567e3fa6f5dd372f8c88e87e0af4ea193646a36` |
| `tmp/fase10/memoria-04.png` | Archivos generados temporales | 116229 | `$R284W6H.png` / `$I284W6H.png` | `b4512d13a40356ae9b5655f6e9cffbb302bb074d4e271541a3d2e268d86359ff` |
| `tmp/fase10/memoria-05.png` | Archivos generados temporales | 221760 | `$RITN9S8.png` / `$IITN9S8.png` | `b6c1e3d07ed79a1d5b969047d52bb57c9bedf3beb9848e106da40b151ad87297` |
| `tmp/fase10/memoria-06.png` | Archivos generados temporales | 170122 | `$RG91WD9.png` / `$IG91WD9.png` | `873033d4e4596a3c2fd487ef77d95222bf140d5cbae6ebbcd862987434c67c5d` |
| `tmp/fase10/memoria-07.png` | Archivos generados temporales | 139433 | `$RRDB952.png` / `$IRDB952.png` | `983b0e14c1cbcd2f00f0174cd5537dd5a68f8260298008693e5fbe369e232568` |
| `tmp/fase10/memoria-08.png` | Archivos generados temporales | 200670 | `$RFSVB7G.png` / `$IFSVB7G.png` | `1cae0732b9fc7d2c939a06ebb97c2d0a6a4f55e945e6836957d652566010681f` |
| `tmp/fase10/memoria-09.png` | Archivos generados temporales | 216379 | `$RGPX82E.png` / `$IGPX82E.png` | `60c9bfe1ef25fee831177d13f9f5d7dc948d87d6ec04fac9ae8f583fdcd92def` |
| `tmp/fase10/memoria-10.png` | Archivos generados temporales | 106926 | `$RP15EWU.png` / `$IP15EWU.png` | `9ab985c961f3737a926af9f5d310630a8adf825a823b7794917d4b850d29f358` |
| `tmp/fase10/memoria-11.png` | Archivos generados temporales | 114618 | `$R94OFUM.png` / `$I94OFUM.png` | `7aaefb221e617dc9a795da141552e2d0fe99b46ea45e894319b17aea455f0558` |
| `tmp/fase10/memoria-12.png` | Archivos generados temporales | 106781 | `$R3TEH7X.png` / `$I3TEH7X.png` | `5f538ab2963f5a72e5369f70c94e353d19b8b7ba8f186e2fd2458ce45ee477fd` |
| `tmp/fase10/memoria-13.png` | Archivos generados temporales | 196073 | `$R9TCFG9.png` / `$I9TCFG9.png` | `2d77d8bd70b82ee2e74c9a907adde935e0020293dd2ac179dd76fd5f66d28b13` |
| `tmp/fase10/memoria-14.png` | Archivos generados temporales | 232523 | `$RXB4QYV.png` / `$IXB4QYV.png` | `9d3b03f94bd0808c139f7454e6e072ff829b9fba684c1b59534d0fd6cc09b5ce` |
| `tmp/fase10/memoria-15.png` | Archivos generados temporales | 163248 | `$R6YTDPX.png` / `$I6YTDPX.png` | `3831b1896de3a56fa5d8db2a97ffb43fa633db2be3d7b057728faa4b7bfa2279` |
| `tmp/fase10/validacion_presentacion.json` | Archivos generados temporales | 9220 | `$RE5DNEE.json` / `$IE5DNEE.json` | `9f409c536e61e6baa7745277835a969801bd992e9b31f3461466a15b7c1a21bd` |

## Comprobación final de preservación

Antes de cerrar los informes se vuelven a comprobar los 537 hashes restaurados, los 537 contenidos y 537 metadatos del respaldo, y los pares de papelera. Solo se añaden los tres Markdown solicitados a `reports`; no se modifican los archivos inventariados. Los nuevos informes no se incorporan retroactivamente a manifiestos históricos. No se ha creado `entrega_profesor`.
