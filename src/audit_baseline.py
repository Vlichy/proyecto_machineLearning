# Auditoría histórica del baseline: selección temporal, umbrales y calibración descriptiva.
"""Auditoría histórica 4.1 del protocolo v1; no altera el protocolo activo v2."""
from pathlib import Path
import hashlib
import json
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import (precision_score, recall_score, f1_score, confusion_matrix,
                             brier_score_loss, log_loss, average_precision_score)

from src.baseline import build_logistic_pipeline, evaluate_predictions, legacy_report_dir
from src.features import (NUMERIC_FEATURES, CATEGORICAL_FEATURES, FEATURES,
                          separate_model_data, LEAKAGE_FEATURES, UNCERTAIN_FEATURES)
from src.splitting import temporal_split_legacy as temporal_split


THRESHOLDS = [0.0, .05, .10, .15, .20, .25, .30, .35, .40, .45, .50, .60, .70, .80, .90, 1.0]
PROFILE_GROUPS = ["entrenamiento", "no_madura_entrenamiento", "validacion", "no_madura_validacion"]


def threshold_table(target, probability, thresholds=THRESHOLDS):
    """Aplica una rejilla descriptiva fijada de antemano; no elige ningún ganador."""
    target, probability = np.asarray(target), np.asarray(probability, dtype=float)
    if not len(target) or not np.isin(target, [0, 1]).all() or len(target) != len(probability) or not np.isfinite(probability).all() or ((probability < 0) | (probability > 1)).any():
        raise ValueError("Probabilidades inválidas o desalineadas.")
    rows = []
    for threshold in thresholds:
        if not 0 <= threshold <= 1:
            raise ValueError("El umbral debe estar entre 0 y 1.")
        predicted = probability >= threshold
        # Contar TN, FP, FN y TP con orden de clases explícito para evitar invertir su interpretación.
        tn, fp, fn, tp = confusion_matrix(target, predicted, labels=[0, 1]).ravel()
        rows.append({"umbral": threshold, "precision": float(precision_score(target, predicted, zero_division=0)),
                     "recall": float(recall_score(target, predicted, zero_division=0)),
                     "f1": float(f1_score(target, predicted, zero_division=0)),
                     "falsos_positivos": int(fp), "falsos_negativos": int(fn),
                     "verdaderos_positivos": int(tp), "verdaderos_negativos": int(tn),
                     "alertas": int(tp + fp), "fraccion_alertas": float((tp + fp) / len(target))})
    return pd.DataFrame(rows)


def reliability_table(target, probability):
    """Diez bandas fijas; incluye recuentos y no ajusta un calibrador."""
    table = pd.DataFrame({"observado": np.asarray(target), "probabilidad": np.asarray(probability)})
    table["banda"] = pd.cut(table.probabilidad, np.linspace(0, 1, 11), include_lowest=True)
    # Resumir la misma población por grupos y conservar sus denominadores antes de comparar tasas.
    grouped = table.groupby("banda", observed=True).agg(
        registros=("observado", "size"), probabilidad_media=("probabilidad", "mean"),
        tasa_observada=("observado", "mean"), cancelaciones=("observado", "sum")).reset_index()
    grouped["banda"] = grouped.banda.astype(str)
    grouped["desviacion_observada_menos_predicha"] = grouped.tasa_observada - grouped.probabilidad_media
    return grouped


def timing_scenarios(status_date, maturity, boundaries):
    """Audita fechas de prueba bajo cierres HIPOTÉTICOS, sin reasignar sus filas."""
    status_date, maturity = pd.to_datetime(status_date), pd.to_datetime(maturity)
    rows = []
    for name, boundary in boundaries.items():
        boundary = pd.Timestamp(boundary)
        rows.append({"escenario_no_verificado": name, "corte_exclusivo": str(boundary.date()),
                     "registros_prueba": len(maturity),
                     "fecha_estado_en_o_despues_del_corte": int(status_date.ge(boundary).sum()),
                     "no_cumple_regla_madurez": int(maturity.ge(boundary).sum()),
                     "cumple_regla_madurez": int(maturity.lt(boundary).sum())})
    return pd.DataFrame(rows)


def _reproduce_original(x_train, y_train, x_valid, saved_probabilities, baseline_record):
    """Reproduce la MISMA logística; esta función no recibe características de prueba."""
    model = build_logistic_pipeline()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        # Aprender los parámetros con el entrenamiento recibido; validación se reserva para medir rendimiento.
        model.fit(x_train, y_train)
    if any(issubclass(w.category, ConvergenceWarning) for w in caught):
        raise RuntimeError("La reproducción no convergió; no se modifican parámetros en esta auditoría.")
    positive_column = list(model.classes_).index(1)
    # Obtener scores con el pipeline ajustado, sin aprender parámetros de estas filas.
    p_train = model.predict_proba(x_train)[:, positive_column]
    # Obtener scores con el pipeline ajustado, sin aprender parámetros de estas filas.
    p_valid = model.predict_proba(x_valid)[:, positive_column]
    np.testing.assert_allclose(p_valid, saved_probabilities, rtol=0, atol=1e-12)
    preprocessor = model.named_steps["preprocessor"]
    numeric = preprocessor.named_transformers_["numeric"]
    imputer, scaler = numeric.named_steps["imputer"], numeric.named_steps["scaler"]
    encoder = preprocessor.named_transformers_["categorical"].named_steps["encoder"]
    np.testing.assert_allclose(imputer.statistics_, x_train[NUMERIC_FEATURES].median().to_numpy())
    imputed_train = imputer.transform(x_train[NUMERIC_FEATURES])
    np.testing.assert_allclose(scaler.mean_, imputed_train.mean(axis=0))
    np.testing.assert_allclose(scaler.var_, imputed_train.var(axis=0))
    expected_scale = np.sqrt(imputed_train.var(axis=0))
    expected_scale[expected_scale == 0] = 1
    np.testing.assert_allclose(scaler.scale_, expected_scale)
    assert int(scaler.n_samples_seen_) == len(x_train)
    for column, categories in zip(CATEGORICAL_FEATURES, encoder.categories_):
        np.testing.assert_array_equal(categories, np.unique(x_train[column].fillna("Desconocido").to_numpy(dtype=str)))
    np.testing.assert_allclose(scaler.mean_, list(baseline_record["auditoria_fit"]["medias_scaler_train"].values()))
    assert preprocessor.get_feature_names_out().tolist() == baseline_record["auditoria_fit"]["feature_names"]
    unseen = []
    for column, categories in zip(CATEGORICAL_FEATURES, encoder.categories_):
        values = x_valid[column].fillna("Desconocido")
        mask = ~values.isin(categories)
        unseen.append({"variable": column, "registros_validacion_categoria_no_vista": int(mask.sum()),
                       "porcentaje": float(100 * mask.mean()), "n_categorias_no_vistas": int(values[mask].nunique())})
    return p_train, p_valid, pd.DataFrame(unseen), {
        "reproduccion_mismo_algoritmo_parametros_y_filas": True,
        "max_diferencia_probabilidad_validacion": float(np.max(np.abs(p_valid - saved_probabilities))),
        "estadisticas_solo_train_verificadas": True,
        "fit_registros": len(x_train), "iteraciones": model.named_steps["classifier"].n_iter_.tolist(),
        "advertencias": [str(w.message) for w in caught],
        "predict_proba_solo_train_y_validacion": True,
    }


def _selection_profiles(features, target, assigned, status_date):
    """Comparaciones dentro de cada ventana; excluye completamente prueba."""
    rows, categories = [], []
    for group in PROFILE_GROUPS:
        mask = assigned.eq(group)
        data, labels = features.loc[mask], target.loc[mask]
        boundary = pd.Timestamp("2016-07-01" if "entrenamiento" in group else "2017-01-01")
        rows.append({"grupo": group, "registros": len(data), "tasa_cancelacion": float(labels.mean()),
                     "lead_time_media": float(data.lead_time.mean()), "lead_time_mediana": float(data.lead_time.median()),
                     "lead_time_p90": float(data.lead_time.quantile(.9)), "noches_media": float(data.total_nights.mean()),
                     "fraccion_city": float(data.hotel.eq("City Hotel").mean()),
                     "estado_final_fechado_antes_corte": int(status_date.loc[mask].lt(boundary).sum())})
        for column in ["hotel", "market_segment", "customer_type", "distribution_channel"]:
            counts = data[column].value_counts(dropna=False)
            for value, count in counts.items():
                categories.append({"grupo": group, "variable": column, "categoria": str(value),
                                   "registros": int(count), "porcentaje_grupo": float(100 * count / len(data))})
    return pd.DataFrame(rows), pd.DataFrame(categories)


# Examinar sesgos, errores y scores del baseline histórico sin decidir una nueva política.
def run_audit(project_root=None):
    root = Path(project_root) if project_root else Path(__file__).resolve().parents[1]
    reports = root / "reports"
    historical = legacy_report_dir(root)
    # Proteger los entregables existentes. La auditoría genera archivos con prefijo propio.
    protected = [root / "data/raw/hotel_bookings.csv", root / "data/processed/hotel_bookings_prepared.csv"]
    protected += [p for p in (root / "src").glob("*.py") if p.name != "audit_baseline.py"]
    protected += list((root / "notebooks").glob("*.ipynb"))
    protected += [p for p in (reports / "figures").glob("*.png") if not p.name.startswith("auditoria_4_1_")]
    protected += [p for p in reports.glob("*") if p.is_file() and not p.name.startswith(("auditoria_4_1", "fase_4_1"))]
    # Calcular una huella determinista para trazabilidad; no usarla como característica predictiva.
    before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    prepared = pd.read_csv(root / "data/processed/hotel_bookings_prepared.csv")
    raw = pd.read_csv(root / "data/raw/hotel_bookings.csv")
    features, target, metadata = separate_model_data(prepared)
    manifest = pd.read_csv(historical / "particiones_temporales.csv")
    assert len(prepared) == len(raw) == len(manifest) == 119390
    assert manifest.meta_row_id.tolist() == metadata.meta_row_id.tolist() == raw.index.tolist()
    assigned = manifest.particion
    pd.testing.assert_series_equal(assigned, temporal_split(metadata), check_names=False)
    assert not (set(features) & set(LEAKAGE_FEATURES + UNCERTAIN_FEATURES + ["is_canceled"]))
    assert len(FEATURES) == 14 and not any(c.startswith("meta_") for c in features)
    baseline_record = json.loads((historical / "baseline_resultados.json").read_text(encoding="utf-8"))
    # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
    assert before["data/raw/hotel_bookings.csv"] == baseline_record["sha256_original"]
    # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
    assert before["data/processed/hotel_bookings_prepared.csv"] == baseline_record["sha256_preparado"]
    status_date = pd.to_datetime(raw.reservation_status_date, errors="raise")
    arrival = pd.to_datetime(metadata.meta_arrival_date)
    booking = pd.to_datetime(metadata.meta_booking_date_proxy)
    maturity = pd.to_datetime(metadata.meta_label_available_after)
    departure = arrival + pd.to_timedelta(features.total_nights, unit="D")
    expected_maturity = pd.concat([departure, status_date], axis=1).max(axis=1) + pd.Timedelta(days=1)
    pd.testing.assert_series_equal(maturity, expected_maturity, check_names=False)
    pd.testing.assert_series_equal(booking, arrival - pd.to_timedelta(features.lead_time, unit="D"), check_names=False)
    profiles, category_profiles = _selection_profiles(features, target, assigned, status_date)
    test = assigned.eq("prueba_reservada")
    # Única inspección de prueba: metadatos temporales; nunca scores, métricas o categorías de X.
    scenarios = timing_scenarios(status_date.loc[test], maturity.loc[test], {
        "cierre_hipotetico_ultimo_dia_llegadas": "2017-09-01",
        "dia_siguiente_al_maximo_estado_no_es_cierre_documentado": "2017-09-15",
        "corte_posterior_al_maximo_de_cota_no_verificado": "2017-09-16",
    })
    train, valid = assigned.eq("entrenamiento"), assigned.eq("validacion")
    saved = pd.read_csv(historical / "baseline_predicciones_validacion.csv").set_index("meta_row_id")
    assert saved.index.tolist() == metadata.loc[valid, "meta_row_id"].tolist()
    np.testing.assert_array_equal(saved.is_canceled, target.loc[valid])
    p_train, p_valid, unseen, reproduction = _reproduce_original(
        features.loc[train], target.loc[train], features.loc[valid],
        saved.probabilidad_logistica.to_numpy(), baseline_record)
    thresholds = threshold_table(target.loc[valid], p_valid)
    calibration = reliability_table(target.loc[valid], p_valid)
    diagnostic_rows, distribution_rows = [], []
    for name, mask, probability in [("entrenamiento_ajuste_interno", train, p_train), ("validacion", valid, p_valid)]:
        labels = target.loc[mask]
        metrics = evaluate_predictions(labels, probability >= .5, probability)
        metrics.pop("matriz_confusion")
        # Medir el error cuadrático de los scores y distinguirlo de la precisión de las alertas.
        diagnostic_rows.append({"grupo": name, "registros": len(labels), **metrics,
                                "brier": float(brier_score_loss(labels, probability)),
                                "log_loss": float(log_loss(labels, probability)),
                                "average_precision": float(average_precision_score(labels, probability))})
        distribution_rows.append({"grupo": name, "tasa_observada": float(labels.mean()),
                                  "probabilidad_media": float(probability.mean()),
                                  "probabilidad_mediana": float(np.median(probability)),
                                  "p10": float(np.quantile(probability, .1)), "p90": float(np.quantile(probability, .9)),
                                  "p95": float(np.quantile(probability, .95)), "fraccion_alertas_05": float((probability >= .5).mean())})
    diagnostics, distribution = pd.DataFrame(diagnostic_rows), pd.DataFrame(distribution_rows)
    # Referencia probabilística constante fijada por prevalencia de entrenamiento, no un algoritmo nuevo.
    prior = float(target.loc[train].mean())
    reference_probability = np.full(int(valid.sum()), prior)
    cost_scenarios = thresholds[["umbral", "falsos_positivos", "falsos_negativos", "alertas"]].copy()
    for ratio in [1, 3, 10]:
        cost_scenarios[f"unidades_relativas_FP_1_FN_{ratio}"] = cost_scenarios.falsos_positivos + ratio * cost_scenarios.falsos_negativos
    tables = {"perfiles_seleccion": profiles, "perfiles_categoricos": category_profiles,
              "cierres_hipoteticos": scenarios, "umbrales_validacion": thresholds,
              "calibracion_validacion": calibration, "diagnosticos_train_validacion": diagnostics,
              "distribucion_probabilidades": distribution, "categorias_nuevas_validacion": unseen,
              "escenarios_coste_relativo": cost_scenarios}
    for name, table in tables.items():
        table.to_csv(reports / f"auditoria_4_1_{name}.csv", index=False)
    cal_error = float((calibration.registros * calibration.desviacion_observada_menos_predicha.abs()).sum() / int(valid.sum()))
    # Medir el error cuadrático de los scores y distinguirlo de la precisión de las alertas.
    result = {
        "reproduccion": reproduction, "modelo_original_modificado": False, "particiones_modificadas": False,
        "algoritmos_nuevos": False, "prueba_solo_metadatos_temporales": True,
        "scores_o_metricas_prueba_generados": False, "umbral_definitivo_seleccionado": False,
        "as_of_date_documentada": None, "madurez_real_garantizada": False,
        "fechas": {"ultimo_dia_llegadas": str(arrival.max().date()), "max_fecha_estado_global": str(status_date.max().date()),
                   "max_fecha_estado_prueba": str(status_date.loc[test].max().date()), "max_cota_madurez_prueba": str(maturity.loc[test].max().date())},
        "reservas_apartadas": int(assigned.str.startswith("no_madura").sum()),
        "regla_implementada_verificada": True,
        "calibracion": {"ece_10_bandas_descriptivo": cal_error,
                        "sesgo_media_predicha_menos_observada": float(p_valid.mean() - target.loc[valid].mean()),
                        "prior_train_constante": prior,
                        "brier_referencia_constante_train_en_validacion": float(brier_score_loss(target.loc[valid], reference_probability)),
                        "log_loss_referencia_constante_train_en_validacion": float(log_loss(target.loc[valid], reference_probability))},
        "tablas": {name: table.to_dict("records") for name, table in tables.items()},
        "conclusion": "Implementación del pipeline correcta; partición solo defendible como benchmark retrospectivo condicionado. Corregir protocolo de cierre, seguimiento y población antes de comparación formal. No se aplican cambios.",
    }
    make_figures(reports, features, target, assigned, p_train, p_valid, profiles, calibration, thresholds)
    for relative, checksum in before.items():
        # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == checksum, relative
    references = json.loads((reports / "verificacion_referencias.json").read_text(encoding="utf-8"))["antes"]
    verified, unavailable = 0, 0
    for filename, checksum in references.items():
        path = Path(filename)
        if not path.is_file():
            unavailable += 1
            continue
        with path.open("rb") as file:
            # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
            assert hashlib.file_digest(file, "sha256").hexdigest() == checksum
        verified += 1
    result["verificacion"] = {"archivos_previos_protegidos": before, "sin_cambios": True,
                              "referencias_sin_cambios": verified, "referencias_no_disponibles": unavailable}
    (reports / "auditoria_4_1_resultados.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(root, result)
    return result


# Representar las tablas de esta fase sin usar el gráfico para ajustar el modelo.
def make_figures(reports, features, target, assigned, p_train, p_valid, profiles, calibration, thresholds):
    """Gráficos de auditoría: nunca utiliza puntuaciones o características de prueba."""
    import os
    os.environ.setdefault("MPLCONFIGDIR", str(reports.parent / ".jupyter_runtime/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    from sklearn.metrics import precision_recall_curve, average_precision_score
    import seaborn as sns
    sns.set_theme(style="whitegrid")
    destination = reports / "figures"

    # Exportar la figura con un nombre estable y cerrar sus recursos gráficos.
    def save(fig, name):
        fig.savefig(destination / f"auditoria_4_1_{name}.png", dpi=140, bbox_inches="tight")
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), layout="constrained")
    for ax, included, excluded, title in [
        (axes[0], "entrenamiento", "no_madura_entrenamiento", "Ventana anterior a julio de 2016"),
        (axes[1], "validacion", "no_madura_validacion", "Ventana julio–diciembre de 2016"),
    ]:
        for group, label, color in [(included, "Incluidas", "#4477AA"), (excluded, "Apartadas por madurez", "#CC6677")]:
            values = np.sort(features.loc[assigned.eq(group), "lead_time"].to_numpy())
            ax.plot(values, np.arange(1, len(values) + 1) / len(values), label=f"{label} (n={len(values):,})", color=color)
        ax.set(title=title, xlabel="Antelación (días)", ylabel="Fracción acumulada", ylim=(0, 1))
        ax.yaxis.set_major_formatter(PercentFormatter(1))
        ax.legend(fontsize=9)
    save(fig, "01_sesgo_antelacion")

    valid = assigned.eq("validacion")
    y_valid = target.loc[valid].to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), layout="constrained")
    axes[0].hist([p_train, p_valid], bins=np.linspace(0, 1, 41), density=True, histtype="step",
                 label=["Entrenamiento (ajuste interno)", "Validación"], color=["#4477AA", "#CC6677"], linewidth=1.6)
    axes[0].set(title="Probabilidades: entrenamiento y validación", xlabel="Probabilidad predicha de cancelación", ylabel="Densidad", xlim=(0, 1))
    axes[0].legend(fontsize=9)
    for value, label, color in [(0, "No canceladas", "#4477AA"), (1, "Canceladas", "#CC6677")]:
        axes[1].hist(p_valid[y_valid == value], bins=np.linspace(0, 1, 41), density=True, histtype="step", label=label, color=color, linewidth=1.6)
    axes[1].axvline(.5, color="gray", linestyle="--", label="Umbral histórico 0,5")
    axes[1].set(title="Validación: distribución por clase real", xlabel="Probabilidad predicha de cancelación", ylabel="Densidad", xlim=(0, 1))
    axes[1].legend(fontsize=9)
    save(fig, "02_distribucion_probabilidades")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), layout="constrained")
    axes[0].plot([0, 1], [0, 1], "--", color="gray", label="Calibración ideal")
    axes[0].plot(calibration.probabilidad_media, calibration.tasa_observada, marker="o", color="#4477AA", label="Logística: validación")
    for row in calibration.itertuples():
        axes[0].annotate(f"n={row.registros}", (row.probabilidad_media, row.tasa_observada), xytext=(3, 6), textcoords="offset points", fontsize=8)
    axes[0].set(title="Fiabilidad en diez bandas fijas", xlabel="Probabilidad media predicha", ylabel="Tasa de cancelación observada", xlim=(0, 1), ylim=(0, 1.05))
    axes[0].legend(fontsize=9)
    axes[1].bar(np.arange(len(calibration)), calibration.registros, color="#4477AA")
    axes[1].set(title="Soporte de cada banda de calibración", xlabel="Banda de probabilidad", ylabel="Registros")
    axes[1].set_xticks(np.arange(len(calibration)), [f"{i/10:.1f}–{(i+1)/10:.1f}" for i in range(len(calibration))], rotation=45)
    save(fig, "03_calibracion_validacion")

    # Describir precision y recall desde scores existentes, sin elegir otra decisión con prueba.
    precision, recall, _ = precision_recall_curve(y_valid, p_valid)
    ap = average_precision_score(y_valid, p_valid)
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8), layout="constrained")
    axes[0].plot(recall, precision, color="#4477AA", label=f"Logística: AP={ap:.4f}")
    axes[0].axhline(y_valid.mean(), linestyle="--", color="gray", label=f"Prevalencia de validación: {y_valid.mean():.2%}")
    for threshold in [.10, .20, .50]:
        row = thresholds.loc[np.isclose(thresholds.umbral, threshold)].iloc[0]
        axes[0].scatter(row.recall, row.precision, color="#CC6677", s=30)
        axes[0].annotate(f"t={threshold:.2f}", (row.recall, row.precision), xytext=(5, 8), textcoords="offset points", fontsize=9)
    axes[0].set(title="Precision-recall: solo validación", xlabel="Recall (cancelaciones detectadas)", ylabel="Precision (acierto entre alertas)", xlim=(0, 1), ylim=(0, 1.03))
    axes[0].legend(fontsize=8)
    for column, label in [("precision", "Precision"), ("recall", "Recall"), ("f1", "F1")]:
        axes[1].plot(thresholds.umbral, thresholds[column], marker="o", markersize=3, label=label)
    axes[1].axvline(.5, color="gray", linestyle="--", label="Umbral histórico 0,5")
    axes[1].set(title="Rejilla descriptiva de umbrales", xlabel="Umbral (sin elección definitiva)", ylabel="Valor de la métrica", xlim=(0, 1), ylim=(0, 1.03))
    axes[1].legend(fontsize=9)
    save(fig, "04_precision_recall_umbrales")


# Formatear una tabla de auditoría respetando sus columnas y valores.
def _markdown_table(table, percentages=(), integers=()):
    table = table.copy()
    for column in percentages:
        table[column] = table[column].map(lambda x: f"{100*x:.2f}%")
    for column in integers:
        table[column] = table[column].map(lambda x: f"{int(x):,}")
    for column in table:
        if pd.api.types.is_float_dtype(table[column]):
            table[column] = table[column].map(lambda x: f"{x:.4f}")
    lines = ["| " + " | ".join(table.columns) + " |", "| " + " | ".join(["---"] * len(table.columns)) + " |"]
    lines += ["| " + " | ".join(str(x) for x in row) + " |" for row in table.itertuples(index=False, name=None)]
    return "\n".join(lines)


# Redactar tablas, metodología y limitaciones desde resultados calculados o guardados.
def write_report(root, result):
    tables = {name: pd.DataFrame(rows) for name, rows in result["tablas"].items()}
    profiles = tables["perfiles_seleccion"]
    diagnostics = tables["diagnosticos_train_validacion"]
    distribution = tables["distribucion_probabilidades"]
    thresholds = tables["umbrales_validacion"]
    t10 = thresholds.loc[np.isclose(thresholds.umbral, .1)].iloc[0]
    t20 = thresholds.loc[np.isclose(thresholds.umbral, .2)].iloc[0]
    t50 = thresholds.loc[np.isclose(thresholds.umbral, .5)].iloc[0]
    extra_fp = int(t10.falsos_positivos - t50.falsos_positivos)
    reduced_fn = int(t50.falsos_negativos - t10.falsos_negativos)
    ratio = extra_fp / reduced_fn
    val_distribution = distribution.loc[distribution.grupo.eq("validacion")].iloc[0]
    calibration = result["calibracion"]
    report = f"""# Fase 4.1 — Auditoría metodológica del baseline

Fecha: 18 de octubre de 2026. Alcance exclusivo de auditoría. Separador decimal de tablas: punto; miles: coma. No se modifican datos, particiones, umbral histórico, parámetros o entregables de fases anteriores. No se usan predicciones de prueba ni se entrena ningún algoritmo nuevo.

## 1. Dictamen

**La implementación del pipeline de regresión logística es correcta respecto a la separación de transformaciones, pero la división temporal solo es defendible como benchmark retrospectivo condicionado a su población elegible. No demuestra una simulación de producción completa.** La selección por madurez sesga antelación y composición. Además, prueba no incorpora una fecha global de cierre ni filtro de madurez. La disponibilidad real de las etiquetas no puede garantizarse con los archivos disponibles.

**No recomiendo pasar todavía a una comparación formal de modelos.** Primero se debe acordar población objetivo, seguimiento y cierre verificable, y aprobar el protocolo corregido. Una comparación académica exploratoria en la validación actual sería posible si se declara expresamente su alcance restringido; no se ha realizado en esta auditoría. No se selecciona un umbral definitivo.

## 2. Qué fechas representan los datos

| Concepto | Representación utilizada | Lo que no demuestra |
|---|---|---|
| Creación de reserva | Llegada prevista menos lead_time, a precisión de día | No hay marca de creación exacta, hora o historial de cambios. |
| Llegada | Reconstruida con año, mes y día previstos | No es alta ni cancelación y puede haber sido modificada. |
| Estado final fechado | reservation_status_date, exclusivamente como metadato | No es necesariamente primera disponibilidad del desenlace ni log de ingestión/publicación. |
| Madurez aproximada | max(llegada + noches, fecha_estado_final) + 1 día | Es una cota artificial conservadora, no conocimiento real demostrado. |
| Cierre de observación de resultados | No está documentado | No se puede inferir un cierre certificado del último día de llegada ni del máximo estado observado. |

Se reprodujeron las fórmulas y se verificó el manifiesto contra temporal_split sin escribirlo. Entrenamiento exige proxy y madurez anteriores al 01/07/2016. Validación exige proxy desde esa fecha hasta antes del 01/01/2017, y madurez anterior al 01/01/2017. Ambos usan desigualdad estricta. Esto añade un margen diario conservador y retrasa también cancelaciones que ya tienen un estado fechado antes de la salida prevista.

No hay un as_of_date global en src/splitting.py. Prueba se asigna únicamente por proxy >= 01/01/2017. Por tanto, no existe un filtro que garantice que su resultado estuviera disponible al cierre. La regla no se ha modificado.

## 3. Reservas apartadas y sesgo de selección

Las 30.386 reservas siguen en el dataset y en el manifiesto: 17.825 pertenecen al periodo de entrenamiento pero no pasan su madurez, y 12.561 al de validación pero no pasan la suya. No son necesariamente etiquetas desconocidas realmente; son **no elegibles bajo la regla implementada**. No se desplazaron a periodos posteriores ni se borraron.

{_markdown_table(profiles[["grupo", "registros", "tasa_cancelacion", "lead_time_media", "lead_time_mediana", "lead_time_p90", "noches_media", "fraccion_city", "estado_final_fechado_antes_corte"]], percentages=["tasa_cancelacion", "fraccion_city"], integers=["registros", "estado_final_fechado_antes_corte"])}

Las comparaciones se hacen dentro de cada ventana del proxy para no confundir toda la diferencia con el cambio de semestre. Hay un sesgo claro hacia menor antelación: mediana 24 días en validación frente a 161 en su grupo apartado; también cambia duración, segmento y tasa de cancelación. En entrenamiento las medianas son 55 frente a 200 días. Las reservas apartadas no son una muestra aleatoria.

Gráfico: [distribuciones acumuladas de antelación](figures/auditoria_4_1_01_sesgo_antelacion.png).

En la validación incluida, Online TA representa aproximadamente 60.04% y Groups 5.07%; en su grupo apartado son 53.19% y 26.89%. El perfil categórico completo está en el CSV auxiliar. El descenso de la tasa entre entrenamiento y validación no puede interpretarse solo como cambio temporal genuino: selección y composición también intervienen.

Hay **5.868** apartadas del periodo de entrenamiento y **4.157** del de validación cuyo estado final está fechado antes de su corte. La regla las retrasa igualmente por la salida prevista o el margen diario. Eso prueba que “apartada por madurez” no equivale a “no hay una fecha de estado anterior”; no prueba que el hotel tuviera efectivamente publicada la etiqueta. No se incorporan automáticamente: hacerlo requiere definir la disponibilidad y revisar el sesgo de observar antes cancelaciones que no cancelaciones.

La extracción está acotada por llegadas. Al clasificar por creación aproximada, faltan además reservas creadas en esas ventanas con llegadas fuera de la cobertura; no basta con recuperar las filas apartadas para reconstruir todas las altas. El proxy anterior a julio de 2015 no implica un histórico completo desde 2013.

## 4. Prueba y cierre del periodo

Última llegada observada: {result['fechas']['ultimo_dia_llegadas']}. Máxima fecha de estado global y de prueba: {result['fechas']['max_fecha_estado_prueba']}. Máxima cota artificial de madurez en prueba: {result['fechas']['max_cota_madurez_prueba']}.

La inspección de prueba en esta auditoría se limita a estas fechas y las comparaciones de elegibilidad. No se analizan sus puntuaciones, calibración, clases para elegir umbral ni métricas predictivas.

{_markdown_table(tables['cierres_hipoteticos'], integers=["registros_prueba", "fecha_estado_en_o_despues_del_corte", "no_cumple_regla_madurez", "cumple_regla_madurez"])}

Los cortes son exclusivos. Si se toma hipotéticamente el cierre del último día de llegadas (31/08/2017; corte 01/09/2017), **368** registros de prueba tienen estado fechado en septiembre y **652** no pasan la regla actual de madurez. No se puede afirmar que toda prueba fuera conocida al acabar agosto. Con corte 15/09 quedan dos registros sin pasar la cota; con 16/09 todos pasarían matemáticamente. **No se elige 16/09 como cierre:** derivarlo del máximo observado sería circular y no certifica seguimiento, ausencia de retrasos o integridad de extracción. Los máximos observados no documentan un as_of_date.

En consecuencia, **la madurez real de todas las etiquetas de prueba no está garantizada**. No se eliminó ninguna de esas filas, ni se modificó el manifiesto o la prueba.

## 5. Auditoría del pipeline y reproducción controlada

El baseline no estaba serializado. Para obtener probabilidades de entrenamiento se reprodujo exclusivamente la misma logística con los mismos parámetros, las mismas 48.428 filas y semilla 42. No se usó fit_and_validate, porque esa función transformaría también prueba; la nueva función solo recibe X_train, y_train y X_valid. No se sustituyó ni persistió el modelo original.

Las probabilidades reproducidas de validación coinciden con el CSV de fase 4 con diferencia máxima {result['reproduccion']['max_diferencia_probabilidad_validacion']:.3g}. Se verificaron medianas numéricas, medias/escalas y categorías contra entrenamiento, así como las 191 columnas transformadas registradas en fase 4. El fit convergió en {result['reproduccion']['iteraciones'][0]} iteraciones. No se cambió C, class_weight, solver, max_iter o el umbral histórico 0.5.

Se mantienen seis numéricas (lead_time, total_nights, adults, children, babies, children_missing) y ocho categóricas (hotel, arrival_date_month, meal, country, market_segment, distribution_channel, reserved_room_type, customer_type). La lista explícita del ColumnTransformer excluye etiqueta, estados, otros campos dudosos y todos los metadatos. No se detectó fuga por ajuste de preprocesamiento con validación o prueba. **Eso no certifica snapshots iniciales de los predictores:** esa limitación semántica continúa.

OneHotEncoder usa handle_unknown='ignore': una categoría inédita se transforma en un bloque de ceros, sin aprender su efecto. El imputador categórico usa Desconocido; no es necesariamente equivalente a una categoría inédita.

{_markdown_table(tables['categorias_nuevas_validacion'], integers=["registros_validacion_categoria_no_vista", "n_categorias_no_vistas"])}

## 6. Entrenamiento frente a validación y distribución probabilística

{_markdown_table(diagnostics, integers=['registros'])}

Las cifras de entrenamiento son **de ajuste interno, optimistas**, no una validación independiente. El descenso de métricas puede reflejar sobreajuste, cambio temporal, composición y censura; estas cifras no permiten atribuirlo a una única causa.

{_markdown_table(distribution, percentages=['tasa_observada', 'probabilidad_media', 'fraccion_alertas_05'])}

En validación la probabilidad media es {val_distribution.probabilidad_media:.2%} frente a {val_distribution.tasa_observada:.2%} observado: infrapredicción media de {-calibration['sesgo_media_predicha_menos_observada']*100:.2f} puntos porcentuales. La mediana es {val_distribution.probabilidad_mediana:.4f}; solo {val_distribution.fraccion_alertas_05:.2%} supera o iguala 0.5. El umbral histórico queda por encima de la mayor parte de las puntuaciones. Los histogramas y la fiabilidad se generan exclusivamente con entrenamiento/validación.

Gráfico: [distribución de probabilidades](figures/auditoria_4_1_02_distribucion_probabilidades.png).

## 7. Calibración: indicios y límites

{_markdown_table(tables['calibracion_validacion'], integers=['registros', 'cancelaciones'])}

Las diez bandas son fijas. Se compara probabilidad media con tasa observada y soporte; bandas altas con pocos casos son inestables. La desviación media y el diagrama indican infrapredicción en esta población. El error absoluto de calibración agrupado (ECE descriptivo, dependiente de bandas) es {calibration['ece_10_bandas_descriptivo']:.4f}; no es una prueba formal ni una corrección.

La infrapredicción no es uniforme: por debajo de 0.5 las tasas observadas superan generalmente las probabilidades medias, mientras que varias bandas superiores a 0.5 sobreestiman el riesgo. La banda 0.9–1.0 contiene solo cinco reservas. El parecido de la media predicha y observada en entrenamiento no acredita calibración fuera de muestra.

Gráfico: [fiabilidad y soporte de bandas](figures/auditoria_4_1_03_calibracion_validacion.png).

Brier/log-loss de la logística están en la tabla de diagnósticos. Como referencia probabilística legítima se usa la prevalencia de entrenamiento ({calibration['prior_train_constante']:.4f}) constante, sin aprender de validación: Brier {calibration['brier_referencia_constante_train_en_validacion']:.4f} y log-loss {calibration['log_loss_referencia_constante_train_en_validacion']:.4f}. No se usa la prevalencia de validación para ajustar esa referencia. Brier y log-loss mezclan discriminación y calibración; una mejora frente a una constante no demostraría buena calibración.

No se ajustó calibración isotónica, sigmoide ni otro algoritmo. Cualquier calibración futura requiere datos de desarrollo separados o predicciones fuera de muestra, sin contaminar la prueba final. Los duplicados/dependencias impiden asumir observaciones independientes sin justificación; no se añadieron intervalos de confianza con esa premisa.

## 8. Umbrales: margen de mejora sin selección definitiva

Regla: alerta si p >= umbral. Rejilla descriptiva fijada en código, sin búsqueda continua, sin máximo F1 elegido y sin acceder a prueba. Precision sin alertas se representa como cero, no como un valor estimable entre alertas inexistentes.

{_markdown_table(thresholds[["umbral", "precision", "recall", "f1", "falsos_positivos", "falsos_negativos", "alertas"]], percentages=['precision', 'recall'], integers=['falsos_positivos', 'falsos_negativos', 'alertas'])}

El punto histórico 0.50 reproduce FP={int(t50.falsos_positivos):,}, FN={int(t50.falsos_negativos):,}, precision {t50.precision:.2%} y recall {t50.recall:.2%}. A 0.20 el recall sube a {t20.recall:.2%}, con {int(t20.falsos_positivos):,} falsas alertas. A 0.10 llega a {t10.recall:.2%}, con {int(t10.falsos_positivos):,} falsas alertas y precision {t10.precision:.2%}. Frente a 0.50, este último escenario detectaría {reduced_fn:,} cancelaciones adicionales a costa de {extra_fp:,} falsos positivos adicionales y de una mayor carga de seguimiento.

La curva precision-recall tiene average precision de validación {diagnostics.loc[diagnostics.grupo.eq('validacion'), 'average_precision'].iloc[0]:.4f}, con prevalencia {val_distribution.tasa_observada:.4f} como referencia de contexto. AP no es el promedio simple de precision/recall ni demuestra utilidad económica. Cambiar el umbral no altera la ordenación/AUC ni corrige la calibración ni recupera las reservas excluidas; cambia la política de alertas sobre las mismas puntuaciones. Las cifras obtenidas al inspeccionar muchos umbrales en validación deben confirmarse posteriormente; no son una evaluación final independiente.

Gráfico: [curva precision-recall y rejilla de umbrales](figures/auditoria_4_1_04_precision_recall_umbrales.png).

## 9. Consecuencias y escenarios de negocio

Un falso negativo deja sin anticipar una cancelación, con posibles errores en previsiones de ocupación y planificación. Un falso positivo puede provocar seguimiento innecesario o contacto molesto con un cliente que mantiene la reserva. Detectar una cancelación no demuestra que una intervención la evite, ni que toda cancelación suponga una pérdida neta de igual importe.

**Supuestos ilustrativos, no costes reales:** penalización relativa FP=1; FN=1, 3 o 10 unidades abstractas. Se calcula FP + r*FN, sin euros y sin seleccionar el menor valor como política definitiva.

{_markdown_table(tables['escenarios_coste_relativo'].loc[tables['escenarios_coste_relativo'].umbral.isin([.1,.2,.3,.5,.7])], integers=['falsos_positivos', 'falsos_negativos', 'alertas', 'unidades_relativas_FP_1_FN_1', 'unidades_relativas_FP_1_FN_3', 'unidades_relativas_FP_1_FN_10'])}

Para la comparación específica 0.10 frente a 0.50, bajo este modelo simplificado el menor umbral compensa la penalización adicional de falsos positivos solo si FN pesa más de {ratio:.3f} veces FP. Esta cuenta es retrospectiva sobre validación, no un coste estimado ni garantía futura. Falta coste de actuar incluso sobre verdaderos positivos, capacidad de seguimiento, eficacia de la intervención y diferencias entre reservas. No puede fijarse un umbral solo por F1 ni convertir probabilidades mal calibradas en una decisión económica exacta.

## 10. Corrección propuesta ANTES de cualquier modificación

1. Obtener fecha de extracción/cierre de resultados documentada y, si existen, logs de creación, cambios de predictores y disponibilidad de etiquetas. No inferir cierre del máximo observado. Mantener prueba congelada hasta aprobar este contrato temporal.
2. Definir la población: todas las altas o solo reservas con horizonte operativo acotado. Si se mantiene una población acotada, justificar un horizonte/capacidad de seguimiento con negocio antes de comparar algoritmos; no elegirlo por métricas.
3. Construir cohortes completas con seguimiento suficiente. La elegibilidad debería depender de reglas operativas conocidas al predecir y un seguimiento prefijado, no de conservar solo los desenlaces ya observados de una cohorte incompleta. Recuperar datos de llegadas fuera de la extracción si se pretende representar todas las altas.
4. Verificar disponibilidad de etiquetas de entrenamiento antes del primer corte, y de validación antes de cualquier decisión que preceda a prueba. Añadir a validación las 12.561 apartadas usando desenlaces posteriores y mantener prueba desde enero de 2017 **no sería una corrección válida** para seleccionar modelos en enero: emplearía resultados futuros. Harían falta ventanas de validación más tempranas, prueba posterior, un horizonte operativo previo o más datos, con la nueva política explícitamente aprobada.
5. Establecer un as_of_date para prueba y su regla de madurez/seguimiento antes de evaluar. Si un escenario exige excluir filas, registrar el cambio y los motivos; los conteos de esta auditoría son hipotéticos, no un nuevo conjunto. No excluir automáticamente las 652 del escenario de agosto ni adoptar septiembre como cierre por conveniencia.
6. Si no se consigue la documentación, reformular el alcance como benchmark retrospectivo de una cohorte de llegadas y declarar que no reproduce todas las nuevas reservas en tiempo real. Cambiar solo a cortes por llegada cambia el objetivo de evaluación y no prueba disponibilidad al crear la reserva.

**No se aplica ninguna corrección de particiones en esta fase.** Tampoco se cambia el modelo o su umbral histórico. Esta auditoría distingue corrección técnica del pipeline de validez del diseño poblacional/temporal.

## 11. Entregables y verificación

Se crean src/audit_baseline.py, tests/test_audit_baseline.py, este informe, auditoria_4_1_resultados.json, nueve CSV auxiliares y cuatro figuras auditoria_4_1_*.png. README solo añade el enlace y el dictamen de auditoría. Los entregables de fases anteriores, original, preparado y manifiesto se comprueban por SHA-256 y se mantienen intactos. El registro completo de huellas está en el JSON de resultados.

La reproducción usa el mismo algoritmo y parámetros, no alternativas ni optimización. Las predicciones de validación coinciden con las guardadas. Los tests auxiliares comprueban conteos/fronteras de umbral, bandas de calibración y escenarios temporales sin modificación de sus entradas. Prueba no recibe predict, predict_proba, transform, calibración ni análisis de umbral durante esta auditoría: solo se examinan sus metadatos de fechas necesarios para la pregunta temporal.

Reproducción desde la raíz: `.venv\\Scripts\\python.exe -m src.audit_baseline`. Las salidas son exclusivamente de auditoría. La comparación de algoritmos requiere aprobación posterior y no se ha iniciado.

**Fin de fase 4.1. Detenerse y presentar el dictamen para revisión.**
"""
    (root / "reports/fase_4_1_auditoria.md").write_text(report, encoding="utf-8")


# Ejecutar la entrada principal solo al invocar este archivo como script.
if __name__ == "__main__":
    result = run_audit()
    print(json.dumps({"informe": "reports/fase_4_1_auditoria.md", "reservas_apartadas": result["reservas_apartadas"],
                      "reproduccion": result["reproduccion"], "calibracion": result["calibracion"],
                      "madurez_real_garantizada": result["madurez_real_garantizada"],
                      "prueba_solo_metadatos_temporales": True}, ensure_ascii=False, indent=2))
