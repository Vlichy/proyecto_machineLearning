"""Integra comentarios y Markdown sin ejecutar los experimentos del proyecto.

La copia previa se escribe y verifica antes de tocar los archivos principales.
Las huellas de ejecuciones históricas no se sustituyen: el nuevo registro une
la versión ejecutada con la versión documentada mediante equivalencia de AST.
"""
from pathlib import Path
import ast
import hashlib
import json
import shutil

from comentar_proyecto import MODULES, NOTEBOOKS

ROOT=Path(__file__).resolve().parents[1]
BACKUP=ROOT/'reports/historico/documentacion_pre_integracion'
REGISTRY=ROOT/'reports/documentacion_integrada_registro.json'

CONTEXT={
    'eda': 'Este análisis describe todo el archivo antes de fijar la prueba definitiva. Las diferencias por hotel, antelación o segmento son asociaciones, no efectos causales. No se eliminan registros ni se ajusta un modelo. La exposición global de los datos se declara como una limitación de la evaluación posterior.',
    'preparacion': 'La preparación conserva las 119.390 filas. Se separan 14 predictores de is_canceled y de los metadatos de auditoría. Los transformadores se construyen sin ajustar: imputación, categorías y escala deben aprenderse solo con entrenamiento. La propuesta temporal de esta fase es histórica y fue sustituida por v3.',
    'baseline': 'Este notebook conserva el baseline histórico v1. La regresión logística sirve como referencia sencilla frente al clasificador mayoritario. Su población y métricas no son las de la evaluación final. Los componentes del pipeline aprenden de train y se aplican a validación sin reajuste.',
    'protocolo_temporal': 'Este experimento pertenece al protocolo histórico v2. La llegada menos lead_time aproxima la creación y la fecha de estado más un día aproxima disponibilidad; ninguna es una marca operativa acreditada. Seleccionar por desenlace disponible introdujo sesgo, corregido después mediante cohortes completas de llegada en v3.',
    'comparacion_modelos': 'La comparación de logística, árbol, Random Forest, XGBoost y LightGBM corresponde a validación v2. Compartir particiones y predictores hace comparable ese experimento interno, pero no lo convierte en una comparación directa con v3. Las métricas globales de scores y las decisiones a 0,5 responden preguntas distintas.',
    'optimizacion': 'La búsqueda pertenece a v2 y utiliza ventanas temporales internas de entrenamiento. Cada subentrenamiento aprende su propio preprocesamiento para evitar información de su validación. AP interna decide la configuración. La evaluación externa no mejoró y no se trasladaron hiperparámetros optimizados a la decisión definitiva v3.',
    'explicabilidad': 'SHAP explica XGBoost inicial en una muestra de validación v2. Las contribuciones en log-odds describen el modelo y esa población; no implican causalidad ni explican la regresión logística final. Al agrupar dummies se suman contribuciones con signo por fila antes de resumir magnitudes.',
    'correccion_sesgo_temporal': 'V3 define cohortes por llegada con embargo: train julio 2015-junio 2016, validación septiembre-diciembre 2016 y prueba marzo-agosto 2017. La asignación no depende de la etiqueta ni del estado final. El seguimiento se audita para bloques completos. El diseño sigue siendo retrospectivo y parte de prueba tuvo exposición previa.',
    'seleccion_final': 'La elección utiliza solo train y validación v3. Se comparan logística y XGBoost iniciales, sin nuevas búsquedas. A la capacidad mensual hipotética del 20%, logística detectó 32 cancelaciones más con el mismo volumen de prioridades y menor complejidad. Es una ventaja pequeña y descriptiva. La decisión se cerró antes de prueba.',
    'evaluacion_final': 'La evaluación de prueba v3 ya se realizó una sola vez. Los scores y las decisiones se congelaron antes de consultar las etiquetas. La política reúne ambos hoteles por mes y aplica floor(0,20 × n_mes), con desempates SHA256 e ID. Los resultados guardados se conservan: estos añadidos documentales no representan una nueva ejecución ni permiten cambiar la decisión.',
}

DETAILS={
    'preparacion': {
        5: 'La mediana, el vocabulario del encoder y el escalado todavía no se calculan con todas las reservas. Los ausentes siguen siendo desconocidos hasta el ajuste exclusivo en train.',
        7: 'La lista cerrada de entradas impide incorporar automáticamente fechas, identificadores o estados finales. Las comprobaciones de recarga buscan pérdidas de filas o cambios de tipos.',
    },
    'baseline': {
        3: 'Accuracy puede ser alta si se predice siempre no cancelación. Precision, recall y F1 permiten examinar la clase positiva; ROC-AUC utiliza scores, no la etiqueta decidida a 0,5.',
    },
    'optimizacion': {
        1: 'Elegir parámetros con la validación externa o prueba confundiría selección con evaluación. Las ventanas internas respetan el tiempo y repiten la imputación y codificación dentro de cada fold.',
    },
    'seleccion_final': {
        1: 'Comparar igual número de alertas mide priorización a capacidad limitada. Un umbral fijo puede alertar volúmenes distintos y no ofrece esa misma comparación.',
        2: 'Brier mide error cuadrático de scores. Un ranking útil no garantiza probabilidades calibradas. No se entrena un calibrador para evaluarlo sobre las mismas observaciones.',
        3: 'La cuota es conjunta, por lo que City y Resort pueden recibir porcentajes diferentes. Se requiere el lote mensual completo y el 20% es un supuesto académico, no una capacidad real acreditada.',
    },
    'evaluacion_final': {
        0: 'Las comprobaciones históricas SHA-256 identifican los bytes ejecutados. Tras esta revisión, la correspondencia del código documentado se verifica con herramientas/auditar_documentacion_integrada.py y el respaldo anterior; no se deben sobrescribir recibos para hacer coincidir los nuevos comentarios.',
        1: 'Precision = TP/(TP+FP), recall = TP/(TP+FN) y F1 es su media armónica. ROC-AUC y AP describen la ordenación global; Brier y el score medio permiten estudiar calibración. El cupo del 20% no equivale a un umbral fijo de probabilidad.',
        2: 'El redondeo se realiza mes a mes. Las diferencias por hotel o calendario no acreditan causalidad y no justifican cambiar la política después de observar prueba.',
        3: 'Los intervalos remuestrean bloques de días conservando scores y prioridades originales. Son descriptivos: no garantizan independencia, cobertura del 95% o rendimiento prospectivo.',
        4: 'Las salidas que aparecen debajo proceden de la ejecución guardada. Esta revisión solo inspecciona estructura y conservación de salidas; no vuelve a lanzar la batería ni el notebook.',
    },
}

OMIT=(
    '# EDICIÓN COMENTADA', '# Solo se añaden comentarios:',
    '# Guardar esta tabla como evidencia reproducible',
    '# Persistir documentación o metadatos para revisar',
    '# Hacer explícito este invariante:',
    '# Comprobar tamaños esperados para detectar',
    '# Leer las columnas y filas solicitadas;',
    '# Crear una figura descriptiva;',
)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def syntax(text):
    # El texto real conserva las magias de IPython; se omiten solo al parsear.
    text='\n'.join('pass' if line.lstrip().startswith(('%','!')) else line for line in text.splitlines())
    return ast.dump(ast.parse(text),include_attributes=False)

def integrate_code(original,reference):
    """Reutiliza solo comentarios explicativos, conservando instrucciones y BOM."""
    before=original.read_text(encoding='utf-8-sig')
    after=reference.read_text(encoding='utf-8-sig')
    # El generador anterior insertó estos comentarios; si ya existían en el
    # original se mantienen. Así no se borran explicaciones históricas útiles.
    original_lines=set(before.splitlines())
    kept=[]
    for line in after.splitlines(keepends=True):
        if line not in original_lines and line.rstrip('\r\n') not in original_lines:
            if line.lstrip().startswith(OMIT):continue
            if line.startswith('// EDICIÓN COMENTADA'):continue
        kept.append(line)
    after=''.join(kept)
    if original.suffix=='.py':assert syntax(before)==syntax(after),original
    return after

def write_preserving_bom(path,text):
    bom=b'\xef\xbb\xbf' if path.read_bytes().startswith(b'\xef\xbb\xbf') else b''
    path.write_bytes(bom+text.encode('utf-8'))

def main():
    # Bloquear una segunda aplicación evita que el respaldo deje de representar
    # exactamente la versión previa a esta integración.
    if BACKUP.exists() or REGISTRY.exists():raise SystemExit('Existe respaldo/registro: revisar antes de repetir integración.')
    reference=json.loads((ROOT/'codigo_comentado/verificacion_comentarios.json').read_text(encoding='utf-8'))
    candidates=[row['original'] for row in reference['archivos']]
    administrative=['README.md','entrega_final/README.md','entrega_final/manifest_entrega.json']
    protected={}
    for folder in ['src','tests','notebooks','data','models','reports','entrega_final','codigo_comentado','herramientas']:
        for path in (ROOT/folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                protected[path.relative_to(ROOT).as_posix()]=sha(path)
    protected['requirements.txt']=sha(ROOT/'requirements.txt')
    for relative in candidates+administrative:
        destination=BACKUP/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/relative,destination)
        assert sha(destination)==sha(ROOT/relative),relative
    pre={'archivos_previos_sha256':protected,'respaldados':{relative:sha(BACKUP/relative) for relative in candidates+administrative}}
    (BACKUP/'registro_previo.json').write_text(json.dumps(pre,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    # A partir de aquí ya existe y está verificado todo el respaldo.
    records=[]
    for row in reference['archivos']:
        path=ROOT/row['original'];source=ROOT/row['comentado']
        assert sha(path)==row['sha256_original'],path
        assert sha(source)==row['sha256_comentado'],source
        if path.suffix=='.ipynb':
            before=json.loads(path.read_text(encoding='utf-8'));annotated=json.loads(source.read_text(encoding='utf-8'))
            nb=json.loads(path.read_text(encoding='utf-8'));cells=[];index=0
            for i,cell in enumerate(nb['cells']):
                if cell['cell_type']=='code':
                    code=''.join(annotated['cells'][i]['source'])
                    original_code=''.join(cell['source']);original_lines=set(original_code.splitlines())
                    code=''.join(line for line in code.splitlines(keepends=True) if not (line.rstrip('\r\n') not in original_lines and line.lstrip().startswith(OMIT)))
                    assert syntax(original_code)==syntax(code)
                    explanation=NOTEBOOKS[path.stem][index]
                    extra=DETAILS.get(path.stem,{}).get(index,'')
                    introduction=(f'### Contexto metodológico\n\n{CONTEXT[path.stem]}\n\n' if index==0 else '')
                    markdown=introduction+f'**Qué se hace y por qué.** {explanation}\n\n'+(extra+'\n\n' if extra else '')
                    cells.append({'cell_type':'markdown','id':f'doc-integrada-{path.stem[:20]}-{index:02d}','metadata':{'revision_documental':'integracion_comentarios'},'source':markdown.splitlines(keepends=True)})
                    cell['source']=code.splitlines(keepends=True);index+=1
                cells.append(cell)
            nb['cells']=cells
            path.write_text(json.dumps(nb,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
            original_code=[c for c in before['cells'] if c['cell_type']=='code'];current_code=[c for c in nb['cells'] if c['cell_type']=='code']
            assert len(original_code)==len(current_code)
            for a,b in zip(original_code,current_code):
                assert syntax(''.join(a['source']))==syntax(''.join(b['source']))
                assert {k:v for k,v in a.items() if k!='source'}=={k:v for k,v in b.items() if k!='source'}
            records.append({'archivo':row['original'],'tipo':'notebook','celdas_markdown_agregadas':index,'codigo_AST_identico':True,'salidas_y_contadores_identicos':True})
        else:
            text=integrate_code(path,source);write_preserving_bom(path,text)
            records.append({'archivo':row['original'],'tipo':'python' if path.suffix=='.py' else 'javascript','codigo_AST_identico':path.suffix=='.py','solo_comentarios':True})
    registry={'revision':'documentacion_integrada_v1','respaldo':BACKUP.relative_to(ROOT).as_posix(),'registro_previo_sha256':sha(BACKUP/'registro_previo.json'),'diferencias_funcionales':False,'experimentos_ejecutados':False,'modelo_y_resultados_modificados':False,'archivos_codigo':records,'archivos_administrativos_autorizados':administrative}
    for row in records:
        row['sha256_antes']=pre['archivos_previos_sha256'][row['archivo']]
        row['sha256_despues']=sha(ROOT/row['archivo'])
        row['sha256_respaldo']=sha(BACKUP/row['archivo'])
    REGISTRY.write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'archivos_codigo_integrados':len(records),'notebooks':sum(r['tipo']=='notebook' for r in records),'markdown_agregado':sum(r.get('celdas_markdown_agregadas',0) for r in records),'respaldo':str(BACKUP),'AST_identico':True,'salidas_conservadas':True},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
