# Preparación de las 119.390 filas sin entrenar transformadores o modelos.
"""Prepara un único CSV sin ajuste estadístico, particiones ni modelos."""
from pathlib import Path
import hashlib
import json

import pandas as pd

from src.cleaning import clean
from src.features import build_features, build_metadata, separate_model_data, audit_availability, TARGET, FEATURES


TEMPORAL_PLAN = {
    "estado": "propuesta pendiente de implementar y revisar en fase 4",
    "ordenacion": "meta_booking_date_proxy; nunca equivale a creación observada",
    "corte_validacion": "2016-07-01",
    "corte_prueba": "2017-01-01",
    "entrenamiento": "proxy < corte_validacion Y label_available_after < corte_validacion",
    "validacion": "corte_validacion <= proxy < corte_prueba Y label_available_after < corte_prueba",
    "prueba": "proxy >= corte_prueba; evaluar solo etiquetas maduras en el momento del análisis",
    "etiquetas": "label_available_after = max(llegada + noches, fecha_estado_final) + 1 día; cota offline no probada como disponibilidad real",
    "grupos": "mantener fechas iguales juntas; verificar que ninguna huella de duplicados cruce conjuntos",
    "transformadores": "fit únicamente en entrenamiento; transform en validación/prueba",
}


def prepare_data(raw):
    """Todas las filas y su orden se mantienen; las decisiones son deterministas."""
    if not raw.index.is_unique:
        raise ValueError("Se requiere índice de fila único para la trazabilidad técnica.")
    cleaned = clean(raw)
    features = build_features(cleaned)
    metadata = build_metadata(raw, cleaned)
    prepared = pd.concat([features, cleaned[TARGET], metadata], axis=1)
    assert len(prepared) == len(raw)
    return prepared


# Verificar el original, exportar la preparación y contrastar su lectura posterior.
def run_preparation(project_root=None):
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    source = root / "data/raw/hotel_bookings.csv"
    with source.open("rb") as file:
        # Calcular una huella determinista para trazabilidad; no usarla como característica predictiva.
        checksum = hashlib.file_digest(file, "sha256").hexdigest()
    expected = json.loads((root / "reports/inspeccion_dataset.json").read_text(encoding="utf-8"))["sha256_csv"]
    if checksum != expected:
        raise ValueError("El CSV original no coincide con la huella de fase 1.")
    raw = pd.read_csv(source, encoding="utf-8", encoding_errors="strict")
    audit_availability(raw.columns).to_csv(root / "reports/preparacion_auditoria_variables.csv", index=False, encoding="utf-8")
    prepared = prepare_data(raw)
    features, target, metadata = separate_model_data(prepared)
    destination = root / "data/processed/hotel_bookings_prepared.csv"
    destination.parent.mkdir(exist_ok=True)
    prepared.to_csv(destination, index=False, date_format="%Y-%m-%d", encoding="utf-8")
    reloaded = pd.read_csv(destination, encoding="utf-8")
    x_reload, y_reload, _ = separate_model_data(reloaded)
    pd.testing.assert_frame_equal(features, x_reload)
    pd.testing.assert_series_equal(target, y_reload)
    with source.open("rb") as file:
        # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
        assert hashlib.file_digest(file, "sha256").hexdigest() == checksum
    # Calcular una huella determinista para trazabilidad; no usarla como característica predictiva.
    summary = {
        "filas_originales": len(raw), "filas_conservadas": len(prepared), "filas_excluidas": 0,
        "duplicados_adicionales_conservados": int(raw.duplicated().sum()),
        "predictores": FEATURES, "n_predictores": len(FEATURES),
        "objetivo": TARGET, "columnas_metadatos": list(metadata.columns),
        "columnas_exportadas": len(prepared.columns),
        "nulos_predictores_sin_imputar": {k: int(v) for k, v in features.isna().sum().items() if v},
        "indicadores_calidad": {c: int(metadata[c].sum()) for c in metadata.columns if c.startswith("meta_") and c not in ["meta_row_id", "meta_duplicate_group", "meta_arrival_date", "meta_booking_date_proxy", "meta_label_available_after"]},
        "sha256_original": checksum,
        "archivo_preparado": str(destination.relative_to(root)).replace("\\", "/"),
        "sha256_preparado": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "ajuste_transformadores_reales": False, "particiones_creadas": False, "modelos_entrenados": False,
        "estrategia_temporal": TEMPORAL_PLAN,
    }
    (root / "reports/preparacion_resumen.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


# Ejecutar la entrada principal solo al invocar este archivo como script.
if __name__ == "__main__":
    print(json.dumps(run_preparation(), ensure_ascii=False, indent=2))
