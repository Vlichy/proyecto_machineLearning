"""Compone gráficos y datos editoriales desde resultados guardados, sin modelos."""
from pathlib import Path
import hashlib,json,shutil
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from sklearn.metrics import roc_curve,precision_recall_curve

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'entrega_final';FIG=OUT/'figuras';FIG.mkdir(exist_ok=True)
read=lambda name:pd.read_csv(ROOT/'reports'/name,float_precision='round_trip')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
snapshot=OUT/'fuentes/integridad_previa.json'
if not snapshot.exists():
    paths=[p for folder in ['data','models','reports','src','notebooks','tests'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths.append(ROOT/'requirements.txt')
    snapshot.write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in paths},indent=2),encoding='utf-8')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#263746','text.color':'#142e43','axes.titlesize':14})
blue='#174a68';teal='#168880';orange='#d4883a'
def save(fig,name,source):
    fig.text(.02,.015,source,fontsize=8,color='#526674');fig.savefig(FIG/name,dpi=170,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4));vals=[75166,44224];ax.barh(['No cancela','Cancela'],vals,color=[blue,teal]);ax.set_xlabel('Registros');ax.set_title('Cancelaciones en el archivo completo, EDA')
for i,v in enumerate(vals):ax.text(v+1000,i,f'{v:,}'.replace(',','.')+f' ({v/119390:.2%})',va='center')
ax.set_xlim(0,100000);fig.tight_layout(rect=(0,.06,1,1));save(fig,'01_cancelaciones.png','Fuente: fase 2, 119.390 registros. Descripción global anterior a la selección v3.')
fig,axes=plt.subplots(1,2,figsize=(10,4))
for ax,labs,values,title in [(axes[0],['City','Resort'],[33102/79330,11122/40060],'Tasa por hotel'),(axes[1],['0 días','Más de 365 días'],[430/6345,2130/3148],'Antelaciones seleccionadas')]:
    ax.bar(labs,values,color=[blue,teal]);ax.set_ylim(0,.8);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_title(title)
    for i,v in enumerate(values):ax.text(i,v+.025,f'{v:.1%}',ha='center')
fig.suptitle('Asociaciones descriptivas del EDA completo',fontsize=16);fig.tight_layout(rect=(0,.07,1,.94));save(fig,'02_eda.png','Fuente: fase 2. Los grupos de antelación son subconjuntos seleccionados. Sin interpretación causal.')
hist=read('comparacion_5_metricas.csv');v3=read('seleccion_8_metricas.csv');names={'regresion_logistica':'Logística','arbol_decision':'Árbol','random_forest':'Random Forest','xgboost':'XGBoost','lightgbm':'LightGBM'}
fig,axes=plt.subplots(1,2,figsize=(11,4.5))
for ax,df,title in [(axes[0],hist,'Histórico v2, validación'),(axes[1],v3,'Definitivo v3, validación')]:
    x=list(range(len(df)));ax.bar([i-.17 for i in x],df.roc_auc,width=.34,label='ROC-AUC',color=blue);ax.bar([i+.17 for i in x],df.average_precision,width=.34,label='AP',color=teal);ax.set_xticks(x,[names[n] for n in df.modelo],rotation=20);ax.set_ylim(0,1);ax.set_title(title);ax.legend()
fig.tight_layout(rect=(0,.08,1,1));save(fig,'03_modelos.png','Fuente: fases 5 y 8. Poblaciones diferentes, métricas entre protocolos no directamente comparables.')
p=read('evaluacion_9_predicciones_congeladas.csv');y=read('evaluacion_9_etiquetas_prueba.csv');assert p.meta_row_id.equals(y.meta_row_id)
fpr,tpr,_=roc_curve(y.is_canceled,p.score);prec,rec,_=precision_recall_curve(y.is_canceled,p.score)
fig,axes=plt.subplots(1,2,figsize=(10,4.5));axes[0].plot(fpr,tpr,color=blue,label='Logística, AUC 0,7802');axes[0].plot([0,1],[0,1],'--',color='gray');axes[0].set(xlabel='Tasa de falsos positivos',ylabel='Recall',title='ROC, prueba v3');axes[0].legend(loc='lower right');axes[1].plot(rec,prec,color=teal,label='Logística, AP 0,7416');axes[1].axhline(y.is_canceled.mean(),ls='--',color='gray',label='Prevalencia 40,01%');axes[1].set(xlabel='Recall',ylabel='Precision',title='Precision-recall, prueba v3');axes[1].legend(loc='lower left')
fig.tight_layout(rect=(0,.08,1,1));save(fig,'04_curvas.png','Fuente: scores y etiquetas congelados de fase 9. Sin nueva inferencia ni selección de política.')
for src,dst in [('evaluacion_9_matriz_calibracion.png','05_matriz_calibracion.png'),('evaluacion_9_mensual.png','06_mensual.png')]:shutil.copyfile(ROOT/'reports/figures'/src,FIG/dst)
h=read('evaluacion_9_hoteles.csv');fig,ax=plt.subplots(figsize=(8,4));x=[0,1];ax.bar([i-.18 for i in x],h.precision,.36,label='Precision',color=blue);ax.bar([i+.18 for i in x],h.recall,.36,label='Recall',color=teal);ax.set_xticks(x,h.hotel);ax.set_ylim(0,1);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_title('Política conjunta del 20%, prueba v3');ax.legend()
for i,row in h.iterrows():ax.text(i,.05,f'{row.porcentaje_priorizado:.2f}% priorizado',ha='center',color='white',fontsize=10)
fig.tight_layout(rect=(0,.08,1,1));save(fig,'07_hoteles.png','Fuente: evaluacion_9_hoteles.csv. La cuota mensual se comparte entre ambos hoteles.')
nb_audit=[]
for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
    nb=json.loads(path.read_text(encoding='utf-8'));cells=[c for c in nb['cells'] if c['cell_type']=='code'];errors=sum(o.get('output_type')=='error' for c in cells for o in c.get('outputs',[]))
    nb_audit.append({'notebook':str(path.relative_to(ROOT)),'celdas_codigo':len(cells),'ejecutadas_guardadas':sum(c.get('execution_count') is not None for c in cells),'errores_guardados':errors,'reejecutado_fase10':False})
(OUT/'fuentes/notebooks_revision.json').write_text(json.dumps(nb_audit,indent=2,ensure_ascii=False),encoding='utf-8')
data={'historico_v2':hist.to_dict('records'),'validacion_v3':v3.to_dict('records'),'capacidades':read('seleccion_8_capacidades.csv').to_dict('records'),'mensual':read('evaluacion_9_mensual.csv').to_dict('records'),'hoteles':h.to_dict('records'),'calibracion':read('seleccion_8_calibracion.csv').to_dict('records')}
(OUT/'fuentes/datos_presentacion.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for path,expected in json.loads(snapshot.read_text()).items():assert sha(ROOT/path)==expected,path
print('Siete figuras y tablas editoriales. Archivos anteriores intactos. No se carga ni ejecuta el modelo.')
