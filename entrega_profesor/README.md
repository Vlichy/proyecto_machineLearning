# Cancelaciones hoteleras · Evolve Academy

Entrega académica basada en cohortes retrospectivas de llegada v3. El notebook reconstruye el proceso desde el CSV: prepara datos, entrena logística/XGBoost, realiza optimización temporal complementaria solo en train y explica la logística con SHAP. No necesita el proyecto de desarrollo ni descarga datos.

## Archivos

- `cancelaciones_hoteleras.ipynb`: único notebook con código, salidas, cinco EDA accionables, métricas, ROC, summary SHAP, dos waterfall y conclusiones.
- `hotel_bookings.csv`: CSV original, 119.390 filas y 32 columnas.
- `presentacion_cancelaciones.pptx`: 16 diapositivas con notas, gráficos y tablas editables; las tres figuras SHAP son imágenes científicas generadas por el notebook.
- `README.md`: entorno, ejecución y límites.

No se entrega la memoria histórica porque el enunciado facilitado exige notebook y presentación. El vídeo solo procede si no hay exposición en clase. Confirmar autoría académica antes del envío; no se ha inventado un nombre.

## Entorno y ejecución

Verificado en Windows con **Python 3.14.5**, en un kernel nuevo y una carpeta aislada cuyo único archivo de entrada era el CSV. No se ha probado instalar desde cero todos los paquetes en otro equipo ni se han bloqueado todas las dependencias transitivas.

Desde esta carpeta, crear un entorno nuevo sin utilizar ni modificar el entorno del proyecto histórico:

```powershell
python -m venv .venv_entrega
.\.venv_entrega\Scripts\python.exe -m pip install numpy==2.4.6 pandas==3.0.3 scipy==1.18.1 matplotlib==3.11.0 seaborn==0.13.2 scikit-learn==1.9.0 xgboost==3.4.1 shap==0.54.1 ipykernel==7.4.0 nbformat==5.11.1 nbclient==0.11.0
```

Abrir el notebook en un editor Jupyter (por ejemplo, VS Code), seleccionar el intérprete `.venv_entrega\Scripts\python.exe`, situar el directorio de trabajo en esta carpeta y elegir **reiniciar kernel y ejecutar todas las celdas**. La interfaz Jupyter no forma parte de las dependencias de cálculo y no se ha fijado una versión de interfaz no comprobada.

La ejecución automática de validación usó la API Python de nbclient con un kernel temporal que apuntaba explícitamente al intérprete verificado; no dependió de un kernel global llamado `python3`.

**Tiempos observados:** primera ejecución completa 22,55 s; ejecución de la versión final 9,07 s, ambas con kernel nuevo (la segunda reutiliza cachés del sistema). La búsqueda de 18 ajustes tardó 2,58 s en la ejecución final. No incluyen instalación de dependencias ni construcción del PowerPoint; no son una garantía para otros equipos.

El notebook no escribe archivos auxiliares, no importa `src`, no carga joblib ni resultados congelados. Reejecutarlo sí entrena y realiza una nueva inferencia de test con la configuración histórica fijada. El uso de bibliotecas/versiones diferentes puede producir variaciones numéricas. Un aviso opcional de widgets de progreso se omite específicamente al importar SHAP; las advertencias de convergencia se tratan como errores.

## Datos

SHA-256 del CSV: `7c2ae42a7353905ea136e5c2287f17c92c5435826598bfbb8491c6f0c7b1fc06`.

Fuente científica: António, Almeida y Nunes (2019), *Hotel booking demand datasets*, DOI [10.1016/j.dib.2018.11.126](https://doi.org/10.1016/j.dib.2018.11.126). El hash conserva trazabilidad de esta copia; no certifica su cadena de descarga o licencia. El Excel del profesor contiene **230 ADR almacenados como fechas**, por ejemplo 24,8 convertido al serial 46258. Por ello se entrega el CSV original, sin alterar datos.

## Resultados y significado

La nueva ejecución reproduce 6.564 prioridades, 5.340 TP, 1.224 FP y 7.796 FN sobre 32.829 reservas; precision de la política 81,35%, recall 40,65%, F1 0,542132 y ROC-AUC del score 0,780186. La política es top 20% de cada mes, ambos hoteles juntos, con redondeo hacia abajo y desempates reproducibles. **No es un umbral fijo de 0,5**; el notebook informa esa clasificación en otra tabla.

La comparación técnica con el modelo histórico encontró igualdad exacta de coeficientes, intercepto, imputación, escalado, categorías, scores y decisiones. La diferencia de Brier es 2,78×10⁻¹⁷, compatible con redondeo en representación/agregación numérica. No se afirma identidad binaria del joblib ni se cambia el recibo histórico de inferencia única.

La búsqueda complementaria posterior prueba `C={0,1;1;10}` y `class_weight={None,balanced}` dentro de train v3, con tres folds temporales completos. Seleccionó C=1 sin pesos (AP media 0,762432), coincidente con la configuración histórica. La diferencia respecto a C=0,1 es pequeña y no demuestra superioridad estable. La búsqueda no intervino en la selección original, no usa test y no sustituye automáticamente el modelo. SHAP explica logística reconstruida con referencia de 500 filas de train y 1.000 ejemplos aleatorios de validación, además de dos casos extremos de validación elegidos sin mirar etiquetas.

## Límites

La ejecución limpia está verificada en el entorno descrito; portabilidad a una instalación nueva sigue sin comprobar. La evaluación es **retrospectiva por llegada**, con snapshots iniciales y cierre de PMS no acreditados. El EDA histórico vio todo el archivo y parte del test participó en desarrollo v2; no es un test completamente independiente. La cuota requiere un mes completo, presupone capacidad y no tiene calibración probabilística acreditada.

No se ha demostrado utilidad en producción, ahorro ni efecto causal de contactar clientes. Antes de uso real se necesitan datos nuevos con trazabilidad, capacidad/costes del hotel, validación externa y piloto humano controlado. Los archivos históricos y su respaldo permanecen intactos.
