"""Fase 8: dos candidatos v3, capacidad prefijada y especificación congelada."""
from pathlib import Path
import importlib.metadata
import json
import platform
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from sklearn.metrics import brier_score_loss, confusion_matrix

from src.splitting import PROTOCOL_V3,temporal_split_v3,audit_followup_v3
from src.features import FEATURES,NUMERIC_FEATURES,CATEGORICAL_FEATURES,separate_model_data
from src.comparison import sha,model_factories,fit_one
from src.temporal_bias_v3 import read_rows,metrics_for
from src.optimization import json_write,markdown,reliability_table
from src.decision_policy import monthly_priority,apply_frozen_policy

THRESHOLDS=[.1,.2,.3,.4,.5,.6,.7,.8,.9]
CAPACITIES=[10,20,30]
SELECTED_CAPACITY=20


def load_v3(root):
    """Lee características/etiquetas solo de train y validación v3."""
    root=Path(root);out=root/'reports'
    state=json.loads((out/'estado_protocolo.json').read_text(encoding='utf-8'))
    division=json.loads((out/'division_temporal.json').read_text(encoding='utf-8'))
    assert state['vigente']==PROTOCOL_V3['version'] and division['protocolo']==PROTOCOL_V3
    meta=pd.read_csv(root/'data/processed/hotel_bookings_prepared.csv',usecols=['meta_row_id','meta_duplicate_group','meta_arrival_date'])
    assigned=temporal_split_v3(meta)
    manifest=pd.read_csv(out/'particiones_temporales.csv')
    pd.testing.assert_frame_equal(manifest,pd.DataFrame({'meta_row_id':meta.meta_row_id,'particion':assigned}))
    assert len(meta)==119390
    mask=assigned.isin(['entrenamiento','validacion']);positions=np.flatnonzero(mask)
    prepared=read_rows(root/'data/processed/hotel_bookings_prepared.csv',FEATURES+['is_canceled'],positions)
    x,y,_=separate_model_data(prepared)
    dates=read_rows(root/'data/raw/hotel_bookings.csv',['reservation_status_date'],positions).reservation_status_date
    audit_followup_v3(meta.loc[mask],assigned.loc[mask],dates,prepared.total_nights)
    train=assigned.loc[mask].eq('entrenamiento');val=assigned.loc[mask].eq('validacion')
    assert (int(train.sum()),int(val.sum()))==(49157,19911)
    return x.loc[train],y.loc[train],x.loc[val],y.loc[val],meta.loc[x.loc[val].index].copy()


def decision_metrics(y,alert):
    y=np.asarray(y);alert=np.asarray(alert,dtype=bool)
    tn,fp,fn,tp=confusion_matrix(y,alert,labels=[0,1]).ravel()
    return {'precision':float(tp/(tp+fp)) if tp+fp else 0.,'recall':float(tp/(tp+fn)) if tp+fn else 0.,
        'f1':float(2*tp/(2*tp+fp+fn)) if 2*tp+fp+fn else 0.,'fp':int(fp),'fn':int(fn),'tp':int(tp),'tn':int(tn),
        'alertas':int(alert.sum()),'porcentaje_alertado':100*float(alert.mean()) if len(alert) else 0.}


def run_selection(root):
    root=Path(root);out=root/'reports';model_dir=root/'models';model_dir.mkdir(exist_ok=True)
    protected=[p for folder in ['data','reports'] for p in (root/folder).rglob('*') if p.is_file()
        and not p.name.startswith('seleccion_8_') and p.name!='fase_8_seleccion_final.md']
    protected += [root/'src'/n for n in ['splitting.py','features.py','preprocessing.py','baseline.py','comparison.py','temporal_bias_v3.py']]
    before={str(p.relative_to(root)):sha(p) for p in protected}
    assert sha(root/'data/raw/hotel_bookings.csv')=='7c2ae42a7353905ea136e5c2287f17c92c5435826598bfbb8491c6f0c7b1fc06'
    assert sha(root/'data/processed/hotel_bookings_prepared.csv')=='2718ad6c88b52da2914b54e5f6eccb51815a2ff3c59100793c093292f900c60c'
    x,y,v,z,meta=load_v3(root)
    ids=meta.meta_row_id.to_numpy();months=pd.to_datetime(meta.meta_arrival_date).dt.strftime('%Y-%m').to_numpy()
    reference=pd.read_csv(out/'protocolo_7_1_predicciones_validacion.csv')
    np.testing.assert_array_equal(ids,reference.meta_row_id);np.testing.assert_array_equal(z,reference.is_canceled)
    metrics_rows=[];models={};notices={};parameters={}
    predictions=pd.DataFrame({'meta_row_id':ids,'mes_llegada':months,'is_canceled':z.to_numpy()})
    factories=model_factories()
    previous=json.loads((out/'protocolo_7_1_modelos.json').read_text(encoding='utf-8'))
    for name in ['regresion_logistica','xgboost']:
        print('Ajuste con train v3:',name,flush=True)
        model=factories[name]
        parameters[name]=model.named_steps['classifier'].get_params()
        for k,value in parameters[name].items():
            expected=previous['parametros'][name][k]
            if isinstance(value,float) and np.isnan(value):assert expected=='NaN'
            else:assert value==expected,(name,k)
        result,p,notices[name]=fit_one(model,x,y,v,z)
        np.testing.assert_allclose(p,reference[name],atol=1e-12,rtol=1e-12)
        metrics_rows.append({'modelo':name,**result})
        predictions[name]=p.astype('float64');models[name]=model
    metrics=pd.DataFrame(metrics_rows)
    threshold_rows=[];capacity_rows=[];boundary_frames=[];allocations={};monthly_rows=[];hotel_rows=[]
    hotel_values=v.hotel.to_numpy()
    for name in models:
        p=predictions[name].to_numpy()
        for t in THRESHOLDS:threshold_rows.append({'modelo':name,'umbral':t,**decision_metrics(z,p>=t)})
        for q in CAPACITIES:
            allocation,boundary=monthly_priority(p,ids,months,q,42)
            alert=allocation.alerta.to_numpy();allocations[(name,q)]=allocation
            capacity_rows.append({'modelo':name,'capacidad_pct':q,**decision_metrics(z,alert)})
            boundary['modelo']=name;boundary_frames.append(boundary)
            if q==SELECTED_CAPACITY:
                for month in sorted(set(months)):
                    mask=months==month
                    monthly_rows.append({'modelo':name,'mes_llegada':month,'n':int(mask.sum()),
                        'tasa_cancelacion':float(np.asarray(z)[mask].mean()),**decision_metrics(np.asarray(z)[mask],alert[mask])})
                for hotel in sorted(set(hotel_values)):
                    mask=hotel_values==hotel
                    hotel_rows.append({'modelo':name,'hotel':hotel,'n':int(mask.sum()),
                        'tasa_cancelacion':float(np.asarray(z)[mask].mean()),**decision_metrics(np.asarray(z)[mask],alert[mask])})
    capacities=pd.DataFrame(capacity_rows)
    calibration_bins,calibration=reliability_table(z,predictions[['regresion_logistica','xgboost']])
    # El resultado observado favorece logística al 20%; la capacidad ya estaba fijada.
    # Una elección nueva necesita una nueva fase, nunca una decisión tras abrir prueba.
    selected='regresion_logistica'
    selected_row=capacities[capacities.modelo.eq(selected)&capacities.capacidad_pct.eq(20)].iloc[0]
    challenger=capacities[capacities.modelo.eq('xgboost')&capacities.capacidad_pct.eq(20)].iloc[0]
    if selected_row.tp<challenger.tp:raise RuntimeError('Revisar selección: resultados no reproducen la justificación congelada; no abrir prueba')
    frozen_model=models[selected]
    model_path=model_dir/'seleccion_8_modelo_congelado.joblib'
    specification_path=out/'seleccion_8_especificacion_congelada.json'
    if not specification_path.exists():joblib.dump(frozen_model,model_path,compress=3)
    loaded=joblib.load(model_path)
    np.testing.assert_allclose(loaded.predict_proba(v)[:,1],predictions[selected],atol=1e-12,rtol=1e-12)
    pre=frozen_model.named_steps['preprocessor']
    specification={'schema_version':1,'estado':'congelada_antes_de_prueba','fase':'8',
        'modelo_seleccionado':selected,'clase_modelo':'sklearn.linear_model.LogisticRegression',
        'protocolo':PROTOCOL_V3,'objetivo':'is_canceled','clase_positiva':1,'predictores':FEATURES,
        'numericas':NUMERIC_FEATURES,'categoricas':CATEGORICAL_FEATURES,'hiperparametros':parameters[selected],'seed':42,
        'preprocesamiento':{'numericas':'SimpleImputer median, keep_empty_features=True + StandardScaler',
            'categoricas':'SimpleImputer constant Desconocido, keep_empty_features=True + OneHotEncoder handle_unknown=ignore sparse_output=True',
            'column_transformer_remainder':'drop','sparse_threshold':1.,'columnas_transformadas':pre.get_feature_names_out().tolist()},
        'entrenamiento_final':{'particion':'entrenamiento','n':len(x),'usar_validacion_para_refit':False,
            'sha_ids_int64':__import__('hashlib').sha256(x.index.to_numpy(dtype='int64').tobytes()).hexdigest()},
        'politica':{'tipo':'top_capacidad_mensual','version_algoritmo':1,'capacidad_pct':SELECTED_CAPACITY,
            'clave_grupo':'mes_llegada_YYYY-MM','ambito_hoteles':'ambos hoteles juntos; sin cuotas por hotel',
            'fraccion_redondeo':'floor','formula_k':'n_del_mes * 20 // 100','seed_desempate':42,
            'desempate':'score_desc_sha256(seed|ID)_asc_ID_asc_sin_redondear_score',
            'unidad_id':'meta_row_id entero único del CSV original; orden de entrada no afecta selección',
            'score':'predict_proba[:, clase 1], float64 sin calibrador ni redondeo',
            'lote':'mes calendario completo de llegada; retrospectivo, no cola online',
            'umbral_fijo':None,'accion':'priorizar seguimiento preventivo humano, sin penalizaciones automáticas'},
        'calibrador':None,'metricas_validacion_modelo_umbral_05':metrics[metrics.modelo.eq(selected)].to_dict('records')[0],
        'metricas_validacion_politica':selected_row.to_dict(),
        'calibracion_validacion':calibration[calibration.modelo.eq(selected)].to_dict('records')[0],
        'artefacto_modelo':str(model_path.relative_to(root)).replace('\\','/'),'artefacto_sha256':sha(model_path),
        'huellas_entradas':{'data/raw/hotel_bookings.csv':sha(root/'data/raw/hotel_bookings.csv'),
            'data/processed/hotel_bookings_prepared.csv':sha(root/'data/processed/hotel_bookings_prepared.csv'),
            'reports/particiones_temporales.csv':sha(out/'particiones_temporales.csv'),
            'reports/division_temporal.json':sha(out/'division_temporal.json'),
            'reports/seleccion_8_plan_previo.md':sha(out/'seleccion_8_plan_previo.md'),
            'src/decision_policy.py':sha(root/'src/decision_policy.py'),
            **{f'src/{name}':sha(root/'src'/name) for name in ['baseline.py','features.py','preprocessing.py','comparison.py']}},
        'versiones':{'python':platform.python_version(),**{k:importlib.metadata.version(k) for k in ['scikit-learn','xgboost','pandas','numpy','scipy','joblib']}},
        'limites':['V3 retrospectivo por llegada, no simulación al alta','Snapshots y cierre PMS no acreditados',
            'Prueba ampliada con exposición previa y EDA global: evaluación exploratoria','Validación reutilizada para seleccionar modelo/política',
            '20% es supuesto ilustrativo, no capacidad real ni óptimo económico','Scores no calibrados; seguimiento no demuestra cancelación evitable',
            'Ranking requiere lote mensual completo; no factibilidad de intervención en tiempo real demostrada'],
        'instruccion_evaluacion_final':'Verificar hashes y versión, cargar este pipeline ya ajustado (sin refit), obtener scores SOLO tras autorización, aplicar política mensual congelada sin etiquetas. No reajustar capacidad, modelo, calibración, empates o definición de lotes mirando prueba.'}
    if specification_path.exists():
        frozen=json.loads(specification_path.read_text(encoding='utf-8'))
        assert frozen['modelo_seleccionado']==selected and frozen['politica']==specification['politica']
        assert frozen['artefacto_sha256']==sha(model_path)
        assert frozen['huellas_entradas']==specification['huellas_entradas']
        assert frozen['versiones']==specification['versiones']
        for key in ['precision','recall','f1','fp','fn','tp','tn','alertas']:
            np.testing.assert_allclose(frozen['metricas_validacion_politica'][key],selected_row[key],atol=1e-12)
    else:json_write(specification_path,specification)
    spec=json.loads(specification_path.read_text(encoding='utf-8'))
    applied,boundaries=apply_frozen_policy(spec,predictions[selected],ids,months)
    np.testing.assert_array_equal(applied.alerta,allocations[(selected,20)].alerta)
    applied['is_canceled']=np.asarray(z)
    tables={'metricas':metrics,'predicciones_validacion':predictions,'umbrales':pd.DataFrame(threshold_rows),
        'capacidades':capacities,'bordes_empates':pd.concat(boundary_frames,ignore_index=True),
        'mensual_capacidad_20':pd.DataFrame(monthly_rows),'hoteles_capacidad_20':pd.DataFrame(hotel_rows),
        'calibracion':calibration,'calibracion_bins':calibration_bins,'politica_validacion':applied}
    for name,table in tables.items():table.to_csv(out/f'seleccion_8_{name}.csv',index=False)
    for path,expected in before.items():assert sha(root/path)==expected,path
    detail={'protocolo':PROTOCOL_V3,'solo_predicciones_v3':True,'n_train':len(x),'n_validacion':len(v),
        'scores_fase_7_1_reproducidos':True,'preprocesamiento_fit_solo_train_auditado':True,
        'modelo':selected,'capacidad_pct':SELECTED_CAPACITY,'advertencias_fit':notices,
        'brier_constante_tasa_train':float(brier_score_loss(z,np.full(len(z),y.mean()))),
        'archivos_previos_intactos':before,'especificacion_sha256':sha(out/'seleccion_8_especificacion_congelada.json'),
        'prueba_transformada_predicha_evaluada':False,'pipeline_serializado_roundtrip_validado':True}
    make_figures(out,tables)
    write_report(root,tables,spec,detail)
    json_write(out/'seleccion_8_verificacion.json',detail)
    return tables,spec,detail


def make_figures(out,tables):
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    for name,g in tables['capacidades'].groupby('modelo',sort=False):
        axes[0].plot(g.capacidad_pct,g.precision,marker='o',label=name)
        axes[1].plot(g.capacidad_pct,g.recall,marker='o',label=name)
    for ax in axes:ax.set(xticks=[10,20,30],xlabel='Capacidad mensual supuesta (%)',ylim=(0,1));ax.legend();ax.grid(alpha=.2)
    axes[0].set_ylabel('Precision');axes[1].set_ylabel('Recall')
    fig.suptitle('Mismo volumen mensual de alertas — validación v3');fig.tight_layout()
    fig.savefig(out/'figures/seleccion_8_capacidades.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    for name,g in tables['calibracion_bins'].groupby('modelo',sort=False):
        axes[0].plot(g.probabilidad_media,g.tasa_observada,marker='o',label=name)
        axes[1].bar(g.bin+(-.2 if name=='regresion_logistica' else .2),g.n,width=.4,label=name)
    axes[0].plot([0,1],[0,1],'--',color='gray');axes[0].set(xlabel='Probabilidad media',ylabel='Tasa observada',title='Calibración sin ajustar, bins de 0,1')
    axes[1].set(xlabel='Intervalo de probabilidad (índice 0–9)',ylabel='Reservas',title='Soporte de los intervalos')
    for ax in axes:ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'figures/seleccion_8_calibracion.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    for name,g in tables['umbrales'].groupby('modelo',sort=False):
        axes[0].plot(g.umbral,g.recall,marker='.',label=name)
        axes[1].plot(g.umbral,g.porcentaje_alertado,marker='.',label=name)
    axes[0].set(xlabel='Umbral fijo diagnóstico',ylabel='Recall',ylim=(0,1));axes[1].set(xlabel='Umbral fijo diagnóstico',ylabel='% alertado')
    for ax in axes:ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'figures/seleccion_8_umbrales.png',dpi=150);plt.close(fig)


def write_report(root,tables,spec,detail):
    def table(frame):return markdown(frame.astype(object).where(frame.notna(),'No estimable'))
    text='''# Fase 8 — Selección final del modelo y política de decisión

Fecha: 18/10/2026. **Selección congelada: regresión logística inicial + prioridad del 20% por mes de llegada**, ambos hoteles juntos. El 20% es un supuesto académico de capacidad fijado antes de comparar capacidades, no un recurso real del hotel ni una política rentable demostrada. Prueba sigue sin predecir ni evaluar. No se modifican v3, predictores, hiperparámetros o calibración.

## 1. Protocolo y artefactos vigentes

Se revisan fase_7_1_correccion_sesgo_temporal.md, splitting.py, temporal_bias_v3.py, comparación/preprocesamiento y manifiesto activo. Versión v3_cohortes_llegada_retrospectivo:

| Rol | Llegadas | Filas | Seguimiento proxy común |
| --- | --- | --- | --- |
| Entrenamiento | 01/07/2015–30/06/2016 | 49157 | Antes de 01/09/2016 |
| Embargo | Julio–agosto 2016 | 9635 | Fuera de ajuste y validación |
| Validación | Septiembre–diciembre 2016 | 19911 | Antes de 01/03/2017 |
| Embargo | Enero–febrero 2017 | 7858 | Fuera de ajuste y validación |
| Prueba reservada | Marzo–agosto 2017 | 32829 | Cierre asumido 01/12/2018, no acreditado; sin auditar aquí |

Train y validación completos pasan la auditoría por bloque de último estado + un día y salida prevista + un día antes de sus cierres. El manifiesto se contrasta con temporal_split_v3 sin reescribirlo; no se llama run_v3, no se generan asignaciones nuevas ni se filtran reservas por resultado temprano. Las altas proxy pueden solaparse: es evaluación retrospectiva por llegada, no predicción al alta.

Entradas activas: reports/estado_protocolo.json, particiones_temporales.csv, division_temporal.json, protocolo_7_1_modelos.json y protocolo_7_1_predicciones_validacion.csv. Se leen características/etiquetas exclusivamente de los IDs train/validación v3; para contrastar todo el manifiesto se leen solo metadatos. No se consultan ni reutilizan predicciones v2. Las huellas de todos los datos e informes previos se conservan.

## 2. Dos candidatos iniciales, sin búsqueda

Se reentrenan únicamente las fábricas iniciales de logística y XGBoost sobre las 49157 filas permitidas, sin validación como eval_set, sin early stopping ni búsquedas. Las probabilidades reproducen fase 7.1. Las medianas, vocabularios y escala se verifican contra train; los transformadores no se ajustan con validación.

- Logística: C=1, solver=lbfgs, max_iter=2000, tol=0.0001, class_weight=None, random_state=42. Imputación numérica por mediana y StandardScaler; imputación categórica constante Desconocido, OneHotEncoder(handle_unknown='ignore', sparse_output=True), remainder='drop'.
- XGBoost: 300 árboles, profundidad 4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, hist, binary:logistic, logloss, cuatro hilos, seed 42. Misma imputación/codificación, sin escala. Se conservan defaults originales.

Los mismos 14 predictores: lead_time, total_nights, adults, children, babies, children_missing, hotel, arrival_date_month, meal, country, market_segment, distribution_channel, reserved_room_type y customer_type. El pipeline ajustado genera 192 columnas. Objetivo y metadatos de seguimiento/ID/mes de lote quedan separados. Los parámetros completos y el preprocesamiento están en la especificación congelada.

Métricas globales con probabilidad y regla diagnóstica p>=0,5:

METRICS

XGBoost tiene mejor ROC-AUC/AP y precision a 0,5; logística mayor recall/F1. A ese umbral no se comparan iguales recursos: logística emite 4997 alertas (25,10%) y XGBoost 4189 (21,04%). Por eso no se usa esa comparación sola para elegir política de seguimiento. AUC/AP describen ordenación global, no el punto concreto que permite atender la capacidad fijada.

## 3. Umbrales fijos: diagnóstico, no política elegida

Se estudian umbrales prefijados 0,1–0,9. Predicción positiva si score>=umbral; las cantidades alertadas pueden cambiar entre meses y modelos. No se escoge el que maximice F1 ni se transforma ese máximo en una política óptima de negocio.

THRESHOLDS

![Umbrales y volúmenes](figures/seleccion_8_umbrales.png)

## 4. Comparación con capacidad mensual igual

El plan se guarda antes del análisis en seleccion_8_plan_previo.md. Se toma cada mes calendario de llegada como lote, **ambos hoteles juntos**. Para capacidad q, k=floor(n_mes*q/100). Se priorizan exactamente k scores por mes, sin exceder la fracción; por redondeo la proporción global puede quedar ligeramente por debajo. Para 20%: 1078, 1240, 890 y 772 alertas en septiembre, octubre, noviembre y diciembre, respectivamente: 3980 en total (19,98895%). No se usa floor del total de los cuatro meses ni un percentil que incluya todos los empates.

CAPACITIES

Al 20%, logística identifica 3407 cancelaciones con 573 FP y 4163 FN, frente a 3375, 605 y 4195 de XGBoost: 32 TP adicionales a idéntico volumen. Precision 85,60% frente a 84,80%; recall 45,01% frente a 44,58%. Es una diferencia descriptiva pequeña (0,80 puntos de precision), sin superioridad estadística o causal acreditada. Duplicados, selección previa y correlación de reservas impiden asumir independencia para inventar intervalos.

Al 10% coinciden los conteos agregados de ambos (1921 TP de 1990 alertas), lo que no significa que elijan las mismas reservas. Al 30% XGBoost es mejor: 4505 TP frente a 4293 con el mismo volumen. Se conserva el 20% fijado por supuesto de capacidad: no se aumenta a 30% para favorecer XGBoost, ni se baja a 10% para maximizar precision. Si el hotel aportase una capacidad distinta habría que diseñar una nueva política y validación, sin decidirla mirando prueba.

![Sensibilidad a capacidad mensual](figures/seleccion_8_capacidades.png)

## 5. Política única y empates reproducibles

**Modelo: logística inicial. Política: top 20% por mes, k=n_mes*20//100, para seguimiento humano.** Alerta es una prioridad académica, no afirmar que una reserva vaya a cancelar con certeza. No se define un umbral fijo de probabilidad; los scores límite observados se registran solo para auditoría y no se trasladan a prueba.

Orden dentro del mes: (1) score predict_proba para clase 1 descendente; (2) ante score EXACTAMENTE igual, SHA256 del texto UTF-8 `42|ID` ascendente; (3) ID numérico ascendente como desempate residual. ID es meta_row_id entero único del CSV original, exclusivamente técnico; no entra en X. El hash evita usar el orden original del CSV como criterio directo. No se redondean scores, no se consulta y y no se escoge semilla por acierto. Ordenar de otra forma el archivo de entrada no cambia qué IDs quedan alertados.

Bordes de logística al 20%:

BORDERS

En septiembre hay 11 casos con score de corte y se eligen 10; en noviembre 12 y se eligen 10. La regla evita superar capacidad al incluir indiscriminadamente todo empate. Los scores de corte difieren entre meses (aproximadamente 0,728, 0,570, 0,642 y 0,572). No constituyen cuatro umbrales aprendidos para aplicar a meses futuros: al siguiente lote se calcula su mismo top-k sin usar etiquetas.

La política presupone lote mensual completo y sus scores. Es retrospectiva y no acredita atender reservas al crearse o antes de conocerse un resultado. Tampoco define lista diaria, presupuesto fijo de contactos por hotel, reasignación de cuotas o exclusión de reservas por cancelación ya conocida. Esas reglas no se improvisarán en prueba. La capacidad es una fracción ilustrativa de filas, no horas de personal ni reservas reales únicas garantizadas; los duplicados se mantienen como en el dataset.

## 6. Estabilidad y distribución del seguimiento

MONTHLY

La pequeña ventaja agregada de logística no es uniforme: XGBoost detecta siete y tres cancelaciones adicionales en septiembre y noviembre; logística once y treinta y una más en octubre y diciembre. En logística, precision mensual varía de 73,58% a 90,24% y recall de 40,63% a 47,03%. No hay evidencia de estabilidad entre años con cuatro meses de validación.

HOTELS

La cuota compartida no garantiza 20% por hotel. Logística alerta 3359 City (24,54% de sus filas) y 621 Resort (9,98%); XGBoost asignaría 3115 y 865. Logística detecta más cancelaciones de City (2853 vs 2702), pero menos de Resort (554 vs 673). Esto limita una afirmación de superioridad universal y debe contrastarse con recursos reales por establecimiento antes de uso. No se introducen ahora cuotas por hotel para cambiar resultados.

## 7. Calibración v3 y necesidad para esta política

CALIBRATION

La tasa observada es 38,02%. Logística promedia 33,10% (brecha −4,92 puntos), XGBoost 30,35% (−7,67). Brier es 0,172380 y 0,165107: XGBoost mejora esa pérdida pese a mayor brecha media; Brier combina calibración y resolución y no es una medida aislada de sesgo medio. Como referencia, probabilidad constante igual a la tasa de train da Brier CONSTANT_BRIER. ECE se informa solo descriptivamente con diez bins fijos, no como garantía ni criterio único de elección.

BINS

No hay solo infrapredicción uniforme: logística, por ejemplo, predice media 5,24% en el primer intervalo y se observa 14,18%, mientras en el rango de 0,6 (incluido) a 0,7 (excluido) predice 64,58% y se observa 54,00%. Las curvas tienen soporte exportado. Las probabilidades no se presentan como frecuencias fiables de producción.

![Calibración y tamaños de bins](figures/seleccion_8_calibracion.png)

**No se ajusta calibrador.** Para top-k solo se necesita un orden: una transformación estrictamente creciente conserva prioridades y empates, por tanto puede cambiar la interpretación probabilística sin cambiar la selección. Una transformación meramente no decreciente (p. ej., con tramos planos) puede crear empates y alterar quién entra al aplicar el hash; diferencias numéricas/representación también deben verificarse. No se asume que cualquier calibración deje la política intacta.

No hace falta calibrar para definir esta priorización académica, pero sí sería necesario un estudio independiente si se quisieran interpretar probabilidades o aplicar reglas económicas basadas en ellas. Faltan bloques separados de calibración/evaluación que no hayan participado en selección y una historia suficiente. No se ajusta en esta validación para luego presentarla como independiente; se conservan scores originales y calibrador=None.

## 8. Justificación final, sin beneficio inventado

Se selecciona **logística inicial** por el equilibrio entre recursos fijados, resultados y simplicidad: al 20% mensual obtiene ligeramente más TP y menos FP/FN, con estructura aditiva más fácil de inspeccionar y menor coste local de ajuste/inferencia. Esa ventaja de capacidad es más pertinente para esta regla que ganar AUC global. La diferencia es pequeña; si el resultado a capacidad fija fuera esencialmente equivalente, la menor complejidad también favorecería logística. No se declara significación estadística ni rentabilidad.

Se reconoce lo que favorece XGBoost: mayor ROC-AUC/AP, menor Brier, mejores resultados a 30% y más cobertura de cancelaciones de Resort bajo cuota compartida. No se descarta por ser complejo ni se elige automáticamente por esas métricas. La selección se limita a esta política académica y datos, no a superioridad general.

Seguimiento posible: contacto preventivo, recordatorio o solicitud de confirmación por personal, siempre con supervisión y eficacia por medir. Un FP es atención innecesaria y posible molestia; un FN es riesgo no anticipado. No se inventan costes o funciones de beneficio, ni se equipara cancelación detectada con cancelación evitada. No se recomiendan penalizaciones o cancelaciones automáticas.

## 9. Especificación y artefacto congelados

- `reports/seleccion_8_especificacion_congelada.json`: modelo, versión v3 completa, objetivo/clase positiva, 14 predictores, grupos numéricos/categóricos, transformaciones, 192 columnas, hiperparámetros completos, semilla, política/empates/lotes, métricas de validación, calibrador=None, versiones y limitaciones.
- `models/seleccion_8_modelo_congelado.joblib`: pipeline ya ajustado exclusivamente con entrenamiento v3, con su SHA-256 en la especificación. Se comprueba el roundtrip de serialización contra scores de validación. **No se reentrena con validación para la evaluación final.**
- Se congelan hashes de original, preparado, manifiesto, división, plan y fuentes del modelo/preprocesamiento/política. ID del original estable; ningún cambio de orden/IDs de la fuente se introduce sin invalidar la especificación. La aplicación de política no acepta etiquetas.

Reproducción futura de la evaluación, solo tras autorización: comprobar hashes/versiones, cargar ese pipeline ya ajustado sin fit, producir scores del bloque reservado y aplicar `apply_frozen_policy` con ID y mes de llegada. Exactamente 20% mensual con floor y hash prefijados, sin escoger capacidad o umbral según prueba. No añadir recalibración, nuevas variables, cuotas o decisiones tras observar sus resultados. El cálculo de top-k con scores del lote es aplicación de una política fijada, no tuning con etiquetas, aunque siga siendo retrospectivo y no online.

Las reejecuciones verifican la especificación/modelo existente y no los sobrescriben; los tiempos de entrenamiento de cada reproducción pueden variar y no son parámetros de decisión. El JSON queda como contrato para la siguiente fase, sin preparar la presentación final ni efectuar esa evaluación.

## 10. Archivos, ejecución y límites

Nuevos: src/final_selection.py, src/decision_policy.py, tests/test_decision_policy.py, notebooks/seleccion_final.ipynb, este informe, plan previo, especificación/artefacto y tablas seleccion_8_* de métricas, scores, umbrales, capacidades, empates, meses, hoteles, calibración y decisiones individuales de validación. Se generan tres PNG. Se actualizan README y src/run_notebook.py, sin nuevas dependencias (joblib ya instalado con scikit-learn).

El notebook se ejecuta completo con salidas. Las pruebas verifican límites/floor por mes, capacidad idéntica, empates por hash, invariancia al orden de entrada, selección preservada por transformaciones estrictamente crecientes, rechazos de entradas inválidas y contrato congelado. Se conservan las pruebas anteriores. Se comprueba integridad de datos/manifiestos/informes históricos, ajuste solo train, scores exclusivamente v3 y correspondencia de IDs de decisiones solo con validación. La reproducción contrasta scores y selección sin alterar modelo/JSON congelados.

Persisten la evaluación retrospectiva por llegada y altas solapadas, falta de snapshots/ingestión real y cierre PMS acreditados, duplicados y validación de solo cuatro meses. El EDA vio todo el archivo y parte de la prueba ampliada se utilizó bajo v2; no puede llamarse prueba totalmente independiente. Esta validación se reutiliza para seleccionar modelo/política y no representa una estimación final libre de selección. La política presupone un lote mensual y recursos compartidos hipotéticos; no tiene beneficio, causalidad de intervención o viabilidad en tiempo real acreditados. Los sesgos de país/mercado/tipo de cliente requieren revisión humana y operacional, no sanciones automáticas.

**Prueba permanece sin transformar, predecir o evaluar en esta fase. No se consultan sus etiquetas para seleccionar ninguna decisión.** El siguiente paso, si se autoriza, será aplicar una vez la especificación congelada sin nuevos ajustes y declarar el alcance exploratorio del resultado; antes de uso real harán falta datos prospectivos y evaluación de intervención. No se avanza a esa fase.

**Fin exclusivo de fase 8. Se espera revisión y autorización del usuario.**
'''
    metric_cols=['modelo','accuracy','precision','recall','f1','roc_auc','average_precision','fp','fn','fit_seconds','predict_seconds']
    borders=tables['bordes_empates'];borders=borders[borders.modelo.eq('regresion_logistica')&borders.capacidad_pct.eq(20)]
    replacements={'METRICS':table(tables['metricas'][metric_cols]),'THRESHOLDS':table(tables['umbrales']),
        'CAPACITIES':table(tables['capacidades']),'BORDERS':table(borders),
        'MONTHLY':table(tables['mensual_capacidad_20']),'HOTELS':table(tables['hoteles_capacidad_20']),
        'CALIBRATION':table(tables['calibracion']),'BINS':table(tables['calibracion_bins']),
        'CONSTANT_BRIER':f"{detail['brier_constante_tasa_train']:.6f}"}
    for key in sorted(replacements,key=len,reverse=True):text=text.replace(key,replacements[key])
    (Path(root)/'reports/fase_8_seleccion_final.md').write_text(text,encoding='utf-8')
