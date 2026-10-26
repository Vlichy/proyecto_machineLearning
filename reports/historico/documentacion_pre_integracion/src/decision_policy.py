"""Priorización mensual determinista: no acepta etiquetas ni aprende umbrales."""
import hashlib
import numpy as np
import pandas as pd


def monthly_priority(scores, row_ids, arrival_months, capacity_pct=20, seed=42):
    """Top floor(n*q/100) por mes; empate score exacto -> hash -> ID."""
    if isinstance(capacity_pct,bool) or not isinstance(capacity_pct,(int,np.integer)) or not 0<=capacity_pct<=100:
        raise ValueError('Capacidad debe ser un entero entre 0 y 100')
    p=np.asarray(scores,dtype='float64');ids=np.asarray(row_ids);months=np.asarray(arrival_months)
    if p.ndim!=1 or ids.ndim!=1 or months.ndim!=1 or not len(p)==len(ids)==len(months):
        raise ValueError('Entradas deben ser vectores alineados')
    if not np.isfinite(p).all() or ((p<0)|(p>1)).any():raise ValueError('Scores deben ser finitos y estar en [0,1]')
    if len(ids) and (not pd.api.types.is_integer_dtype(ids.dtype) or pd.Series(ids).duplicated().any() or (ids<0).any()):
        raise ValueError('IDs técnicos deben ser enteros no negativos y únicos')
    if pd.isna(months).any():raise ValueError('Mes desconocido')
    if len(months):
        dates=pd.to_datetime(months.astype(str),format='%Y-%m',errors='raise')
        if not np.array_equal(dates.strftime('%Y-%m'),months.astype(str)):raise ValueError('Usar meses YYYY-MM')
    data=pd.DataFrame({'meta_row_id':ids,'mes_llegada':months,'score':p})
    data['desempate_sha256']=[hashlib.sha256(f'{seed}|{int(i)}'.encode('utf-8')).hexdigest() for i in ids]
    data['alerta']=False;data['puesto_mensual']=0
    rows=[]
    for month,g in data.groupby('mes_llegada',sort=True,observed=True):
        ordered=g.sort_values(['score','desempate_sha256','meta_row_id'],ascending=[False,True,True],kind='stable')
        n=len(g);k=n*int(capacity_pct)//100
        data.loc[ordered.index,'puesto_mensual']=np.arange(1,n+1)
        data.loc[ordered.index[:k],'alerta']=True
        cutoff=float(ordered.score.iloc[k-1]) if k else None
        rows.append({'mes_llegada':month,'n':n,'k':k,'capacidad_pct':int(capacity_pct),
            'porcentaje_alertado':100*k/n,'score_min_alertado':cutoff,
            'score_max_no_alertado':float(ordered.score.iloc[k]) if k<n else None,
            'empate_total_en_corte':int(g.score.eq(cutoff).sum()) if k else 0,
            'empate_alertado_en_corte':int(ordered.iloc[:k].score.eq(cutoff).sum()) if k else 0})
    return data,pd.DataFrame(rows)


def apply_frozen_policy(specification, scores, row_ids, arrival_months):
    policy=specification['politica']
    if policy['tipo']!='top_capacidad_mensual' or policy['version_algoritmo']!=1:
        raise ValueError('Política no compatible')
    if policy['fraccion_redondeo']!='floor' or policy['clave_grupo']!='mes_llegada_YYYY-MM':
        raise ValueError('Cambian agrupación o redondeo congelados')
    if policy['desempate']!='score_desc_sha256(seed|ID)_asc_ID_asc_sin_redondear_score':
        raise ValueError('Desempate no compatible')
    return monthly_priority(scores,row_ids,arrival_months,policy['capacidad_pct'],policy['seed_desempate'])
