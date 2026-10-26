"""Protocolo v2 aproximado y reproducción explícita del protocolo histórico v1."""
import pandas as pd

from src.preparation import TEMPORAL_PLAN


PARTITIONS_LEGACY = ["entrenamiento", "validacion", "prueba_reservada",
                     "no_madura_entrenamiento", "no_madura_validacion"]
PARTITIONS = PARTITIONS_LEGACY + ["no_madura_prueba"]
PROTOCOL_V2 = {
    "version": "v2_estado_fechado_aproximado",
    "validation_start": "2016-07-01", "test_start": "2017-01-01",
    "assumed_as_of_exclusive": "2018-12-01", "accredited_as_of": None,
    "status_recording_lag_days": 1,
    "publication_date_reference": "2018-11-29",
    "as_of_basis": "Supuesto retrospectivo: comienzo del mes siguiente a la publicación; no fecha de extracción ni cierre PMS acreditados.",
    "availability_rule": "reservation_status_date + 1 día, estrictamente anterior al corte; aproximación, no primera disponibilidad demostrada.",
}


def temporal_split_legacy(metadata, validation_start=None, test_start=None):
    """Asigna cada fila una sola vez; las etiquetas tardías quedan en auditoría."""
    first = pd.Timestamp(validation_start or TEMPORAL_PLAN["corte_validacion"])
    second = pd.Timestamp(test_start or TEMPORAL_PLAN["corte_prueba"])
    if first >= second:
        raise ValueError("El corte de validación debe preceder al de prueba.")
    if not metadata.index.is_unique or not metadata.meta_row_id.is_unique:
        raise ValueError("La trazabilidad de filas debe ser única.")
    booking = pd.to_datetime(metadata.meta_booking_date_proxy, errors="raise")
    mature = pd.to_datetime(metadata.meta_label_available_after, errors="raise")
    if booking.isna().any() or mature.isna().any():
        raise ValueError("No se permiten fechas desconocidas en la partición.")
    if mature.le(booking).any():
        raise ValueError("La madurez debe ser posterior al proxy de reserva.")
    masks = {
        "entrenamiento": booking.lt(first) & mature.lt(first),
        "validacion": booking.ge(first) & booking.lt(second) & mature.lt(second),
        "prueba_reservada": booking.ge(second),
        "no_madura_entrenamiento": booking.lt(first) & mature.ge(first),
        "no_madura_validacion": booking.ge(first) & booking.lt(second) & mature.ge(second),
    }
    if not pd.DataFrame(masks).sum(axis=1).eq(1).all():
        raise ValueError("Las particiones deben cubrir todas las filas una sola vez.")
    assigned = pd.DataFrame(masks).idxmax(axis=1).rename("particion")
    grouped = pd.DataFrame({"grupo": metadata.meta_duplicate_group, "particion": assigned})
    if grouped.groupby("grupo").particion.nunique().gt(1).any():
        raise ValueError("Un grupo duplicado cruza particiones.")
    return assigned


def add_status_availability(metadata, status_dates):
    """Añade un proxy de disponibilidad SOLO a los metadatos, sin tocar X o raw."""
    if not metadata.index.equals(status_dates.index):
        raise ValueError("Fechas de estado y metadatos deben estar alineados por fila.")
    dates = pd.to_datetime(status_dates, errors="raise")
    if dates.isna().any():
        raise ValueError("No se puede auditar disponibilidad sin fecha de estado.")
    result = metadata.copy(deep=True)
    result["meta_label_available_proxy"] = dates + pd.Timedelta(days=PROTOCOL_V2["status_recording_lag_days"])
    return result


def temporal_split(metadata, validation_start=None, test_start=None, as_of_date=None):
    """V2: usa estado fechado + margen; prueba también exige elegibilidad al cierre asumido."""
    first = pd.Timestamp(validation_start or PROTOCOL_V2["validation_start"])
    second = pd.Timestamp(test_start or PROTOCOL_V2["test_start"])
    close = pd.Timestamp(as_of_date or PROTOCOL_V2["assumed_as_of_exclusive"])
    if not first < second < close:
        raise ValueError("Los cortes deben cumplir entrenamiento < prueba < cierre.")
    if not metadata.index.is_unique or not metadata.meta_row_id.is_unique:
        raise ValueError("Se requiere trazabilidad de filas única.")
    if "meta_label_available_proxy" not in metadata:
        raise ValueError("Falta el proxy v2 de disponibilidad; no usar automáticamente la cota v1.")
    booking = pd.to_datetime(metadata.meta_booking_date_proxy, errors="raise")
    available = pd.to_datetime(metadata.meta_label_available_proxy, errors="raise")
    if booking.isna().any() or available.isna().any():
        raise ValueError("No se permiten fechas desconocidas.")
    if available.le(booking).any():
        raise ValueError("Disponibilidad no posterior al proxy de reserva: requiere revisión.")
    # La selección usa fechas, nunca el valor 0/1 de la etiqueta o una métrica.
    masks = {
        "entrenamiento": booking.lt(first) & available.lt(first),
        "validacion": booking.ge(first) & booking.lt(second) & available.lt(second),
        "prueba_reservada": booking.ge(second) & available.lt(close),
        "no_madura_entrenamiento": booking.lt(first) & available.ge(first),
        "no_madura_validacion": booking.ge(first) & booking.lt(second) & available.ge(second),
        "no_madura_prueba": booking.ge(second) & available.ge(close),
    }
    if not pd.DataFrame(masks).sum(axis=1).eq(1).all():
        raise ValueError("Cada fila debe tener exactamente una asignación.")
    assigned = pd.DataFrame(masks).idxmax(axis=1).rename("particion")
    groups = pd.DataFrame({"grupo": metadata.meta_duplicate_group, "particion": assigned})
    if groups.groupby("grupo").particion.nunique().gt(1).any():
        raise ValueError("Un grupo duplicado cruza particiones.")
    return assigned


def describe_split(features, target, metadata, assigned):
    """Resumen descriptivo de clases/fechas; no evalúa predicciones en prueba."""
    rows = []
    for partition in PARTITIONS_LEGACY:
        mask = assigned.eq(partition)
        dates = metadata.loc[mask]
        n = int(mask.sum())
        row = {"particion": partition, "registros": n,
               "no_canceladas": int(target.loc[mask].eq(0).sum()),
               "canceladas": int(target.loc[mask].eq(1).sum()),
               "tasa_cancelacion": float(target.loc[mask].mean()) if n else None}
        for column, prefix in [("meta_booking_date_proxy", "proxy"),
                               ("meta_arrival_date", "llegada"),
                               ("meta_label_available_after", "madurez")]:
            values = pd.to_datetime(dates[column])
            row[prefix + "_min"] = str(values.min().date()) if n else None
            row[prefix + "_max"] = str(values.max().date()) if n else None
        rows.append(row)
    train = assigned.eq("entrenamiento")
    arrival_month = pd.to_datetime(metadata.loc[train, "meta_arrival_date"]).dt.month
    hotel_months = pd.crosstab(features.loc[train, "hotel"], arrival_month).reindex(columns=range(1, 13), fill_value=0)
    return pd.DataFrame(rows), hotel_months
