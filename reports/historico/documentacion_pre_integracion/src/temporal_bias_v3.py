"""Fase 7.1: cohortes completas por llegada, seguimiento y modelos iniciales."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (average_precision_score, roc_auc_score, accuracy_score,
                             precision_score, recall_score, f1_score)

from src.features import FEATURES, separate_model_data
from src.splitting import PROTOCOL_V3, temporal_split_v3, audit_followup_v3
from src.comparison import sha, model_factories, fit_one
from src.baseline import evaluate_predictions
from src.optimization import json_write, markdown


ACTIVE_FILES = ['particiones_temporales.csv','division_temporal.json','baseline_resultados.json',
                'baseline_predicciones_validacion.csv','baseline_verificacion.json','estado_protocolo.json']


def read_rows(path, columns, positions):
    """Lee resultados solo de filas autorizadas; no carga etiquetas de prueba."""
    positions=np.asarray(positions,dtype='int64')
    if len(np.unique(positions))!=len(positions) or not np.array_equal(positions,np.sort(positions)):
        raise ValueError('Las posiciones deben ser únicas y crecientes')
    keep=set(positions.tolist())
    result=pd.read_csv(path,usecols=columns,skiprows=lambda line: line>0 and line-1 not in keep)
    if len(result)!=len(positions):raise ValueError('Lectura selectiva no alineada')
    result.index=positions
    return result


def verify_history(root):
    for version in ['protocolo_v1','protocolo_v2']:
        history=root/'reports/historico'/version
        record=json.loads((history/'registro_historico.json').read_text(encoding='utf-8'))
        for path,expected in record['archivos_sha256'].items():
            assert sha(history/path)==expected,(version,path)


def metrics_for(y,p):
    predicted=np.asarray(p)>=.5
    result={'accuracy':float(accuracy_score(y,predicted)),
            'precision':float(precision_score(y,predicted,zero_division=0)),
            'recall':float(recall_score(y,predicted,zero_division=0)),
            'f1':float(f1_score(y,predicted,zero_division=0)),
            'roc_auc':float(roc_auc_score(y,p)) if pd.Series(y).nunique()==2 else None,
            'average_precision':float(average_precision_score(y,p)) if np.any(np.asarray(y)==1) else 0.}
    return result


def audit_v2(root):
    """Diagnóstico histórico sobre validación v2; nunca prueba v1/v2."""
    history=root/'reports/historico/protocolo_v2/reports'
    predictions=pd.read_csv(history/'comparacion_5_predicciones_validacion.csv')
    old_manifest=pd.read_csv(history/'particiones_temporales.csv')
    assert set(predictions.meta_row_id)==set(old_manifest.loc[old_manifest.particion.eq('validacion'),'meta_row_id'])
    old_test=set(old_manifest.loc[old_manifest.particion.eq('prueba_reservada'),'meta_row_id'])
    assert not (set(predictions.meta_row_id)&old_test)
    meta=pd.read_csv(root/'data/processed/hotel_bookings_prepared.csv',usecols=['meta_row_id','meta_arrival_date','meta_booking_date_proxy','lead_time'])
    selected=meta.set_index('meta_row_id').loc[predictions.meta_row_id].reset_index()
    future=pd.to_datetime(selected.meta_arrival_date).ge('2017-01-01').to_numpy()
    rows=[]
    for group,mask in [('validacion_v2_completa',np.ones(len(predictions),dtype=bool)),('llegada_antes_2017',~future),('llegada_desde_2017',future)]:
        y=predictions.loc[mask,'is_canceled']
        for name in ['regresion_logistica','xgboost']:
            p=predictions.loc[mask,name]
            rows.append({'grupo':group,'modelo':name,'n':len(y),'canceladas':int(y.sum()),
                         'tasa_cancelacion':float(y.mean()),**metrics_for(y,p)})
    assert int(future.sum())==3917 and predictions.loc[future,'is_canceled'].eq(1).all()
    division=json.loads((history/'division_temporal.json').read_text(encoding='utf-8'))
    selected_row=next(r for r in division['particiones'] if r['particion']=='validacion')
    pending=next(r for r in division['particiones'] if r['particion']=='no_madura_validacion')
    mechanism=[]
    for label,key in [('canceladas','canceladas'),('no_canceladas','no_canceladas')]:
        included=selected_row[key];excluded=pending[key]
        mechanism.append({'resultado':label,'incluidas_v2':included,'apartadas_v2':excluded,
                          'proporcion_incluida':included/(included+excluded)})
    return pd.DataFrame(rows),pd.DataFrame(mechanism)


def run_v3(root):
    root=Path(root);out=root/'reports'
    verify_history(root)
    # Se preservan todos los informes históricos y CSV. Solo seis nombres activos
    # son reemplazables porque ya están congelados en el histórico v2.
    protected=[p for folder in ['data','reports'] for p in (root/folder).rglob('*') if p.is_file()
        and not p.name.startswith('protocolo_7_1_') and p.name!='fase_7_1_correccion_sesgo_temporal.md'
        and not (p.parent==out and p.name in ACTIVE_FILES)]
    before={str(p.relative_to(root)):sha(p) for p in protected}
    assert sha(root/'data/raw/hotel_bookings.csv')=='7c2ae42a7353905ea136e5c2287f17c92c5435826598bfbb8491c6f0c7b1fc06'
    assert sha(root/'data/processed/hotel_bookings_prepared.csv')=='2718ad6c88b52da2914b54e5f6eccb51815a2ff3c59100793c093292f900c60c'
    # No se carga la columna objetivo aquí.
    prepared=pd.read_csv(root/'data/processed/hotel_bookings_prepared.csv',usecols=FEATURES+[
        'meta_row_id','meta_duplicate_group','meta_arrival_date','meta_booking_date_proxy'])
    assert len(prepared)==119390
    meta=prepared.filter(regex='^meta_').copy()
    assigned=temporal_split_v3(meta)
    modified=meta.assign(is_canceled=np.arange(len(meta))%2,reservation_status_date='2099-01-01')
    pd.testing.assert_series_equal(assigned,temporal_split_v3(modified))
    development=assigned.isin(['entrenamiento','validacion'])
    dev_positions=np.flatnonzero(development)
    old_manifest=pd.read_csv(out/'historico/protocolo_v2/reports/particiones_temporales.csv')
    old_test=set(old_manifest.loc[old_manifest.particion.eq('prueba_reservada'),'meta_row_id'])
    if set(meta.loc[development,'meta_row_id'])&old_test:raise ValueError('Prueba histórica entra en desarrollo')
    labels=read_rows(root/'data/processed/hotel_bookings_prepared.csv',['is_canceled'],dev_positions).is_canceled
    statuses=read_rows(root/'data/raw/hotel_bookings.csv',['reservation_status_date'],dev_positions).reservation_status_date
    # Auditoría por bloque: no influye en la asignación individual y bloquea si falla.
    followup=audit_followup_v3(meta.loc[development],assigned.loc[development],statuses,prepared.loc[development,'total_nights'])
    dev=prepared.loc[development].copy();dev['is_canceled']=labels
    features,target,_=separate_model_data(dev)
    train=assigned.loc[development].eq('entrenamiento');val=assigned.loc[development].eq('validacion')
    x_train,y_train=features.loc[train],target.loc[train]
    x_val,y_val=features.loc[val],target.loc[val]
    for y in [y_train,y_val]:assert y.nunique()==2
    partitions=[]
    for role in ['entrenamiento','embargo_train_validacion','validacion','embargo_validacion_prueba','prueba_reservada','fuera_cobertura']:
        mask=assigned.eq(role);m=meta.loc[mask];n=int(mask.sum())
        row={'particion':role,'n':n,'canceladas':None,'no_canceladas':None,'tasa_cancelacion':None,
             'lead_p10':float(prepared.loc[mask,'lead_time'].quantile(.1)) if n else None,
             'lead_mediana':float(prepared.loc[mask,'lead_time'].median()) if n else None,
             'lead_p90':float(prepared.loc[mask,'lead_time'].quantile(.9)) if n else None}
        for column,prefix in [('meta_arrival_date','llegada'),('meta_booking_date_proxy','reserva_proxy')]:
            d=pd.to_datetime(m[column]);row[prefix+'_min']=str(d.min().date()) if n else None;row[prefix+'_max']=str(d.max().date()) if n else None
        if role in ['entrenamiento','validacion']:
            y=target.loc[assigned.loc[development].eq(role)]
            row.update(canceladas=int(y.sum()),no_canceladas=int(y.eq(0).sum()),tasa_cancelacion=float(y.mean()))
        partitions.append(row)
    partition_table=pd.DataFrame(partitions)
    transition=pd.crosstab(old_manifest.particion,assigned).reset_index()
    exposure=[]
    for role in ['prueba_reservada','embargo_validacion_prueba']:
        mask=assigned.eq(role)
        for old_role in old_manifest.particion.unique():
            exposure.append({'destino_v3':role,'origen_v2':old_role,'n':int((mask&old_manifest.particion.eq(old_role)).sum())})
    old_audit,mechanism=audit_v2(root)
    # Registrar protocolo/manifiesto ANTES de los dos ajustes v3.
    manifest=pd.DataFrame({'meta_row_id':meta.meta_row_id,'particion':assigned})
    manifest.to_csv(out/'particiones_temporales.csv',index=False)
    json_write(out/'division_temporal.json',{'protocolo':PROTOCOL_V3,'particiones':partition_table.astype(object).where(partition_table.notna(),None).to_dict('records'),
        'seguimiento_train_validacion':followup.to_dict('records'),'labels_prueba_consultadas':False,
        'ids_prueba_historica_en_desarrollo':0,'n_prueba_historica_protegida':len(old_test),
        'independencia_nueva_prueba_garantizada':False,'elegibilidad_no_usa_y_o_status':True,
        'n_total':len(manifest),'propuesta_previa_sha256':sha(out/'protocolo_7_1_propuesta_previa.md')})
    json_write(out/'estado_protocolo.json',{'vigente':PROTOCOL_V3['version'],'fase':'7.1','manifiesto':'reports/particiones_temporales.csv',
        'metricas_vigentes':'reports/protocolo_7_1_modelos.json','historico_v1':'reports/historico/protocolo_v1',
        'historico_v2':'reports/historico/protocolo_v2','metricas_v2_historicas_no_comparables_con_v3':True,
        'prueba_evaluada':False,'uso_admisible':PROTOCOL_V3['purpose']})
    manifest_hash=sha(out/'particiones_temporales.csv')
    predictions=pd.DataFrame({'meta_row_id':meta.loc[x_val.index,'meta_row_id'],'is_canceled':y_val})
    metrics_rows=[];audits={};parameters={}
    factories=model_factories()
    for name in ['regresion_logistica','xgboost']:
        print('Ajuste v3:',name,flush=True)
        model=factories[name];parameters[name]=model.named_steps['classifier'].get_params()
        result,p,notices=fit_one(model,x_train,y_train,x_val,y_val)
        metrics_rows.append({'modelo':name,**result})
        predictions[name]=p.astype('float64')
        audits[name]={'n_train':len(x_train),'n_validacion':len(x_val),'fit_solo_train_auditado':True,
                      'advertencias':notices,'n_transformadas':len(model.named_steps['preprocessor'].get_feature_names_out())}
    metrics=pd.DataFrame(metrics_rows)
    validation=features.loc[x_val.index].copy();validation['is_canceled']=y_val
    validation['mes_llegada']=pd.to_datetime(meta.loc[x_val.index,'meta_arrival_date']).dt.to_period('M').astype(str)
    validation['antelacion_grupo']=pd.cut(validation.lead_time,[-np.inf,7,30,90,180,np.inf],labels=['0-7','8-30','31-90','91-180','181+']).astype(str)
    segment_rows=[]
    for name in ['regresion_logistica','xgboost']:
        for dimension in ['hotel','mes_llegada','antelacion_grupo']:
            for value,g in validation.groupby(dimension,observed=True,sort=True):
                y=g.is_canceled;p=predictions.loc[g.index,name]
                segment_rows.append({'modelo':name,'dimension':dimension,'grupo':str(value),'n':len(g),
                    'canceladas':int(y.sum()),'no_canceladas':int(y.eq(0).sum()),'tasa_cancelacion':float(y.mean()),
                    'suficiente_descriptivo':len(y)>=100 and y.eq(0).sum()>=30 and y.eq(1).sum()>=30,
                    'probabilidad_media':float(p.mean()),**metrics_for(y,p)})
    validation_future=int(pd.to_datetime(meta.loc[x_val.index,'meta_arrival_date']).ge(PROTOCOL_V3['validation_end_exclusive']).sum())
    assert validation_future==0 and sha(out/'particiones_temporales.csv')==manifest_hash
    for path,h in before.items():assert sha(root/path)==h,path
    tables={'particiones':partition_table,'seguimiento':followup,'transicion_v2_v3':transition,
            'exposicion_prueba':pd.DataFrame(exposure),'auditoria_v2':old_audit,'seleccion_resultado_v2':mechanism,
            'metricas':metrics,'predicciones_validacion':predictions,'segmentos':pd.DataFrame(segment_rows)}
    for name,table in tables.items():table.to_csv(out/f'protocolo_7_1_{name}.csv',index=False)
    model_result={'protocolo':PROTOCOL_V3,'umbral_diagnostico':.5,'parametros':parameters,'auditorias':audits,
        'metricas':metrics.to_dict('records'),'prueba_evaluada':False,'comparacion_con_v2_como_ranking':False}
    json_write(out/'protocolo_7_1_modelos.json',model_result)
    logistic=metrics[metrics.modelo.eq('regresion_logistica')].iloc[0]
    json_write(out/'baseline_resultados.json',{'protocolo_version':PROTOCOL_V3['version'],
        'evaluacion':'Solo validación v3 por llegada','parametros':parameters['regresion_logistica'],
        'metricas':{'regresion_logistica':{k:logistic[k] for k in ['accuracy','precision','recall','f1','roc_auc','average_precision']}},
        'matriz_confusion':[[int(logistic.tn),int(logistic.fp)],[int(logistic.fn),int(logistic.tp)]],'prueba_evaluada':False})
    baseline_predictions=predictions[['meta_row_id','is_canceled','regresion_logistica']].rename(columns={'regresion_logistica':'probabilidad_logistica'})
    baseline_predictions['prediccion_logistica']=baseline_predictions.probabilidad_logistica.ge(.5).astype(int)
    baseline_predictions.to_csv(out/'baseline_predicciones_validacion.csv',index=False)
    detail={'protocolo':PROTOCOL_V3,'n_total':len(prepared),'n_train':len(x_train),'n_validacion':len(x_val),
        'manifiesto_sha256':manifest_hash,'original_y_preparado_intactos':True,'historicos_v1_v2_intactos':True,
        'elegibilidad_invariante_a_etiqueta_y_estado':True,'filas_validacion_llegada_futura':validation_future,
        'etiquetas_leidas_desde_preparado_solo_train_validacion_v3':len(dev_positions),
        'auditoria_v2_solo_predicciones_historicas_validacion':True,'ids_prueba_v1_v2_reutilizados_desarrollo':0,
        'prueba_transformada_predicha_evaluada':False,'independencia_nueva_prueba':False,
        'archivos_previos_intactos':before,'auditorias_fit':audits}
    make_figures(out,tables)
    write_report(root,tables,detail)
    json_write(out/'protocolo_7_1_verificacion.json',detail)
    json_write(out/'baseline_verificacion.json',detail)
    return tables,detail


def make_figures(out,tables):
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for ax,row in zip(axes,tables['metricas'].itertuples()):
        matrix=np.array([[row.tn,row.fp],[row.fn,row.tp]])
        ax.imshow(matrix,cmap='Blues')
        for (i,j),value in np.ndenumerate(matrix):ax.text(j,i,str(value),ha='center',va='center',color='white' if value>matrix.max()*.55 else 'black')
        ax.set(xticks=[0,1],yticks=[0,1],xlabel='Predicción',ylabel='Real',title=row.modelo+' — v3, umbral 0,5')
    fig.tight_layout();fig.savefig(out/'figures/protocolo_7_1_matrices.png',dpi=150);plt.close(fig)
    data=tables['segmentos'];fig,axes=plt.subplots(1,2,figsize=(12,4))
    for name in ['regresion_logistica','xgboost']:
        subset=data[data.modelo.eq(name)&data.dimension.eq('mes_llegada')]
        axes[0].plot(subset.grupo,subset.roc_auc,marker='o',label=name)
        axes[1].plot(subset.grupo,subset.recall,marker='o',label=name)
    for ax in axes:ax.set_ylim(0,1);ax.legend();ax.grid(alpha=.2);ax.set_xlabel('Mes de llegada en validación v3')
    axes[0].set_ylabel('ROC-AUC');axes[1].set_ylabel('Recall a 0,5')
    fig.tight_layout();fig.savefig(out/'figures/protocolo_7_1_estabilidad.png',dpi=150);plt.close(fig)


def write_report(root,tables,detail):
    def table(frame):return markdown(frame.astype(object).where(frame.notna(),'No consultado/no estimable'))
    text='''# Fase 7.1 — Corrección del sesgo de selección temporal

Fecha: 18/10/2026. **V3 sustituye v2 como protocolo activo.** Se selecciona la alternativa B, cohortes completas por llegada con seguimiento común por bloque y embargo. Es una evaluación retrospectiva exploratoria, no una simulación rigurosa de predicción al crear reservas. No se optimiza, calibra o fija umbral operativo y no se evalúa prueba.

## 1. Problema y causa de selección dependiente del resultado

Se revisaron fases 4.2, 5, 6 y 7, fuentes de división/preprocesamiento/entrenamiento y convenciones de notebooks. En v2, las altas aproximadas de validación están entre julio y diciembre de 2016, pero la llegada prevista puede situarse después. Exigir fecha de último estado + un día anterior a enero de 2017 permite incluir una cancelación anticipada para una llegada futura. Una estancia no cancelada que aún no ha ocurrido no puede satisfacer esa disponibilidad con un resultado final. El conjunto queda condicionado por el propio desenlace y el tiempo hasta observarlo.

El código no necesita consultar is_canceled para producir sesgo: fecha del resultado y cancelación están relacionadas. La regla es una selección informativa por disponibilidad, no una muestra neutral de todas las reservas del periodo. En el universo histórico de altas de validación v2 se incorporó 77,49% de cancelaciones frente a 62,44% de no cancelaciones:

MECHANISM

Las 3917 filas de validación v2 con llegada desde enero de 2017 están todas canceladas. Una reserva puede crearse antes del corte y cancelarse antes de llegar; eso justifica disponer de su etiqueta para aprender, pero no justifica una evaluación que incluye solo sus resultados tempranos y omite los negativos aún abiertos. Para XGBoost, 3166 de sus 4176 TP vienen de ese subgrupo. No se trata de corregir el algoritmo o de eliminar únicamente esos positivos para obtener un resultado preferido.

Diagnóstico usando exclusivamente las probabilidades y etiquetas de validación v2 ya congeladas, sin prueba histórica:

V2_AUDIT

La precision 1 y AP 1 en el subgrupo de una sola clase son efectos de su composición: no prueban discriminación, y ROC-AUC no se estima. La AP depende de prevalencia. En las 14180 con llegada anterior a 2017, XGBoost tiene precision 0,603706, recall 0,263295, ROC-AUC 0,772138 y AP 0,538114, frente a los indicadores agregados de la validación v2 seleccionada. No son nuevas alternativas de modelos ni una evaluación de prueba.

## 2. Cuatro fechas que no se confunden

| Fecha | Significado y uso |
| --- | --- |
| Alta aproximada | Llegada prevista menos lead_time. Proxy sin hora ni historial, conservado para auditoría. |
| Llegada prevista | Define el bloque v3; no se añade como nuevo predictor a X. El mes ya formaba parte de los 14 predictores. |
| Resultado fechado | reservation_status_date es último estado, no primera disponibilidad ni ingestión real. Solo se lee para auditar train/validación. |
| Cierre de seguimiento | Una fecha común prefijada por bloque, posterior a sus llegadas; no la fecha individual en que canceló cada reserva. |

Se conserva el objetivo is_canceled y los mismos 14 campos predictivos. Fecha final, IDs y metadatos no llegan a imputadores, codificadores o modelos. La evidencia previa de la fuente, resumida en fase 4.2, no acredita snapshots iniciales ni cierre PMS; esta limitación no se resuelve con v3.

## 3. Alternativas evaluadas antes de resultados v3

| Aspecto | A: cohortes por alta, seguimiento común | B: cohortes por llegada y embargo — seleccionada |
| --- | --- | --- |
| Población | Reservas creadas en determinados periodos, idealmente todas las altas del PMS. | Reservas registradas en la extracción para llegadas de bloques concretos. |
| Inclusión | Cohortes enteras con un horizonte/seguimiento completo prefijado, no filas porque cancelaron pronto. | Todas las filas con llegada en el bloque, sin filtrar por y o último estado. |
| Apartadas | Cohortes no observables hasta completar seguimiento; no solo negativos aún abiertos. | Meses de embargo y fechas fuera de cobertura; conservados en manifiesto. |
| Sesgo evitado | Rescatar resultados tempranos si la cohorte completa es observable. | Rescatar cancelaciones anticipadas con llegada posterior y excluir estancias aún abiertas. |
| Disponibilidad aquí | La extracción está delimitada por llegadas, no por altas; no acredita cohortes completas por creación. | Se ajusta al calendario de llegadas documentado y permite comprobar bloques observados con ambas clases. |
| Cronología | Un cierre común tardío no permite afirmar que el entrenamiento conocía todas sus etiquetas antes de las siguientes altas. | Se deja seguimiento del bloque previo antes del inicio de llegadas del siguiente, sin afirmar disponibilidad al alta. |
| Limitación restante | Faltan logs, cohortes completas, horizonte de negocio y versiones iniciales; un límite arbitrario de lead_time cambiaría la población. | Altas pueden solaparse; llegada y predictores pueden ser versiones actualizadas. No reproduce la decisión inicial. |
| Negocio | Sería la estrategia preferible para validar un sistema al reservar con datos prospectivos adecuados. | Sirve para estudiar generalización retrospectiva entre cohortes de llegada, con alcance académico reducido. |

Usar para A todos los resultados finales a cierre asumido de 2018 retiraría el filtro individual de madurez, pero no resolvería truncamiento por llegadas ni disponibilidad histórica para aprender antes de las altas evaluadas. A podría sostenerse con nuevos logs y seguimiento; no se selecciona aquí para afirmar una simulación al alta. B es más defendible para lo que este archivo realmente cubre, sin basarse en métricas mejores. La propuesta se guardó antes del manifiesto/modelos en protocolo_7_1_propuesta_previa.md; su hash queda en division_temporal.json. No se entrenó ningún modelo para escoger entre alternativas.

## 4. Reglas definitivas v3 y seguimiento comparable

Se mantiene un año completo de llegadas de entrenamiento y se fijan dos meses de calendario de embargo entre bloques. No se ajusta ese margen mirando métricas ni se presenta como una demora PMS universal:

- Entrenamiento: 2015-07-01 <= llegada < 2016-07-01. Cierre común exclusivo 2016-09-01.
- Embargo train/validación: 2016-07-01 <= llegada < 2016-09-01.
- Validación: 2016-09-01 <= llegada < 2017-01-01. Cierre común exclusivo 2017-03-01.
- Embargo validación/prueba: 2017-01-01 <= llegada < 2017-03-01.
- Prueba reservada: 2017-03-01 <= llegada < 2017-09-01. No se leen sus etiquetas, predicen ni evalúan modelos sobre ella.

La asignación solo usa fecha de llegada, unicidad y grupos técnicos para verificar cruces; es idéntica al cambiar etiquetas o fechas de estado. Esto es independencia funcional del criterio, no independencia estadística entre cohortes y cancelación. Las cohortes pueden tener prevalencias distintas por su composición.

Después de asignar y antes de entrenar, TODA la cohorte de entrenamiento/validación debe cumplir último estado + un día y salida prevista + un día anteriores a su cierre común. Si alguna fila falla se bloquea el bloque completo: no se elimina esa reserva ni se rescatan cancelaciones tempranas. No se usa esa condición para filtrar individualmente el manifiesto. La salida prevista se calcula con total_nights sin imputar etiquetas.

FOLLOWUP

En entrenamiento, la última disponibilidad proxy es 20/07/2016, con 43 días hasta el cierre. En validación es 15/01/2017, con 45 días. Las últimas salidas previstas son 19/07/2016 y 14/01/2017. No quedan estados o salidas posteriores al cierre en ninguno de los dos bloques. Es seguimiento compatible con los registros disponibles, no prueba de que el PMS tuviese todos los resultados o actualizaciones en esas fechas. El cierre de prueba de 01/12/2018 conserva únicamente el supuesto retrospectivo previo y queda pendiente de auditoría autorizada; no se valida con sus etiquetas en esta fase.

## 5. Particiones, filas apartadas y antelación

PARTITIONS

Se conservan **119390 filas** en un solo manifiesto, sin solapamientos de IDs, grupos exactos ni ventanas de llegada. Se usan 69068 en entrenamiento/validación; 17493 quedan en embargos y 32829 en prueba. Nada se borra del CSV. Las clases de embargos/prueba se dejan sin consultar; una celda vacía no significa cero cancelaciones.

La mediana de antelación es 56 días en entrenamiento y 66 en validación; los percentiles 90 son 254 y 313. Los embargos tienen medianas 117 y 28; prueba, 103, solo como metadato. V3 conserva reservas de larga antelación dentro de cada cohorte elegida, sin imponer un máximo para cerrar resultados. No hace iguales las distribuciones ni elimina estacionalidad.

Las altas proxy reales se solapan entre roles: validación contiene reservas con alta aproximada desde febrero de 2015. Por ello no es una separación cronológica de altas ni una simulación de un modelo disponible cuando se crearon esas reservas. La coherencia adoptada es el orden de cohortes de llegada y el seguimiento del bloque previo antes del siguiente bloque; se declara el cambio de objetivo.

Transición de v2 a v3, solo por IDs y asignaciones:

TRANSITION

## 6. Protección de prueba y exposición previa

Los 26565 IDs de prueba v1/v2 nunca pasan a desarrollo v3: 22357 quedan en prueba v3 y 4208 en el embargo enero-febrero. Se excluye incluso su lectura de etiquetas del nuevo ajuste y de la selección del protocolo. Solo se leen estados/objetivos nuevos para los 69068 IDs de entrenamiento/validación v3; el diagnóstico histórico aparte lee únicamente la validación v2 congelada, expresamente requerida para investigar el sesgo.

EXPOSURE

De los 32829 IDs de prueba v3, 319 estuvieron en entrenamiento v2 y 2718 en validación v2; otros 7435 proceden de sus grupos pendientes. Por tanto, redefinirla no restaura independencia: hay exposición previa de parte de sus casos a aprendizaje/análisis, además del EDA global. No se consultan nuevas etiquetas, predicciones o métricas de prueba para escoger v3. La composición por roles anteriores se obtiene solo del manifiesto. La futura evaluación sobre este bloque será exploratoria; una prueba prospectiva verdaderamente nueva requeriría más datos.

## 7. Logística y XGBoost iniciales, solo validación v3

Mismas fábricas, semillas y parámetros de fases anteriores. Logística: C=1, lbfgs, max_iter=2000, class_weight=None, random_state=42. XGBoost: 300 árboles, profundidad 4, tasa 0,05, subsample=0,8, colsample_bytree=0,8, hist, cuatro hilos, seed 42. No se usa la configuración optimizada de fase 6. Cada pipeline aprende medianas y vocabulario solo de las 49157 filas de entrenamiento; logística escala, árboles no. OneHotEncoder ignora desconocidas y la lista explícita excluye objetivo y metadatos. Umbral común diagnóstico 0,5; no se modifica para mejorar resultados.

METRICS

Matrices, filas reales y columnas predichas [0,1]:

MATRICES

![Matrices en validación v3](figures/protocolo_7_1_matrices.png)

En v3, XGBoost ofrece mayor ordenación (ROC-AUC 0,830592 y AP 0,790062 frente a 0,794590 y 0,762161), y mayor precision (83,05% frente a 77,25%). Sin embargo, detecta menos cancelaciones (recall 45,96% frente a 50,99%) y su F1 es inferior (0,591717 frente a 0,614307). Reduce 427 FP pero deja 381 FN adicionales. No se elige un modelo nuevo ni se cambia el umbral; estos son los dos modelos solicitados para revisar el protocolo. Los tiempos son orientativos del equipo, no un benchmark controlado.

**Las métricas v2 quedan históricas: no se restan de las v3 para atribuir una mejora/empeoramiento al algoritmo.** Cambian población, eje temporal, entrenamiento, composición y seguimiento. La comparación metodológica es que v2 condicionaba filas por resultado disponible; v3 utiliza cohortes enteras por llegada con embargos. No se afirma que v3 sea mejor porque su métrica sea mayor o menor.

## 8. Comprobación del sesgo y estabilidad restante

La validación v3 contiene cero llegadas desde enero de 2017: ya no se admiten cancelaciones anticipadas de una cohorte futura dentro del bloque evaluado. Incluye también todas las no cancelaciones de septiembre-diciembre que v2 podía apartar por disponibilidad, junto con las canceladas de esas mismas llegadas, sin selección individual por su fecha de resultado.

Antelación >180 días: **5742 filas, 3291 canceladas y 2451 no canceladas, tasa 57,31%**. Deja de ser el grupo artificialmente 100% positivo encontrado en v2. Todos los meses de validación v3 tienen ambas clases. Esto corrige el mecanismo concreto de rescate de cancelaciones futuras; no prueba que los datos sean libres de todo sesgo.

Train tiene tasa 35,77% y validación 38,02%, diferencia aproximada de 2,25 puntos porcentuales, sin ajustar prevalencias artificialmente. La tasa por mes de validación oscila de 36,22% a 40,53%; sigue habiendo composición y estacionalidad. No se calcula tasa de prueba en esta fase.

SEGMENTS

XGBoost tiene ROC-AUC mensual alrededor de 0,849 en septiembre-noviembre y 0,782 en diciembre; el recall varía de 34,48% a 53,36%. Por hotel, AUC 0,839 en City y 0,772 en Resort; recall 46,74% y 43,10%, respectivamente. Logística ofrece más recall en City (54,32%) y menos en Resort (38,79%). Las diferencias son descriptivas y no acreditan superioridad estable o significación; se conservan tamaños/clases y se marcan segmentos con n<100 o menos de 30 de alguna clase. Con una clase no se estima AUC; AP 0/1 sería degenerada por composición.

![Estabilidad mensual v3](figures/protocolo_7_1_estabilidad.png)

En 0–7 días, XGBoost apenas detecta 3 de 282 cancelaciones (recall 1,06%) a 0,5, aunque su accuracy 90,26% parezca alta. La corrección de cohorte no elimina dificultades del algoritmo ni convierte el umbral en una política adecuada. No se inicia otro análisis de umbrales, calibración u optimización.

## 9. Trazabilidad, ejecución y verificaciones

V1 permanece intacto. V2 se congela antes de la modificación en reports/historico/protocolo_v2, con 139 archivos de informes, fuentes, pruebas, notebooks, README y dependencias, más registro de hashes. Los informes raíz de fases anteriores conservan sus resultados históricos. Se sustituyen únicamente los nombres activos de manifiesto, división, baseline, predicciones/verificación baseline y estado. Los nuevos resultados de ambos modelos se guardan con prefijo protocolo_7_1_ y versión explícita.

splitting.py conserva las funciones históricas v1/v2 y añade temporal_split_v3, PROTOCOL_V3 y auditoría por bloque. temporal_split sin sufijo sigue siendo v2 para compatibilidad histórica; la entrada vigente src/temporal_bias_v3.py llama explícitamente temporal_split_v3. Las cargas/ejecuciones históricas v2 sobre el workspace activo v3 se bloquean para evitar sobrescritura o comparar manifiestos diferentes. Para reproducir v2 se requiere copia aislada del árbol archivado, junto con los CSV originales verificados; no se edita el histórico congelado.

Se crea notebooks/correccion_sesgo_temporal.ipynb y tests/test_temporal_bias_v3.py; se actualizan README y ejecutor, sin nuevas dependencias. Las pruebas comprueban fronteras y embargos, asignación ajena a etiqueta/estado, rechazo de fechas/duplicados, seguimiento tardío que bloquea cohorte completa, prohibición de auditar resultados de prueba, lectura selectiva de etiquetas y protección de entradas v2. Se conservan pruebas anteriores. El notebook se ejecuta completo y el registro recoge integridad, fit solo train, manifestación previa a métricas y ausencia de predicciones de prueba. La reproducción usa las mismas reglas/semillas y contrasta scores; no hay búsqueda de alternativas por métricas.

## 10. Limitaciones y recomendación

1. **Ninguna alternativa permite garantizar una simulación temporal rigurosa al alta con este archivo.** V3 define una evaluación retrospectiva por llegada que sí elimina la selección individual por resultados tempranos, pero cambia el problema temporal evaluado.
2. La extracción sigue seleccionada por llegadas, sin altas completas, logs de valores iniciales o IDs reales de reserva/cliente. Las fechas pueden reflejar planes actualizados. No se introducen fechas finales en X, pero tampoco se acredita que los 14 valores sean iniciales.
3. Último estado + un día es un proxy, no ingestión/primera disponibilidad garantizada. La coherencia de fechas observadas y los márgenes no prueban que falten cero resultados. El cierre de prueba de 2018 sigue sin acreditar.
4. Los embargos excluyen llegadas de verano y enero-febrero de desarrollo actual: las métricas describen septiembre-diciembre, no el año completo ni todas las altas. Un entrenamiento de doce meses no equivale a varias réplicas anuales de validación.
5. Duplicados conservados y grupos comerciales pueden sobreponderar patrones. El EDA y la comparación anterior vieron datos que ahora son validación/prueba ampliada. Las conclusiones y la futura prueba son exploratorias, no una evaluación totalmente independiente.
6. Se conserva la representación CSR y sus ceros implícitos del modelo inicial, explicada en fase 7. No se cambia ahora limpieza/representación para alterar resultados. No se recalibran ni optimizan modelos bajo v3; los rankings SHAP y umbrales de v2 quedan históricos, no se transfieren como decisiones v3.

Antes de continuar: revisar y aceptar el alcance retrospectivo v3 y sus embargos; mantener ambos modelos de referencia y decidir, en fase posterior autorizada, si se necesita nueva validación temporal de calibración/modelo y datos prospectivos con snapshots. No reutilizar hiperparámetros, umbral o calibración elegidos en v2 como si estuvieran validados en v3. Para una evaluación final, congelar previamente todas las decisiones y declarar exposición del bloque reservado; para validar uso al alta hará falta un dataset adicional adecuado. No se evalúa prueba, preparan entregables finales ni se avanza de fase.

**Fin exclusivo de fase 7.1. Se espera revisión y autorización del usuario.**
'''
    matrices=[]
    for r in tables['metricas'].itertuples():matrices.append({'modelo':r.modelo,'matriz':str([[r.tn,r.fp],[r.fn,r.tp]])})
    replacements={'MECHANISM':table(tables['seleccion_resultado_v2']),'V2_AUDIT':table(tables['auditoria_v2']),
        'FOLLOWUP':table(tables['seguimiento']),'PARTITIONS':table(tables['particiones']),
        'TRANSITION':table(tables['transicion_v2_v3']),'EXPOSURE':table(tables['exposicion_prueba']),
        'METRICS':table(tables['metricas']),'MATRICES':table(pd.DataFrame(matrices)),
        'SEGMENTS':table(tables['segmentos'])}
    for key in sorted(replacements,key=len,reverse=True):text=text.replace(key,replacements[key])
    (Path(root)/'reports/fase_7_1_correccion_sesgo_temporal.md').write_text(text,encoding='utf-8')
