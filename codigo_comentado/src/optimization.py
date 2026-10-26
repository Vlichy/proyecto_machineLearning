# EDICIÓN COMENTADA PARA LECTURA. Las fuentes ejecutadas y selladas permanecen en la raíz.
# Optimización histórica v2: búsqueda dentro de train y reproducción de resultados congelados.
# Solo se añaden comentarios: no se han ejecutado instrucciones de esta copia.
"""Fase 6: búsqueda temporal interna, evaluación externa única y auditoría."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import time
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.metrics import (average_precision_score, roc_auc_score, brier_score_loss,
                             precision_recall_curve)
from sklearn.model_selection import ParameterSampler, RandomizedSearchCV

from src.comparison import sha, load_development, model_factories, fit_one
from src.baseline import evaluate_predictions
from src.features import FEATURES, NUMERIC_FEATURES, CATEGORICAL_FEATURES
from src.splitting import add_status_availability, PROTOCOL_V2


SEED = 42
FOLD_DATES = [('2015-10-01', '2016-01-01'), ('2016-01-01', '2016-04-01'),
              ('2016-04-01', '2016-07-01')]
THRESHOLDS = [.1, .2, .3, .4, .5, .6, .7, .8, .9]
SEARCH_SPACES = {
    'xgboost': {
        'classifier__n_estimators': [200, 400],
        'classifier__max_depth': [3, 5],
        'classifier__learning_rate': [.03, .08],
        'classifier__subsample': [.8, 1.],
        'classifier__colsample_bytree': [.8, 1.],
        'classifier__min_child_weight': [1, 10],
        'classifier__reg_lambda': [1., 5.],
    },
    'lightgbm': {
        'classifier__n_estimators': [200, 400],
        'classifier__num_leaves': [15, 31],
        'classifier__learning_rate': [.03, .08],
        'classifier__subsample': [.8, 1.],
        'classifier__colsample_bytree': [.8, 1.],
        'classifier__min_child_samples': [20, 60],
        'classifier__reg_lambda': [0., 5.],
    },
}


# Serializar resultados con tipos compatibles con JSON y una salida legible.
def json_write(path, value):
    # Convertir escalares y estructuras al formato serializable sin cambiar el cálculo del modelo.
    def normalize(item):
        if isinstance(item, dict): return {k: normalize(v) for k,v in item.items()}
        if isinstance(item, (list, tuple)): return [normalize(v) for v in item]
        if isinstance(item, (float, np.floating)) and not np.isfinite(item):
            return 'NaN' if np.isnan(item) else str(item)
        if isinstance(item, np.generic): return item.item()
        return item
    # Persistir documentación o metadatos para revisar las decisiones sin volver a ejecutar el modelo.
    Path(path).write_text(json.dumps(normalize(value), ensure_ascii=False, indent=2, default=str,
                                    allow_nan=False)+'\n', encoding='utf-8')


def make_folds(metadata, y, dates=FOLD_DATES):
    """Índices POSICIONALES solo dentro de train externo, con purga por madurez."""
    if not metadata.index.equals(y.index) or not metadata.index.is_unique:
        raise ValueError('Metadatos y etiquetas deben estar alineados y ser únicos')
    booking = pd.to_datetime(metadata.meta_booking_date_proxy)
    available = pd.to_datetime(metadata.meta_label_available_proxy)
    if booking.isna().any() or available.isna().any() or available.le(booking).any():
        raise ValueError('Fechas inválidas para validación interna')
    if not (booking.lt('2016-07-01') & available.lt('2016-07-01')).all():
        raise ValueError('La CV solo admite entrenamiento externo elegible v2')
    folds, rows = [], []
    previous_end = None
    for number, (start, end) in enumerate(dates):
        start, end = pd.Timestamp(start), pd.Timestamp(end)
        if not start < end <= pd.Timestamp('2016-07-01') or (previous_end is not None and start < previous_end):
            raise ValueError('Ventanas internas inválidas o solapadas')
        train = booking.lt(start) & available.lt(start)
        val_period = booking.ge(start) & booking.lt(end)
        val = val_period & available.lt(end)
        if not train.any() or not val.any() or y.loc[train].nunique()!=2 or y.loc[val].nunique()!=2:
            raise ValueError('Cada fold necesita suficientes datos y ambas clases')
        if (train & val).any() or not booking.loc[train].max() < booking.loc[val].min():
            raise ValueError('Solapamiento temporal interno')
        if set(metadata.loc[train,'meta_duplicate_group']) & set(metadata.loc[val,'meta_duplicate_group']):
            raise ValueError('Duplicados cruzan el fold')
        folds.append((np.flatnonzero(train), np.flatnonzero(val)))
        # Calcular una huella determinista para trazabilidad; no usarla como característica predictiva.
        rows.append({'fold': number, 'inicio_validacion': str(start.date()), 'fin_exclusivo': str(end.date()),
                     'n_train': int(train.sum()), 'n_validacion': int(val.sum()),
                     'tasa_train': float(y.loc[train].mean()), 'tasa_validacion': float(y.loc[val].mean()),
                     'apartadas_train_por_disponibilidad': int((booking.lt(start) & ~available.lt(start)).sum()),
                     'apartadas_val_por_disponibilidad': int((val_period & ~available.lt(end)).sum()),
                     'max_disponibilidad_train': str(available.loc[train].max().date()),
                     'max_disponibilidad_val': str(available.loc[val].max().date()),
                     'sha_ids_train': hashlib.sha256(metadata.iloc[np.flatnonzero(train)].meta_row_id.to_numpy(dtype='int64').tobytes()).hexdigest(),
                     'sha_ids_val': hashlib.sha256(metadata.iloc[np.flatnonzero(val)].meta_row_id.to_numpy(dtype='int64').tobytes()).hexdigest()})
        previous_end = end
    return folds, pd.DataFrame(rows)


def audit_preprocessor(model, train):
    """Comprueba cada ajuste de CV contra su train concreto, sin datos externos."""
    pre = model.named_steps['preprocessor']
    np.testing.assert_array_equal(pre.feature_names_in_, FEATURES)
    numeric = pre.named_transformers_['numeric']
    expected = train[NUMERIC_FEATURES].median().fillna(0).to_numpy()
    np.testing.assert_allclose(numeric.named_steps['imputer'].statistics_, expected)
    encoder = pre.named_transformers_['categorical'].named_steps['encoder']
    for actual, column in zip(encoder.categories_, CATEGORICAL_FEATURES):
        np.testing.assert_array_equal(actual, np.unique(train[column].fillna('Desconocido').to_numpy(dtype=str)))
    # Hacer explícito este invariante: si falla, no se deben interpretar los resultados como válidos.
    assert encoder.handle_unknown == 'ignore'
    if 'scaler' in numeric.named_steps:
        scaler = numeric.named_steps['scaler']
        # Comprobar tamaños esperados para detectar pérdidas de filas o desalineación.
        assert int(scaler.n_samples_seen_) == len(train)
        np.testing.assert_allclose(scaler.mean_, train[NUMERIC_FEATURES].fillna(train[NUMERIC_FEATURES].median()).mean())


def candidate_parameters(name, model):
    """Ocho muestras sin reemplazo más referencia inicial; ninguna usa métricas."""
    sampled = list(ParameterSampler(SEARCH_SPACES[name], n_iter=8, random_state=SEED))
    initial = {key: model.get_params()[key] for key in SEARCH_SPACES[name]}
    return [initial] + sampled


# Evaluar candidatos con folds temporales internos y seleccionar por AP media.
def search_one(name, model, x, y, folds):
    configurations = candidate_parameters(name, model)
    # Con subsample_freq=1 en LGBM, subsample sí tiene efecto; el candidato inicial
    # se ejecuta con freq=0 y conserva exactamente la configuración de fase 5.
    if name == 'lightgbm':
        for i, configuration in enumerate(configurations):
            configuration['classifier__subsample_freq'] = 0 if i == 0 else 1
    candidates = [{k: [v] for k,v in params.items()} for params in configurations]
    lookup = {tuple(x.iloc[v].index): t for t,v in folds}
    audit_count = []
    # Auditar el subentrenamiento de cada fold antes de medir AP y ROC-AUC de su validación.
    def scorer(estimator, validation, target):
        train_positions = lookup[tuple(validation.index)]
        audit_preprocessor(estimator, x.iloc[train_positions])
        # Obtener scores con el pipeline ajustado, sin aprender parámetros de estas filas.
        probability = estimator.predict_proba(validation)[:, 1]
        audit_count.append(len(train_positions))
        return {'average_precision': average_precision_score(target, probability),
                'roc_auc': roc_auc_score(target, probability)}
    search = RandomizedSearchCV(model, param_distributions=candidates, n_iter=len(candidates),
                                scoring=scorer, refit=False, cv=folds, random_state=SEED,
                                n_jobs=1, error_score='raise', return_train_score=False)
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        # Ejecutar la búsqueda histórica con sus folds internos; la prueba queda fuera de selección.
        search.fit(x, y)
    elapsed = time.perf_counter() - start
    results = search.cv_results_
    # AP media no ponderada entre periodos; ROC-AUC solo desempata.
    # Seleccionar por AP interna y usar ROC-AUC solo para desempatar, sin consultar prueba.
    order = sorted(range(len(results['params'])), key=lambda i: (
        -results['mean_test_average_precision'][i], -results['mean_test_roc_auc'][i], i))
    best = order[0]
    rows = []
    for i, params in enumerate(results['params']):
        row = {'modelo': name, 'candidato': i, 'seleccionado': i == best,
               'inicial_fase_5': params == configurations[0],
               'parametros': json.dumps(params, sort_keys=True),
               'mean_ap': float(results['mean_test_average_precision'][i]),
               'std_ap': float(results['std_test_average_precision'][i]),
               'mean_roc_auc': float(results['mean_test_roc_auc'][i]),
               'std_roc_auc': float(results['std_test_roc_auc'][i]),
               'mean_fit_seconds': float(results['mean_fit_time'][i])}
        for fold in range(len(folds)):
            row[f'fold_{fold}_ap'] = float(results[f'split{fold}_test_average_precision'][i])
            row[f'fold_{fold}_roc_auc'] = float(results[f'split{fold}_test_roc_auc'][i])
        rows.append(row)
    # Comprobar tamaños esperados para detectar pérdidas de filas o desalineación.
    assert len(audit_count) == len(candidates)*len(folds)
    return results['params'][best], pd.DataFrame(rows), {
        'segundos': elapsed, 'ajustes': len(audit_count), 'advertencias': [str(w.message) for w in caught],
        'parametros_seleccionados': results['params'][best], 'candidatos_planificados': configurations}


# Auxiliar de Optimización histórica v2: búsqueda dentro de train y reproducción de resultados congelados.
def threshold_table(y, probabilities, thresholds=THRESHOLDS):
    rows = []
    for name in probabilities:
        for threshold in thresholds:
            metrics = evaluate_predictions(y, probabilities[name].ge(threshold), probabilities[name])
            tn,fp,fn,tp = np.asarray(metrics['matriz_confusion']).ravel()
            rows.append({'modelo': name, 'umbral': threshold, 'precision': metrics['precision'],
                         'recall': metrics['recall'], 'f1': metrics['f1'], 'fp': int(fp), 'fn': int(fn),
                         'tp': int(tp), 'tn': int(tn), 'alertas': int(tp+fp),
                         'porcentaje_alto_riesgo': 100*float((tp+fp)/len(y))})
    return pd.DataFrame(rows)


def reliability_table(y, probabilities):
    """Diez bins fijos: no se ajusta calibrador ni se evalúa en datos de fit."""
    rows, summary = [], []
    for name in probabilities:
        p = np.asarray(probabilities[name], dtype=float)
        bins = np.minimum((p*10).astype(int), 9)
        weighted_gap = 0.
        for bin_id in range(10):
            mask = bins == bin_id
            if not mask.any():
                continue
            observed, predicted = float(np.asarray(y)[mask].mean()), float(p[mask].mean())
            weighted_gap += mask.mean()*abs(observed-predicted)
            rows.append({'modelo': name, 'bin': bin_id, 'limite_inferior': bin_id/10,
                         'limite_superior': (bin_id+1)/10, 'n': int(mask.sum()),
                         'probabilidad_media': predicted, 'tasa_observada': observed})
        # Medir el error cuadrático de los scores y distinguirlo de la precisión de las alertas.
        summary.append({'modelo': name, 'brier': float(brier_score_loss(y, p)),
                        'probabilidad_media': float(p.mean()), 'tasa_observada': float(np.mean(y)),
                        'brecha_media': float(p.mean()-np.mean(y)), 'ece_10_bins_descriptivo': float(weighted_gap)})
    return pd.DataFrame(rows), pd.DataFrame(summary)


def scenario_table(thresholds):
    """Unidades arbitrarias de error, sin imputar euros ni efecto de intervención."""
    frames = []
    for c_fp,c_fn in [(1,1),(1,5),(5,1)]:
        scenario = thresholds.copy()
        scenario['coste_fp_supuesto'] = c_fp
        scenario['coste_fn_supuesto'] = c_fn
        scenario['carga_relativa_errores'] = c_fp*scenario.fp + c_fn*scenario.fn
        scenario['carga_por_1000_reservas'] = scenario.carga_relativa_errores*1000/(scenario.tp+scenario.tn+scenario.fp+scenario.fn)
        frames.append(scenario)
    return pd.concat(frames, ignore_index=True)


# Usar checkpoints si existen; la búsqueda original se limita al entrenamiento v2.
def run_optimization(root):
    root = Path(root)
    output = root/'reports'
    # Distinguir resultados ya guardados de una ejecución pendiente antes de continuar.
    if (output/'optimizacion_6_verificacion.json').exists():
        print('Reproducción desde resultados congelados: sin nuevos ajustes o predicciones externas.', flush=True)
        return replay_optimization(root)
    # Distinguir resultados ya guardados de una ejecución pendiente antes de continuar.
    if (output/'optimizacion_6_predicciones_validacion.csv').exists():
        raise RuntimeError('Hay resultados sin registro final: auditar y recuperar antes de repetir entrenamiento.')
    protected = [p for folder in ['data','reports'] for p in (root/folder).rglob('*') if p.is_file()
                 and not p.name.startswith('optimizacion_6') and p.name!='fase_6_optimizacion.md']
    protected += [root/'src'/name for name in ['splitting.py','features.py','preprocessing.py','baseline.py','comparison.py']]
    hashes = {str(p.relative_to(root)): sha(p) for p in protected}
    x,y,x_val,y_val,ids = load_development(root)
    prior_verification = json.loads((output/'comparacion_5_verificacion.json').read_text(encoding='utf-8'))
    # Hacer explícito este invariante: si falla, no se deben interpretar los resultados como válidos.
    assert prior_verification['protocolo'] == PROTOCOL_V2
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    prepared_meta = pd.read_csv(root/'data/processed/hotel_bookings_prepared.csv',
        usecols=['meta_row_id','meta_duplicate_group','meta_booking_date_proxy','meta_arrival_date'])
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    dates = pd.read_csv(root/'data/raw/hotel_bookings.csv', usecols=['reservation_status_date'])
    metadata = add_status_availability(prepared_meta, dates.reservation_status_date)
    train_meta = metadata.loc[x.index].copy()
    folds, fold_table = make_folds(train_meta, y)
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    fold_table.to_csv(output/'optimizacion_6_folds.csv', index=False)
    assignments = []
    for fold,(train,val) in enumerate(folds):
        for positions, role in [(train,'ajuste'),(val,'validacion_interna')]:
            assignments.append(pd.DataFrame({'fold':fold, 'meta_row_id':train_meta.iloc[positions].meta_row_id, 'rol':role}))
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    pd.concat(assignments).to_csv(output/'optimizacion_6_ids_folds.csv', index=False)
    models = model_factories()
    plan = {'protocolo': PROTOCOL_V2, 'seed':SEED, 'folds': FOLD_DATES,
            'espacios_busqueda': SEARCH_SPACES, 'muestras_aleatorias_por_modelo': 8,
            'incluye_referencia_inicial': True, 'total_configuraciones_por_modelo':9,
            'total_ajustes_cv':54, 'scoring':'media AP no ponderada; desempate ROC-AUC; después índice',
            'refit_cv':False, 'early_stopping':False, 'hilos_por_modelo':4, 'busquedas_paralelas':1,
            'umbrales_descriptivos':THRESHOLDS, 'calibracion_ajustada':False,
            'regla_candidato':'Conservar inicial si la seleccionada no mejora simultáneamente AP y ROC-AUC externos; entre familias priorizar ambas, revisar errores, Brier, estabilidad y coste. Sin umbral operativo final.'}
    json_write(output/'optimizacion_6_plan.json', plan)
    selections, all_results, searches = {}, [], {}
    for name in ['xgboost','lightgbm']:
        print(f'Búsqueda interna: {name}, 9 configuraciones × 3 folds', flush=True)
        selections[name], table, searches[name] = search_one(name, clone(models[name]), x, y, folds)
        all_results.append(table)
    cv_table = pd.concat(all_results, ignore_index=True)
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    cv_table.to_csv(output/'optimizacion_6_busqueda.csv', index=False)
    # Archivo previo a la primera predicción externa de las nuevas configuraciones.
    selected_record = {'protocolo':PROTOCOL_V2['version'], 'seleccion_solo_cv_interna':True,
                       'validacion_externa_usada_para_hiperparametros':False, 'busquedas':searches}
    json_write(output/'optimizacion_6_seleccion_prevalidacion.json', selected_record)
    selection_hash = sha(output/'optimizacion_6_seleccion_prevalidacion.json')
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    predictions = pd.read_csv(output/'comparacion_5_predicciones_validacion.csv')
    np.testing.assert_array_equal(predictions.meta_row_id, ids)
    np.testing.assert_array_equal(predictions.is_canceled, y_val)
    reference_names = ['regresion_logistica','xgboost','lightgbm']
    predictions = predictions[['meta_row_id','is_canceled']+reference_names].copy()
    metrics_rows, final_parameters, external_warnings = [], {}, {}
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    prior_metrics = pd.read_csv(output/'comparacion_5_metricas.csv').set_index('modelo')
    for name in reference_names:
        metrics = evaluate_predictions(y_val, predictions[name].ge(.5), predictions[name])
        metrics['average_precision'] = float(average_precision_score(y_val,predictions[name]))
        tn,fp,fn,tp = np.asarray(metrics.pop('matriz_confusion')).ravel()
        metrics.update(tn=int(tn),fp=int(fp),fn=int(fn),tp=int(tp))
        for key in ['accuracy','precision','recall','f1','roc_auc','average_precision','tn','fp','fn','tp']:
            np.testing.assert_allclose(metrics[key],prior_metrics.loc[name,key],atol=1e-12,rtol=1e-12)
        metrics_rows.append({'modelo':name, **metrics, 'fit_seconds':float(prior_metrics.loc[name,'fit_seconds']),
                             'predict_seconds':float(prior_metrics.loc[name,'predict_seconds']), 'origen':'fase_5_guardado'})
    for name in ['xgboost','lightgbm']:
        model = clone(models[name]).set_params(**selections[name])
        print(f'Ajuste completo y única predicción externa: {name}', flush=True)
        metrics,p,external_warnings[name] = fit_one(model,x,y,x_val,y_val)
        predictions[name+'_optimizado'] = p
        final_parameters[name] = model.named_steps['classifier'].get_params()
        metrics_rows.append({'modelo':name+'_optimizado', **metrics, 'origen':'fase_6_seleccion_interna'})
    # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
    assert sha(output/'optimizacion_6_seleccion_prevalidacion.json') == selection_hash
    metrics_table = pd.DataFrame(metrics_rows)
    probabilities = predictions.drop(columns=['meta_row_id','is_canceled'])
    thresholds = threshold_table(y_val,probabilities)
    calibration_bins, calibration_summary = reliability_table(y_val,probabilities)
    scenarios = scenario_table(thresholds)
    # Estabilidad descriptiva por mes externo: sin usarla para reajustar modelos.
    months = pd.to_datetime(metadata.loc[x_val.index,'meta_booking_date_proxy']).dt.to_period('M').astype(str).to_numpy()
    stability = []
    for name in probabilities:
        for month in sorted(set(months)):
            mask = months == month
            if y_val.iloc[np.flatnonzero(mask)].nunique()!=2:
                continue
            # Medir la capacidad de ordenar scores; esta métrica no fija la política de alertas.
            stability.append({'modelo':name, 'mes':month, 'n':int(mask.sum()),
                'tasa_cancelacion':float(y_val.iloc[np.flatnonzero(mask)].mean()),
                'roc_auc':float(roc_auc_score(np.asarray(y_val)[mask],probabilities[name].to_numpy()[mask])),
                'average_precision':float(average_precision_score(np.asarray(y_val)[mask],probabilities[name].to_numpy()[mask]))})
    for name,frame in [('metricas',metrics_table),('predicciones_validacion',predictions),('umbrales',thresholds),
                       ('calibracion_bins',calibration_bins),('calibracion',calibration_summary),
                       ('escenarios',scenarios),('estabilidad_mensual',pd.DataFrame(stability))]:
        # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
        frame.to_csv(output/f'optimizacion_6_{name}.csv',index=False)
    for path,expected in hashes.items():
        # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
        assert sha(root/path)==expected, path
    # Medir el error cuadrático de los scores y distinguirlo de la precisión de las alertas.
    detail = {'protocolo':PROTOCOL_V2, 'n_train':len(x), 'n_validacion':len(x_val),
              'plan':plan, 'busquedas':searches, 'parametros_completos_seleccionados':final_parameters,
              'advertencias_externas':external_warnings, 'sha_seleccion_antes_evaluacion':selection_hash,
              'archivos_previos_intactos':hashes, 'auditorias_fit_cv':54,
              'predicciones_externas_nuevas_por_modelo':1, 'prueba_transformada_predicha_evaluada':False,
              'brier_constante_tasa_train':float(brier_score_loss(y_val,np.full(len(y_val),y.mean()))),
              'versiones':{k:importlib.metadata.version(k) for k in ['scikit-learn','xgboost','lightgbm','numpy','pandas']}}
    make_figures(root,predictions,calibration_bins,thresholds,cv_table)
    write_report(root,metrics_table,fold_table,cv_table,calibration_summary,thresholds,detail)
    detail['huellas_resultados'] = {str(p.relative_to(root)):sha(p) for p in output.glob('optimizacion_6_*') if p.is_file()}
    json_write(output/'optimizacion_6_verificacion.json',detail)
    return metrics_table, fold_table, cv_table, calibration_summary, thresholds, detail


def replay_optimization(root):
    """Recalcula análisis sobre scores congelados; nunca llama fit/predict_proba."""
    root=Path(root);output=root/'reports'
    detail=json.loads((output/'optimizacion_6_verificacion.json').read_text(encoding='utf-8'))
    # Hacer explícito este invariante: si falla, no se deben interpretar los resultados como válidos.
    assert detail['protocolo']==PROTOCOL_V2
    for key in ['archivos_previos_intactos','huellas_resultados']:
        for path,expected in detail[key].items(): assert sha(root/path)==expected,path
    x,y,x_val,y_val,ids=load_development(root)
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    predictions=pd.read_csv(output/'optimizacion_6_predicciones_validacion.csv')
    # XGBoost devuelve float32; CSV escribe su representación decimal corta.
    # Restituir ese dtype reproduce los scores originales, también para Brier.
    predictions['xgboost_optimizado']=predictions['xgboost_optimizado'].astype('float32')
    np.testing.assert_array_equal(predictions.meta_row_id,ids)
    np.testing.assert_array_equal(predictions.is_canceled,y_val)
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    tables={name:pd.read_csv(output/f'optimizacion_6_{name}.csv') for name in
            ['metricas','folds','busqueda','calibracion','umbrales']}
    for row in tables['metricas'].itertuples():
        scores=predictions[row.modelo]
        values=evaluate_predictions(y_val,scores.ge(.5),scores)
        for key in ['accuracy','precision','recall','f1','roc_auc']:
            np.testing.assert_allclose(getattr(row,key),values[key],atol=1e-12,rtol=1e-12)
        np.testing.assert_allclose(row.average_precision,average_precision_score(y_val,scores),atol=1e-12)
        np.testing.assert_array_equal([row.tn,row.fp,row.fn,row.tp],np.asarray(values['matriz_confusion']).ravel())
    p=predictions.drop(columns=['meta_row_id','is_canceled'])
    pd.testing.assert_frame_equal(tables['umbrales'],threshold_table(y_val,p),atol=1e-12,rtol=1e-12)
    _,calibration=reliability_table(y_val,p)
    pd.testing.assert_frame_equal(tables['calibracion'],calibration,atol=1e-12,rtol=1e-12)
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    meta=pd.read_csv(root/'data/processed/hotel_bookings_prepared.csv',usecols=['meta_row_id','meta_duplicate_group','meta_booking_date_proxy'])
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    status=pd.read_csv(root/'data/raw/hotel_bookings.csv',usecols=['reservation_status_date'])
    _,folds=make_folds(add_status_availability(meta,status.reservation_status_date).loc[x.index],y)
    pd.testing.assert_frame_equal(tables['folds'],folds,atol=1e-12,rtol=1e-12)
    models=model_factories()
    for name in ['xgboost','lightgbm']:
        candidates=candidate_parameters(name,models[name])
        if name=='lightgbm':
            for i,c in enumerate(candidates): c['classifier__subsample_freq']=0 if i==0 else 1
        # Hacer explícito este invariante: si falla, no se deben interpretar los resultados como válidos.
        assert candidates==detail['busquedas'][name]['candidatos_planificados']
        rows=tables['busqueda'].loc[tables['busqueda'].modelo.eq(name)].sort_values('candidato')
        # Hacer explícito este invariante: si falla, no se deben interpretar los resultados como válidos.
        assert [json.loads(p) for p in rows.parametros]==candidates
        best=rows.sort_values(['mean_ap','mean_roc_auc','candidato'],ascending=[False,False,True]).iloc[0]
        # Hacer explícito este invariante: si falla, no se deben interpretar los resultados como válidos.
        assert best.seleccionado and json.loads(best.parametros)==detail['busquedas'][name]['parametros_seleccionados']
    write_report(root,tables['metricas'],tables['folds'],tables['busqueda'],tables['calibracion'],tables['umbrales'],detail)
    return tables['metricas'],tables['folds'],tables['busqueda'],tables['calibracion'],tables['umbrales'],detail


# Representar las tablas de esta fase sin usar el gráfico para ajustar el modelo.
def make_figures(root, predictions, bins, thresholds, cv_table):
    path = Path(root)/'reports/figures'
    names = predictions.columns[2:]
    # Crear una figura descriptiva; sus ejes y títulos deben identificar población y versión del protocolo.
    fig,axes = plt.subplots(1,2,figsize=(13,5))
    for name in names:
        # Describir precision y recall desde scores existentes, sin elegir otra decisión con prueba.
        p,r,_ = precision_recall_curve(predictions.is_canceled,predictions[name])
        axes[0].plot(r,p,label=name)
        points = bins[bins.modelo.eq(name)]
        axes[1].plot(points.probabilidad_media,points.tasa_observada,marker='o',label=name)
    axes[0].axhline(predictions.is_canceled.mean(),color='gray',linestyle='--')
    axes[0].set(xlabel='Recall',ylabel='Precision',title='Precision-recall — validación v2')
    axes[1].plot([0,1],[0,1],'--',color='gray')
    axes[1].set(xlabel='Probabilidad media',ylabel='Tasa observada',title='Calibración — bins fijos de amplitud 0,1')
    for ax in axes: ax.legend(fontsize=7); ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(path/'optimizacion_6_pr_calibracion.png',dpi=150);plt.close(fig)
    # Crear una figura descriptiva; sus ejes y títulos deben identificar población y versión del protocolo.
    fig,axes = plt.subplots(1,2,figsize=(13,5))
    for name in names:
        points=thresholds[thresholds.modelo.eq(name)]
        axes[0].plot(points.umbral,points.recall,marker='.',label=name)
        axes[1].plot(points.umbral,points.porcentaje_alto_riesgo,marker='.',label=name)
    axes[0].set(xlabel='Umbral',ylabel='Recall',title='Cobertura de cancelaciones')
    axes[1].set(xlabel='Umbral',ylabel='% reservas alertadas',title='Carga de seguimiento')
    for ax in axes: ax.legend(fontsize=7); ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(path/'optimizacion_6_umbrales.png',dpi=150);plt.close(fig)
    # Crear una figura descriptiva; sus ejes y títulos deben identificar población y versión del protocolo.
    fig,ax=plt.subplots(figsize=(9,4))
    for name in ['xgboost','lightgbm']:
        for role in ['inicial_fase_5','seleccionado']:
            row=cv_table[cv_table.modelo.eq(name)&cv_table[role]].iloc[0]
            ax.plot(range(1,4),[row[f'fold_{f}_ap'] for f in range(3)],marker='o',label=f'{name} {role}')
    ax.set(xticks=[1,2,3],xlabel='Ventana interna (orden temporal)',ylabel='Average Precision',title='Estabilidad interna — periodos con prevalencias diferentes')
    ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(path/'optimizacion_6_estabilidad.png',dpi=150);plt.close(fig)


# Formatear una tabla como Markdown para incluirla en el informe.
def markdown(frame):
    lines=['| '+' | '.join(frame.columns)+' |','| '+' | '.join(['---']*len(frame.columns))+' |']
    for row in frame.itertuples(index=False,name=None):
        lines.append('| '+' | '.join(f'{v:.6f}' if isinstance(v,float) else str(v) for v in row)+' |')
    return '\n'.join(lines)


# Redactar tablas, metodología y limitaciones desde resultados calculados o guardados.
def write_report(root, metrics, folds, cv, calibration, thresholds, detail):
    root=Path(root)
    selected=cv[cv.inicial_fase_5|cv.seleccionado]
    cv_columns=['modelo','inicial_fase_5','seleccionado','mean_ap','std_ap','mean_roc_auc',
                'fold_0_ap','fold_1_ap','fold_2_ap']
    fold_columns=['fold','inicio_validacion','fin_exclusivo','n_train','n_validacion','tasa_train',
                  'tasa_validacion','max_disponibilidad_train','max_disponibilidad_val']
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    scenarios=pd.read_csv(root/'reports/optimizacion_6_escenarios.csv')
    scenario_view=scenarios[scenarios.modelo.eq('xgboost') & scenarios.umbral.isin([.2,.3,.5,.7])]
    scenario_columns=['umbral','coste_fp_supuesto','coste_fn_supuesto','carga_relativa_errores','carga_por_1000_reservas']
    threshold_columns=['modelo','umbral','precision','recall','f1','fp','fn','alertas','porcentaje_alto_riesgo']
    # Codificar las categorías de train e ignorar las nuevas sin aprenderlas de validación o prueba.
    text = '''# Fase 6 — Optimización de modelos y análisis de umbrales

Fecha: 18/10/2026. Se completa exclusivamente fase 6, con protocolo **v2_estado_fechado_aproximado** intacto. Se recomienda **XGBoost inicial**, conservando la configuración de fase 5: la búsqueda mejora sus resultados internos, pero no mejora la evaluación externa. No se fija umbral operativo ni se acredita despliegue.

## 1. Revisión y contrato de datos

Se revisaron fase_4_2_protocolo_temporal.md, fase_5_comparacion_modelos.md, comparison.py, baseline.py, splitting.py, features.py y preprocessing.py, el manifiesto v2 y las convenciones de los proyectos Python y Estadística. Las métricas activas de fases 4.2 y 5 corresponden a v2; no se usan las métricas históricas v1. Se mantiene la organización de módulos, notebook narrado en español y reportes reproducibles del curso. No se dispone de materiales oficiales suficientes para acreditar el temario completo de optimización; RandomizedSearchCV sigue la técnica pedida.

Se mantienen 119.390 filas, 14 predictores, 54.164 filas de entrenamiento (23.074 canceladas, 42,60%) y 18.097 de validación externa (7.753 canceladas, 42,84%). Los cortes externos siguen siendo 01/07/2016 y 01/01/2017. Alta aproximada = llegada prevista − lead_time; disponibilidad aproximada = reservation_status_date + un día, con desigualdad estricta antes del corte. Cierre retrospectivo asumido 01/12/2018, sin cierre PMS acreditado. No se cambian madurez, IDs, limpieza ni listas de variables. Las 26.565 de prueba y 20.564 pendientes no se transforman, predicen ni evalúan. Leer fechas e IDs para contrastar el manifiesto no incorpora sus predictores a ajuste.

## 2. Validación temporal interna

Tres folds expansivos, fijados antes de comparar configuraciones y construidos exclusivamente dentro del entrenamiento externo. En cada fold: ajuste con alta y disponibilidad anteriores al inicio; validación con alta desde inicio hasta fin exclusivo y disponibilidad anterior a fin. Las filas con resultado posterior se purgan del rol correspondiente; no se desplazan a una validación anterior. Todas las fechas son proxies del mismo protocolo v2.

FOLDS

Las validaciones internas no se solapan en altas/IDs y ningún grupo exacto cruza ajuste y validación de un fold. Los conjuntos de ajuste sí crecen y reutilizan observaciones de periodos anteriores: es lo previsto para una ventana expansiva. No se exige que las llegadas previstas no se superpongan: una cancelación ya registrada puede referirse a una llegada futura.

Las primeras ventanas no tienen un año completo de llegadas realizadas: el archivo empieza por llegadas en julio de 2015. Ver doce meses previstos en cancelaciones de largo plazo no equivale a historia anual observada. La alternativa conservadora adoptada es una búsqueda pequeña, referencias iniciales incluidas y ninguna afirmación de robustez entre años; una validación aleatoria ocultaría el cambio temporal. No se cambian ventanas tras observar sus resultados. Las filas apartadas de cada fold se cuentan en optimizacion_6_folds.csv respecto al universo ya elegible de entrenamiento externo; no son toda la censura del dataset original.

## 3. Búsqueda limitada y preprocesamiento

RandomizedSearchCV con ocho muestras sin reemplazo por algoritmo y una configuración inicial adicional: **nueve candidatos × tres folds × dos modelos = 54 ajustes internos**, más dos ajustes completos seleccionados. Seed 42, búsqueda secuencial (n_jobs=1), cuatro hilos por modelo, sin early stopping, refit=False. Criterio: media no ponderada de Average Precision de los tres periodos; desempate por ROC-AUC media y después índice del candidato. AP depende de prevalencia, por lo que se conservan tasas y resultados por periodo. ROC-AUC/AP se calculan con probabilidades, no con etiquetas a 0,5.

| Parámetro | XGBoost: valores muestreados | LightGBM: valores muestreados |
| --- | --- | --- |
| n_estimators | 200, 400 | 200, 400 |
| learning_rate | 0.03, 0.08 | 0.03, 0.08 |
| complejidad | max_depth: 3, 5 | num_leaves: 15, 31 |
| subsample | 0.8, 1.0 | 0.8, 1.0 |
| colsample_bytree | 0.8, 1.0 | 0.8, 1.0 |
| mínimo por hijo/hoja | min_child_weight: 1, 10 | min_child_samples: 20, 60 |
| reg_lambda | 1, 5 | 0, 5 |

Cada espacio tiene 128 combinaciones posibles; se muestrean ocho, no se recorre la cuadrícula. Los candidatos iniciales quedan fuera de esa cuadrícula cuando procede. LightGBM usa subsample_freq=1 en las ocho propuestas para activar submuestreo; la referencia conserva freq=0 y los parámetros de fase 5. XGBoost conserva tree_method=hist y objective=binary:logistic. No se añaden variables, algoritmos, balanceo ni pesos de clase.

Cada clon del pipeline aprende medianas numéricas y categorías exclusivamente de su subentrenamiento. Se imputa categoría constante Desconocido y se aplica OneHotEncoder(handle_unknown='ignore'); categorías nuevas quedan a cero en su bloque, sin aprender su efecto. No se escalan árboles. Logística conserva su pipeline escalado y sus predicciones congeladas v2 de fase 5. El scorer audita contra el subentrenamiento las medianas, categorías y lista de 14 entradas en **los 54 ajustes**. El ajuste completo usa las mismas auditorías de fit_one y comprueba que los parámetros de transformación no cambian al predecir validación. Ninguna fecha/ID/etiqueta entra en X.

SELECTION

Mejores parámetros por validación interna:

PARAMS

TIMES

Los parámetros completos, defaults y versiones se registran en optimizacion_6_verificacion.json. El default missing=NaN de XGBoost se representa como la cadena 'NaN' solo en ese registro JSON; la fábrica sigue utilizando el valor numérico original. El plan y la selección se escriben antes de predecir validación externa. No se seleccionan hiperparámetros con ella.

## 4. Evaluación externa de las dos selecciones

Una predicción externa nueva por configuración seleccionada, tras ajuste en las 54.164 filas permitidas. Para referencias se leen las probabilidades de fase 5 y se verifican sus métricas, sin volver a entrenarlas. Umbral inicial común **0,5**. 'Optimizado' significa seleccionado por búsqueda interna, no rendimiento mejor garantizado.

METRICS

Matrices [[TN, FP], [FN, TP]], filas reales y columnas predichas, orden [0,1]:

MATRICES

XGBoost seleccionado baja ROC-AUC de 0,858927 a 0,855129 y AP de 0,842275 a 0,838477. A 0,5 reduce 11 falsas alarmas, pero deja 172 cancelaciones adicionales sin detectar (FN 3577 → 3749). F1 cae de 0,663278 a 0,645338. No aporta mejora externa frente a su versión inicial.

LightGBM seleccionado baja ROC-AUC de 0,848655 a 0,843851 y AP de 0,830643 a 0,827120. Detecta cinco cancelaciones adicionales, pero genera 37 falsas alarmas más; F1 también desciende. Su Brier baja ligeramente, sin compensar la pérdida de discriminación ni acreditar utilidad mayor.

No se modifican espacios, ventanas o ensayos al observar esos resultados. Se conservan ambas configuraciones iniciales en lugar de sustituirlas por las seleccionadas internamente. Las diferencias son descriptivas: no se prueba significación ni generalización prospectiva. Tiempos de referencia proceden de fase 5 y los nuevos de fase 6, sin equivaler a benchmark controlado.

## 5. Estabilidad y límites de la optimización

Las AP internas medias suben de 0,5352 a 0,6008 en XGBoost y de 0,5094 a 0,6006 en LightGBM, pero varían mucho entre ventanas. Para XGBoost seleccionado, AP es 0,6820 / 0,6687 / 0,4518, y ROC-AUC 0,8154 / 0,6711 / 0,4839. LightGBM seleccionado termina con ROC-AUC 0,4678 en el tercer fold. **La discriminación cercana o inferior a 0,5 en esa ventana es una señal relevante de inestabilidad**, no un resultado que deba ocultarse con la media. La selección mejora las medias internas, sin resolver el cambio de población ni trasladarse a la externa.

También se exporta estabilidad externa por mes sin reajustar nada. XGBoost inicial tiene ROC-AUC mensual entre 0,7390 y 0,9665; AP entre 0,6513 y 0,9847. La prevalencia mensual pasa de aproximadamente 35–37% en julio-octubre a 53,47% en noviembre y 66,23% en diciembre. El filtro de disponibilidad al cierre favorece resultados tempranos cerca del corte; estos cambios no son evidencia de una mejora causal del modelo con el tiempo. La AP agregada no resume estabilidad operacional, ni permite comparar meses ignorando su composición.

![Estabilidad interna](figures/optimizacion_6_estabilidad.png)

## 6. Análisis de umbrales, solo validación

Rejilla prefijada 0,1 a 0,9, con predicción positiva si probabilidad >= umbral. No se busca un umbral definitivo por F1 o por costes hipotéticos. Tabla del candidato conservado, XGBoost inicial:

THRESHOLDS_MAIN

Comparación de los cinco modelos a 0,3 / 0,5 / 0,7; los 45 casos completos están en optimizacion_6_umbrales.csv:

THRESHOLDS_ALL

Bajar XGBoost de 0,5 a 0,3 aumenta recall de 53,86% a 78,67%, pero reduce precision de 86,30% a 69,47% y eleva alertas de 4839 a 8779 (26,74% → 48,51%). Se evitarían 1923 FN en esta clasificación, a cambio de 2017 FP adicionales; no significa que un contacto evitase esas cancelaciones. A 0,7 precision alcanza 96,12%, pero solo se detecta 36,39% de cancelaciones. El umbral 0,3 ilustra un equilibrio, no una recomendación definitiva ni un máximo continuo certificado.

![Carga y cobertura por umbral](figures/optimizacion_6_umbrales.png)

## 7. Calibración sin ajustar un calibrador

CALIBRATION

Brier de referencia con probabilidad constante igual a la tasa de entrenamiento: BRIER_CONSTANT. Menor Brier es mejor, pero combina calibración, resolución y variabilidad del objetivo; no demuestra calibración por sí solo. ECE usa diez bins fijos y es descriptivo, sensible a la partición, no una garantía estadística. optimizacion_6_calibracion_bins.csv conserva tamaños y medias, sin dibujar bins vacíos.

Todos los modelos infrapredicen la cancelación en promedio. XGBoost inicial promedia 35,68% frente a 42,84% observado, brecha −7,16 puntos porcentuales. En su rango de 0,5 (incluido) a 0,6 (excluido), la probabilidad media es 54,34% frente a tasa 69,02% (1178 filas). Las curvas muestran desviaciones también en otros rangos. No cabe tratar esas salidas como probabilidades fiables de producción. XGBoost inicial tiene el menor Brier (0,155458), pero **no está suficientemente acreditada su calibración**. Logística tampoco queda calibrada por ser más sencilla; su Brier es 0,172022.

![Precision-recall y calibración](figures/optimizacion_6_pr_calibracion.png)

Ordenación (ROC-AUC/AP), probabilidad (Brier/curvas) y decisión de contactar son diferentes. No se ha calibrado con esta validación ni se ha ensayado un calibrador para conservar el que mejor salga aquí.

Para calibrar sin fuga haría falta prefijar un bloque temporal de calibración dentro del entrenamiento externo, con etiquetas disponibles al corte, entrenar el modelo base antes de ese bloque y congelarlo para producir los scores de calibración. Ni ese bloque ni un bloque posterior de evaluación se usarían para elegir hiperparámetros; alternativamente, generar scores temporales fuera de ajuste en un diseño anidado con purga por disponibilidad. Los folds internos ya usados para tuning no constituyen una calibración independiente por sí mismos. Tras ajustar el calibrador solo en el bloque permitido, evaluar una vez en un periodo posterior nuevo no utilizado. La validación actual ya explorada no puede recuperar independencia cambiándole el nombre; más historia y nuevos snapshots serían preferibles. Se explica el diseño, no se implementa en esta fase.

## 8. Escenarios de negocio hipotéticos

Contacto preventivo o solicitud de confirmación por personal del hotel, con capacidad y criterios de atención definidos. FP implica contacto innecesario, carga de trabajo y posible molestia; FN deja una cancelación sin anticipar y limita planificación. No se propone cancelar automáticamente, exigir penalizaciones ni cambiar derechos usando solo la predicción.

Los pesos siguientes son **supuestos ilustrativos en unidades arbitrarias por error**, no euros, no costes reales ni estimaciones de beneficio: FP/FN 1/1, 1/5 y 5/1. Carga = peso_FP × FP + peso_FN × FN. No incluye todos los costes de atención ni demuestra que intervenir reduzca la cancelación.

SCENARIOS

Por ejemplo, si FN pesara cinco veces FP, a 0,2 la carga ilustrativa sería 8877 frente a 18548 a 0,5. Si FP pesara cinco veces FN, sería 21753 frente a 6892. Cambiar supuestos cambia la preferencia; no se adopta ninguno como política real. Tampoco se transforma esa relación en una fórmula de umbral de probabilidad mientras la calibración sea incierta. La proporción alertada debe contrastarse con la capacidad de atención; la eficacia de contactar requeriría una evaluación de intervención separada.

## 9. Candidato principal para la siguiente fase

**XGBoost inicial de fase 5**, no la variante seleccionada por búsqueda: 300 árboles, profundidad máxima 4, learning_rate=0,05, subsample=0,8, colsample_bytree=0,8, min_child_weight=1 y reg_lambda=1 efectivos por defecto, tree_method=hist, seed 42, cuatro hilos. Se conserva la fábrica original; en su interfaz sklearn min_child_weight/reg_lambda pueden figurar None porque delegan al default del motor. No se cambia el umbral operativo.

Ofrece la mayor ROC-AUC y AP externa entre las cinco referencias, el mejor Brier observado, precision 86,30% y recall 53,86% a 0,5. Frente a logística reduce 330 FP y siete FN, con complejidad mayor pero entrenamiento local inferior a un segundo en esta configuración. La ganancia de detección a 0,5 es pequeña; la capacidad de ordenar mejor podría servir para seguimiento con recursos limitados, aún sin utilidad acreditada. Los ensembles son menos transparentes que logística y requieren una revisión posterior autorizada. Logística se conserva como referencia interpretable y rápida. LightGBM no ofrece una ventaja suficiente aquí.

La elección es **provisional para estudio**, no modelo listo para producción. Estabilidad interna deficiente, calibración sesgada y disponibilidad histórica incierta pesan más que una mejora decimal de AUC. Conservar la inicial sigue la instrucción de no sustituirla cuando la optimización no mejora.

## 10. Ejecución, archivos e integridad

Se crearon src/optimization.py, tests/test_optimization.py, notebooks/optimizacion.ipynb, este informe, registros optimizacion_6_* de plan, selección previa a evaluación, búsqueda completa, folds y sus IDs, métricas, predicciones externas, umbrales, bins/calibración, escenarios, estabilidad mensual y verificación, más tres PNG. Se actualizan README y src/run_notebook.py; no se necesitan nuevas dependencias.

La búsqueda real y los dos ajustes/predicciones externas terminaron. El primer intento de exportar la verificación final falló por el default NaN de XGBoost, después de guardar tablas, predicciones y figuras. Se corrigió su normalización JSON y se recuperó el registro desde esos artefactos y los parámetros seleccionados, sin repetir las predicciones externas. Los tiempos internos y selección proceden del archivo previo a evaluación; el registro de advertencias externas en memoria no se recuperó y se marca como desconocido, sin asumir que estuviera vacío. Las auditorías de ajuste sí habían finalizado. El notebook completo posterior verifica y presenta los resultados congelados sin errores ni nuevos ajustes, y conserva todas sus salidas.

Reejecutar el notebook detecta el registro final, verifica hashes/IDs, reconstruye folds y candidatos con la misma semilla, recalcula métricas, umbrales y calibración sobre scores guardados y regenera el informe. No ajusta de nuevo ni añade predicciones externas. Para reproducir la búsqueda desde cero se dispone del código y el plan; requeriría una copia de trabajo sin los artefactos fase 6, preservando la evidencia actual. No se elimina ningún registro para relanzar tuning tras ver validación. Reproducción de análisis no equivale a dos ejecuciones completas de búsqueda; solo hubo una búsqueda de 54 ajustes y dos predicciones externas nuevas. Los scores nuevos de XGBoost se restauran como float32 al leer su representación decimal CSV, para reproducir también Brier con precisión numérica. No se guardan modelos serializados ni predicciones de prueba.

Las 26 pruebas automatizadas del proyecto se superaron. Las pruebas sintéticas comprueban cortes estrictos, exclusión por disponibilidad, rechazo de filas externas y duplicados cruzados, ventanas no solapadas, semillas/espacios, umbrales, escenarios, bins y detección de un preprocesador ajustado indebidamente con datos futuros. Se conservan las pruebas anteriores. Se verifican también las huellas de los datos, manifiesto, informes e histórico, y los módulos del protocolo. El registro técnico incluye versiones y trazabilidad de la recuperación.

## 11. Limitaciones y propuesta posterior

No hay alta real ni primera disponibilidad de resultados acreditadas, snapshots iniciales de predictores ni cierre PMS demostrado. El filtro por resultados registrados conserva sesgo hacia menor antelación/cancelaciones tempranas y no representa todas las reservas. Duplicados conservados pueden sobreponderar patrones; no hay IDs reales de reserva/cliente. El EDA vio todo el archivo. La validación externa se ha utilizado para comparar en fase 5 y para revisar candidatos/umbrales/calibración aquí: no es una evaluación final independiente de selección. Ni la elección de modelo ni los umbrales explorados deben presentarse como validados en producción. No se calculan intervalos suponiendo independencia no acreditada. La búsqueda cubre ocho propuestas por familia, no todos los parámetros posibles, y las medias internas sobre periodos correlacionados no son una garantía de estabilidad.

Para la siguiente fase, tras autorización: revisar explicabilidad y errores del XGBoost inicial manteniendo logística como referencia, documentar disponibilidad real de variables y decidir un diseño temporal separado para calibración y decisión de contacto con costes/capacidad reales. No se ejecuta SHAP, no se preparan entregables finales ni se abre prueba. Una evaluación final solo tendrá sentido con decisiones congeladas y una declaración explícita de estas limitaciones; datos prospectivos serían necesarios para respaldar uso al crear reservas.

**Fin exclusivo de fase 6. Se espera revisión y autorización del usuario.**
'''
    parameter_rows=[]
    time_rows=[]
    matrix_rows=[]
    for name in ['xgboost','lightgbm']:
        search=detail['busquedas'][name]
        parameter_rows.append({'modelo':name,'parametros':json.dumps(search['parametros_seleccionados'],ensure_ascii=False)})
        time_rows.append({'modelo':name,'ajustes_internos':search['ajustes'],'segundos_busqueda':search['segundos']})
    for row in metrics.itertuples():
        matrix_rows.append({'modelo':row.modelo,'matriz':str([[row.tn,row.fp],[row.fn,row.tp]])})
    replacements={
        'FOLDS':markdown(folds[fold_columns]), 'SELECTION':markdown(selected[cv_columns]),
        'PARAMS':markdown(pd.DataFrame(parameter_rows)), 'TIMES':markdown(pd.DataFrame(time_rows)),
        'METRICS':markdown(metrics), 'MATRICES':markdown(pd.DataFrame(matrix_rows)),
        'CALIBRATION':markdown(calibration), 'BRIER_CONSTANT':f"{detail['brier_constante_tasa_train']:.6f}",
        'THRESHOLDS_MAIN':markdown(thresholds[thresholds.modelo.eq('xgboost')][threshold_columns]),
        'THRESHOLDS_ALL':markdown(thresholds[thresholds.umbral.isin([.3,.5,.7])][threshold_columns]),
        'SCENARIOS':markdown(scenario_view[scenario_columns])}
    for key,value in replacements.items():text=text.replace(key,value)
    # Persistir documentación o metadatos para revisar las decisiones sin volver a ejecutar el modelo.
    (Path(root)/'reports/fase_6_optimizacion.md').write_text(text,encoding='utf-8')
