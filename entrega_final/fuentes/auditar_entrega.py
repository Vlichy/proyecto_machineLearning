# Auditoría de solo lectura: hashes, cifras, notebooks y estructura de entregables.
"""Auditoría editorial y de integridad, sin entrenar, predecir o ejecutar notebooks."""
from pathlib import Path
import csv,hashlib,json,math,re,zipfile
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'entrega_final'
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
# Calcular una huella determinista para trazabilidad; no usarla como característica predictiva.
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Auditoría de solo lectura: hashes, cifras, notebooks y estructura de entregables.
def main():
    previous=load(OUT/'fuentes/integridad_previa.json')
    for path,h in previous.items():assert sha(ROOT/path)==h,('Cambio en archivo anterior',path)
    reference=load(ROOT/'reports/verificacion_referencias.json')['antes']
    for path,h in reference.items():assert sha(Path(path))==h,('Referencia del curso modificada',path)
    receipt=load(ROOT/'reports/evaluacion_9_recibo.json')
    assert receipt['estado']=='completada' and receipt['llamadas_predict_proba']==1
    assert receipt['reentrenamientos']==receipt['recalibraciones']==0
    for path,h in receipt['archivos_resultados_sha256'].items():assert sha(ROOT/path)==h,path
    # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
    assert sha(ROOT/'reports/seleccion_8_especificacion_congelada.json')==receipt['especificacion_sha256']
    # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
    assert sha(ROOT/'models/seleccion_8_modelo_congelado.joblib')==receipt['modelo_sha256']
    # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
    assert sha(ROOT/'reports/particiones_temporales.csv')==receipt['manifiesto_sha256']
    metrics=load(ROOT/'reports/evaluacion_9_metricas.json');p=metrics['politica'];g=metrics['modelo_global']
    for k,v in {'n':32829,'priorizadas':6564,'tp':5340,'fp':1224,'fn':7796,'tn':18469}.items():assert p[k]==v,k
    assert p['matriz_confusion']==[[18469,1224],[7796,5340]]
    assert g['canceladas']==13136
    for k,v in {'precision':5340/6564,'recall':5340/13136,'f1':10680/19700}.items():assert math.isclose(p[k],v,abs_tol=1e-12)
    for k,v in {'roc_auc':.7801860434187309,'average_precision':.7416008556912017,'brier':.1853395244762256}.items():assert math.isclose(g[k],v,abs_tol=1e-12)
    monthly=list(csv.DictReader((ROOT/'reports/evaluacion_9_mensual.csv').open(encoding='utf-8')))
    assert len(monthly)==6
    for row in monthly:assert int(row['priorizadas'])==int(row['n'])*20//100
    for k in ['n','priorizadas','tp','fp','fn','tn']:assert sum(int(row[k]) for row in monthly)==p[k]
    notebooks=[]
    for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
        nb=load(path);code=[c for c in nb['cells'] if c['cell_type']=='code']
        assert all(c.get('execution_count') is not None for c in code),path
        assert not any(o.get('output_type')=='error' for c in code for o in c.get('outputs',[])),path
        notebooks.append({'archivo':str(path.relative_to(ROOT)),'celdas_ejecutadas_guardadas':len(code),'errores':0,'ejecutado_fase10':False})
    ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
    ppt=OUT/'presentacion_final.pptx'
    with zipfile.ZipFile(ppt) as z:
        assert z.testzip() is None
        slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
        notes=[n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
        charts=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/charts/chart\d+\.xml',n)]
        books=[n for n in z.namelist() if n.endswith('.xlsx')]
        assert len(slides)==len(notes)==15 and len(charts)==len(books)==3
        for note in notes:assert len(' '.join(ET.fromstring(z.read(note)).itertext()))>80
        text=' '.join(' '.join(ET.fromstring(z.read(n)).itertext()) for n in slides)
        for expected in ['81,35%','40,65%','0,5421','0,7802 / 0,7416','0,18534','5.340','6.564']:assert expected in text,expected
        for number in [4,7,10,12]:assert ET.fromstring(z.read(f'ppt/slides/slide{number}.xml')).find('.//a:tbl',ns) is not None
    # ReportLab escribe los diccionarios de página sin comprimir.
    pdf_pages=len(re.findall(rb'/Type\s*/Page\b',(OUT/'memoria_final.pdf').read_bytes()));assert pdf_pages==15,pdf_pages
    for path in [ROOT/'README.md',*OUT.glob('*.md')]:
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8-sig')):
            if not target.startswith(('http:','https:','#')):
                resolved=path.parent/target
                if resolved not in [OUT/'manifest_entrega.json',OUT/'verificacion_entrega.json']:
                    assert resolved.exists(),(str(path),target)
    assert len(list((OUT/'figuras').glob('*.png')))==7
    memo=(OUT/'memoria_final.md').read_text(encoding='utf-8')
    for expected in ['32.829','13.136','6.564','5.340','1.224','7.796','18.469','81,35%','40,65%','0,5421','0,7802','0,7416','0,18534']:assert expected in memo,expected
    finalization=load(ROOT/'tmp/fase10/validacion_presentacion.json') if (ROOT/'tmp/fase10/validacion_presentacion.json').exists() else None
    if finalization:
        # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
        assert finalization['finalSha256']==sha(ppt)
        assert finalization['packageIntegrity']['finding_count']==finalization['presentationLayout']['finding_count']==0
        assert finalization['firstPartyImport']['passed']
    manifest={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ['manifest_entrega.json','verificacion_entrega.json'] and '__pycache__' not in p.parts}
    (OUT/'manifest_entrega.json').write_text(json.dumps({'formato':'SHA-256','excluye':['manifest_entrega.json','verificacion_entrega.json'],'archivos':manifest},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    verification={'estado':'verificado','fase':10,'archivos_anteriores_intactos':len(previous),'referencias_curso_intactas':len(reference),'modelo_y_especificacion_sin_cambios':True,'particiones_v3_sin_cambios':True,'predicciones_y_metricas_fase9_sin_cambios':True,'llamadas_predict_proba_registradas_total':1,'entrenamientos_fase10':0,'inferencias_fase10':0,'paginas_pdf':pdf_pages,'diapositivas':15,'notas_incorporadas':15,'graficos_editables':3,'tablas_editables':4,'figuras_memoria':7,'notebooks':notebooks,'notebooks_reejecutados':0,'exportacion_pptx_validada':finalization is not None,'revision_visual':{'paginas_pdf':15,'diapositivas_finales':15},'apertura_en_PowerPoint_no_realizada':True,'archivos_entrega':len(manifest),'enunciado_oficial_localizado':False,'autoria_academica_confirmada':False}
    (OUT/'verificacion_entrega.json').write_text(json.dumps(verification,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    assert (OUT/'manifest_entrega.json').exists() and (OUT/'verificacion_entrega.json').exists()
    print(json.dumps({k:v for k,v in verification.items() if k!='notebooks'},ensure_ascii=False,indent=2))
# Ejecutar la entrada principal solo al invocar este archivo como script.
if __name__=='__main__':main()
