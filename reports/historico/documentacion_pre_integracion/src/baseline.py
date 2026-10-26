"""Fit compartido de logística; carga e informe históricos v1, nunca evaluación en prueba."""
from pathlib import Path
import hashlib
import json
import warnings

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning, NotFittedError
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, confusion_matrix)
from sklearn.pipeline import Pipeline
from sklearn.utils.validation import check_is_fitted

from src.features import (FEATURES, NUMERIC_FEATURES, CATEGORICAL_FEATURES,
                          LEAKAGE_FEATURES, UNCERTAIN_FEATURES, separate_model_data)
from src.preprocessing import build_preprocessor
from src.preparation import TEMPORAL_PLAN
from src.splitting import temporal_split_legacy as temporal_split, describe_split


SEED = 42


def legacy_report_dir(root):
    """Entrada histórica v1 congelada: solo lectura después de archivarla."""
    history = Path(root) / "reports/historico/protocolo_v1"
    return history if history.is_dir() else Path(root) / "reports"


def legacy_output_dir(root):
    """Reejecuciones históricas separadas: no alteran archivo v1 ni resultados v2."""
    source = legacy_report_dir(root)
    output = source / "reproduccion" if source.name == "protocolo_v1" else source
    output.mkdir(parents=True, exist_ok=True)
    return output


def build_logistic_pipeline():
    """Configuración fijada antes de evaluar; max_iter es límite de convergencia."""
    return Pipeline([
        ("preprocessor", build_preprocessor(scale_numeric=True)),
        ("classifier", LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000,
                                           class_weight=None, random_state=SEED)),
    ])


def evaluate_predictions(target, predicted, probability):
    """Clase positiva: cancelación (1). Ceros en precision/F1 indefinidas del trivial."""
    return {
        "accuracy": float(accuracy_score(target, predicted)),
        "precision": float(precision_score(target, predicted, zero_division=0)),
        "recall": float(recall_score(target, predicted, zero_division=0)),
        "f1": float(f1_score(target, predicted, zero_division=0)),
        "roc_auc": float(roc_auc_score(target, probability)),
        "matriz_confusion": confusion_matrix(target, predicted, labels=[0, 1]).tolist(),
    }


def load_baseline_data(project_root=None):
    """Carga histórica v1. El protocolo vigente v2 usa src.temporal_protocol."""
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    output = legacy_output_dir(root)
    path = root / "data/processed/hotel_bookings_prepared.csv"
    summary = json.loads((root / "reports/preparacion_resumen.json").read_text(encoding="utf-8"))
    if hashlib.sha256(path.read_bytes()).hexdigest() != summary["sha256_preparado"]:
        raise ValueError("El CSV preparado ha cambiado desde la fase 3.")
    original = root / "data/raw/hotel_bookings.csv"
    if hashlib.sha256(original.read_bytes()).hexdigest() != summary["sha256_original"]:
        raise ValueError("El dataset original ha cambiado.")
    prepared = pd.read_csv(path, encoding="utf-8")
    features, target, metadata = separate_model_data(prepared)
    if len(features) != 119390 or list(features.columns) != FEATURES:
        raise ValueError("La preparación no conserva las dimensiones acordadas.")
    if set(features) & set(LEAKAGE_FEATURES + UNCERTAIN_FEATURES + ["is_canceled"]):
        raise ValueError("Se han incluido campos prohibidos en X.")
    assigned = temporal_split(metadata)
    table, hotel_months = describe_split(features, target, metadata, assigned)
    # Comprobar el ciclo anual ANTES de cualquier ajuste.
    if not hotel_months.gt(0).all().all():
        raise ValueError("El entrenamiento no representa los doce meses en ambos hoteles; revisar estrategia antes de entrenar.")
    for name in ["entrenamiento", "validacion", "prueba_reservada"]:
        if not assigned.eq(name).any() or target.loc[assigned.eq(name)].nunique() != 2:
            raise ValueError(f"Partición vacía o sin ambas clases: {name}")
    for name in ["entrenamiento", "validacion"]:
        if features.loc[assigned.eq(name), NUMERIC_FEATURES].isna().all().any():
            raise ValueError(f"Hay una columna numérica completamente ausente en {name}.")
    # Guardar reglas/asignación antes de observar métricas: solo IDs, nunca otros datasets.
    pd.DataFrame({"meta_row_id": metadata.meta_row_id, "particion": assigned}).to_csv(
        output / "particiones_temporales.csv", index=False)
    split_report = {"cortes": {"validacion": TEMPORAL_PLAN["corte_validacion"], "prueba": TEMPORAL_PLAN["corte_prueba"]},
                    "regla_madurez": TEMPORAL_PLAN["etiquetas"], "particiones": table.to_dict("records"),
                    "meses_entrenamiento_por_hotel": {hotel: {str(k): int(v) for k, v in row.items()} for hotel, row in hotel_months.to_dict("index").items()},
                    "sin_solapamientos": True, "sin_grupos_compartidos": True,
                    "filas_cubiertas": len(assigned), "sha256_preparado": summary["sha256_preparado"],
                    "observacion_prueba": "Solo auditoría de clases/fechas y transform; sin predicciones ni métricas."}
    (output / "division_temporal.json").write_text(json.dumps(split_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return features, target, metadata, assigned, table, hotel_months


def fit_and_validate(features, target, assigned, transform_test=True):
    """Fit en train y evaluación validación; v2 desactiva también transform de prueba."""
    train = assigned.eq("entrenamiento")
    validation = assigned.eq("validacion")
    reserved_test = assigned.eq("prueba_reservada")
    x_train, y_train = features.loc[train], target.loc[train]
    x_valid, y_valid = features.loc[validation], target.loc[validation]
    model = build_logistic_pipeline()
    try:
        check_is_fitted(model)
    except NotFittedError:
        pass
    else:
        raise AssertionError("La fábrica debe devolver un pipeline sin ajustar.")
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        model.fit(x_train, y_train)
    convergence = [str(w.message) for w in captured if issubclass(w.category, ConvergenceWarning)]
    if convergence:
        raise RuntimeError("No se logró convergencia; revisar exclusivamente la configuración numérica: " + str(convergence))
    fitted = model.named_steps["preprocessor"]
    numeric = fitted.named_transformers_["numeric"]
    imputer = numeric.named_steps["imputer"]
    scaler = numeric.named_steps["scaler"]
    encoder = fitted.named_transformers_["categorical"].named_steps["encoder"]
    np.testing.assert_allclose(imputer.statistics_, x_train[NUMERIC_FEATURES].median().to_numpy())
    imputed = imputer.transform(x_train[NUMERIC_FEATURES])
    np.testing.assert_allclose(scaler.mean_, imputed.mean(axis=0))
    assert int(scaler.n_samples_seen_) == len(x_train)
    expected_categories = [np.unique(x_train[column].fillna("Desconocido").to_numpy(dtype=str)) for column in CATEGORICAL_FEATURES]
    for actual, expected in zip(encoder.categories_, expected_categories):
        np.testing.assert_array_equal(actual, expected)
    before = (imputer.statistics_.copy(), scaler.mean_.copy(), scaler.scale_.copy(),
              [c.copy() for c in encoder.categories_])
    probabilities = model.predict_proba(x_valid)[:, list(model.classes_).index(1)]
    predicted = (probabilities >= 0.5).astype("int64")
    # Requisito de aplicar parámetros de entrenamiento a prueba: NO se predice ni se evalúa.
    if transform_test:
        transformed_test = fitted.transform(features.loc[reserved_test])
        assert np.isfinite(transformed_test.data if hasattr(transformed_test, "toarray") else transformed_test).all()
    for actual, expected in zip([imputer.statistics_, scaler.mean_, scaler.scale_], before[:3]):
        np.testing.assert_array_equal(actual, expected)
    for actual, expected in zip(encoder.categories_, before[3]):
        np.testing.assert_array_equal(actual, expected)
    # El trivial aprende solo qué clase es mayoritaria en entrenamiento; ignora las características.
    dummy = DummyClassifier(strategy="most_frequent", random_state=SEED)
    dummy.fit(np.zeros((len(y_train), 1)), y_train)
    dummy_prediction = dummy.predict(np.zeros((len(y_valid), 1)))
    dummy_probability = dummy.predict_proba(np.zeros((len(y_valid), 1)))[:, list(dummy.classes_).index(1)]
    metrics = {"mayoritario": evaluate_predictions(y_valid, dummy_prediction, dummy_probability),
               "regresion_logistica": evaluate_predictions(y_valid, predicted, probabilities)}
    feature_names = fitted.get_feature_names_out().tolist()
    assert not any(name.startswith("remainder__") or "meta_" in name or "is_canceled" in name for name in feature_names)
    audit = {
        "n_train_fit": len(x_train), "n_valid_evaluadas": len(x_valid),
        "n_test_solo_transformadas": int(reserved_test.sum()) if transform_test else 0, "test_predict_ejecutado": False,
        "n_features_transformadas": len(feature_names), "feature_names": feature_names,
        "estadisticas_solo_train_verificadas": True, "estadisticas_inmutables_al_transformar": True,
        "medianas_train": dict(zip(NUMERIC_FEATURES, imputer.statistics_.tolist())),
        "medias_scaler_train": dict(zip(NUMERIC_FEATURES, scaler.mean_.tolist())),
        "iteraciones_logistica": model.named_steps["classifier"].n_iter_.tolist(),
        "advertencias_fit": [str(w.message) for w in captured],
        "parametros": {"C": 1.0, "solver": "lbfgs", "max_iter": 2000, "class_weight": None,
                       "random_state": SEED, "umbral": 0.5, "tol": 0.0001},
        "clase_mayoritaria_train": int(y_train.mode().iloc[0]),
    }
    predictions = pd.DataFrame({"is_canceled": y_valid, "probabilidad_logistica": probabilities,
                                "prediccion_logistica": predicted, "prediccion_mayoritaria": dummy_prediction}, index=y_valid.index)
    return model, metrics, audit, predictions


def write_baseline_report(project_root):
    """Regenera el informe a partir de resultados ejecutados, sin volver a entrenar."""
    root = Path(project_root)
    output = legacy_output_dir(root)
    results_path = output / "baseline_resultados.json"
    if not results_path.is_file():
        results_path = legacy_report_dir(root) / "baseline_resultados.json"
    result = json.loads(results_path.read_text(encoding="utf-8"))
    logistic = result["metricas"]["regresion_logistica"]
    dummy = result["metricas"]["mayoritario"]
    audit = result["auditoria_fit"]
    tn, fp = logistic["matriz_confusion"][0]
    fn, tp = logistic["matriz_confusion"][1]
    partition_lines = []
    date_lines = []
    for row in result["particiones"]:
        partition_lines.append(f"| {row['particion']} | {row['registros']:,} | {row['no_canceladas']:,} | {row['canceladas']:,} | {row['tasa_cancelacion']:.2%} |")
        date_lines.append(f"| {row['particion']} | {row['proxy_min']} a {row['proxy_max']} | {row['llegada_min']} a {row['llegada_max']} | {row['madurez_max']} |")
    metric_lines = []
    for name, values in result["metricas"].items():
        metric_lines.append(f"| {name} | {values['accuracy']:.6f} | {values['precision']:.6f} | {values['recall']:.6f} | {values['f1']:.6f} | {values['roc_auc']:.6f} |")
    text = f"""# Informe de fase 4 — División temporal y modelo baseline

Fecha: 18 de octubre de 2026. Resultado de una ejecución real, con los valores completos guardados en baseline_resultados.json. Clase positiva: is_canceled=1. Separador decimal de las tablas generadas: punto; miles: coma. Se completa exclusivamente la fase 4 solicitada: división y regresión logística, sin optimización ni modelos avanzados.

## 1. Revisión de preparación

Se revisaron los informes de fases 1–3, preparacion.ipynb y todos los módulos existentes de src. Se conservan 119.390 registros, sus 31.994 duplicados adicionales y los 14 predictores seleccionados. No se modifican original, CSV preparado, reglas de limpieza ni supuestos de disponibilidad inicial.

X contiene seis numéricas (lead_time, total_nights, adults, children, babies, children_missing) y ocho categóricas (hotel, arrival_date_month, meal, country, market_segment, distribution_channel, reserved_room_type, customer_type). is_canceled es únicamente y. Los diez metadatos, estados finales y las doce variables inciertas excluidas en fase 3 no llegan a X ni a la salida del ColumnTransformer. Se construyó un pipeline nuevo sin ajustar; no se reutilizaron transformadores entrenados sobre todo el archivo.

Se contrastaron las huellas SHA-256 de original y preparado con fase 3, y se verificó la integridad posterior. No se ha regenerado otro dataset de características por partición: el manifiesto guarda solo ID técnico y asignación.

## 2. Cortes y madurez temporal

Se mantienen los cortes propuestos, fijados antes de entrenar:

- Entrenamiento: proxy de creación < 2016-07-01 y madurez < 2016-07-01.
- Validación: 2016-07-01 <= proxy < 2017-01-01 y madurez < 2017-01-01.
- Prueba reservada: proxy >= 2017-01-01. No se evalúa aquí.
- Dos grupos aparte: reservas del periodo de entrenamiento/validación cuya etiqueta no había madurado al corte correspondiente. Permanecen en el dataset y en el manifiesto, sin desplazarlas a un periodo posterior.

El proxy es llegada prevista menos lead_time. La cota de madurez es max(llegada + noches, fecha_estado_final) + 1 día, con desigualdad estricta respecto al corte. La fecha final solo interviene en elegibilidad retrospectiva de etiquetas, nunca como predictor. Es una aproximación conservadora a disponibilidad, no un registro histórico demostrado; puede retrasar una cancelación ya conocida antes de la salida prevista.

| Partición | Reservas | No canceladas | Canceladas | Tasa de cancelación |
|---|---:|---:|---:|---:|
{chr(10).join(partition_lines)}

| Partición | Rango observado del proxy | Rango observado de llegada | Máxima cota de madurez |
|---|---|---|---|
{chr(10).join(date_lines)}

Los límites teóricos y los rangos observados son distintos: por ejemplo, entrenamiento termina el 29/06/2016 en proxy/llegada por la restricción de madurez. La tabla evita describir junio como un mes completo.

Todas las filas se asignan exactamente a un grupo; no hay cruces de filas ni de huellas de duplicados. Entrenamiento incluye julio de 2015–junio de 2016 y los doce meses están representados en ambos hoteles, con junio parcial. El proxy se extiende desde junio de 2013, pero la extracción solo contiene llegadas desde julio de 2015: no hay cobertura completa de todas las altas desde 2013.

### Limitación detectada antes del ajuste y tratamiento

Las 30.386 reservas no elegibles por madurez no son una pérdida de datos ni una muestra aleatoria. Se hizo explícita su asignación en vez de eliminarlas o incorporarlas al entrenamiento con información futura. La validación resultante favorece menor antelación/llegadas cercanas, y sus métricas no describen todas las reservas creadas durante el semestre. Las tasas de los grupos apartados reflejan esa diferencia de composición. Esta solución mantiene la cronología propuesta, pero no resuelve la censura ni hace representativo el subconjunto.

No se modificaron cortes tras observar métricas. En prueba se describieron clases y fechas únicamente como auditoría requerida. Su cota de madurez máxima es septiembre de 2017: antes de la futura evaluación habrá que justificar seguimiento suficiente y fecha de extracción. No se ha supuesto una fecha exacta de creación ni una disponibilidad operacional certificada.

## 3. Pipeline ajustado exclusivamente con entrenamiento

Pipeline: ColumnTransformer de fase 3 seguido de LogisticRegression.

- Numéricas: SimpleImputer(strategy='median', keep_empty_features=True) y StandardScaler.
- Categóricas: categoría constante Desconocido y OneHotEncoder(handle_unknown='ignore').
- Resto de columnas: drop por lista explícita. La etiqueta/metadatos quedan separados antes de fit.
- Regresión logística: C=1.0, solver=lbfgs, class_weight=None, random_state=42, tol=0.0001, max_iter=2000. Umbral fijado a 0.5.

max_iter es un límite numérico fijado antes de evaluar; no se buscaron hiperparámetros. El modelo convergió en {audit['iteraciones_logistica'][0]} iteraciones, sin advertencias de fit. La representación resultante tiene {audit['n_features_transformadas']} columnas. Las medianas, medias y categorías aprendidas se verificaron contra las {audit['n_train_fit']:,} filas de entrenamiento y no cambiaron al transformar validación ni prueba. No hay columnas numéricas completamente ausentes en entrenamiento.

La prueba se transformó solo para comprobar que se usan parámetros aprendidos de entrenamiento y que la salida es finita. No se ejecutó predict ni predict_proba del clasificador sobre prueba, ni se calcularon métricas allí. Los desconocidos se toleran por la regla establecida en fase 3, sin aprender categorías de validación/prueba.

La logística se elige por sencillez, reproducibilidad y carácter de primera referencia de clasificación probabilística. Impone linealidad/aditividad en log-odds y no captura automáticamente todas las interacciones. No se presupone calibración de probabilidades.

## 4. Comparación en validación

El trivial es DummyClassifier(strategy='most_frequent'), entrenado solo con y_train: siempre predice clase {audit['clase_mayoritaria_train']}. Usa una entrada constante porque ignora los predictores. No se eligió su clase a partir de validación.

| Clasificador | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
{chr(10).join(metric_lines)}

Precision/F1 sin positivos predichos del trivial se consignan como cero mediante zero_division=0; precision no se puede estimar entre alertas inexistentes. Su puntuación constante no discrimina y da ROC-AUC 0.5. El AUC de la logística usa probabilidad, no etiqueta binaria.

La logística mejora accuracy en {(logistic['accuracy'] - dummy['accuracy']) * 100:.4f} puntos porcentuales; detecta algunas cancelaciones frente a ninguna del trivial y tiene mayor AUC. La mejora de accuracy es pequeña y no basta para declarar que el sistema sea bueno o útil. El recall {logistic['recall']:.2%} indica una detección limitada al umbral fijado.

## 5. Matrices de confusión e interpretación de errores

Filas: realidad [no cancelación, cancelación]. Columnas: predicción [no cancelación, cancelación].

Trivial:

| Real / predicción | No cancelación | Cancelación |
|---|---:|---:|
| No cancelación | {dummy['matriz_confusion'][0][0]:,} | {dummy['matriz_confusion'][0][1]:,} |
| Cancelación | {dummy['matriz_confusion'][1][0]:,} | {dummy['matriz_confusion'][1][1]:,} |

Regresión logística (0.5):

| Real / predicción | No cancelación | Cancelación |
|---|---:|---:|
| No cancelación | {tn:,} | {fp:,} |
| Cancelación | {fn:,} | {tp:,} |

Se generan {tp + fp:,} alertas: {tp:,} corresponden a cancelaciones y {fp:,} son falsas alarmas. Quedan {fn:,} cancelaciones sin detectar ({1 - logistic['recall']:.2%} del total cancelado elegible). Los falsos positivos pueden consumir seguimiento innecesario; los falsos negativos dejan riesgo sin anticipar para la planificación. No se atribuyen importes económicos sin conocer costes y actuaciones.

Precision {logistic['precision']:.2%} describe acierto entre alertas; recall {logistic['recall']:.2%}, cobertura de cancelaciones. El umbral 0.5 no es una decisión óptima de negocio demostrada. No se ensayaron otros umbrales, reponderaciones o remuestreos en esta fase. F1 no incorpora costes; ROC-AUC mide ordenación, no calibración, causalidad o rentabilidad. Las gráficas de matrices y ROC son únicamente de validación.

## 6. Desbalance y limitaciones

La clase mayoritaria es no cancelación: el trivial ya alcanza {dummy['accuracy']:.2%} en validación. El entrenamiento tiene 35.81% de cancelación frente a 26.17% en validación; precisión y accuracy dependen de esa composición. La logística sin ponderación y a umbral 0.5 puede favorecer la clase mayoritaria. Este resultado no demuestra que ponderar o cambiar el umbral vaya a mejorar la utilidad; deberá investigarse con autorización, sin recurrir a prueba.

Los duplicados siguen pudiendo sobreponderar patrones, aunque no crucen particiones. Las huellas incluyen las columnas finales y no identifican una reserva real: no descartan duplicados parciales, relaciones entre clientes/grupos ni reservas distintas con iguales predictores. No se construyen intervalos de confianza suponiendo independencia sin justificarla.

Los 14 predictores conservan el supuesto de representar datos iniciales; no hay logs para verificar versiones. La partición es una simulación offline basada en proxy de creación y madurez aproximada, no una evaluación de producción certificada. La prueba queda reservada respecto a este baseline, pero el EDA ya exploró todo el archivo y esa exposición previa sigue siendo una limitación. Faltan requisitos académicos oficiales y documentación temporal. Se necesita validación externa/prospectiva para confirmar generalización y utilidad.

## 7. Archivos y comprobaciones

Creados: notebooks/baseline.ipynb; src/splitting.py; src/baseline.py; tests/test_baseline.py; reports/particiones_temporales.csv (solo ID y asignación); reports/division_temporal.json; reports/baseline_resultados.json; reports/baseline_predicciones_validacion.csv; reports/baseline_verificacion.json; este informe y tres PNG baseline_* en reports/figures.

Modificados: README y src/run_notebook.py para permitir el notebook baseline. Las dependencias y decisiones de preparación se mantienen. No se guardan copias de X por partición, transformadores entrenados sobre todo el dataset ni predicciones de prueba. El pipeline entrenado reside en memoria y se reproduce ejecutando el notebook; no se exportó un modelo serializado.

El notebook se ejecutó completo con salidas conservadas. Nueve pruebas comprueban preparación, fronteras temporales, madurez, prohibición de grupos compartidos y orientación de métricas. Se verifican también hashes de datos, estado inicial sin fit, estadísticas aprendidas solo de train, inmutabilidad al transformar y 105 archivos de referencia sin cambios. El detalle de ejecución y rutas se conserva en baseline_verificacion.json. Las figuras se revisan visualmente.

## 8. Recomendación para la siguiente fase

Revisar primero la detección limitada del baseline y la población elegible para validación. Tras autorización, comparar modelos estudiados con estas mismas reglas, manteniendo preprocesamiento dentro de cada ajuste y prueba reservada. Los costes de alertas y cancelaciones no detectadas, la calibración y la posible elección de umbral necesitan una fase posterior autorizada; no se han optimizado ahora. No relajar exclusiones temporales solo para mejorar métricas.

**Fin de fase 4. No se continúa sin confirmación del usuario.**
"""
    destination = output / "fase_4_baseline.md"
    destination.write_text(text, encoding="utf-8")
    return destination
