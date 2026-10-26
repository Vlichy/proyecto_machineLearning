"""Comparación exploratoria: v2 inmutable, fit train y evaluación validación."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import time
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_curve, precision_recall_curve

from src.baseline import build_logistic_pipeline, evaluate_predictions
from src.preprocessing import build_preprocessor
from src.features import separate_model_data, FEATURES, NUMERIC_FEATURES, CATEGORICAL_FEATURES
from src.splitting import PROTOCOL_V2, add_status_availability, temporal_split


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def model_factories():
    """Una configuración por algoritmo, fijada antes de obtener resultados."""
    from xgboost import XGBClassifier
    from lightgbm import LGBMClassifier
    def tree_pipeline(classifier):
        return Pipeline([('preprocessor', build_preprocessor(scale_numeric=False)),
                         ('classifier', classifier)])
    return {
        'regresion_logistica': build_logistic_pipeline(),
        'arbol_decision': tree_pipeline(DecisionTreeClassifier(
            max_depth=8, min_samples_leaf=20, random_state=42)),
        'random_forest': tree_pipeline(RandomForestClassifier(
            n_estimators=200, min_samples_leaf=5, n_jobs=4, random_state=42)),
        'xgboost': tree_pipeline(XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8,
            colsample_bytree=0.8, tree_method='hist', objective='binary:logistic',
            eval_metric='logloss', n_jobs=4, random_state=42)),
        'lightgbm': tree_pipeline(LGBMClassifier(
            n_estimators=300, num_leaves=31, learning_rate=0.05, min_child_samples=20,
            deterministic=True, force_col_wise=True, verbosity=-1, n_jobs=4, random_state=42)),
    }


def load_development(root):
    """Verifica manifiesto sin escribirlo. Solo devuelve filas de desarrollo."""
    root = Path(root)
    assert sha(root/'data/raw/hotel_bookings.csv') == '7c2ae42a7353905ea136e5c2287f17c92c5435826598bfbb8491c6f0c7b1fc06'
    assert sha(root/'data/processed/hotel_bookings_prepared.csv') == '2718ad6c88b52da2914b54e5f6eccb51815a2ff3c59100793c093292f900c60c'
    baseline = json.loads((root/'reports/baseline_resultados.json').read_text(encoding='utf-8'))
    assert baseline['protocolo_version'] == PROTOCOL_V2['version']
    prepared = pd.read_csv(root/'data/processed/hotel_bookings_prepared.csv')
    assert len(prepared) == 119390
    x, y, meta = separate_model_data(prepared)
    status = pd.read_csv(root/'data/raw/hotel_bookings.csv', usecols=['reservation_status_date'])
    assigned = temporal_split(add_status_availability(meta, status.reservation_status_date))
    manifest = pd.read_csv(root/'reports/particiones_temporales.csv')
    pd.testing.assert_frame_equal(manifest, pd.DataFrame({'meta_row_id': meta.meta_row_id, 'particion': assigned}))
    train, val = assigned.eq('entrenamiento'), assigned.eq('validacion')
    assert (int(train.sum()), int(val.sum())) == (54164, 18097)
    assert list(x.columns) == FEATURES
    return x.loc[train].copy(), y.loc[train].copy(), x.loc[val].copy(), y.loc[val].copy(), meta.loc[val, 'meta_row_id'].copy()


def fit_one(model, x_train, y_train, x_val, y_val):
    """No admite prueba ni eval_set; auditoría de estadísticas y categorías."""
    if not x_train.index.intersection(x_val.index).empty:
        raise ValueError('Entrenamiento y validación se solapan')
    assert list(x_train.columns) == list(x_val.columns) == FEATURES
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        model.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - start
    pre = model.named_steps['preprocessor']
    numeric = pre.named_transformers_['numeric']
    np.testing.assert_allclose(numeric.named_steps['imputer'].statistics_, x_train[NUMERIC_FEATURES].median())
    encoder = pre.named_transformers_['categorical'].named_steps['encoder']
    for actual, column in zip(encoder.categories_, CATEGORICAL_FEATURES):
        np.testing.assert_array_equal(actual, np.unique(x_train[column].fillna('Desconocido').to_numpy(dtype=str)))
    if 'scaler' in numeric.named_steps:
        scaler = numeric.named_steps['scaler']
        assert int(scaler.n_samples_seen_) == len(x_train)
        np.testing.assert_allclose(scaler.mean_, x_train[NUMERIC_FEATURES].fillna(x_train[NUMERIC_FEATURES].median()).mean())
    before = hashlib.sha256(repr(pre).encode() + numeric.named_steps['imputer'].statistics_.tobytes()
                            + b''.join(c.astype(str).tobytes() for c in encoder.categories_)).hexdigest()
    start = time.perf_counter()
    probability = model.predict_proba(x_val)[:, 1]
    predict_seconds = time.perf_counter() - start
    after = hashlib.sha256(repr(pre).encode() + numeric.named_steps['imputer'].statistics_.tobytes()
                           + b''.join(c.astype(str).tobytes() for c in encoder.categories_)).hexdigest()
    assert before == after
    assert np.isfinite(probability).all() and ((probability >= 0) & (probability <= 1)).all()
    metrics = evaluate_predictions(y_val, probability >= 0.5, probability)
    metrics['average_precision'] = float(average_precision_score(y_val, probability))
    tn, fp, fn, tp = np.array(metrics.pop('matriz_confusion')).ravel()
    metrics.update(tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp),
                   fit_seconds=fit_seconds, predict_seconds=predict_seconds)
    return metrics, probability, [str(w.message) for w in captured]


def run_comparison(root):
    root = Path(root)
    # Todos los archivos preexistentes de datos, informes e historia quedan protegidos.
    protected = list((root/'data').rglob('*')) + list((root/'reports').rglob('*'))
    protected = [p for p in protected if p.is_file() and not p.name.startswith('comparacion_5')
                 and p.name != 'fase_5_comparacion_modelos.md']
    before = {str(p.relative_to(root)): sha(p) for p in protected}
    x_train, y_train, x_val, y_val, ids = load_development(root)
    models = model_factories()
    rows, params, notices = [], {}, {}
    predictions = pd.DataFrame({'meta_row_id': ids, 'is_canceled': y_val})
    for name, model in models.items():
        print('Entrenando:', name, flush=True)
        params[name] = model.named_steps['classifier'].get_params()
        metrics, probability, notices[name] = fit_one(model, x_train, y_train, x_val, y_val)
        rows.append({'modelo': name, **metrics})
        predictions[name] = probability
    reference = pd.read_csv(root/'reports/baseline_predicciones_validacion.csv')
    np.testing.assert_array_equal(ids, reference.meta_row_id)
    np.testing.assert_allclose(predictions.regresion_logistica, reference.probabilidad_logistica, atol=1e-12, rtol=1e-12)
    for relative, expected in before.items():
        assert sha(root/relative) == expected, relative
    table = pd.DataFrame(rows)
    output = root/'reports'
    table.to_csv(output/'comparacion_5_metricas.csv', index=False)
    predictions.to_csv(output/'comparacion_5_predicciones_validacion.csv', index=False)
    detail = {'protocolo': PROTOCOL_V2, 'umbral': 0.5, 'train': len(x_train), 'validacion': len(x_val),
              'features': FEATURES, 'parametros': params, 'advertencias_fit': notices,
              'versiones': {k: importlib.metadata.version(k) for k in ['scikit-learn','xgboost','lightgbm','numpy','pandas']},
              'integridad_archivos': before, 'baseline_v2_reproducido': True,
              'prueba_transformada_predicha_evaluada': False, 'preprocesamiento_auditado_train': True}
    (output/'comparacion_5_verificacion.json').write_text(json.dumps(detail, ensure_ascii=False, indent=2, default=str)+'\n', encoding='utf-8')
    figures(root, predictions, table)
    write_report(root, table, detail)
    return table, detail, predictions


def figures(root, predictions, table):
    path = Path(root)/'reports/figures'
    path.mkdir(exist_ok=True)
    y = predictions.is_canceled
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for name in table.modelo:
        fpr, tpr, _ = roc_curve(y, predictions[name])
        p, r, _ = precision_recall_curve(y, predictions[name])
        axes[0].plot(fpr, tpr, label=name)
        axes[1].plot(r, p, label=name)
    axes[0].plot([0,1],[0,1], '--', color='gray')
    axes[1].axhline(y.mean(), linestyle='--', color='gray', label='Prevalencia validación')
    axes[0].set(xlabel='Tasa de falsos positivos', ylabel='Recall', title='ROC — validación v2')
    axes[1].set(xlabel='Recall', ylabel='Precision', title='Precision-recall — validación v2')
    for ax in axes: ax.legend(fontsize=8); ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(path/'comparacion_5_curvas.png', dpi=150); plt.close(fig)
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for ax, row in zip(axes.flat, table.itertuples()):
        matrix = np.array([[row.tn,row.fp],[row.fn,row.tp]])
        ax.imshow(matrix, cmap='Blues', vmin=0, vmax=10344)
        for (i,j), value in np.ndenumerate(matrix): ax.text(j,i,str(value),ha='center',va='center',color='white' if value>5500 else 'black')
        ax.set(xticks=[0,1], yticks=[0,1], xlabel='Predicción', ylabel='Real', title=row.modelo)
    axes.flat[-1].axis('off')
    fig.suptitle('Matrices de validación — umbral 0,5; clase 1 = cancelación')
    fig.tight_layout(); fig.savefig(path/'comparacion_5_matrices.png', dpi=150); plt.close(fig)
    fig, ax = plt.subplots(figsize=(11,5))
    table.set_index('modelo')[['precision','recall','f1','roc_auc','average_precision']].plot.bar(ax=ax)
    ax.set(ylim=(0,1), ylabel='Valor en validación', xlabel='', title='Métricas complementarias — umbral 0,5 para precision/recall/F1')
    ax.tick_params(axis='x', rotation=15); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(path/'comparacion_5_metricas.png', dpi=150); plt.close(fig)


def write_report(root, table, detail):
    def markdown(frame):
        lines = ['| ' + ' | '.join(frame.columns) + ' |', '| ' + ' | '.join(['---']*len(frame.columns)) + ' |']
        for row in frame.itertuples(index=False, name=None):
            lines.append('| ' + ' | '.join(f'{v:.6f}' if isinstance(v, float) else str(v) for v in row) + ' |')
        return '\n'.join(lines)
    text = '''# Fase 5 — Comparación de modelos de clasificación

Fecha: 18/10/2026. Comparación académica exploratoria, exclusivamente validación v2. No se selecciona modelo definitivo ni umbral. Se revisaron fase 4.2, fase 4 histórica, splitting.py, baseline.py, preparación y las convenciones de los proyectos Python/Estadística del curso.

## 1. Protocolo y población

Se preservan los 119.390 registros y los 14 predictores. Se lee el manifiesto existente y se contrasta, sin escribirlo, contra la regla v2: alta aproximada = llegada − lead_time; disponibilidad aproximada = último estado + un día. Entrenamiento exige ambas fechas anteriores a 01/07/2016; validación, alta desde esa fecha y anterior a 01/01/2017, con disponibilidad anterior a este segundo corte. El cierre retrospectivo supuesto 01/12/2018 sigue intacto. No es un cierre PMS acreditado.

Entrenamiento: 54.164, de ellas 23.074 canceladas (42,60%). Validación: 18.097, de ellas 7.753 canceladas (42,84%). Las 20.564 pendientes y las 26.565 de prueba reservada no intervienen en ajuste, transformación, predicción o evaluación. Se cargan metadatos para verificar el manifiesto completo, y solo se devuelven train/validación a las funciones de modelos. Las métricas históricas v1 no participan en la comparación.

## 2. Pipelines y parámetros

Numéricas: lead_time, total_nights, adults, children, babies, children_missing. Categóricas: hotel, arrival_date_month, meal, country, market_segment, distribution_channel, reserved_room_type, customer_type. Objetivo is_canceled separado. Metadatos, estados finales y campos inciertos excluidos no entran en X.

Cada modelo crea un ColumnTransformer nuevo: imputación numérica por mediana, imputación categórica constante Desconocido, OneHotEncoder(handle_unknown='ignore', sparse_output=True), remainder='drop'. Solo logística añade StandardScaler. Los árboles no requieren escala. Una categoría desconocida queda a cero en su bloque; no se estima su efecto. Se verifican medianas, categorías y estadísticas de escalado contra train y su conservación al predecir validación. Representación one-hot común: 196 columnas; no se usa codificación nativa de categorías en boosting.

Configuraciones fijadas antes de evaluar, una por algoritmo, sin búsqueda, early stopping, calibración, remuestreo ni pesos de clase. Semilla 42, cuatro hilos en ensembles:

| Algoritmo | Parámetros iniciales explícitos |
| --- | --- |
| Logística | C=1, solver=lbfgs, max_iter=2000, class_weight=None; misma fábrica baseline v2 |
| Árbol | max_depth=8, min_samples_leaf=20; resto por defecto |
| Random Forest | n_estimators=200, min_samples_leaf=5, max_depth=None; resto por defecto |
| XGBoost | n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, tree_method=hist, objective=binary:logistic, eval_metric=logloss |
| LightGBM | n_estimators=300, num_leaves=31, learning_rate=0.05, min_child_samples=20, deterministic=True, force_col_wise=True, verbosity=-1 |

Árbol limitado para referencia interpretable; bosque con hojas mínimas para reducir fragmentación; boosting con tasa moderada y presupuesto fijo. No representan la capacidad óptima de cada familia. Todos los parámetros completos y versiones, incluidos defaults, constan en comparacion_5_verificacion.json. XGBoost 3.4.1 y LightGBM 4.7.0 se instalaron con wheels compatibles en el entorno local; la primera descarga requirió acceso de red fuera del sandbox. No fue necesario compilar.

## 3. Métricas en validación

Clase positiva 1 = cancelación. Umbral común 0,5, sin optimizar. La misma escala de salida probabilística permite comparar esa regla, pero no acredita calibración equivalente. Average Precision (AP) resume precision-recall sin integración trapezoidal; no se etiqueta como área trapezoidal PR-AUC. Referencia constante AP = prevalencia 0,428414; ROC-AUC = 0,5.

TABLE

TN/FP/FN/TP describen matrices [[TN, FP], [FN, TP]], con filas reales y columnas predichas, orden [0,1]. Tiempos en segundos, observados en este equipo; son mediciones orientativas, no un benchmark controlado. El trivial v2 ya documentado predice 0: accuracy 0,571586, precision/recall/F1 cero y matriz [[10344,0],[7753,0]]. La logística se reentrena y sus probabilidades coinciden con el baseline activo a tolerancia 1e-12.

## 4. Gráficos

![ROC y precision-recall](figures/comparacion_5_curvas.png)

![Matrices de confusión](figures/comparacion_5_matrices.png)

![Métricas complementarias](figures/comparacion_5_metricas.png)

Curvas comparan ordenación en todo el rango, sin seleccionar umbrales. Las matrices muestran la carga de alertas a 0,5. No se añaden gráficos redundantes de accuracy.

## 5. Interpretación y candidatos

XGBoost obtiene mayor ROC-AUC (0,8589), AP (0,8423), F1 (0,6633) y recall (0,5386). Frente a logística aumenta ROC-AUC en 0,0382 y AP en 0,0347; reduce falsos positivos de 993 a 663 (330 menos), con siete falsos negativos menos (3584 → 3577). La mejora de detección al umbral fijo es pequeña: aún omite el 46,14% de cancelaciones elegibles. Su precision aumenta de 80,76% a 86,30%. No basta para demostrar utilidad operacional.

LightGBM mejora discriminación respecto a logística (ROC-AUC 0,8487 y AP 0,8306) y reduce 402 falsas alarmas, pero pierde 423 detecciones: recall 48,32%. Su accuracy 74,59% es ligeramente inferior a logística pese a mayor AUC/AP: ordenación y decisión a umbral fijo son dimensiones distintas.

Random Forest alcanza la mayor precision (88,35%) y menos FP (459), a costa de recall 44,91% y 4271 FN; tarda más en este entorno. El árbol individual es más sencillo de inspeccionar, pero su recall 40,66%, ROC-AUC 0,7862 y AP 0,7524 quedan por debajo de logística. No se inicia explicabilidad. Logística conserva valor por sencillez, rapidez y mayor detección que árbol, bosque y LightGBM a 0,5, aunque su forma aditiva limita interacciones.

**Candidatos propuestos: XGBoost y LightGBM.** El primero ofrece el equilibrio más favorable observado de discriminación, precision, recall y errores, con coste acotado. El segundo aporta la siguiente mejor discriminación/AP y rapidez en esta configuración, con menor carga de falsas alertas que logística, pero menor recall. Ambos son menos transparentes que logística/árbol y requieren más control de complejidad; se mantiene logística como referencia obligatoria. No se declara superioridad estadística ni óptimo global. El bosque sería una alternativa si negocio priorizara pocas alertas; no se sustituye el criterio por accuracy.

FN significa no anticipar una cancelación y perder oportunidad de seguimiento o planificación; FP significa seguimiento innecesario y posible molestia para una reserva que se mantendría. Sin costes y acciones definidos no se calcula rentabilidad. AUC/AP no garantizan calibración ni efecto causal de intervenir.

## 6. Verificación, reproducibilidad y límites

El notebook se ejecuta completo con salidas y tres figuras. Las pruebas sintéticas comprueban exclusión de categorías exclusivas de validación, estadísticas de train, rechazo de solapamiento y reproducción de probabilidades con semillas para los cinco algoritmos. Se conservan hashes de todos los archivos preexistentes de datos/reportes e historia, y se comprueba su igualdad tras entrenar. No se serializan modelos ni se generan predicciones de prueba. Los resultados tabulares y probabilidades permiten recalcular todas las métricas. La reproducción íntegra se comprueba mediante una segunda ejecución con comparación de probabilidades; los tiempos pueden variar.

Persisten las limitaciones de 4.2: alta aproximada, última fecha de estado distinta de primera disponibilidad, cierre no acreditado y valores iniciales de los 14 predictores sin historial verificable. La selección de etiquetas disponibles favorece cancelaciones tempranas y menor antelación; no describe toda la cohorte. Duplicados conservados pueden sobreponderar patrones; no cruzan particiones exactas, pero faltan IDs reales. El EDA vio todo el archivo. Hay una sola validación temporal y escoger candidatos sobre ella introduce selección; no se presentan intervalos suponiendo independencia ni garantías de producción. Las configuraciones no están igualmente optimizadas, y diferencias pequeñas pueden variar con época o parámetros. No se acredita que estos cinco algoritmos estén todos cubiertos por materiales oficiales del curso, que no están aportados; se siguen los algoritmos pedidos y las convenciones de sus proyectos.

## 7. Archivos y siguiente fase propuesta

Nuevos: notebooks/comparacion_modelos.ipynb, src/comparison.py, tests/test_comparison.py, este informe, comparacion_5_metricas.csv, comparacion_5_predicciones_validacion.csv, comparacion_5_verificacion.json y tres PNG comparacion_5_* en reports/figures. Modificados: README, requirements.txt y src/run_notebook.py. Los artefactos del protocolo v2 permanecen intactos.

Para una fase 6 autorizada: definir costes/acciones con negocio y un presupuesto limitado de optimización de XGBoost/LightGBM; diseñar validación temporal interna respetando madurez y preprocesamiento por fold. Mantener logística como referencia, revisar calibración/umbral bajo un plan explícito y reservar prueba hasta congelar decisiones. Antes de cualquier pretensión de despliegue, obtener snapshots iniciales y seguimiento acreditado. No se ejecuta ninguna de esas tareas aquí.

**Fin de fase 5. Se espera revisión y autorización del usuario.**
'''
    text = text.replace('TABLE', markdown(table))
    (Path(root)/'reports/fase_5_comparacion_modelos.md').write_text(text, encoding='utf-8')
