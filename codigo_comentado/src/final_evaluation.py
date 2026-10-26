# EDICIÓN COMENTADA PARA LECTURA. Las fuentes ejecutadas y selladas permanecen en la raíz.
# Evaluación final: scores congelados antes de leer objetivos y una sola inferencia.
# Solo se añaden comentarios: no se han ejecutado instrucciones de esta copia.
"""Fase 9: inferencia única, decisiones congeladas antes de leer y; nunca fit."""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
import hashlib
import importlib.metadata
import json
import math
import pickle
import platform

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import (roc_auc_score,average_precision_score,brier_score_loss,confusion_matrix)

from src.features import FEATURES,NUMERIC_FEATURES,CATEGORICAL_FEATURES
from src.splitting import PROTOCOL_V3,temporal_split_v3
from src.temporal_bias_v3 import read_rows
from src.decision_policy import apply_frozen_policy
from src.comparison import sha
from src.optimization import json_write,markdown

CODE_VERSION='fase9_v1_inferencia_unica'
BOOTSTRAP_REPS=500
BLOCK_DAYS=14
BOOTSTRAP_SEED=42


# Registrar el instante UTC para demostrar el orden de las operaciones de evaluación.
def utc_now():
    return datetime.now(timezone.utc).isoformat()


# Detener la evaluación si una condición contradice la especificación congelada.
def require(condition,message):
    if not condition:raise ValueError('Discrepancia previa a evaluación: '+message)


# Contrastar IDs y roles contra v3 y comprobar integridad y ausencia de solapamientos.
def verify_partitions(manifest,metadata):
    require(len(manifest)==119390 and manifest.meta_row_id.is_unique,'manifiesto incompleto o IDs duplicados')
    require(manifest.meta_row_id.tolist()==metadata.meta_row_id.tolist(),'orden/IDs de metadatos')
    # Asignar cohortes por llegada sin seleccionar filas según su desenlace individual.
    expected=temporal_split_v3(metadata)
    require(manifest.particion.equals(expected),'asignaciones distintas de v3')
    roles={role:set(manifest.loc[manifest.particion.eq(role),'meta_row_id']) for role in ['entrenamiento','validacion','prueba_reservada']}
    require(not (roles['prueba_reservada']&roles['entrenamiento']) and not (roles['prueba_reservada']&roles['validacion']),'solapamiento prueba/desarrollo')
    require([len(roles[k]) for k in ['entrenamiento','validacion','prueba_reservada']]==[49157,19911,32829],'tamaños de particiones')
    return expected


# Resumir el estado aprendido para comprobar que la inferencia no lo modifica.
def learned_fingerprint(model):
    pre=model.named_steps['preprocessor'];clf=model.named_steps['classifier']
    numeric=pre.named_transformers_['numeric'];cat=pre.named_transformers_['categorical']
    state=(clf.get_params(),clf.coef_,clf.intercept_,clf.classes_,clf.n_iter_,
           numeric.named_steps['imputer'].statistics_,numeric.named_steps['scaler'].mean_,
           numeric.named_steps['scaler'].scale_,numeric.named_steps['scaler'].n_samples_seen_,
           cat.named_steps['imputer'].statistics_,cat.named_steps['encoder'].categories_)
    return hashlib.sha256(pickle.dumps(state,protocol=5)).hexdigest()


def predict_without_fit(model,features):
    """Una llamada predict_proba; bloquea también fit de todos sus transformadores."""
    # Bloquear explícitamente cualquier intento de ajuste durante la inferencia final.
    def forbidden(*args,**kwargs):raise RuntimeError('Reentrenamiento prohibido en fase 9')
    with ExitStack() as stack:
        for cls in [Pipeline,LogisticRegression,ColumnTransformer,SimpleImputer,StandardScaler,OneHotEncoder]:
            for name in ['fit','fit_transform']:
                if hasattr(cls,name):stack.enter_context(patch.object(cls,name,forbidden))
        return np.asarray(model.predict_proba(features)[:,1],dtype='float64')


# Verificar hashes, versiones, modelo, entradas y política antes de consultar objetivos.
def preflight(root):
    """Ninguna lectura de la columna objetivo, ninguna predicción."""
    root=Path(root);out=root/'reports';spec_path=out/'seleccion_8_especificacion_congelada.json'
    spec=json.loads(spec_path.read_text(encoding='utf-8'))
    anchor=json.loads((out/'seleccion_8_reproduccion.json').read_text(encoding='utf-8'))
    require(sha(spec_path)==anchor['especificacion_sha256'],'SHA de especificación')
    for path,expected in spec['huellas_entradas'].items():require(sha(root/path)==expected,'SHA de '+path)
    require(spec['modelo_seleccionado']=='regresion_logistica' and spec['clase_modelo']=='sklearn.linear_model.LogisticRegression','modelo seleccionado')
    require(spec['protocolo']==PROTOCOL_V3,'protocolo congelado')
    require(spec['predictores']==FEATURES and spec['numericas']==NUMERIC_FEATURES and spec['categoricas']==CATEGORICAL_FEATURES,'predictores')
    require(spec['calibrador'] is None and spec['entrenamiento_final']['usar_validacion_para_refit'] is False,'calibración/refit')
    policy=spec['politica']
    require(policy['tipo']=='top_capacidad_mensual' and policy['capacidad_pct']==20 and policy['seed_desempate']==42,'capacidad/política/seed')
    require(policy['clave_grupo']=='mes_llegada_YYYY-MM' and policy['fraccion_redondeo']=='floor' and policy['umbral_fijo'] is None,'lote/redondeo/umbral')
    require(policy['desempate']=='score_desc_sha256(seed|ID)_asc_ID_asc_sin_redondear_score','desempate')
    require(policy['ambito_hoteles']=='ambos hoteles juntos; sin cuotas por hotel','ámbito de capacidad')
    require(platform.python_version()==spec['versiones']['python'],'versión de Python')
    for library,version in spec['versiones'].items():
        if library!='python':require(importlib.metadata.version(library)==version,'versión de '+library)
    model_path=root/spec['artefacto_modelo']
    require(sha(model_path)==spec['artefacto_sha256']==anchor['modelo_sha256'],'SHA del modelo')
    state=json.loads((out/'estado_protocolo.json').read_text(encoding='utf-8'))
    division=json.loads((out/'division_temporal.json').read_text(encoding='utf-8'))
    require(state['vigente']==PROTOCOL_V3['version'] and division['protocolo']==PROTOCOL_V3,'archivos activos')
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    manifest=pd.read_csv(out/'particiones_temporales.csv')
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    metadata=pd.read_csv(root/'data/processed/hotel_bookings_prepared.csv',usecols=['meta_row_id','meta_arrival_date','meta_duplicate_group'])
    assigned=verify_partitions(manifest,metadata)
    require(np.array_equal(metadata.meta_row_id,np.arange(len(metadata))),'IDs técnicos distintos de posiciones originales')
    train_ids=manifest.loc[assigned.eq('entrenamiento'),'meta_row_id'].to_numpy(dtype='int64')
    # Calcular una huella determinista para trazabilidad; no usarla como característica predictiva.
    require(hashlib.sha256(train_ids.tobytes()).hexdigest()==spec['entrenamiento_final']['sha_ids_int64'],'IDs del fit congelado')
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    header=pd.read_csv(root/'data/processed/hotel_bookings_prepared.csv',nrows=0)
    require(all(c in header for c in FEATURES),'columnas de entrada incompletas')
    # Recuperar el artefacto ya entrenado; cargarlo no autoriza refit ni recalibración.
    model=joblib.load(model_path)
    require(isinstance(model,Pipeline) and list(model.named_steps)==['preprocessor','classifier'],'estructura del pipeline')
    clf=model.named_steps['classifier'];pre=model.named_steps['preprocessor']
    require(isinstance(clf,LogisticRegression) and clf.get_params()==spec['hiperparametros'],'clase/hiperparámetros')
    require(clf.classes_.tolist()==[0,1] and spec['clase_positiva']==1,'clase positiva')
    require(pre.feature_names_in_.tolist()==FEATURES,'nombres de entrada del modelo')
    require(pre.get_feature_names_out().tolist()==spec['preprocesamiento']['columnas_transformadas'],'columnas transformadas')
    require(pre.remainder=='drop' and pre.sparse_threshold==1.,'ColumnTransformer')
    require(list(pre.named_transformers_['numeric'].named_steps)==['imputer','scaler'],'pipeline numérico')
    require(list(pre.named_transformers_['categorical'].named_steps)==['imputer','encoder'],'pipeline categórico')
    num=pre.named_transformers_['numeric'];cat=pre.named_transformers_['categorical']
    require(num.named_steps['imputer'].strategy=='median' and num.named_steps['imputer'].keep_empty_features,'imputación numérica')
    require(cat.named_steps['imputer'].strategy=='constant' and cat.named_steps['imputer'].fill_value=='Desconocido','imputación categórica')
    require(cat.named_steps['encoder'].handle_unknown=='ignore' and cat.named_steps['encoder'].sparse_output,'OneHotEncoder')
    require(int(num.named_steps['scaler'].n_samples_seen_)==49157,'muestra de entrenamiento del scaler')
    code_paths=['src/final_evaluation.py','src/decision_policy.py','src/splitting.py','src/temporal_bias_v3.py','src/features.py']
    protected=[p for folder in ['data','reports','models'] for p in (root/folder).rglob('*') if p.is_file()
               and not p.name.startswith('evaluacion_9_') and p.name!='fase_9_evaluacion_final.md']
    # Calcular una huella determinista para trazabilidad; no usarla como característica predictiva.
    check={'timestamp_utc':utc_now(),'codigo_version':CODE_VERSION,'codigo_sha256':{p:sha(root/p) for p in code_paths},
        'especificacion_sha256':sha(spec_path),'modelo_sha256':sha(model_path),'manifesto_sha256':sha(out/'particiones_temporales.csv'),
        'n_train':49157,'n_validacion':19911,'n_prueba':32829,'ids_sin_solapamientos':True,'objetivos_prueba_leidos':False,
        'reentrenamiento_permitido':False,'recalibracion_permitida':False,'cambios_politica_permitidos':False,
        'sha_ids_prueba_int64':hashlib.sha256(metadata.loc[assigned.eq('prueba_reservada'),'meta_row_id'].to_numpy(dtype='int64').tobytes()).hexdigest(),
        'versiones':spec['versiones'],'archivos_previos_sha256':{str(p.relative_to(root)):sha(p) for p in protected},
        'plan_previo_sha256':sha(out/'evaluacion_9_plan_previo.md')}
    return spec,model,metadata.loc[assigned.eq('prueba_reservada')].copy(),check


# Separar métricas de la política binaria de las métricas globales calculadas con scores.
def measure(y,scores,alerts):
    y=np.asarray(y,dtype='int64');p=np.asarray(scores,dtype='float64');a=np.asarray(alerts,dtype=bool)
    if not len(y) or len(y)!=len(p) or len(y)!=len(a) or not np.isin(y,[0,1]).all():raise ValueError('Resultados no alineados o etiquetas inválidas')
    # Contar TN, FP, FN y TP con orden de clases explícito para evitar invertir su interpretación.
    # Mantener clases [0,1]: TN y FP pertenecen a no cancelaciones; FN y TP a cancelaciones.
    tn,fp,fn,tp=confusion_matrix(y,a,labels=[0,1]).ravel()
    policy={'n':len(y),'priorizadas':int(a.sum()),'porcentaje_priorizado':100*float(a.mean()),
        'precision':float(tp/(tp+fp)) if tp+fp else 0.,'recall':float(tp/(tp+fn)) if tp+fn else 0.,
        'f1':float(2*tp/(2*tp+fp+fn)) if 2*tp+fp+fn else 0.,
        'fp':int(fp),'fn':int(fn),'tp':int(tp),'tn':int(tn),'matriz_confusion':[[int(tn),int(fp)],[int(fn),int(tp)]]}
    # Medir la capacidad de ordenar scores; esta métrica no fija la política de alertas.
    global_metrics={'roc_auc':float(roc_auc_score(y,p)) if np.unique(y).size==2 else None,
        'average_precision':float(average_precision_score(y,p)) if y.any() else 0.,
        'brier':float(brier_score_loss(y,p)),'tasa_cancelacion':float(y.mean()),'probabilidad_media':float(p.mean()),
        'canceladas':int(y.sum()),'brecha_media':float(p.mean()-y.mean())}
    return policy,global_metrics


def moving_day_indices(dates,block_days,repetitions,seed):
    """Genera muestras de días completos; no altera scores ni decisiones."""
    dates=pd.to_datetime(dates).normalize();calendar=pd.date_range(dates.min(),dates.max(),freq='D')
    if block_days<1 or block_days>len(calendar):raise ValueError('Bloque temporal inválido')
    day_rows=[np.flatnonzero(dates==day) for day in calendar]
    rng=np.random.default_rng(seed)
    for _ in range(repetitions):
        starts=rng.integers(0,len(calendar)-block_days+1,size=math.ceil(len(calendar)/block_days))
        selected_days=np.concatenate([np.arange(start,start+block_days) for start in starts])[:len(calendar)]
        yield np.concatenate([day_rows[i] for i in selected_days])


# Resumir remuestreo de bloques de días con decisiones originales fijas.
def uncertainty(data,repetitions=BOOTSTRAP_REPS,block_days=BLOCK_DAYS,seed=BOOTSTRAP_SEED):
    rows=[]
    y=data.is_canceled.to_numpy();p=data.score.to_numpy();a=data.alerta.to_numpy()
    for number,index in enumerate(moving_day_indices(pd.DatetimeIndex(data.fecha_llegada),block_days,repetitions,seed)):
        policy,global_metrics=measure(y[index],p[index],a[index])
        rows.append({'replica':number,**{k:policy[k] for k in ['precision','recall','f1']},
            **{k:global_metrics[k] for k in ['roc_auc','average_precision','brier','tasa_cancelacion','probabilidad_media']}})
    reps=pd.DataFrame(rows)
    policy,global_metrics=measure(y,p,a);points={**policy,**global_metrics};intervals=[]
    for column in reps.columns.drop('replica'):
        values=reps[column].dropna()
        intervals.append({'metrica':column,'estimacion':points[column],'p2_5':float(values.quantile(.025)),
            'p97_5':float(values.quantile(.975)),'replicas_validas':len(values)})
    return reps,pd.DataFrame(intervals)


# Reproducir el checkpoint completo o realizar la inferencia autorizada y congelarla antes de leer y.
def run_evaluation(root):
    root=Path(root);out=root/'reports';receipt_path=out/'evaluacion_9_recibo.json'
    spec,model,meta,check=preflight(root)
    scores_path=out/'evaluacion_9_predicciones_congeladas.csv'
    # Distinguir resultados ya guardados de una ejecución pendiente antes de continuar.
    if receipt_path.exists():
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        require(receipt['especificacion_sha256']==check['especificacion_sha256'],'especificación cambió desde inferencia')
        require(receipt['modelo_sha256']==check['modelo_sha256'],'modelo cambió desde inferencia')
        require(receipt['manifiesto_sha256']==check['manifesto_sha256'],'manifiesto cambió desde inferencia')
        require(receipt['codigo_inferencia_sha256']==sha(Path(__file__)),'código cambió desde inferencia; no repetir automáticamente')
        if receipt['estado']=='inicio_inferencia':raise RuntimeError('Iniciar otra inferencia está bloqueado: revisar/documentar fallo técnico')
        require(sha(scores_path)==receipt['scores_sha256'],'scores congelados alterados')
        print('Reproducción de resultados congelados: cero llamadas de inferencia, sin entrenamiento.',flush=True)
    else:
        # Prueba de todas las condiciones obligatorias antes de cualquier y_test.
        json_write(out/'evaluacion_9_preflight.json',check)
        (out/'evaluacion_9_fuente_ejecucion.py').write_bytes(Path(__file__).read_bytes())
        receipt={'estado':'inicio_inferencia','timestamp_utc':utc_now(),'codigo_version':CODE_VERSION,
            'codigo_inferencia_sha256':sha(Path(__file__)),'especificacion_sha256':check['especificacion_sha256'],
            'modelo_sha256':check['modelo_sha256'],'manifiesto_sha256':check['manifesto_sha256'],
            'llamadas_predict_proba':0,'reentrenamientos':0,'recalibraciones':0}
        json_write(receipt_path,receipt)
        positions=meta.index.to_numpy()
        x=read_rows(root/'data/processed/hotel_bookings_prepared.csv',spec['predictores'],positions)
        require(x.columns.tolist()==spec['predictores'],'orden de columnas al leer predictores')
        x[NUMERIC_FEATURES]=x[NUMERIC_FEATURES].astype('float64')
        for c in CATEGORICAL_FEATURES:x[c]=x[c].astype(object).where(x[c].notna(),np.nan)
        require('is_canceled' not in x and not any(c.startswith('meta_') for c in x),'objetivo/metadatos dentro de X')
        fingerprint=learned_fingerprint(model)
        print('Única llamada de inferencia sobre prueba v3, sin acceso a etiquetas.',flush=True)
        receipt.update(llamadas_predict_proba=1,timestamp_inicio_predict_utc=utc_now())
        json_write(receipt_path,receipt)
        p=predict_without_fit(model,x)
        require(learned_fingerprint(model)==fingerprint,'estadísticas aprendidas cambiaron')
        require(np.isfinite(p).all() and ((p>=0)&(p<=1)).all(),'probabilidades inválidas')
        months=pd.to_datetime(meta.meta_arrival_date).dt.strftime('%Y-%m').to_numpy()
        predictions,borders=apply_frozen_policy(spec,p,meta.meta_row_id.to_numpy(),months)
        predictions['fecha_llegada']=meta.meta_arrival_date.to_numpy()
        predictions['hotel']=x.hotel.to_numpy()
        # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
        predictions.to_csv(scores_path,index=False)
        # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
        borders.to_csv(out/'evaluacion_9_bordes_empates.csv',index=False)
        # Confirmar scores y decisiones antes de abrir las etiquetas evita cambiar la política según sus aciertos.
        receipt.update(estado='predicciones_congeladas',timestamp_congelacion_utc=utc_now(),scores_sha256=sha(scores_path),
                       huella_parametros_antes_despues=fingerprint,objetivos_prueba_leidos=False)
        json_write(receipt_path,receipt)
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    frozen=pd.read_csv(scores_path)
    require(frozen.meta_row_id.tolist()==meta.meta_row_id.tolist(),'IDs de scores y prueba distintos')
    # Se valida de nuevo la cuota SIN objetivos antes de leerlos.
    reapplied,borders=apply_frozen_policy(spec,frozen.score,frozen.meta_row_id,frozen.mes_llegada)
    require(np.array_equal(frozen.alerta,reapplied.alerta),'selección no reproduce política congelada')
    # Un recibo completo activa lectura de resultados: esta rama no vuelve a predecir prueba.
    if receipt['estado']=='completada':
        for path,expected in receipt['archivos_resultados_sha256'].items():require(sha(root/path)==expected,path+' cambió')
        result=json.loads((out/'evaluacion_9_metricas.json').read_text(encoding='utf-8'))
        # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
        tables={name:pd.read_csv(out/f'evaluacion_9_{name}.csv') for name in ['mensual','hoteles','comparacion_validacion','composicion','intervalos','calibracion_bins']}
        make_figures(out,tables,result)
        write_report(root,tables,result,receipt)
        return tables,result,receipt
    # Primera lectura de etiquetas: posterior a commit de scores/selección y hash.
    require(sha(scores_path)==receipt['scores_sha256'],'scores cambiaron antes de leer etiquetas')
    print('Decisiones guardadas; ahora se leen las etiquetas para evaluar, sin reajustes.',flush=True)
    labels_path=out/'evaluacion_9_etiquetas_prueba.csv'
    # Registrar la primera consulta de y después de la congelación permite verificar el orden temporal.
    receipt.setdefault('timestamp_primer_acceso_etiquetas_utc',utc_now())
    receipt['scores_sha256_verificado_antes_etiquetas']=sha(scores_path)
    json_write(receipt_path,receipt)
    # Distinguir resultados ya guardados de una ejecución pendiente antes de continuar.
    if labels_path.exists():
        require(sha(labels_path)==receipt.get('etiquetas_sha256'),'snapshot de etiquetas sin huella válida')
        # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
        labels=pd.read_csv(labels_path).set_index('meta_row_id').loc[frozen.meta_row_id].is_canceled.to_numpy()
    else:
        labels=read_rows(root/'data/processed/hotel_bookings_prepared.csv',['is_canceled'],meta.index.to_numpy()).is_canceled.to_numpy()
        # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
        pd.DataFrame({'meta_row_id':frozen.meta_row_id,'is_canceled':labels}).to_csv(labels_path,index=False)
    receipt.update(etiquetas_sha256=sha(labels_path),estado='etiquetas_congeladas')
    json_write(receipt_path,receipt)
    data=frozen.copy();data['is_canceled']=labels
    require(np.isin(labels,[0,1]).all(),'etiquetas no binarias')
    policy,global_metrics=measure(labels,data.score,data.alerta)
    monthly=[];hotels=[]
    for column,rows in [('mes_llegada',monthly),('hotel',hotels)]:
        for value,g in data.groupby(column,sort=True,observed=True):
            pol,glob=measure(g.is_canceled,g.score,g.alerta)
            if column=='mes_llegada':require(pol['priorizadas']==len(g)*20//100,'capacidad mensual incorrecta')
            rows.append({column:value,**{k:v for k,v in pol.items() if k!='matriz_confusion'},**glob})
    # Auditoría posterior del seguimiento observado, sin cambiar elegibilidad/política.
    status=read_rows(root/'data/raw/hotel_bookings.csv',['reservation_status_date'],meta.index.to_numpy())
    availability=pd.to_datetime(status.reservation_status_date)+pd.Timedelta(days=1)
    close=pd.Timestamp(PROTOCOL_V3['test_followup_assumed_exclusive'])
    followup={'cierre_asumido_exclusivo':str(close.date()),'cierre_operativo_acreditado':None,
        'max_disponibilidad_proxy':str(availability.max().date()),'estados_proxy_no_anteriores_cierre':int(availability.ge(close).sum()),
        'filas_retiradas':0,'no_garantiza_integridad_real':True}
    validation=json.loads((out/'seleccion_8_especificacion_congelada.json').read_text(encoding='utf-8'))
    comparison=[]
    previous={**validation['metricas_validacion_politica'],
              'roc_auc':validation['metricas_validacion_modelo_umbral_05']['roc_auc'],
              'average_precision':validation['metricas_validacion_modelo_umbral_05']['average_precision'],
              'brier':validation['calibracion_validacion']['brier'],
              'tasa_cancelacion':validation['calibracion_validacion']['tasa_observada'],
              'probabilidad_media':validation['calibracion_validacion']['probabilidad_media']}
    for key in ['precision','recall','f1','roc_auc','average_precision','brier','tasa_cancelacion','probabilidad_media']:
        current={**policy,**global_metrics}[key]
        comparison.append({'metrica':key,'validacion_v3':previous[key],'prueba_v3':current,'diferencia_prueba_menos_validacion':current-previous[key]})
    # Composición sin cambiar segmentos/política: hoteles y rasgos ya previstos.
    test_profiles=read_rows(root/'data/processed/hotel_bookings_prepared.csv',['lead_time','market_segment','customer_type'],meta.index.to_numpy())
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    vmanifest=pd.read_csv(out/'particiones_temporales.csv');vpos=np.flatnonzero(vmanifest.particion.eq('validacion'))
    vprofiles=read_rows(root/'data/processed/hotel_bookings_prepared.csv',['hotel','lead_time','market_segment','customer_type'],vpos)
    test_profiles['hotel']=data.hotel.to_numpy()
    composition=[]
    for column in ['hotel','market_segment','customer_type']:
        values=sorted(set(vprofiles[column].astype(str))|set(test_profiles[column].astype(str)))
        for value in values:composition.append({'variable':column,'categoria':value,
            'n_validacion':int(vprofiles[column].eq(value).sum()),'n_prueba':int(test_profiles[column].eq(value).sum()),
            'proporcion_validacion':float(vprofiles[column].eq(value).mean()),'proporcion_prueba':float(test_profiles[column].eq(value).mean())})
    lead_summary={'validacion':{str(q):float(vprofiles.lead_time.quantile(q)) for q in [.1,.5,.9]},
                  'prueba':{str(q):float(test_profiles.lead_time.quantile(q)) for q in [.1,.5,.9]}}
    reps,intervals=uncertainty(data)
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    reps.to_csv(out/'evaluacion_9_bootstrap_replicas.csv',index=False)
    calibration=[]
    bins=np.minimum((data.score.to_numpy()*10).astype(int),9)
    for k in range(10):
        g=data.iloc[np.flatnonzero(bins==k)]
        if len(g):calibration.append({'bin':k,'n':len(g),'probabilidad_media':float(g.score.mean()),'tasa_observada':float(g.is_canceled.mean())})
    tables={'mensual':pd.DataFrame(monthly),'hoteles':pd.DataFrame(hotels),'comparacion_validacion':pd.DataFrame(comparison),
            'composicion':pd.DataFrame(composition),'intervalos':intervals,'calibracion_bins':pd.DataFrame(calibration)}
    for name,table in tables.items():table.to_csv(out/f'evaluacion_9_{name}.csv',index=False)
    result={'codigo_version':CODE_VERSION,'protocolo':PROTOCOL_V3,'modelo':'regresion_logistica_congelada_fase_8',
        'politica':policy,'modelo_global':global_metrics,'politica_especificada':spec['politica'],
        'seguimiento_proxy':followup,'antelacion_cuantiles':lead_summary,
        'incertidumbre':{'metodo':'bloques móviles no circulares de días; decisiones originales fijas',
            'longitud_dias':BLOCK_DAYS,'replicas':BOOTSTRAP_REPS,'seed':BOOTSTRAP_SEED,'percentiles':[.025,.975],
            'cobertura_frecuentista_garantizada':False},'n_inferencias':1,'refit':False,'recalibracion':False,
        'especificacion_sha256':check['especificacion_sha256'],'modelo_sha256':check['modelo_sha256'],
        'scores_congelados_sha256':receipt['scores_sha256'],'etiquetas_sha256':sha(labels_path)}
    json_write(out/'evaluacion_9_metricas.json',result)
    for path,expected in check['archivos_previos_sha256'].items():require(sha(root/path)==expected,'archivo previo '+path)
    receipt.update(estado='completada',timestamp_final_utc=utc_now(),objetivos_prueba_leidos=True,
        etiquetas_leidas_despues_de_congelacion_scores=True)
    receipt['archivos_resultados_sha256']={str(p.relative_to(root)):sha(p) for p in out.glob('evaluacion_9_*') if p.is_file() and p.name!='evaluacion_9_recibo.json'}
    json_write(receipt_path,receipt)
    make_figures(out,tables,result)
    write_report(root,tables,result,receipt)
    return tables,result,receipt


# Representar las tablas de esta fase sin usar el gráfico para ajustar el modelo.
def make_figures(out,tables,result):
    # Crear una figura descriptiva; sus ejes y títulos deben identificar población y versión del protocolo.
    fig,axes=plt.subplots(1,2,figsize=(12,4.5));monthly=tables['mensual']
    axes[0].plot(monthly.mes_llegada,monthly.precision,marker='o',label='Precision política')
    axes[0].plot(monthly.mes_llegada,monthly.recall,marker='o',label='Recall política')
    axes[0].set(ylim=(0,1),ylabel='Valor',title='Política mensual congelada — prueba v3')
    axes[1].plot(monthly.mes_llegada,monthly.tasa_cancelacion,marker='o',label='Tasa observada')
    axes[1].plot(monthly.mes_llegada,monthly.probabilidad_media,marker='o',label='Score medio')
    axes[1].set(ylim=(0,1),ylabel='Valor',title='Composición y puntuaciones por mes')
    for ax in axes:ax.legend(fontsize=8);ax.grid(alpha=.2);ax.tick_params(axis='x',rotation=25)
    fig.tight_layout();fig.savefig(out/'figures/evaluacion_9_mensual.png',dpi=150);plt.close(fig)
    # Crear una figura descriptiva; sus ejes y títulos deben identificar población y versión del protocolo.
    fig,axes=plt.subplots(1,2,figsize=(10,4.5));matrix=np.array(result['politica']['matriz_confusion'])
    axes[0].imshow(matrix,cmap='Blues')
    for (i,j),value in np.ndenumerate(matrix):axes[0].text(j,i,str(value),ha='center',va='center',color='white' if value>matrix.max()*.55 else 'black')
    axes[0].set(xticks=[0,1],yticks=[0,1],xlabel='Prioridad (0/1)',ylabel='Cancelación real (0/1)',title='Matriz de la política, no umbral 0,5')
    b=tables['calibracion_bins'];axes[1].plot(b.probabilidad_media,b.tasa_observada,marker='o')
    axes[1].plot([0,1],[0,1],'--',color='gray');axes[1].set(xlabel='Score medio',ylabel='Tasa observada',title='Calibración descriptiva — sin reajuste')
    fig.tight_layout();fig.savefig(out/'figures/evaluacion_9_matriz_calibracion.png',dpi=150);plt.close(fig)


# Redactar tablas, metodología y limitaciones desde resultados calculados o guardados.
def write_report(root,tables,result,receipt):
    # Preparar una tabla legible para la documentación de esta fase.
    def table(frame):return markdown(frame.astype(object).where(frame.notna(),'No estimable'))
    p=result['politica'];g=result['modelo_global']
    text=f'''# Fase 9 — Evaluación final de la especificación congelada sobre prueba v3

Se completa exclusivamente fase 9. Modelo: regresión logística inicial congelada en fase 8, sin refit, optimización o recalibración. Política: top 20% por mes de llegada, City y Resort conjuntamente; k=n_mes*20//100, scores descendentes, hash SHA256 de `42|ID` y después ID numérico para empates exactos. No es un umbral fijo de probabilidad. El modelo, la política y el protocolo no se cambian tras ver resultados.

## 1. Verificaciones antes de etiquetas y predicciones

Se revisaron informe/especificación/plan de fase 8, joblib, manifiesto v3 y decision_policy.py. SHA de especificación y modelo coinciden con las referencias de fase 8; todos los hashes de entradas, fuentes, versiones y modelo son conformes. Se comprueban clase/hiperparámetros, preprocesamiento, 14 entradas, 192 columnas transformadas, clase positiva 1 y scaler ajustado en 49157 filas. Se verifica hash de IDs de entrenamiento y que los 32829 IDs de prueba no cruzan entrenamiento/validación ni grupos exactos.

El preflight se guarda antes de leer etiquetas. La inferencia bloquea fit/fit_transform de pipeline, clasificador y transformadores; se contrasta la huella de parámetros aprendidos antes/después. Una única llamada predict_proba genera scores de prueba con el pipeline ya ajustado. Se aplica la política sin y y se guardan decisiones, scores y SHA antes de acceder a etiquetas. No se recalibra ni se ensayan otros modelos, cuotas, capacidades o umbrales sobre prueba.

El recibo evaluacion_9_recibo.json registra timestamps, versión/código, hashes y una llamada de inferencia. Las reejecuciones verifican esos archivos y presentan resultados congelados sin otra inferencia. No se repite la evaluación para seleccionar un resultado. No se ejecutan tests históricos que entrenan algoritmos: solo pruebas puras de política y evaluación sin entrenamiento.

## 2. Resultado de la política de seguimiento

Reservas evaluadas: **{p['n']}**. Priorizadas: **{p['priorizadas']} ({p['porcentaje_priorizado']:.4f}%)**, tras floor por cada mes. Canceladas observadas: {g['canceladas']}.

POLICY

Matriz [[TN, FP], [FN, TP]], filas reales y columnas de prioridad [0,1]: **{p['matriz_confusion']}**. Alerta significa seguimiento, no cancelación segura. Precision describe acierto entre prioridades, recall cobertura de cancelaciones; F1 combina ambas sin incorporar costes reales. FP son seguimientos innecesarios y FN cancelaciones no anticipadas; ninguna métrica acredita que un contacto evitaría cancelaciones.

## 3. Métricas globales y calidad probabilística

GLOBAL

ROC-AUC y AP se calculan con scores continuos, no con prioridad binaria; AP depende de prevalencia. Brier mide error cuadrático probabilístico y combina calibración/resolución. La probabilidad media se compara con la tasa observada y se dibujan bins descriptivos sin ajustar un calibrador. No se convierte el 20% de recursos en una probabilidad de corte constante.

![Matriz y calibración](figures/evaluacion_9_matriz_calibracion.png)

## 4. Comparación con validación v3

COMPARISON

Las diferencias son prueba menos validación, sobre la misma política/modelo congelados. La validación sirvió para seleccionar y es optimista respecto a selección; no se afirma independencia total de prueba, que tuvo exposición parcial bajo v2. Variaciones de prevalencia, calendario y mezcla pueden modificar precision/AP y cobertura. Se conserva la especificación aunque algún indicador empeore. No se atribuye causalmente el cambio a una sola variable ni se prueba significación mediante comparar dos intervalos marginales.

Cambios de composición observados, sin filtrar ni reponderar filas:

COMPOSITION

Cuantiles de antelación (p10/p50/p90), validación y prueba: **{result['antelacion_cuantiles']}**. Las distribuciones se describen después de evaluar; no se usan para adaptar pipeline, cuotas o calibración.

## 5. Meses de prueba y comprobación exacta de capacidad

MONTHS

En los seis meses se verifica exactamente n_priorizadas=n_mes*20//100. No se reaplica cuota separadamente a cada hotel. Los scores de borde y empates están en evaluacion_9_bordes_empates.csv; son resultados de aplicar la regla, no umbrales nuevos para meses siguientes. Las diferencias mensuales son descriptivas, condicionadas a sus tamaños/composición y sin demostrar deterioro uniforme o generalización anual.

![Evolución mensual](figures/evaluacion_9_mensual.png)

## 6. Hoteles bajo una cuota compartida

HOTELS

El porcentaje alertado puede diferir entre hoteles porque compiten por el mismo top-k mensual. Se mantiene esa distribución sin introducir cuotas a posteriori. Prevalencia, tipos de reservas y tamaños explican parte de las diferencias, sin atribuir causalidad o superioridad universal. No hay datos de capacidad real por establecimiento.

## 7. Incertidumbre descriptiva con dependencia temporal

INTERVALS

500 réplicas, seed 42, bloques móviles no circulares de 14 días de llegada; se arrastran juntas todas las reservas de cada día y ambos hoteles, preservando también duplicados exactos de ese día. Se sortean bloques con reemplazo hasta tantos días como el calendario original, truncando el último. La longitud/semilla/número se fijaron en el plan antes de acceder a resultados. Como referencia para remuestrear bloques en datos dependientes: [Künsch (1989), versión del autor](https://www.researchgate.net/publication/2355926_The_Jackknife_and_the_Bootstrap_for_General_Stationary_Observations).

Scores y prioridades originales permanecen fijos: no se repriorizan réplicas, no se predice de nuevo y no se ajusta nada. Los porcentajes alertados pueden cambiar en la réplica al remuestrear días. Estos percentiles describen incertidumbre condicional de las decisiones observadas, no la de volver a ejecutar una cuota en un futuro lote completo ni la selección/entrenamiento del modelo. Las observaciones no se tratan como filas independientes.

La dependencia más allá de 14 días, clientes/grupos sin ID, la estacionalidad y solo seis meses limitan supuestos de estacionariedad e intercambiabilidad local de bloques. No se garantiza cobertura frecuentista del 95%, independencia de bloques reales o extrapolación prospectiva. Son intervalos de remuestreo ilustrativos, no una certificación de producción. Las réplicas y su tamaño se exportan, sin elegir las favorables.

## 8. Seguimiento, trazabilidad y limitaciones

Auditoría de metadatos posterior a congelar decisiones: **{result['seguimiento_proxy']}**. El último estado + un día frente al cierre asumido puede comprobar coherencia del archivo, pero no acredita cuándo se conoció/ingirió cada resultado ni ausencia de reservas o actualizaciones faltantes. No se retiran filas ni se modifica v3 por esa auditoría.

Se declaran expresamente: (1) v3 retrospectivo por llegada, con altas aproximadas solapadas; (2) ausencia de snapshots iniciales acreditados de los 14 predictores; (3) alta=llegada−lead_time y disponibilidad=último estado+un día son aproximaciones; (4) no hay cierre operativo PMS documentado, y 01/12/2018 es supuesto; (5) exposición previa de parte de prueba al desarrollo v2 y al EDA global; (6) selección de modelo/política con validación reutilizada; (7) costes/capacidad reales y eficacia de contacto desconocidos; (8) necesidad del lote mensual completo para priorizar, sin simulación de atención al alta o cola online. Se conservan duplicados y no hay ID real de reserva/cliente, lo que también limita incertidumbre y unidades operativas.

No se presenta como validación prospectiva real, rentabilidad, efecto causal o autorización de despliegue. Priorizar no significa cancelar, penalizar o tratar adversamente de forma automática. El resultado corresponde a la especificación académica congelada y población observada; no generaliza sin evidencia adicional.

## 9. Archivos y reproducción sin nueva evaluación

Nuevos: src/final_evaluation.py, tests/test_final_evaluation.py, notebooks/evaluacion_final.ipynb y este informe. Evidencia evaluacion_9_*: plan, preflight, copia/hash del código ejecutado, recibo, scores/decisiones congelados sin etiqueta, etiquetas en archivo separado, métricas, comparación, meses, hoteles, composición, bins, réplicas e intervalos y verificación. Se generan dos figuras. Solo se muestran agregados en informe/notebook; CSV de reproducción usa IDs técnicos, sin nombres/contactos personales.

Se actualizan README y ejecutor; no hay nuevas dependencias ni cambios en archivos congelados de fase 8, datos originales o manifiesto v3. Las pruebas comprueban separación, bloqueo de fit, cuota mensual/desempate, coherencia de métricas y bloques completos, sin entrenar modelos. La reejecución del notebook valida checkpoints y reproduce presentación desde scores/resultados guardados; no vuelve a llamar predict_proba sobre prueba.

La especificación/modelo congelados siguen con SHA **{receipt['especificacion_sha256']}** / **{receipt['modelo_sha256']}**. No se decide ningún ajuste con los resultados. Se espera revisión antes de cualquier fase posterior, sin preparar presentación final.

**Fin exclusivo de fase 9. No se avanza a fase 10 sin autorización.**
'''
    summary_cols=['n','priorizadas','porcentaje_priorizado','precision','recall','f1','fp','fn','tp','tn']
    replacements={'POLICY':table(pd.DataFrame([{k:p[k] for k in summary_cols}])),
        'GLOBAL':table(pd.DataFrame([g])),'COMPARISON':table(tables['comparacion_validacion']),
        'COMPOSITION':table(tables['composicion']),'MONTHS':table(tables['mensual']),
        'HOTELS':table(tables['hoteles']),'INTERVALS':table(tables['intervalos'])}
    for key in sorted(replacements,key=len,reverse=True):text=text.replace(key,replacements[key])
    # Persistir documentación o metadatos para revisar las decisiones sin volver a ejecutar el modelo.
    (Path(root)/'reports/fase_9_evaluacion_final.md').write_text(text,encoding='utf-8')
