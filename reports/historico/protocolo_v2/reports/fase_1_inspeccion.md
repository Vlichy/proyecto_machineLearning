# Informe de fase 1 — Inspección y organización

Fecha: 18 de octubre de 2026. Alcance: revisión de referencias, inspección inicial del dataset y estructura básica. No se han transformado los datos ni iniciado el EDA completo.

## 1. Proyectos anteriores revisados

- **proyecto_python**: README, dependencias, notebook `eda.ipynb`, estructura y módulos auxiliares. Usa `data/raw/`, `data/processed/`, `notebooks/`, `src/`, `main.py`, README y requirements. Notebook con objetivo, preguntas de negocio, código, gráficos, interpretación por pregunta y conclusiones generales. Funciones en `snake_case`, nombres de módulos en inglés, variables originales del dataset conservadas, `df`, constantes de rutas en mayúsculas y `pathlib`. Comentarios y docstrings en español. Las visualizaciones se muestran en el notebook; existe un módulo auxiliar para gráficos.
- **proyecto_estadistica**: README, dependencias, notebook `analisis_estadistico.ipynb` y módulo de características. Usa `data/` directamente porque parte del dataset ya procesado, además de `notebooks/` y `src/`. Expone pregunta de investigación, comprobaciones de consistencia, preparación justificada, distribuciones, relaciones, modelos, diagnósticos, limitaciones y conclusiones. Combina Markdown y código, conserva nombres de variables del dataset e incorpora variables derivadas descriptivas en inglés. No se trasladan sus técnicas de regresión OLS a esta clasificación automáticamente.
- **Practica**: inventario, notebook `clase_terminal_def.ipynb` y estructura del ejercicio de terminal. Es material de terminal, no evidencia de metodología de Machine Learning.
- Archivo suelto `Untitled-1.py`: práctica básica de Python; no aporta estructura para el nuevo proyecto. Existe un requirements compartido y un entorno `venv`; no se modificaron.
- **Referencia adicional** fuera de DataScience: `hotel-booking-prediction-99-5-acc (1).ipynb`, en el directorio Curso. Se inspeccionaron sus celdas en modo lectura. Contiene comparaciones de clasificadores y una red neuronal; usa rutas de Kaggle, partición aleatoria sin semilla explícita y el conjunto de prueba como validación durante el entrenamiento de la red. No acredita requisitos del profesor ni la metodología impartida. Su cifra de accuracy del título no es un resultado de este proyecto. No se copió ni ejecutó su código.

No se localizaron un enunciado del profesor ni prácticas identificables como clases específicas de Machine Learning en los archivos inspeccionados. No se presupone qué algoritmos o técnicas se exigen.

## 2. Dataset localizado

Origen local: `Curso/MachineLearning/archive.zip`. Único miembro: `hotel_bookings.csv` (CSV de 16.855.599 bytes). Esquema compatible con Hotel Booking Demand.

- Dimensiones comprobadas: **119.390 filas y 32 columnas**.
- Hoteles: City Hotel **79.330**; Resort Hotel **40.060**.
- Objetivo `is_canceled`: 0 **75.166**; 1 **44.224**; sin nulos.
- Tipos inferidos por pandas: enteros, flotantes y cadenas. Los tipos completos están en `inspeccion_dataset.json`. `reservation_status_date` se lee como cadena; `agent` y `company` aparecen como flotantes por sus nulos, lo que no significa que sean cantidades continuas. No se corrigieron tipos.
- Ausentes: `children` **4**; `country` **488**; `agent` **16.340**; `company` **112.593**.
- Duplicados exactos adicionales respecto de la primera aparición: **31.994**. Filas participantes en grupos duplicados, incluyendo primeras apariciones: **40.165**. No se eliminaron; sin identificador único no puede concluirse que sean errores o reservas distintas.
- Lectura UTF-8 estricta correcta; no se detectó el carácter de sustitución Unicode. Esto comprueba la lectura, no garantiza por sí solo la calidad semántica de cada valor.

### Riesgo preliminar de fuga de información

`reservation_status` y `reservation_status_date` describen el estado final y su fecha: deben quedar fuera de los predictores. Se conservan intactos en el CSV original.

Revisar especialmente `assigned_room_type`, `booking_changes` y `days_in_waiting_list`, que pueden reflejar asignaciones o acontecimientos posteriores a la creación. También `adr`, `deposit_type`, `required_car_parking_spaces`, `total_of_special_requests` y otros campos editables requieren comprobar que representan el valor disponible al crear la reserva. Los contadores históricos (`previous_cancellations`, `previous_bookings_not_canceled`) y `is_repeated_guest` necesitan una definición temporal verificable. No se da por válida ninguna variable solo por aparecer en el CSV. La política conservadora será excluir de los predictores los campos cuya disponibilidad inicial no pueda acreditarse; la selección definitiva corresponde a fases posteriores.

No hay una columna explícita de fecha exacta de creación. Los componentes `arrival_date_*` corresponden a llegada; restar `lead_time` podría ofrecer una aproximación, pendiente de validar su significado y posibles actualizaciones. No equivale a disponer de una marca de creación observada. Todavía no se fijan cortes temporales; habrá que considerar también cuándo se conoce el resultado de cada reserva al simular entrenamiento histórico. Imputación, codificación y escalado se aprenderán únicamente en entrenamiento.

## 3. Estructura y justificación

El árbol completo figura en el README. Se adopta `data/raw/` y `data/processed/` del proyecto Python porque aquí se parte de datos originales. Se mantienen `notebooks/`, `src/`, README y requirements. Se añade `reports/` para la trazabilidad de esta fase y los resultados necesarios; evita recargar la raíz. No se crean módulos vacíos de limpieza o modelado ni un orquestador para tareas todavía no desarrolladas. `notebooks/` y `data/processed/` permanecen vacías.

## 4. Cambios realizados

Se crearon las carpetas `data/raw/`, `data/processed/`, `notebooks/`, `src/` y `reports/`; README, .gitignore, requirements, `src/__init__.py`, `src/inspection.py` y los tres informes de `reports/`. Se extrajo una única copia de `hotel_bookings.csv` a `data/raw/`. No se copió código de los proyectos anteriores. No se trasladaron ni eliminaron archivos de origen.

## 5. Verificaciones

- El ZIP pasó su comprobación CRC; se leyó y extrajo únicamente el miembro CSV identificado.
- SHA-256 del CSV extraído coincide con los bytes del CSV dentro del ZIP: `7c2ae42a7353905ea136e5c2287f17c92c5435826598bfbb8491c6f0c7b1fc06`.
- El ZIP original se conserva. Su huella figura en el informe JSON del dataset.
- Se calcularon las huellas SHA-256 de 105 archivos de `proyecto_python`, `proyecto_estadistica` y `Practica` antes de organizar el proyecto, y se comprobaron después: sin cambios. Detalle en `verificacion_referencias.json`. La captura se hizo después de las lecturas iniciales; no se ejecutó código ni se escribió en las referencias en ningún momento.
- Entorno ejecutado: Python **3.14.5**, pandas **3.0.3** del entorno existente. No hubo instalaciones. La inspección ejecutable se verificó contra el informe guardado.
- CSV accesible desde la estructura final. Rutas internas relativas; el módulo resuelve la ruta desde su ubicación. No se ha reescrito el CSV mediante pandas.

## 6. Limitaciones y requisitos pendientes

Faltan el enunciado oficial, materiales específicos de las clases de Machine Learning y diccionario de datos con semántica temporal. El ZIP no acredita fuente, licencia o versión de descarga. El notebook adicional no sustituye esas referencias. Debe confirmarse el formato de entrega, métricas exigidas, modelos obligatorios y duración de la presentación. La inspección de esta fase no aborda todavía valores atípicos, incoherencias o distribuciones completas.

El alias global de Python no se pudo ejecutar; el intérprete del entorno compartido funcionó, aunque emite una advertencia sobre su ubicación original. No se modificó ni reparó ese entorno. Las dependencias actuales se limitan a lo utilizado; Jupyter y bibliotecas de EDA se fijarán al preparar la siguiente fase.

## 7. Siguiente fase propuesta: EDA

Tras la autorización, crear un notebook en español siguiendo la secuencia pregunta de negocio → comprobación/tabla/gráfico → interpretación → conclusión parcial. Empezar por estructura y calidad, estudiar cancelaciones y diferencias entre hoteles, revisar nulos y duplicados sin eliminaciones automáticas, distribuciones y anomalías, relaciones relevantes y cobertura temporal de llegadas. Distinguir asociaciones de causalidad y advertir sobre los campos posteriores a la reserva. Planificar qué observaciones pueden usarse para explorar sin comprometer una prueba final reservada. No se realizarán transformaciones aprendidas sobre todos los datos.

**Fin de la fase 1. Se requiere revisión y autorización del usuario antes de comenzar la fase 2.**
