"""Verifica documentación añadida sin ejecutar código del proyecto o sus modelos."""
from pathlib import Path
import ast
from collections import Counter
import difflib
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]

def sha(path):
    # Comparar bytes tanto del original como de la edición comentada.
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ast_without_positions(text):
    # Las magias de IPython se conservan en la copia; solo se omiten al parsear.
    normalized='\n'.join('pass' if line.lstrip().startswith(('%','!')) else line for line in text.splitlines())
    return ast.dump(ast.parse(normalized),include_attributes=False)

def inserted_comments(original,commented,prefix):
    # El diff no debe borrar, sustituir o mover ninguna instrucción original.
    before=original.splitlines();after=commented.splitlines()
    added=0
    for operation,a,b,c,d in difflib.SequenceMatcher(a=before,b=after,autojunk=False).get_opcodes():
        if operation=='equal':continue
        assert operation=='insert',('Se han cambiado instrucciones',operation,a,b)
        assert all(line.lstrip().startswith(prefix) for line in after[c:d]),after[c:d]
        added+=d-c
    return added

def main():
    manifest=json.loads((ROOT/'codigo_comentado/verificacion_comentarios.json').read_text(encoding='utf-8'))
    totals=Counter();comments=0
    for row in manifest['archivos']:
        original=ROOT/row['original'];commented=ROOT/row['comentado']
        assert sha(original)==row['sha256_original'],original
        assert sha(commented)==row['sha256_comentado'],commented
        if original.suffix=='.ipynb':
            a=json.loads(original.read_text(encoding='utf-8'));b=json.loads(commented.read_text(encoding='utf-8'))
            assert len(a['cells'])==len(b['cells'])
            for left,right in zip(a['cells'],b['cells']):
                if left['cell_type']=='code':
                    before=''.join(left['source']);after=''.join(right['source'])
                    comments+=inserted_comments(before,after,'#')
                    assert ast_without_positions(before)==ast_without_positions(after)
                    # Solo source cambia: salidas, metadata y contador son los originales.
                    assert {k:v for k,v in left.items() if k!='source'}=={k:v for k,v in right.items() if k!='source'}
                else:assert left==right
            assert {k:v for k,v in a.items() if k!='cells'}=={k:v for k,v in b.items() if k!='cells'}
            totals['notebooks']+=1
        else:
            before=original.read_text(encoding='utf-8-sig');after=commented.read_text(encoding='utf-8-sig')
            comments+=inserted_comments(before,after,'#' if original.suffix=='.py' else '//')
            if original.suffix=='.py':
                assert ast_without_positions(before)==ast_without_positions(after)
                # Compilar en memoria comprueba sintaxis sin ejecutar ni generar .pyc.
                compile(after,str(commented),'exec')
                totals['python']+=1
            else:totals['javascript']+=1
    assert comments==manifest['comentarios_nuevos']
    assert len(manifest['archivos'])==44
    print(json.dumps({'archivos_verificados':44,'comentarios_nuevos':comments,**totals,'solo_comentarios_insertados':True,'instrucciones_y_salidas_identicas':True,'modelos_entrenados':0,'predicciones_recalculadas':0},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
