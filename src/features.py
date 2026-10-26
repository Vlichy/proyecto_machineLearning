# Separación explícita entre predictores, objetivo futuro y metadatos de auditoría.
"""Lista explícita de predictores y separación de etiqueta y metadatos."""
import numpy as np
import pandas as pd

from src.cleaning import arrival_date


# Cerrar las entradas admitidas impide que una columna nueva o un estado final entre por accidente en X.
NUMERIC_FEATURES = ["lead_time", "total_nights", "adults", "children", "babies", "children_missing"]
CATEGORICAL_FEATURES = ["hotel", "arrival_date_month", "meal", "country", "market_segment",
                        "distribution_channel", "reserved_room_type", "customer_type"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "is_canceled"
LEAKAGE_FEATURES = ["reservation_status", "reservation_status_date"]
UNCERTAIN_FEATURES = ["assigned_room_type", "booking_changes", "days_in_waiting_list",
                      "deposit_type", "adr", "total_of_special_requests",
                      "required_car_parking_spaces", "previous_cancellations",
                      "previous_bookings_not_canceled", "is_repeated_guest", "agent", "company"]


def audit_availability(columns):
    """Clasifica las 32 variables: disponibilidad operativa y decisión son distintas."""
    reasons = {
        "reservation_status": "Estado final: revela el desenlace.",
        "reservation_status_date": "Última actualización del estado final, no creación.",
        "assigned_room_type": "Asignación inicial o posterior no distinguible.",
        "booking_changes": "Total acumulado; no se observa su valor en la creación.",
        "days_in_waiting_list": "La espera conocida depende de pre-reserva frente a confirmación.",
        "deposit_type": "Puede ser política inicial válida, pero no se acredita su versión inicial.",
        "adr": "Podría ser tarifa inicial o promedio actualizado; no se acredita snapshot inicial.",
        "total_of_special_requests": "Solicitudes potencialmente añadidas tras reservar.",
        "required_car_parking_spaces": "No se acredita si es petición inicial o posterior.",
        "previous_cancellations": "No hay documentación del instante de cómputo del historial.",
        "previous_bookings_not_canceled": "No hay documentación del instante de cómputo del historial.",
        "is_repeated_guest": "No se acredita versión histórica disponible al reservar.",
        "agent": "ID comercial posiblemente inicial; sin prueba de versión ni significado de ausencias.",
        "company": "ID comercial posiblemente inicial; sin prueba de versión ni significado de ausencias.",
    }
    rows = []
    for column in columns:
        if column == TARGET:
            availability, decision, reason = "No disponible (objetivo futuro)", "Etiqueta separada", "No es una característica."
        elif column in LEAKAGE_FEATURES:
            availability, decision, reason = "No disponible", "Excluir de X", reasons[column]
        elif column in UNCERTAIN_FEATURES:
            availability, decision, reason = "Incierta", "Excluir de X por incertidumbre", reasons[column]
        else:
            availability = "Disponible en la operación inicial (supuesto de trabajo)"
            reason = "Dato del plan de reserva/origen; el archivo no permite certificar su versión inicial."
            if column in FEATURES:
                decision = "Incluir en X bajo supuesto explícito"
            elif column in ["stays_in_week_nights", "stays_in_weekend_nights"]:
                decision = "Sustituir por total_nights en X"
            else:
                decision = "Excluir de X; calendario para auditoría o redundante"
        rows.append({"variable": column, "disponibilidad": availability, "decision": decision, "justificacion": reason})
    return pd.DataFrame(rows)


def build_features(cleaned):
    """Crea predictores sin consultar la etiqueta ni los estados finales."""
    data = cleaned.copy()
    # Sumar noches previstas sin usar el desenlace; esta derivación no aprende parámetros.
    data["total_nights"] = data.stays_in_week_nights + data.stays_in_weekend_nights
    data["children_missing"] = data.children.isna().astype("int64")
    # Extraer exclusivamente los predictores autorizados, en un orden reproducible.
    features = data.loc[:, FEATURES].copy()
    # scikit-learn recibe np.nan, no pd.NA, con semántica numérica/categórica explícita.
    features[NUMERIC_FEATURES] = features[NUMERIC_FEATURES].astype("float64")
    for column in CATEGORICAL_FEATURES:
        features[column] = features[column].astype(object).where(features[column].notna(), np.nan)
    return features


def build_metadata(raw, cleaned):
    """Datos de auditoría/división, separados de X y nunca predictores."""
    arrival = arrival_date(cleaned)
    nights = cleaned.stays_in_week_nights + cleaned.stays_in_weekend_nights
    guests = cleaned[["adults", "children", "babies"]].sum(axis=1, min_count=3)
    status_date = pd.to_datetime(raw.reservation_status_date, errors="raise")
    if status_date.isna().any():
        raise ValueError("Falta fecha del estado final para auditar madurez de etiquetas.")
    departure = arrival + pd.to_timedelta(nights.astype("int64"), unit="D")
    # Regla conservadora propuesta: después de salida prevista Y del último estado.
    # Es una cota de elegibilidad offline, no un timestamp histórico demostrado.
    # Esta cota pertenece a la preparación histórica: no sustituye al protocolo v3 vigente por llegada.
    label_after = pd.concat([departure, status_date], axis=1).max(axis=1) + pd.Timedelta(days=1)
    return pd.DataFrame({
        "meta_row_id": np.arange(len(raw)),
        # Huella técnica del registro completo: no identifica una reserva real.
        # Usa etiqueta/estados solo para auditoría de duplicados, nunca como entrada del modelo.
        "meta_duplicate_group": pd.util.hash_pandas_object(raw, index=False).map(lambda x: f"{x:016x}"),
        "meta_arrival_date": arrival,
        "meta_booking_date_proxy": arrival - pd.to_timedelta(cleaned.lead_time.astype("int64"), unit="D"),
        "meta_label_available_after": label_after,
        "meta_adr_negative": raw.adr.lt(0).astype("int64"),
        "meta_adr_zero": raw.adr.eq(0).astype("int64"),
        "meta_zero_nights": nights.eq(0).astype("int64"),
        "meta_zero_guests": guests.eq(0).fillna(False).astype("int64"),
        "meta_guests_unknown": guests.isna().astype("int64"),
    }, index=raw.index)


def separate_model_data(prepared):
    """Devuelve X, y y metadatos; nunca usar drop(target) para construir X."""
    missing = set(FEATURES + [TARGET]) - set(prepared.columns)
    if missing:
        raise ValueError(f"Faltan columnas preparadas: {sorted(missing)}")
    features = prepared.loc[:, FEATURES].copy()
    features[NUMERIC_FEATURES] = features[NUMERIC_FEATURES].astype("float64")
    for column in CATEGORICAL_FEATURES:
        features[column] = features[column].astype(object).where(features[column].notna(), np.nan)
    target = prepared[TARGET].copy()
    if target.isna().any() or not target.isin([0, 1]).all():
        raise ValueError("Etiqueta preparada inválida.")
    metadata = prepared.filter(regex="^meta_").copy()
    return features, target.astype("int64"), metadata
