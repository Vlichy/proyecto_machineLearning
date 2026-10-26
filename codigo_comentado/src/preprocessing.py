# EDICIÓN COMENTADA PARA LECTURA. Las fuentes ejecutadas y selladas permanecen en la raíz.
# Construcción de transformadores nuevos: sus parámetros se aprenden únicamente en train.
# Solo se añaden comentarios: no se han ejecutado instrucciones de esta copia.
"""Transformadores sin ajustar: aprenderán solo al recibir X_train."""
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.features import NUMERIC_FEATURES, CATEGORICAL_FEATURES


def build_preprocessor(scale_numeric=True):
    """Crea un objeto nuevo y sin fit; no recibe ni consulta el dataset completo."""
    # Definir la imputación; la creación del objeto todavía no calcula estadísticas del dataset.
    numeric_steps = [("imputer", SimpleImputer(strategy="median", keep_empty_features=True))]
    if scale_numeric:
        # Definir el escalado numérico de la logística; media y escala se aprenderán al ajustar.
        numeric_steps.append(("scaler", StandardScaler()))
    numeric = Pipeline(numeric_steps)
    # Codificar las categorías de train e ignorar las nuevas sin aprenderlas de validación o prueba.
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Desconocido", keep_empty_features=True)),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
    ])
    # Seleccionar por nombre y descartar el resto mantiene la etiqueta y los metadatos fuera del modelo.
    return ColumnTransformer([
        ("numeric", numeric, NUMERIC_FEATURES),
        ("categorical", categorical, CATEGORICAL_FEATURES),
    ], remainder="drop", sparse_threshold=1.0)
