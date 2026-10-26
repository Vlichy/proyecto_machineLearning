"""Audita una revisión documental sin importar ni ejecutar modelos o notebooks.

Los hashes históricos se contrastan con el respaldo de los bytes ejecutados.
Las fuentes actuales deben coincidir con el registro documental y conservar
las mismas instrucciones. Datos, modelos y resultados siguen exigiendo SHA
exacto: la equivalencia estructural no se aplica a esos artefactos.
"""
from pathlib import Path
from collections import Counter
import ast
import difflib
import hashlib
import io
import json
import tokenize

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'reports/documentacion_integrada_registro.json'

def sha(path):
    # Hash de los bytes reales; nunca se normaliza un archivo para fingir que
    # conserva una huella anterior después de añadir documentación.
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def ast_text(text):
    # IPython añade sintaxis propia. Para el AST se sustituye cada línea mágica
    # por pass, y la comparación de tokens de debajo comprueba la línea real.
    plain='\n'.join('pass' if line.lstrip().startswith(('%','!')) else line for line in text.splitlines())
    tree=ast.parse(plain)
    compile(tree,'<comprobacion_estatica>','exec')
    return ast.dump(tree,include_attributes=False)

def tokens(text):
    # Se ignoran comentarios y separadores no significativos, conservando
    # literales, operadores, nombres, indentaciones y las magias de IPython.
    ignored={tokenize.COMMENT,tokenize.NL,tokenize.ENCODING}
    return [(t.type,t.string) for t in tokenize.generate_tokens(io.StringIO(text).readline) if t.type not in ignored]

def inserted_comments(before,after,prefix):
    count=0
    # Ninguna línea de código original puede borrarse, cambiarse o moverse.
    for operation,a,b,c,d in difflib.SequenceMatcher(a=before.splitlines(),b=after.splitlines(),autojunk=False).get_opcodes():
        if operation=='equal':continue
        assert operation=='insert',('Diff distinto de comentarios añadidos',operation,a,b)
        added=after.splitlines()[c:d]
        assert all(line.lstrip().startswith(prefix) for line in added),added
        count+=len(added)
    return count

def source_equivalent(before,after):
    count=inserted_comments(before,after,'#')
    assert ast_text(before)==ast_text(after),'AST diferente'
    assert tokens(before)==tokens(after),'Tokens ejecutables diferentes'
    return count

def main():
    registry=read_json(REGISTRY);backup=ROOT/registry['respaldo']
    assert sha(backup/'registro_previo.json')==registry['registro_previo_sha256']
    previous=read_json(backup/'registro_previo.json')
    counts=Counter();comments=0;markdown=0;code_cells=0
    for row in registry['archivos_codigo']:
        old=backup/row['archivo'];current=ROOT/row['archivo']
        assert sha(old)==row['sha256_antes']==row['sha256_respaldo'],old
        assert sha(current)==row['sha256_despues'],current
        if row['tipo']=='notebook':
            a=read_json(old);b=read_json(current)
            assert {k:v for k,v in a.items() if k!='cells'}=={k:v for k,v in b.items() if k!='cells'}
            new_markdown=[c for c in b['cells'] if c.get('metadata',{}).get('revision_documental')=='integracion_comentarios']
            # Eliminar únicamente las celdas documentales nuevas permite alinear
            # de nuevo todas las celdas originales, incluidas sus identificaciones.
            retained=[c for c in b['cells'] if c not in new_markdown]
            assert len(retained)==len(a['cells'])
            assert len(new_markdown)==row['celdas_markdown_agregadas']
            assert all(c['cell_type']=='markdown' for c in new_markdown)
            for left,right in zip(a['cells'],retained):
                if left['cell_type']=='code':
                    comments+=source_equivalent(''.join(left['source']),''.join(right['source']))
                    assert {k:v for k,v in left.items() if k!='source'}=={k:v for k,v in right.items() if k!='source'}
                    code_cells+=1
                else:assert left==right
            ids=[c['id'] for c in b['cells'] if 'id' in c];assert len(ids)==len(set(ids))
            markdown+=len(new_markdown)
        else:
            before=old.read_text(encoding='utf-8-sig');after=current.read_text(encoding='utf-8-sig')
            if row['tipo']=='python':comments+=source_equivalent(before,after)
            else:comments+=inserted_comments(before,after,'//')
        counts[row['tipo']]+=1
    allowed={row['archivo'] for row in registry['archivos_codigo']}|set(registry['archivos_administrativos_autorizados'])
    unchanged=0
    for path,expected in previous['archivos_previos_sha256'].items():
        if path not in allowed:
            assert sha(ROOT/path)==expected,('Archivo fuera de la revisión modificado',path)
            unchanged+=1
    for path,expected in previous['respaldados'].items():assert sha(backup/path)==expected,path
    for row in registry.get('archivos_administrativos',[]):
        assert sha(backup/row['archivo'])==row['sha256_antes']
        assert sha(ROOT/row['archivo'])==row['sha256_despues']
    for path,expected in registry.get('evidencias_documentales_sha256',{}).items():
        assert sha(ROOT/path)==expected,('Evidencia documental modificada',path)
    # Los recibos históricos conservan sus hashes de origen. Solo se acepta
    # una fuente nueva si está respaldada y su AST/tokens coinciden con esa fuente.
    spec=read_json(ROOT/'reports/seleccion_8_especificacion_congelada.json')
    receipt=read_json(ROOT/'reports/evaluacion_9_recibo.json')
    preflight=read_json(ROOT/'reports/evaluacion_9_preflight.json')
    def verify_historical(path,expected):
        current=ROOT/path
        if sha(current)==expected:return
        match=[r for r in registry['archivos_codigo'] if Path(r['archivo'])==Path(path)]
        assert len(match)==1 and sha(backup/path)==expected,('Huella histórica sin respaldo válido',path)
        if current.suffix=='.py':source_equivalent((backup/path).read_text(encoding='utf-8-sig'),current.read_text(encoding='utf-8-sig'))
        else:assert current.suffix=='.ipynb','Equivalencia documental no admitida para artefactos'
    for path,expected in spec['huellas_entradas'].items():verify_historical(path,expected)
    for path,expected in preflight['codigo_sha256'].items():verify_historical(path,expected)
    for path,expected in receipt['archivos_resultados_sha256'].items():assert sha(ROOT/path)==expected,path
    assert sha(backup/'src/final_evaluation.py')==receipt['codigo_inferencia_sha256']
    assert sha(ROOT/'reports/seleccion_8_especificacion_congelada.json')==receipt['especificacion_sha256']
    assert sha(ROOT/spec['artefacto_modelo'])==spec['artefacto_sha256']==receipt['modelo_sha256']
    assert sha(ROOT/'reports/particiones_temporales.csv')==receipt['manifiesto_sha256']
    assert receipt['llamadas_predict_proba']==1 and receipt['reentrenamientos']==receipt['recalibraciones']==0
    metrics=read_json(ROOT/'reports/evaluacion_9_metricas.json')
    assert {key:metrics['politica'][key] for key in ['n','priorizadas','tp','fp','fn','tn']}=={'n':32829,'priorizadas':6564,'tp':5340,'fp':1224,'fn':7796,'tn':18469}
    for path,expected in read_json(ROOT/'reports/verificacion_referencias.json')['antes'].items():assert sha(Path(path))==expected,path
    manifest=read_json(ROOT/'entrega_final/manifest_entrega.json')
    for path,expected in manifest['archivos'].items():assert sha(ROOT/'entrega_final'/path)==expected,path
    report={'estado':'verificado','revision':registry['revision'],'archivos_codigo_modificados':len(registry['archivos_codigo']),'tipos':dict(counts),'archivos_administrativos_modificados':len(registry.get('archivos_administrativos',[])),'total_archivos_existentes_modificados':len(registry['archivos_codigo'])+len(registry.get('archivos_administrativos',[])),'comentarios_nuevos':comments,'celdas_markdown_nuevas':markdown,'celdas_codigo_AST_y_tokens_identicos':code_cells,'salidas_contadores_metadatos_y_celdas_previas_conservados':True,'python_AST_y_tokens_identicos':counts['python'],'javascript_solo_insercion_comentarios':counts['javascript'],'archivos_previos_fuera_de_revision_intactos':unchanged,'respaldo_verificado':True,'especificacion_modelo_particiones_datos_scores_y_metricas_intactos':True,'diferencias_funcionales_en_codigo':False,'notebooks_ejecutados':0,'modelos_entrenados':0,'predicciones_prueba_recalculadas':0,'inferencias_totales_registradas_fase9':1,'recibos_historicos_intactos':True,'auditoria_vigente':'herramientas/auditar_documentacion_integrada.py','auditorias_SHA_historicas':'Comparar fuentes de la ejecución contra respaldo; no sustituir hashes de origen por los actuales.'}
    (ROOT/'reports/documentacion_integrada_verificacion.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
