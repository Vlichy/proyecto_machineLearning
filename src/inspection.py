# Inspección inicial: dimensiones, tipos, ausentes y repeticiones del CSV.
"""Comprobaciones iniciales sin transformar ni sobrescribir los datos originales."""
from pathlib import Path
import hashlib
import json
import pandas as pd


def inspect_dataset(file_path):
    """Devuelve dimensiones, tipos, nulos y duplicados del CSV original."""
    file_path = Path(file_path)
    df = pd.read_csv(file_path, encoding="utf-8", encoding_errors="strict")
    with file_path.open("rb") as file:
        # Calcular una huella determinista para trazabilidad; no usarla como característica predictiva.
        checksum = hashlib.file_digest(file, "sha256").hexdigest()
    return {
        "sha256_csv": checksum,
        "filas": len(df),
        "columnas": len(df.columns),
        "tipos": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "hoteles": df["hotel"].value_counts(dropna=False).to_dict(),
        "objetivo": {str(key): int(value) for key, value in
                     df["is_canceled"].value_counts(dropna=False).items()},
        "nulos": {column: int(count) for column, count in
                  df.isna().sum().items() if count},
        "duplicados_adicionales": int(df.duplicated().sum()),
        "filas_en_grupos_duplicados": int(df.duplicated(keep=False).sum()),
    }


# Ejecutar la entrada principal solo al invocar este archivo como script.
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    print(json.dumps(inspect_dataset(project_root / "data/raw/hotel_bookings.csv"),
                     ensure_ascii=False, indent=2))
