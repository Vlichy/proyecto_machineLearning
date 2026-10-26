"""Limpieza determinista: conserva filas y no aprende estadísticas del conjunto."""
import numpy as np
import pandas as pd


MONTHS = {name: number for number, name in enumerate([
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
], start=1)}


def clean(df):
    """Devuelve una copia tipada, sin eliminar duplicados ni imputar desconocidos."""
    data = df.copy(deep=True)
    if data.is_canceled.isna().any() or not data.is_canceled.isin([0, 1]).all():
        raise ValueError("La etiqueta debe contener únicamente 0/1, sin nulos.")
    data["is_canceled"] = data.is_canceled.astype("int64")
    # Las cuentas enteras conservan la ausencia mediante Int64 nullable.
    counts = ["children", "adults", "babies", "lead_time", "stays_in_week_nights",
              "stays_in_weekend_nights", "arrival_date_year", "arrival_date_day_of_month",
              "arrival_date_week_number"]
    for column in counts:
        data[column] = pd.to_numeric(data[column], errors="raise").astype("Int64")
        if data[column].lt(0).any():
            raise ValueError(f"Conteo negativo sin política definida: {column}")
    for column in ["agent", "company"]:
        # Un ID no es una magnitud; no se convierte ausencia en agente/empresa 0.
        data[column] = pd.to_numeric(data[column], errors="raise").astype("Int64").astype("string")
    for column in ["hotel", "arrival_date_month", "meal", "country", "market_segment",
                   "distribution_channel", "reserved_room_type", "customer_type"]:
        data[column] = data[column].astype("string")
    # Se desconoce la tarifa correcta: no se adivina su signo o su importe.
    data["adr"] = pd.to_numeric(data.adr, errors="raise").mask(data.adr.lt(0), np.nan)
    return data


def arrival_date(df):
    """Reconstruye la llegada prevista, nunca la fecha observada de creación."""
    result = pd.to_datetime(pd.DataFrame({
        "year": df.arrival_date_year,
        "month": df.arrival_date_month.map(MONTHS),
        "day": df.arrival_date_day_of_month,
    }, index=df.index), errors="raise")
    if result.isna().any():
        raise ValueError("No se permite construir fechas de llegada desconocidas.")
    return result
