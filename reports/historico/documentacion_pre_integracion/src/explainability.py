"""Fase 7: explicación del XGBoost inicial, sin tuning ni acceso predictivo a prueba."""
from pathlib import Path
import json
import time
import importlib.metadata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import expit
from scipy import sparse
import shap
from sklearn.metrics import roc_auc_score, brier_score_loss, confusion_matrix

from src.comparison import load_development, model_factories, fit_one, sha
from src.features import FEATURES, NUMERIC_FEATURES, CATEGORICAL_FEATURES
from src.optimization import json_write, markdown
from src.splitting import PROTOCOL_V2

SEED = 42
SAMPLE_SIZE = 3000
MIN_N = 100
MIN_CLASS = 30


def feature_mapping(preprocessor):
    """Mapeo por estructura del encoder, sin trocear nombres con guiones bajos."""
    names = preprocessor.get_feature_names_out()
    encoder = preprocessor.named_transformers_['categorical'].named_steps['encoder']
    assert encoder.drop is None and encoder.min_frequency is None
    originals = list(NUMERIC_FEATURES)
    for column, categories in zip(CATEGORICAL_FEATURES, encoder.categories_):
        originals.extend([column]*len(categories))
    assert len(names)==len(originals) and set(originals)<=set(FEATURES)
    expected = ['numeric__'+c for c in NUMERIC_FEATURES]
    expected += ['categorical__'+n for n in encoder.get_feature_names_out(CATEGORICAL_FEATURES)]
    np.testing.assert_array_equal(names,expected)
    return pd.DataFrame({'posicion':range(len(names)), 'transformada':names, 'original':originals})


def group_contributions(values, mapping):
    values=np.asarray(values)
    if values.ndim!=2 or values.shape[1]!=len(mapping):
        raise ValueError('Valores SHAP y mapeo no corresponden')
    grouped=np.column_stack([values[:,mapping.original.eq(c).to_numpy()].sum(axis=1) for c in FEATURES])
    np.testing.assert_allclose(grouped.sum(axis=1),values.sum(axis=1),atol=2e-5,rtol=1e-5)
    return grouped


def segment_metrics(data, columns):
    """Denominadores explícitos. AUC solo con ambas clases; pequeños señalados."""
    rows=[]
    for column in columns:
        for value,group in data.groupby(column,dropna=False,observed=True,sort=True):
            y=group.is_canceled.to_numpy();p=group.probabilidad.to_numpy();pred=p>=.5
            tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
            n0,n1=int(tn+fp),int(fn+tp)
            precision=float(tp/(tp+fp)) if tp+fp else None
            recall=float(tp/n1) if n1 else None
            rows.append({'dimension':column,'grupo':str(value),'n':len(group),'no_canceladas':n0,'canceladas':n1,
                'tasa_cancelacion':float(y.mean()),'probabilidad_media':float(p.mean()),
                'brecha_calibracion':float(p.mean()-y.mean()), 'brier':float(brier_score_loss(y,p)),
                'roc_auc':float(roc_auc_score(y,p)) if n0 and n1 else None,
                'precision':precision,'recall':recall,'f1':float(2*tp/(2*tp+fp+fn)) if 2*tp+fp+fn else 0.,
                'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp),
                'fpr':float(fp/n0) if n0 else None,'fnr':float(fn/n1) if n1 else None,
                'tasa_error':float((fp+fn)/len(group)),
                'suficiente_descriptivo':len(group)>=MIN_N and n0>=MIN_CLASS and n1>=MIN_CLASS})
    return pd.DataFrame(rows)


def calibration_bins(data):
    rows=[]
    populations=[('Todos',data)]+[(str(h),g) for h,g in data.groupby('hotel',observed=True)]
    for hotel,group in populations:
        bin_ids=np.minimum((group.probabilidad.to_numpy()*10).astype(int),9)
        for k in range(10):
            subset=group.iloc[np.flatnonzero(bin_ids==k)]
            if subset.empty:continue
            rows.append({'hotel':hotel,'bin':k,'inferior':k/10,'superior':(k+1)/10,'n':len(subset),
                         'probabilidad_media':float(subset.probabilidad.mean()),'tasa_observada':float(subset.is_canceled.mean()),
                         'n_al_menos_100':len(subset)>=MIN_N})
    return pd.DataFrame(rows)


def select_cases(y, probabilities):
    """Caso de probabilidad mediana en cada tipo; desempate por orden original."""
    y=np.asarray(y);p=np.asarray(probabilities)
    masks={'TP':(y==1)&(p>=.5),'TN':(y==0)&(p<.5),'FP':(y==0)&(p>=.5),'FN':(y==1)&(p<.5)}
    selected={}
    for label,mask in masks.items():
        positions=np.flatnonzero(mask)
        if not len(positions):raise ValueError(f'No hay ejemplos {label}')
        ordered=positions[np.argsort(p[positions],kind='stable')]
        selected[label]=int(ordered[(len(ordered)-1)//2])
    return selected


def run_explainability(root):
    root=Path(root);out=root/'reports';figdir=out/'figures'
    protected=[p for folder in ['data','reports'] for p in (root/folder).rglob('*') if p.is_file()
               and not p.name.startswith('explicabilidad_7') and p.name!='fase_7_explicabilidad.md']
    protected += [root/'src'/n for n in ['splitting.py','features.py','preprocessing.py','baseline.py','comparison.py','optimization.py']]
    protected += [p for p in (root/'notebooks').glob('*.ipynb') if p.name!='explicabilidad.ipynb']
    hashes={str(p.relative_to(root)):sha(p) for p in protected}
    x,y,v,z,ids=load_development(root)
    prior=json.loads((out/'optimizacion_6_verificacion.json').read_text(encoding='utf-8'))
    assert prior['candidato_principal']=='xgboost_inicial_fase_5' and prior['protocolo']==PROTOCOL_V2
    model=model_factories()['xgboost']
    before_params=model.named_steps['classifier'].get_params()
    phase5=json.loads((out/'comparacion_5_verificacion.json').read_text(encoding='utf-8'))['parametros']['xgboost']
    # El único NaN paramétrico de XGBoost es el sentinel missing; se compara aparte.
    for key,value in before_params.items():
        expected=phase5[key]
        if isinstance(value,float) and np.isnan(value): assert key=='missing' and (expected=='NaN' or pd.isna(expected))
        else: assert value==expected,(key,value,expected)
    print('Reconstruyendo XGBoost inicial, sin optimización.',flush=True)
    metrics,probability,notices=fit_one(model,x,y,v,z)
    reference=pd.read_csv(out/'comparacion_5_predicciones_validacion.csv')
    np.testing.assert_array_equal(ids,reference.meta_row_id)
    np.testing.assert_allclose(probability,reference.xgboost,atol=1e-7,rtol=1e-7)
    np.testing.assert_array_equal(probability>=.5,reference.xgboost.ge(.5))
    # Usar los scores congelados para el diagnóstico mantiene la base numérica de fase 6.
    data=v.copy();data['meta_row_id']=ids;data['is_canceled']=z;data['probabilidad']=reference.xgboost.to_numpy()
    metadata=pd.read_csv(root/'data/processed/hotel_bookings_prepared.csv',usecols=['meta_booking_date_proxy','meta_arrival_date'])
    data['mes_reserva_proxy']=pd.to_datetime(metadata.loc[v.index,'meta_booking_date_proxy']).dt.to_period('M').astype(str)
    data['antelacion_grupo']=pd.cut(data.lead_time,[-np.inf,7,30,90,180,np.inf],labels=['0-7','8-30','31-90','91-180','181+']).astype(str)
    data['llegada_respecto_corte']=np.where(pd.to_datetime(metadata.loc[v.index,'meta_arrival_date']).ge('2017-01-01'),'Desde 2017-01-01','Antes de 2017-01-01')
    dimensions=['hotel','antelacion_grupo','market_segment','distribution_channel','arrival_date_month','customer_type','mes_reserva_proxy','llegada_respecto_corte']
    segments=segment_metrics(data,dimensions);bins=calibration_bins(data)
    pre=model.named_steps['preprocessor'];classifier=model.named_steps['classifier'];booster=classifier.get_booster()
    mapping=feature_mapping(pre);assert len(mapping)==196
    gain=booster.get_score(importance_type='total_gain');gain_values=np.zeros(len(mapping))
    for name,value in gain.items():
        index=int(name[1:]) if name.startswith('f') and name[1:].isdigit() else mapping.transformada.tolist().index(name)
        gain_values[index]=value
    importance=mapping.copy();importance['total_gain']=gain_values
    importance['proporcion_gain']=gain_values/gain_values.sum()
    grouped_gain=importance.groupby('original',sort=False)[['total_gain','proporcion_gain']].sum().sort_values('total_gain',ascending=False).reset_index()
    rng=np.random.default_rng(SEED);sample_positions=np.sort(rng.choice(len(v),size=min(SAMPLE_SIZE,len(v)),replace=False))
    cases=select_cases(z,reference.xgboost)
    union=np.unique(np.r_[sample_positions,list(cases.values())]);position_lookup={int(p):i for i,p in enumerate(union)}
    transformed=pre.transform(v.iloc[union]);assert sparse.issparse(transformed)
    start=time.perf_counter()
    explainer=shap.TreeExplainer(classifier,model_output='raw',feature_perturbation='tree_path_dependent',feature_names=mapping.transformada.tolist())
    values=np.asarray(explainer.shap_values(transformed,check_additivity=True))
    elapsed=time.perf_counter()-start
    assert values.shape==(len(union),len(mapping)) and np.isfinite(values).all()
    base=float(np.asarray(explainer.expected_value).item())
    margin=classifier.predict(transformed,output_margin=True)
    reconstructed=base+values.sum(axis=1)
    np.testing.assert_allclose(reconstructed,margin,atol=2e-5,rtol=2e-5)
    np.testing.assert_allclose(expit(reconstructed),probability[union],atol=2e-6,rtol=2e-6)
    grouped=group_contributions(values,mapping)
    sample_indices=[position_lookup[int(p)] for p in sample_positions]
    sample_values=values[sample_indices];sample_grouped=grouped[sample_indices]
    global_shap=pd.DataFrame({'original':FEATURES,'mean_abs_group_sum':np.abs(sample_grouped).mean(axis=0),
                             'mean_signed_group_sum':sample_grouped.mean(axis=0),
                             'sum_mean_abs_dummies':[np.abs(sample_values[:,mapping.original.eq(c).to_numpy()]).mean(axis=0).sum() for c in FEATURES]}).sort_values('mean_abs_group_sum',ascending=False)
    transformed_shap=mapping.copy();transformed_shap['mean_abs_shap']=np.abs(sample_values).mean(axis=0)
    sample_audit=[]
    for column in ['hotel','is_canceled','mes_reserva_proxy']:
        for value in data[column].unique():
            sample_audit.append({'dimension':column,'grupo':str(value),'n_validacion':int(data[column].eq(value).sum()),
                'n_muestra':int(data.iloc[sample_positions][column].eq(value).sum()),
                'proporcion_validacion':float(data[column].eq(value).mean()),'proporcion_muestra':float(data.iloc[sample_positions][column].eq(value).mean())})
    profiles=dependence_profiles(data.iloc[sample_positions],sample_grouped)
    case_rows=[];local_rows=[]
    for label,position in cases.items():
        i=position_lookup[position];row=v.iloc[position]
        case_rows.append({'caso':label,'meta_row_id':int(ids.iloc[position]),'real':int(z.iloc[position]),
            'probabilidad':float(probability[position]),'base_log_odds':base,'margen':float(margin[i]),
            'margen_reconstruido':float(reconstructed[i]),'hotel':row.hotel,'lead_time':row.lead_time,
            'market_segment':row.market_segment,'distribution_channel':row.distribution_channel,'arrival_date_month':row.arrival_date_month})
        for j,column in enumerate(FEATURES):
            # Se omite el valor de país del ejemplo público; SHAP no lo convierte en causa.
            value='categoría omitida en ejemplo local' if column=='country' else str(row[column])
            local_rows.append({'caso':label,'variable':column,'valor':value,'shap_log_odds':float(grouped[i,j])})
    tables={'mapa_caracteristicas':mapping,'gain_transformadas':importance,'gain_originales':grouped_gain,
            'shap_global':global_shap,'shap_transformadas':transformed_shap,'segmentos':segments,'calibracion_bins':bins,
            'muestra_perfil':pd.DataFrame(sample_audit),'casos':pd.DataFrame(case_rows),'contribuciones_locales':pd.DataFrame(local_rows),
            'dependencia_perfil':profiles,
            'muestra_ids':pd.DataFrame({'meta_row_id':ids.iloc[sample_positions].to_numpy()}),
            'predicciones_validacion':data[['meta_row_id','is_canceled','probabilidad']]}
    for name,table in tables.items():table.to_csv(out/f'explicabilidad_7_{name}.csv',index=False)
    # IDs de la unión diferencian muestra global y ejemplos añadidos; no contienen X.
    np.savez_compressed(out/'explicabilidad_7_shap.npz',values=values,grouped_values=grouped,base=base,
                        meta_row_id=ids.iloc[union].to_numpy(),sample_union_positions=np.asarray(sample_indices),
                        transformed_names=mapping.transformada.to_numpy(dtype=str))
    make_figures(figdir,importance,grouped_gain,global_shap,transformed_shap,sample_values,
                 transformed[sample_indices].toarray(),v.iloc[sample_positions],sample_grouped,
                 pd.DataFrame(local_rows),pd.DataFrame(case_rows),segments,bins)
    for path,expected in hashes.items():assert sha(root/path)==expected,path
    detail={'protocolo':PROTOCOL_V2,'parametros':before_params,'metricas':metrics,'advertencias_fit':notices,
        'n_train':len(x),'n_validacion':len(v),'umbral_diagnostico':.5,'umbral_operativo':None,'calibrador_ajustado':False,
        'shap_version':shap.__version__,'xgboost_version':importlib.metadata.version('xgboost'),'seed_muestra':SEED,
        'muestra_global':len(sample_positions),'muestra_union_con_casos':len(union),'seleccion_muestra':'aleatoria simple sin reemplazo, independiente de etiqueta; seed42',
        'shap_method':'TreeExplainer/tree_path_dependent/raw/exact sobre CSR; background implícito en árboles de train',
        'n_transformadas':len(mapping),'base_log_odds':base,'segundos_shap':elapsed,
        'max_error_aditividad_margen':float(np.max(np.abs(reconstructed-margin))),
        'max_error_probabilidad':float(np.max(np.abs(expit(reconstructed)-probability[union]))),
        'predicciones_fase_5_reproducidas':True,'datos_anteriores_intactos':hashes,
        'prueba_transformada_predicha_evaluada':False,'criterio_segmento_descriptivo':{'n':MIN_N,'min_por_clase':MIN_CLASS}}
    json_write(out/'explicabilidad_7_verificacion.json',detail)
    write_report(root,tables,detail)
    return tables,detail


def dependence_profiles(sample, grouped):
    """Medias descriptivas de contribuciones según valores observados, sin intervenir."""
    rows=[]
    for column in ['country','market_segment','customer_type','hotel','antelacion_grupo']:
        source='lead_time' if column=='antelacion_grupo' else column
        series=sample[column].fillna('Desconocido').astype(str)
        for value in series.unique():
            mask=series.eq(value).to_numpy()
            rows.append({'variable':source,'valor_grupo':value,'n_muestra':int(mask.sum()),
                'shap_medio_log_odds':float(grouped[mask,FEATURES.index(source)].mean()),
                'probabilidad_media':float(sample.iloc[np.flatnonzero(mask)].probabilidad.mean()),
                'tasa_cancelacion':float(sample.iloc[np.flatnonzero(mask)].is_canceled.mean())})
    return pd.DataFrame(rows)


def make_figures(path,importance,gain,global_shap,transformed_shap,values,colors,raw,grouped,locals_,cases,segments,bins):
    path.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    gain.head(10).iloc[::-1].plot.barh(x='original',y='proporcion_gain',ax=axes[0],legend=False)
    global_shap.head(10).iloc[::-1].plot.barh(x='original',y='mean_abs_group_sum',ax=axes[1],legend=False)
    axes[0].set(title='XGBoost — total_gain agregado',xlabel='Fracción de ganancia de entrenamiento',ylabel='')
    axes[1].set(title='SHAP — suma por variable original',xlabel='Media |suma SHAP| (log-odds)',ylabel='')
    fig.tight_layout();fig.savefig(path/'explicabilidad_7_importancias.png',dpi=150);plt.close(fig)
    np.random.seed(SEED)
    explanation=shap.Explanation(values=values,data=colors,feature_names=transformed_shap.transformada.tolist())
    shap.plots.beeswarm(explanation,max_display=16,show=False)
    plt.gcf().set_size_inches(11,7);plt.tight_layout();plt.savefig(path/'explicabilidad_7_shap_resumen.png',dpi=150,bbox_inches='tight');plt.close()
    # Dependencia sobre valores observados: no intervenciones ni extrapolación.
    chosen=[c for c in global_shap.original if c in ['lead_time','total_nights','country','market_segment','hotel']][:3]
    fig,axes=plt.subplots(1,len(chosen),figsize=(15,5))
    for ax,column in zip(np.atleast_1d(axes),chosen):
        contribution=grouped[:,FEATURES.index(column)]
        if column in NUMERIC_FEATURES:
            ax.scatter(raw[column],contribution,s=5,alpha=.25)
            ax.set_xlabel(column)
        else:
            cats=raw[column].fillna('Desconocido').astype(str)
            top=cats.value_counts().head(6).index.tolist()
            arrays=[contribution[cats.eq(c).to_numpy()] for c in top]
            labels=[f'{c}\n(n={len(a)})' for c,a in zip(top,arrays)]
            ax.boxplot(arrays,tick_labels=labels,showfliers=False)
            ax.tick_params(axis='x',rotation=30)
            ax.set_xlabel(column+' (6 categorías más frecuentes)')
        ax.set_ylabel('Suma SHAP de la variable (log-odds)');ax.grid(alpha=.2)
    fig.suptitle('Dependencia descriptiva en muestra de validación');fig.tight_layout()
    fig.savefig(path/'explicabilidad_7_dependencias.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(13,9))
    for ax,row in zip(axes.flat,cases.itertuples()):
        contributions=locals_[locals_.caso.eq(row.caso)].copy()
        contributions['abs']=contributions.shap_log_odds.abs()
        top=contributions.nlargest(6,'abs').sort_values('shap_log_odds')
        rest=contributions.shap_log_odds.sum()-top.shap_log_odds.sum()
        labels=top.variable.tolist()+['Resto (suma)'];v=top.shap_log_odds.tolist()+[rest]
        ax.barh(labels,v,color=['#c64444' if value>0 else '#3876b5' for value in v]);ax.axvline(0,color='gray')
        ax.set(title=f'{row.caso}: real={row.real}, p={row.probabilidad:.3f}; base={row.base_log_odds:.3f}',xlabel='Contribución al margen (log-odds)')
    fig.suptitle('Casos medianos de cada tipo — explicaciones del modelo, no causas');fig.tight_layout()
    fig.savefig(path/'explicabilidad_7_locales.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(15,4.5))
    for ax,dimension in zip(axes,['hotel','antelacion_grupo','mes_reserva_proxy']):
        d=segments[segments.dimension.eq(dimension)].copy()
        if dimension=='antelacion_grupo':
            d=d.set_index('grupo').reindex(['0-7','8-30','31-90','91-180','181+']).reset_index()
        d.plot(x='grupo',y=['fpr','fnr'],kind='bar',ax=ax)
        ax.set(title=dimension,xlabel='',ylabel='Tasa sobre su clase real',ylim=(0,1))
        ax.tick_params(axis='x',rotation=35);ax.legend(['FPR = FP / no canceladas','FNR = FN / canceladas'],fontsize=7)
        for position,value in enumerate(d.fpr):
            if pd.isna(value):ax.text(position-.12,.04,'N/A',rotation=90,fontsize=8,ha='center')
    fig.tight_layout();fig.savefig(path/'explicabilidad_7_errores.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    hotel_colors={'Todos':'#666666','City Hotel':'#2779b0','Resort Hotel':'#e17c17'}
    for hotel,group in bins.groupby('hotel',sort=False):
        axes[0].plot(group.probabilidad_media,group.tasa_observada,marker='o',color=hotel_colors[hotel],label=hotel)
        small=group[group.n.lt(100)]
        if len(small):axes[0].scatter(small.probabilidad_media,small.tasa_observada,s=85,facecolors='white',edgecolors=hotel_colors[hotel],zorder=5)
        if hotel!='Todos':axes[1].plot(group.probabilidad_media,group.n,marker='o',color=hotel_colors[hotel],label=hotel)
    axes[0].plot([0,1],[0,1],'--',color='gray');axes[0].set(xlabel='Probabilidad media',ylabel='Tasa observada',title='Calibración por hotel — bins 0,1')
    axes[1].set(xlabel='Probabilidad media del bin',ylabel='Reservas en el bin',title='Soporte de las curvas por hotel')
    axes[1].axhline(100,color='gray',linestyle=':',label='100 reservas; huecos en curva: n<100')
    for ax in axes:ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(path/'explicabilidad_7_calibracion.png',dpi=150);plt.close(fig)


def write_report(root,tables,detail):
    segments=tables['segmentos']
    def table(frame):return markdown(frame.fillna('No estimable'))
    text='''# Fase 7 — Explicabilidad y análisis de errores del modelo

Fecha: 18/10/2026. Se analiza exclusivamente **XGBoost inicial de fase 5**, conservado tras fase 6. No se optimiza, cambia protocolo/predictores, ajusta calibrador, elige umbral operativo ni evalúa prueba. El candidato sigue siendo provisional. La interpretación es del modelo y de la validación elegible, no de causas de cancelación ni del conjunto completo de altas.

## 1. Modelo, revisión y reproducibilidad

Se revisaron los informes de fases 5 y 6, el protocolo temporal v2, comparison.py, optimization.py, baseline.py, splitting.py, features.py, preprocessing.py y las convenciones narrativas de los notebooks del proyecto y proyectos anteriores del curso. Se conserva la organización data/notebooks/src/reports.

300 árboles, max_depth=4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, tree_method=hist, objective=binary:logistic, eval_metric=logloss, n_jobs=4, random_state=42. La fábrica original mantiene defaults: no se sustituye por el modelo de 200 árboles de la búsqueda. Se contrastan todos los parámetros contra el registro de fase 5. Como no había modelo serializado, se reconstruye con las mismas 54.164 filas de entrenamiento; imputación por mediana, ausencia categórica Desconocido y OneHotEncoder(handle_unknown='ignore'), sin escalado. Medianas/categorías y conservación de estadísticas se auditan con fit_one. Las predicciones coinciden con las congeladas en fase 5 dentro de precisión float32 y producen idéntica matriz [[9681,663],[3577,4176]]. No se consultan predictores o resultados de prueba para explicar, comparar o decidir.

Validación externa: 18.097 filas, tasa observada 42,84%; umbral **0,5 exclusivamente diagnóstico**, accuracy 0,765707, precision 0,862988, recall 0,538630, F1 0,663278, ROC-AUC 0,858927 y AP 0,842275. El diagnóstico completo de errores/calibración utiliza las probabilidades ya guardadas; el modelo reconstruido sirve para importancia y SHAP. No hay actualización del modelo definitivo.

## 2. Importancia del modelo

Se utiliza **total_gain**, suma de la reducción del objetivo en los splits de entrenamiento de cada columna. Se normaliza y se suman las columnas derivadas por variable original; no se confunde esa suma con el promedio gain. La definición se contrasta en la [API oficial de XGBoost](https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.Booster.get_score). Las columnas sin splits tienen importancia cero.

GAIN

Antelación representa 32,57% de ganancia, país 27,71%, segmento de mercado 12,65% y tipo de cliente 10,38%. Esta medida depende de splits, cardinalidad, interacciones y variables correlacionadas; no mide mejora causal, efecto de cambiar un dato ni importancia fuera de muestra. Una variable con muchas categorías dispone de más oportunidades de partición; la agregación facilita leerla pero no elimina ese sesgo. children_missing no interviene en splits; su cero no demuestra irrelevancia universal de la información ausente.

## 3. SHAP global y correspondencia de características

SHAP_VERSION

TreeExplainer, tree_path_dependent, model_output=raw y cálculo exacto (no Saabas). El fondo se obtiene de las rutas del entrenamiento almacenadas en los árboles, sin elegir datos de prueba o un fondo de validación. La salida explicada es el margen log-odds: **base + suma SHAP = margen; sigmoide(margen) = probabilidad**. No son puntos porcentuales. Esta semántica y las comprobaciones de aditividad están documentadas en [SHAP TreeExplainer](https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html).

Los 14 predictores se convierten en 196 columnas. Su correspondencia se construye a partir del orden numérico y las categorías del encoder, sin partir nombres por guiones bajos. Se conserva la matriz CSR durante predicción y SHAP; densificarla introduciría ceros explícitos donde el árbol trata entradas dispersas como ausentes y podría cambiar la función explicada. La [FAQ oficial de XGBoost](https://xgboost.readthedocs.io/en/stable/faq.html#why-do-i-see-different-results-with-sparse-and-dense-data) aclara esa diferencia. Solo se densifica una copia para colorear el resumen, nunca para calcular atribuciones. La semántica heredada de ceros implícitos también puede afectar ceros numéricos reales; se mantiene para explicar el modelo existente y queda como aspecto de representación a revisar antes de uso operacional, sin cambiarlo en esta fase.

Muestra global: **3000 de 18.097** filas, aleatoria simple sin reemplazo, generador NumPy seed 42, sin condicionar a etiqueta o error. Se incluyen ambos hoteles y los seis meses proxy. Hay 2072 City y 928 Resort; cancelación de la muestra 41,27% frente a 42,84% poblacional. Se exporta el perfil completo y los IDs técnicos: la muestra se aproxima a la composición de validación, sin representatividad certificada de todas las reservas. Cuatro ejemplos medianos por tipo de error se explican en la misma unión si faltaban, pero no se agregan a la media global.

ADDITIVITY

Se suman contribuciones **con signo por fila** de todas las dummies de cada variable y después se calcula media absoluta (mean_abs_group_sum). También se publica la suma de medias absolutas por dummy, generalmente mayor porque no cancela signos. La suma conserva el margen local; no recalcula el juego Shapley considerando cada variable original como un jugador único ni resuelve dependencia entre dummies.

SHAP_GLOBAL

País es primero en media absoluta agrupada (1,043 log-odds), seguido de antelación (0,821), tipo de cliente (0,503), segmento (0,428) y hotel (0,345). El cambio de orden frente a total_gain es coherente con medidas distintas: estructura del entrenamiento frente a contribuciones sobre esta muestra. El signo medio no describe una relación monótona ni un efecto de intervención. Una dummy con cero puede contribuir: también se explica ausencia de esa categoría/ruta, no solo categorías activas.

![Importancias agregadas](figures/explicabilidad_7_importancias.png)

![Resumen SHAP sobre columnas transformadas](figures/explicabilidad_7_shap_resumen.png)

## 4. Dependencias y riesgo estimado

Los gráficos muestran antelación y las variables relevantes disponibles, con dispersión numérica o cajas de categorías más frecuentes. Son valores observados y contribuciones, sin variar artificialmente una categoría manteniendo combinaciones imposibles. Las cajas no son intervalos de confianza. El perfil de categorías y antelación de la muestra se guarda en explicabilidad_7_dependencia_perfil.csv.

PROFILES

Antelación, país, tipo de cliente y mercado participan conjuntamente; no hay una regla universal de riesgo basada en uno de ellos. En esta validación, Groups tiene probabilidad media 73,01% frente a 13,08% en Direct; 91–180 días, 63,50%, frente a 11,21% en 0–7 días. Son asociaciones del score con segmentos condicionados por elegibilidad, no efectos causales de reservar antes o usar un canal. Que país tenga importancia alta puede reflejar mezcla comercial/geográfica, selección y relaciones con otras variables; no autoriza decisiones de trato adverso por origen.

![Dependencias observadas](figures/explicabilidad_7_dependencias.png)

## 5. Cuatro explicaciones individuales

Se elige la reserva con probabilidad mediana dentro de TP/TN/FP/FN, orden estable para desempatar. No se buscan casos extremos favorables. Los cuatro ejemplos resultan de City Hotel y no representan todos los perfiles ni errores de Resort. Las referencias exportadas son IDs técnicos de fila, no IDs personales; el informe omite esos números y el valor de país. No se publican nombres/contactos, agente o empresa.

CASES

Contribuciones agrupadas principales, en log-odds; valores positivos aumentan el margen respecto a la base y negativos lo reducen:

LOCALS

- **TP, p≈0,876:** antelación 169 días y tipo Transient empujan al alza (+0,549 y +0,566); la contribución agrupada de país suma +1,284. Offline TA/TO compensa parcialmente (−0,378). Realmente canceló; no se afirma que esas variables lo causaran.
- **TN, p≈0,125:** antelación de 14 días (−0,845), mercado Direct (−0,518) y contribución de país (−1,268) reducen el margen. Otros factores suben, pero la suma queda por debajo del corte; la reserva se mantuvo.
- **FP, p≈0,587:** país (+0,967), Transient (+0,408) y City (+0,195) superan parcialmente aportes negativos de Corporate (−0,387) y antelación de 31 días (−0,284). El modelo alertaría sobre una reserva que no canceló: SHAP explica el score equivocado, no demuestra un problema real del huésped.
- **FN, p≈0,317:** Transient-Party aporta −1,647 y domina pese a país (+1,061) y Groups (+0,484). La reserva sí canceló, pero quedó sin alerta. Esto ilustra una combinación que el modelo infravalora; no demuestra que el tipo de cliente explique todos los FN.

La base común es −0,30405 log-odds, no la tasa media de validación. La probabilidad se obtiene después de sumar todas las contribuciones; sumar probabilidades individuales de las barras sería incorrecto. El gráfico muestra seis aportes principales y resto agregado para mantener la suma.

![Explicaciones locales](figures/explicabilidad_7_locales.png)

## 6. Errores por segmentos y sus denominadores

Se analiza validación completa. FPR = FP / no canceladas; FNR = FN / canceladas; tasa de error = (FP+FN)/n. Los tamaños, cantidades por clase, precision, recall, F1, AUC, probabilidad media y prevalencia se exportan para todas las dimensiones solicitadas. Un grupo se marca suficiente solo para descripción si n>=100 y cada clase tiene al menos 30 casos: es una regla de prudencia, no una prueba estadística. Con una clase, ROC-AUC no se estima. Los grupos pequeños quedan visibles y señalados, sin ranking concluyente.

ERRORS

City acumula más errores por su volumen: 534 FP y 2425 FN, frente a 129 y 1152 en Resort. Sin embargo, Resort omite 64,25% de sus cancelaciones frente a 40,69% en City. La tasa global de error parece similar (23,12% y 23,57%), pero oculta coberturas de cancelación diferentes.

Online TA concentra 542 FP y 2665 FN; dentro de sus 10441 filas, FPR=9,36% y FNR=57,34%. Direct tiene solo 15 FP, pero omite 314 de 354 cancelaciones (FNR=88,70%): pocas falsas alarmas no equivalen a buena detección. Los canales son otra clasificación de las mismas reservas: TA/TO tiene 618 FP y 3062 FN, sin poder sumarlos a los de Online TA. Entre 31–90 días se acumulan 1586 FN, FNR=57,84%, con n=6058. Con 0–7 días hay 371 FN de 390 cancelaciones (95,13%), aunque el error sobre todas las reservas es solo 10,20% por su baja prevalencia. No se cambia umbral para corregir estos resultados.

**Señal metodológica esencial:** las 1540 reservas elegibles con antelación >180 días son todas canceladas. Los meses de llegada enero-junio también tienen una sola clase en validación. Son grupos con suficiente volumen pero sin contraste de clases; no se declara ROC-AUC ni evidencia de detección de no cancelaciones. La llegada posterior al cierre proxy y la exigencia de resultado antes de 2017 favorecen cancelaciones ya registradas frente a estancias que aún no han ocurrido. Se audita llegada respecto al corte solo como metadato, nunca como predictor nuevo:

ARRIVAL_AUDIT

De las 3917 reservas con llegada desde 2017-01-01, todas están canceladas y 3166 son TP: aproximadamente 75,8% de los TP totales procede de este subgrupo de una sola clase. En las 14180 con llegada anterior al corte, la tasa observada es 27,05%, ROC-AUC 0,7721, precision 60,37% y recall 26,33%. Esta descomposición es una auditoría de la misma validación, no una nueva partición para seleccionar modelo. Evidencia cuánto condiciona el resultado agregado la elegibilidad por fecha de estado.

No significa que en negocio todas las reservas largas o para esos meses cancelen. Parte de la facilidad del modelo para ordenar puede proceder de esa selección temporal. La interpretación del calendario y antelación debe declarar este sesgo; no se relajan cortes ni se incorporan etiquetas futuras para mejorar métricas.

![Tasas de error por clase](figures/explicabilidad_7_errores.png)

## 7. Estabilidad temporal y meses de llegada

MONTHS

Julio proxy tiene AUC 0,7390 y precision 64,06%; diciembre, AUC 0,9665 y precision 99,81%. El recall aumenta de 43,69% a 72,64%, pero la prevalencia también cambia de 36,55% a 66,23% y cambia el mecanismo de selección cerca del corte. No se interpreta como mejora temporal del sistema. Los meses se evalúan en las mismas reservas de validación que ya se han utilizado para seleccionar/comparar; no son un nuevo holdout independiente.

Meses de llegada (distintos del mes proxy de reserva):

ARRIVAL_MONTHS

Octubre tiene recall 21,00% (760 FN), noviembre 26,02% (637 FN). Enero-junio carecen de negativos por elegibilidad, por lo que su aparente precision 100% no acredita desempeño completo. Las comparaciones son marginales, sin controlar simultáneamente país, mercado, hotel y fechas, y se realizan varias inspecciones; diferencias pequeñas no son hallazgos concluyentes. Duplicados y agrupaciones comerciales reducen el tamaño efectivo; no se inventan intervalos de confianza asumiendo independencia.

## 8. Calibración por intervalos y hotel

Global: Brier **0,155458**; probabilidad media 35,68% frente a 42,84% observado, infrapredicción de 7,16 puntos porcentuales. Brier combina resolución y calibración, no las separa. Por hotel:

HOTEL_CAL

Resort infrapredice 10,88 puntos frente a 5,52 en City; ambos tienen miles de filas. La comparación debe considerar sus distintas composiciones y prevalencias. No se propone un calibrador por hotel a partir de este mismo diagnóstico. Los intervalos fijos de 0,1 conservan tamaños; los menores de 100 se señalan y no se interpretan con el mismo peso. El último intervalo incluye probabilidad 1.

BINS

![Curvas de calibración por hotel y soporte](figures/explicabilidad_7_calibracion.png)

No se ha ajustado ningún calibrador. Para una fase posterior, diseñar antes de mirar resultados un bloque temporal de calibración dentro del entrenamiento, distinto de selección de hiperparámetros y con resultados disponibles al corte; entrenar el modelo base solo antes del bloque, congelarlo y obtener scores fuera de ajuste. Ajustar calibración en ese bloque y evaluarla una vez en un periodo posterior no utilizado para decidir. Alternativa: diseño temporal anidado de scores fuera de ajuste, con purga de etiquetas tardías. Los folds de fase 6, ya usados para tuning, no son automáticamente independientes para calibrar y evaluar. La validación externa actual ya ha sido explorada; no recupera independencia por cambiarle el nombre. Más historia, snapshots iniciales y seguimiento acreditado son preferibles para un nuevo diseño. No se emplea prueba para aprender calibración ni se inicia ese trabajo aquí.

## 9. Lectura para revenue management

El modelo combina sobre todo país, antelación, tipo de cliente y mercado; puede ayudar a ordenar una lista de seguimiento, pero la cifra de probabilidad no es una frecuencia de negocio acreditada. Groups y antelaciones largas reciben puntuaciones elevadas en esta población seleccionada; Direct, estancias cercanas y varias combinaciones de cliente/canal plantean cancelaciones difíciles de detectar. Online TA concentra la mayor carga de errores por mercado y merece revisar datos/proceso, sin confundir volumen con peor tasa universal.

Podrían evaluarse contactos preventivos, recordatorios o solicitudes de confirmación con supervisión humana, capacidad y efectos medidos. No se recomienda cancelar, penalizar ni alterar condiciones automáticamente por el score o por país. Una alerta no prueba intención de cancelar; un FN no demuestra ausencia de señales humanas. Las atribuciones ayudan a auditar la función, pero no acreditan qué acción evitaría una cancelación. Faltan costes y eficacia causal de intervenciones para establecer rentabilidad.

## 10. Ejecución, archivos y limitaciones

Nuevos: src/explainability.py, tests/test_explainability.py, notebooks/explicabilidad.ipynb, este informe, tablas explicabilidad_7_* (mapeo, gain, SHAP global/transformado, muestra/perfil/IDs, contribuciones locales, segmentos, bins, dependencias y scores) y explicabilidad_7_shap.npz con valores y base. Se generan seis figuras PNG. Modificados: README, requirements.txt (SHAP 0.54.1) y src/run_notebook.py. Las dependencias previas se conservan; SHAP usa wheels compatibles, sin compilar. La primera descarga sin acceso de red falló; la instalación autorizada sí terminó.

Se ejecuta el notebook completo con salidas, pruebas automatizadas y comprobaciones de scores/aditividad y huellas. La prueba de compatibilidad sintética usa CSR con ceros y reconstruye margen y probabilidad. Se verifican mapeo one-hot, suma agrupada, denominadores de segmentos con una clase, bins y selección reproducible de ejemplos. La ejecución de pruebas en sandbox encontró una restricción sobre el temporal de una prueba anterior; fuera del sandbox se superan. El registro final conserva tamaños, versiones, tiempos, errores numéricos y hashes de datos, particiones, informes, módulos y notebooks previos. No se guardan nombres ni datos personales de clientes; país agregado es una variable predictiva, no identificación individual. No se evalúa prueba.

Persisten: alta y disponibilidad aproximadas, cierre PMS no acreditado, predictores sin versiones iniciales verificadas, censura/selección por resultados registrados, duplicados conservados, relaciones entre variables y mezcla comercial no controladas. El EDA vio todo el archivo y la validación se ha reutilizado en fases anteriores. SHAP depende de la función y de su referencia/path-dependence; variables correlacionadas pueden repartirse atribución de forma no única y la agrupación de dummies no convierte las atribuciones en efectos originales causales. El ranking se calcula en una muestra de validación, no toda la demanda. Su composición puede cambiar en otro periodo. Aditividad correcta no valida disponibilidad de datos, causalidad, calibración ni producción.

## 11. Recomendación antes de evaluación final

Mantener XGBoost inicial como candidato provisional y logística como referencia, sin presentar explicabilidad como autorización de despliegue. Revisar primero los segmentos de una sola clase, el papel de calendario/antelación y la semántica de ceros dispersos; para contrastes adicionales se necesita un protocolo separado autorizado, no modificar retrospectivamente v2. Obtener evidencia de variables iniciales y seguimiento real. Diseñar calibración temporal independiente y política de contacto con costes/capacidad reales; congelar modelo, transformación, calibración y umbral antes de una evaluación final autorizada. Prueba permanece cerrada y sus resultados no se usan para ninguna de estas decisiones. Con los datos actuales, una evaluación final seguirá requiriendo declarar todas las limitaciones; para afirmar utilidad operacional se necesitaría validación prospectiva y evaluación de intervención.

**Fin exclusivo de fase 7. Se espera revisión y autorización del usuario.**
'''
    local=tables['contribuciones_locales'];parts=[]
    for case,g in local.groupby('caso',sort=False):
        parts.append(g.assign(abs=g.shap_log_odds.abs()).nlargest(5,'abs').drop(columns='abs'))
    error_columns=['dimension','grupo','n','canceladas','fp','fn','fpr','fnr','suficiente_descriptivo']
    stability_cols=['grupo','n','tasa_cancelacion','probabilidad_media','roc_auc','precision','recall','f1']
    profiles=tables['dependencia_perfil']
    profiles=profiles[profiles.variable.isin(['lead_time','country','customer_type','market_segment','hotel']) & profiles.n_muestra.ge(100)]
    replacements={
        'GAIN':table(tables['gain_originales']), 'SHAP_GLOBAL':table(tables['shap_global']),
        'SHAP_VERSION':f"Compatibilidad comprobada con SHAP {detail['shap_version']} y XGBoost {detail['xgboost_version']}, tanto en prueba sintética como en el modelo real.",
        'ADDITIVITY':f"Error máximo de reconstrucción del margen: {detail['max_error_aditividad_margen']:.8f}; de probabilidad: {detail['max_error_probabilidad']:.9f}. El cálculo SHAP tardó {detail['segundos_shap']:.3f} segundos en este equipo; no es un benchmark.",
        'PROFILES':table(profiles), 'CASES':table(tables['casos'].drop(columns='meta_row_id')),
        'LOCALS':table(pd.concat(parts)), 'ERRORS':table(segments[segments.dimension.isin(['hotel','antelacion_grupo','market_segment','distribution_channel'])][error_columns]),
        'ARRIVAL_AUDIT':table(segments[segments.dimension.eq('llegada_respecto_corte')][['grupo','n','canceladas','no_canceladas','tasa_cancelacion','roc_auc']]),
        'MONTHS':table(segments[segments.dimension.eq('mes_reserva_proxy')][stability_cols]),
        'ARRIVAL_MONTHS':table(segments[segments.dimension.eq('arrival_date_month')][stability_cols+['suficiente_descriptivo']]),
        'HOTEL_CAL':table(segments[segments.dimension.eq('hotel')][['grupo','n','probabilidad_media','tasa_cancelacion','brecha_calibracion','brier']]),
        'BINS':table(tables['calibracion_bins'])}
    for key in sorted(replacements,key=len,reverse=True):text=text.replace(key,replacements[key])
    (Path(root)/'reports/fase_7_explicabilidad.md').write_text(text,encoding='utf-8')
