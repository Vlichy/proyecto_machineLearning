"""Genera una edición didáctica sin alterar las fuentes selladas de los experimentos.

Los comentarios se insertan en posiciones de sentencias obtenidas con AST.
No se ejecuta el código documentado. La equivalencia se comprueba ignorando
comentarios y posiciones, pero conservando todas las instrucciones y literales.
"""
from pathlib import Path
import ast
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'codigo_comentado'

MODULES = {
    'inspection': 'Inspección inicial: dimensiones, tipos, ausentes y repeticiones del CSV.',
    'cleaning': 'Limpieza determinista: tipar y señalar anomalías, conservando las reservas.',
    'features': 'Separación explícita entre predictores, objetivo futuro y metadatos de auditoría.',
    'preprocessing': 'Construcción de transformadores nuevos: sus parámetros se aprenden únicamente en train.',
    'preparation': 'Preparación de las 119.390 filas sin entrenar transformadores o modelos.',
    'splitting': 'Reglas temporales: v3 es el protocolo vigente; v1 y v2 se conservan como historia.',
    'baseline': 'Baseline histórico y fábrica de logística reutilizada por los experimentos posteriores.',
    'audit_baseline': 'Auditoría histórica del baseline: selección temporal, umbrales y calibración descriptiva.',
    'temporal_protocol': 'Protocolo histórico v2: usa proxies de alta y disponibilidad del resultado.',
    'comparison': 'Comparación histórica de cinco clasificadores y auditoría del ajuste de sus pipelines.',
    'optimization': 'Optimización histórica v2: búsqueda dentro de train y reproducción de resultados congelados.',
    'explainability': 'Explicabilidad histórica: SHAP describe XGBoost v2, no la logística definitiva.',
    'temporal_bias_v3': 'Corrección a cohortes completas por llegada con embargo y seguimiento común por bloque.',
    'decision_policy': 'Política definitiva: cuota mensual conjunta y desempates independientes de la etiqueta.',
    'final_selection': 'Selección en validación v3: modelo y capacidad se cierran antes de utilizar prueba.',
    'final_evaluation': 'Evaluación final: scores congelados antes de leer objetivos y una sola inferencia.',
    'evaluation_narrative': 'Interpretación de resultados guardados, sin cargar ni ejecutar el modelo.',
    'run_notebook': 'Ejecución controlada de notebooks y protección contra sobrescrituras históricas.',
    '__init__': 'Marca el directorio src como paquete importable por los notebooks.',
    'preparar_entrega': 'Construcción editorial de figuras desde resultados guardados, sin nueva inferencia.',
    'exportar_pdf': 'Maquetación de la memoria Markdown mediante estilos, tablas e imágenes de ReportLab.',
    'auditar_entrega': 'Auditoría de solo lectura: hashes, cifras, notebooks y estructura de entregables.',
}

FUNCTIONS = {
    'sha': 'Calcular SHA-256 de los bytes para detectar cualquier cambio en el archivo.',
    'model_factories': 'Definir las configuraciones iniciales sin escoger parámetros con validación o prueba.',
    'tree_pipeline': 'Crear un pipeline nuevo para árboles, con imputación y codificación sin escalado.',
    'fit_one': 'Ajustar solo con entrenamiento y comprobar que validación no modifica el preprocesamiento.',
    'run_comparison': 'Comparar las configuraciones v2 sobre la misma validación histórica y guardar evidencia.',
    'run_audit': 'Examinar sesgos, errores y scores del baseline histórico sin decidir una nueva política.',
    'run_optimization': 'Usar checkpoints si existen; la búsqueda original se limita al entrenamiento v2.',
    'search_one': 'Evaluar candidatos con folds temporales internos y seleccionar por AP media.',
    'scorer': 'Auditar el subentrenamiento de cada fold antes de medir AP y ROC-AUC de su validación.',
    'run_explainability': 'Reconstruir el XGBoost histórico y explicar una muestra de validación v2.',
    'group_contributions': 'Sumar contribuciones con signo por variable original antes de resumir magnitudes.',
    'calibration_bins': 'Comparar score medio y frecuencia observada por banda, sin ajustar un calibrador.',
    'run_v3': 'Asignar cohortes por llegada, auditar seguimiento y comparar solo los dos modelos iniciales.',
    'verify_history': 'Comprobar que las copias históricas v1 y v2 conservan sus huellas originales.',
    'metrics_for': 'Calcular métricas diagnósticas a 0,5, distinguiéndolas de la política mensual posterior.',
    'load_v3': 'Leer train y validación v3 sin incorporar etiquetas de prueba a selección.',
    'decision_metrics': 'Contar aciertos y errores de una decisión binaria sobre una población determinada.',
    'run_selection': 'Comparar candidatos en validación v3 y congelar la decisión antes de prueba.',
    'apply_frozen_policy': 'Validar el contrato de la política y aplicar la capacidad y desempates ya fijados.',
    'utc_now': 'Registrar el instante UTC para demostrar el orden de las operaciones de evaluación.',
    'require': 'Detener la evaluación si una condición contradice la especificación congelada.',
    'verify_partitions': 'Contrastar IDs y roles contra v3 y comprobar integridad y ausencia de solapamientos.',
    'learned_fingerprint': 'Resumir el estado aprendido para comprobar que la inferencia no lo modifica.',
    'forbidden': 'Bloquear explícitamente cualquier intento de ajuste durante la inferencia final.',
    'preflight': 'Verificar hashes, versiones, modelo, entradas y política antes de consultar objetivos.',
    'measure': 'Separar métricas de la política binaria de las métricas globales calculadas con scores.',
    'uncertainty': 'Resumir remuestreo de bloques de días con decisiones originales fijas.',
    'run_evaluation': 'Reproducir el checkpoint completo o realizar la inferencia autorizada y congelarla antes de leer y.',
    'add_narrative': 'Añadir la interpretación de las cifras ya guardadas sin volver a evaluar el modelo.',
    'json_write': 'Serializar resultados con tipos compatibles con JSON y una salida legible.',
    'normalize': 'Convertir escalares y estructuras al formato serializable sin cambiar el cálculo del modelo.',
    'records': 'Convertir tablas a registros JSON, incluyendo el caso de una partición vacía.',
    'write_json': 'Guardar metadatos y resultados con formato consistente para su auditoría.',
    'run_protocol': 'Ejecutar el baseline bajo el protocolo histórico v2 y exportar sus verificaciones.',
    'run_preparation': 'Verificar el original, exportar la preparación y contrastar su lectura posterior.',
    'make_figures': 'Representar las tablas de esta fase sin usar el gráfico para ajustar el modelo.',
    'figures': 'Dibujar los resultados de la comparación sobre la validación correspondiente.',
    'write_report': 'Redactar tablas, metodología y limitaciones desde resultados calculados o guardados.',
    'write_baseline_report': 'Crear el informe del baseline desde sus métricas, sin otro entrenamiento.',
    'markdown': 'Formatear una tabla como Markdown para incluirla en el informe.',
    '_markdown_table': 'Formatear una tabla de auditoría respetando sus columnas y valores.',
    'table': 'Preparar una tabla legible para la documentación de esta fase.',
    'save': 'Exportar la figura con un nombre estable y cerrar sus recursos gráficos.',
    'inline': 'Escapar texto y aplicar el formato admitido por el generador de PDF.',
    'page': 'Dibujar el pie y número de página sin invadir el contenido de la memoria.',
}

NOTEBOOKS = {
    'eda': [
        'Preparar rutas y bibliotecas y leer el CSV conservando una huella del original.',
        'Crear auxiliares descriptivos de fechas, huéspedes y agrupación sin alterar el CSV.',
        'Cuantificar ausencias globales y por hotel para estudiar su distribución.',
        'Distinguir repeticiones adicionales de todas las filas que participan en un grupo repetido.',
        'Describir el objetivo y las diferencias entre hoteles mediante conteos y tasas.',
        'Representar antelación y tarifa por resultado; los patrones son asociaciones.',
        'Comparar depósito, canal, segmento y cliente sin convertir la asociación en causalidad.',
        'Examinar historial y solicitudes; su disponibilidad histórica todavía debe auditarse.',
        'Agrupar duración y huéspedes para describir cancelaciones y casos anómalos.',
        'Resumir volúmenes y tasas por mes de llegada, diferenciando calendario y fecha de reserva.',
        'Examinar correlaciones como descripción, sin seleccionar predictores automáticamente.',
        'Documentar qué campos revelan resultados y cuáles tienen disponibilidad incierta.',
        'Redactar hallazgos a partir de las tablas reales del EDA.',
        'Comprobar conservación de filas, contenido, CSV y archivos de referencia.',
    ],
    'preparacion': [
        'Cargar datos, reglas y dependencias y registrar huellas antes de preparar.',
        'Comparar el efecto hipotético de deduplicar; la decisión aplicada conserva todas las filas.',
        'Aplicar tipos y explicar ausencias sin aprender medianas de todo el archivo.',
        'Cuantificar anomalías y conservarlas con sus metadatos de auditoría.',
        'Justificar inclusiones y exclusiones por disponibilidad, no por puntuación predictiva.',
        'Construir los 14 predictores y demostrar que el preprocesador sigue sin ajustar.',
        'Mostrar la propuesta temporal original de fase 3, previa al protocolo definitivo v3.',
        'Exportar preparación y verificar la separación entre X, y y metadatos.',
        'Comprobar las reglas de preparación y la conservación de los archivos de origen.',
    ],
    'baseline': [
        'Preparar datos y revisar el protocolo histórico v1 y sus particiones.',
        'Inspeccionar tamaños, clases y cobertura anual antes de ajustar el baseline.',
        'Mostrar la logística inicial y sus parámetros prefijados, sin optimización.',
        'Ajustar el baseline histórico en train y medirlo en validación frente al trivial.',
        'Representar matrices de confusión y discriminación de aquella validación.',
        'Ejecutar las verificaciones históricas y contrastar la integridad del original.',
    ],
    'protocolo_temporal': [
        'Construir el protocolo histórico v2 y registrar sus reglas antes del baseline.',
        'Examinar población, reincorporaciones y exclusiones bajo sus proxies temporales.',
        'Ajustar y evaluar el baseline de aquella fase histórica, separado del resultado final v3.',
        'Comprobar resultados y archivos protegidos de la ejecución histórica.',
    ],
    'comparacion_modelos': [
        'Resolver rutas e importar la comparación de modelos del protocolo histórico v2.',
        'Comparar cinco configuraciones iniciales sobre la misma validación v2.',
        'Mostrar ROC, precision-recall y matrices de aquella población.',
        'Verificar la comparación histórica y la ausencia de cambios en archivos protegidos.',
    ],
    'optimizacion': [
        'Preparar rutas y localizar los checkpoints del experimento de optimización v2.',
        'Mostrar folds y selección interna; si existe checkpoint se reproduce sin buscar otra vez.',
        'Comparar métricas externas y calibración descriptiva de las configuraciones históricas.',
        'Examinar umbrales e inestabilidad sin fijar una decisión con datos de prueba.',
        'Verificar el experimento y las huellas de los datos e informes anteriores.',
    ],
    'explicabilidad': [
        'Cargar el análisis histórico de XGBoost v2 y su muestra de validación.',
        'Mostrar importancia y SHAP agrupado; no son explicaciones de la logística final.',
        'Explicar casos TP, TN, FP y FN sin atribuir efectos causales.',
        'Describir errores por hotel, antelación y mes de la población analizada.',
        'Comparar scores y frecuencias observadas sin ajustar un calibrador.',
        'Contrastar reconstrucción, pruebas y conservación de los resultados históricos.',
    ],
    'correccion_sesgo_temporal': [
        'Aplicar el protocolo v3 por llegada y cargar sus auditorías y resultados de desarrollo.',
        'Mostrar cómo la selección v2 dependía de la disponibilidad del desenlace.',
        'Revisar cohortes completas, embargos, seguimiento y exposición previa de prueba.',
        'Comparar logística y XGBoost iniciales en validación v3, sin usar prueba.',
        'Revisar segmentos y condiciones que acreditan el alcance de la corrección.',
        'Verificar invariantes de v3 y que los históricos siguen intactos.',
    ],
    'seleccion_final': [
        'Cargar la comparación de los dos candidatos y la especificación congelada de fase 8.',
        'Contrastar umbrales y capacidad igual, distinguiendo ranking y clasificación fija.',
        'Describir calibración sin ajustar y evaluar un calibrador sobre las mismas filas.',
        'Mostrar la única política seleccionada y sus resultados por mes y hotel en validación.',
        'Verificar las decisiones y los artefactos protegidos de la selección.',
    ],
    'evaluacion_final': [
        'Verificar y reproducir la evaluación congelada; un recibo completo evita repetir inferencia.',
        'Separar las métricas de la política mensual de las métricas globales de scores.',
        'Comprobar cupos exactos por mes y describir diferencias por hotel y composición.',
        'Mostrar incertidumbre por bloques y seguimiento proxy sin retirar filas.',
        'Comprobar política y evaluación con pruebas que no entrenan modelos.',
    ],
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def parseable(text):
    # La única magia utilizada es una configuración gráfica de IPython.
    # Se omite solo para comparar sintaxis; la celda comentada conserva la magia.
    return '\n'.join('pass' if line.lstrip().startswith(('%','!')) else line for line in text.splitlines())

def syntax(text):
    return ast.dump(ast.parse(parseable(text)), include_attributes=False)

def purpose(node, module):
    if node.name in FUNCTIONS:
        return FUNCTIONS[node.name]
    if node.name.startswith('test_'):
        labels = {
            'ties': 'comprobar que los empates se resuelven igual aunque cambie el orden de entrada',
            'floor': 'comprobar el redondeo inferior por mes, incluyendo cupos extremos y entradas vacías',
            'strictly': 'comprobar que una transformación estrictamente creciente conserva prioridades',
            'frozen': 'comprobar que se aplica la especificación congelada y se rechazan contratos incompatibles',
            'duplicate': 'comprobar el tratamiento o rechazo de duplicados según el contrato de esta función',
            'leak': 'comprobar que la etiqueta y los campos excluidos no se utilizan como predictores',
            'fit': 'comprobar las restricciones del ajuste y la conservación de parámetros aprendidos',
            'metric': 'contrastar las métricas con los recuentos esperados de aciertos y errores',
            'block': 'comprobar que el remuestreo respeta bloques temporales y es reproducible',
            'hash': 'contrastar la integridad de los archivos con sus huellas de referencia',
            'split': 'comprobar límites, alineación y separación de las particiones temporales',
            'unknown': 'comprobar el comportamiento ante categorías no observadas en entrenamiento',
        }
        for fragment, explanation in labels.items():
            if fragment in node.name:
                return 'Prueba: ' + explanation + '.'
        return 'Prueba del contrato ' + node.name[5:].replace('_',' ') + ': datos controlados y resultado esperado.'
    doc = ast.get_docstring(node)
    if doc:
        return doc.split('\n')[0]
    if node.name in ['setUp','setUpClass']:
        return 'Preparar datos controlados y recursos compartidos de las pruebas de esta clase.'
    if node.name in ['tearDown','tearDownClass']:
        return 'Liberar los recursos temporales creados por las pruebas.'
    if node.name=='main':
        return MODULES.get(module,'Coordinar la entrada de este script y sus comprobaciones.')
    return 'Auxiliar de ' + MODULES.get(module,module).rstrip('.') + '.'

def block_comment(node, segment, module):
    """Explica operaciones con consecuencias metodológicas o de trazabilidad."""
    if isinstance(node,(ast.Import,ast.ImportFrom)):
        return None
    if isinstance(node,ast.Assert):
        if 'sha' in segment or 'hash' in segment or 'checksum' in segment:
            return 'La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.'
        if 'len(' in segment or 'shape' in segment:
            return 'Comprobar tamaños esperados para detectar pérdidas de filas o desalineación.'
        return 'Hacer explícito este invariante: si falla, no se deben interpretar los resultados como válidos.'
    if isinstance(node,ast.Return):
        return None
    checks = [
        ('.fit_transform(', 'Aprender esta transformación únicamente con los datos de entrenamiento de esta llamada.'),
        ('search.fit(', 'Ejecutar la búsqueda histórica con sus folds internos; la prueba queda fuera de selección.'),
        ('.fit(', 'Aprender los parámetros con el entrenamiento recibido; validación se reserva para medir rendimiento.'),
        ('predict_proba(', 'Obtener scores con el pipeline ajustado, sin aprender parámetros de estas filas.'),
        ('joblib.load(', 'Recuperar el artefacto ya entrenado; cargarlo no autoriza refit ni recalibración.'),
        ('joblib.dump(', 'Persistir el pipeline seleccionado con su preprocesamiento para evitar reconstrucciones ambiguas.'),
        ('OneHotEncoder(', 'Codificar las categorías de train e ignorar las nuevas sin aprenderlas de validación o prueba.'),
        ('SimpleImputer(', 'Definir la imputación; la creación del objeto todavía no calcula estadísticas del dataset.'),
        ('StandardScaler(', 'Definir el escalado numérico de la logística; media y escala se aprenderán al ajustar.'),
        ('ColumnTransformer(', 'Aplicar transformaciones por lista cerrada de variables y excluir el resto de columnas.'),
        ('sort_values([\'score\'', 'Ordenar por riesgo y desempates exactos; ninguna etiqueta participa en esta prioridad.'),
        ('n*int(capacity_pct)//100', 'Calcular el cupo con división entera dentro de cada mes, evitando exceder la capacidad.'),
        ("data['desempate_sha256']", 'Construir el desempate reproducible con semilla e ID técnico, independiente del resultado.'),
        ('temporal_split_v3(', 'Asignar cohortes por llegada sin seleccionar filas según su desenlace individual.'),
        ('audit_followup_v3(', 'Auditar el seguimiento de cohortes completas; si falla una fila no se rescatan las demás.'),
        ('pd.read_csv(', 'Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.'),
        ('confusion_matrix(', 'Contar TN, FP, FN y TP con orden de clases explícito para evitar invertir su interpretación.'),
        ('roc_auc_score(', 'Medir la capacidad de ordenar scores; esta métrica no fija la política de alertas.'),
        ('precision_recall_curve(', 'Describir precision y recall desde scores existentes, sin elegir otra decisión con prueba.'),
        ('brier_score_loss(', 'Medir el error cuadrático de los scores y distinguirlo de la precisión de las alertas.'),
        ('TreeExplainer(', 'Explicar este modelo de árboles y su población; las contribuciones no se trasladan a logística.'),
        ('.to_csv(', 'Guardar esta tabla como evidencia reproducible de la población y fase indicadas.'),
        ('.write_text(', 'Persistir documentación o metadatos para revisar las decisiones sin volver a ejecutar el modelo.'),
        ('hashlib.', 'Calcular una huella determinista para trazabilidad; no usarla como característica predictiva.'),
        ('warnings.catch_warnings(', 'Registrar advertencias del ajuste para no ocultar convergencia u otros problemas numéricos.'),
        ('unittest.TextTestRunner(', 'Ejecutar la batería indicada y conservar su salida; comprobar qué pruebas admite esta fase.'),
        ('discover(', 'Seleccionar las pruebas de esta llamada; los conjuntos históricos pueden incluir entrenamientos.'),
        ('groupby(', 'Resumir la misma población por grupos y conservar sus denominadores antes de comparar tasas.'),
        ('plt.subplots(', 'Crear una figura descriptiva; sus ejes y títulos deben identificar población y versión del protocolo.'),
    ]
    # En sentencias compuestas se comenta el control, y sus instrucciones internas
    # se documentan por separado para no atribuir al bloque una operación parcial.
    if isinstance(node,(ast.If,ast.For,ast.With,ast.Try)):
        if isinstance(node,ast.If):
            condition=ast.unparse(node.test)
            if '__name__' in condition:return 'Ejecutar la entrada principal solo al invocar este archivo como script.'
            if 'exists' in condition:return 'Distinguir resultados ya guardados de una ejecución pendiente antes de continuar.'
        return None
    for needle,explanation in checks:
        if needle in segment:return explanation
    return None

def annotate(text,module,header):
    tree=ast.parse(parseable(text));lines=text.splitlines(keepends=True);insertions={}
    def add(line,comment):
        indent=re.match(r'\s*',lines[line-1]).group(0)
        # Un salto aislado no debe incorporarse a la sangría del comentario.
        indent=indent.rstrip('\r\n')
        insertions.setdefault(line,[])
        if comment not in insertions[line]:insertions[line].append(comment)
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            line=min([node.lineno]+[d.lineno for d in node.decorator_list])
            explanation=purpose(node,module)
            if explanation != (ast.get_docstring(node) or '').split('\n')[0]:
                add(line,explanation)
        elif isinstance(node,ast.ClassDef):
            add(node.lineno,'Agrupar las comprobaciones relacionadas para verificar el contrato de esta parte del proyecto.')
        elif isinstance(node,ast.stmt):
            segment=ast.get_source_segment(parseable(text),node) or ''
            explanation=block_comment(node,segment,module)
            # Evitar insertar dentro de una línea que ya contiene la cabecera
            # de una función, un if o un bucle de una sola línea.
            if explanation and node.col_offset==len(lines[node.lineno-1])-len(lines[node.lineno-1].lstrip(' ')):
                add(node.lineno,explanation)
    details={
        'cleaning': {
            'data = df.copy(deep=True)': 'Trabajar sobre una copia mantiene intactos los valores originales para poder auditarlos.',
            'counts = [': 'Los conteos usan enteros anulables: un valor desconocido no equivale a cero.',
        },
        'features': {
            'NUMERIC_FEATURES =': 'Cerrar las entradas admitidas impide que una columna nueva o un estado final entre por accidente en X.',
            'data["total_nights"]': 'Sumar noches previstas sin usar el desenlace; esta derivación no aprende parámetros.',
            'features = data.loc': 'Extraer exclusivamente los predictores autorizados, en un orden reproducible.',
            'label_after =': 'Esta cota pertenece a la preparación histórica: no sustituye al protocolo v3 vigente por llegada.',
        },
        'preprocessing': {
            'return ColumnTransformer': 'Seleccionar por nombre y descartar el resto mantiene la etiqueta y los metadatos fuera del modelo.',
        },
        'comparison': {
            'np.testing.assert_allclose(numeric': 'Contrastar las medianas aprendidas con train permite detectar un ajuste accidental sobre otras filas.',
            'for actual, column in zip': 'Comprobar que cada vocabulario del encoder procede solo de las categorías de entrenamiento.',
            'before = hashlib': 'Capturar el estado del preprocesador antes de validación para demostrar que transformarlo no lo reentrena.',
            'after = hashlib': 'Repetir la huella después de predecir: debe coincidir exactamente con la anterior.',
        },
        'decision_policy': {
            'p=np.asarray(scores': 'Normalizar tipos y comprobar alineación; cada score debe corresponder a su ID y mes.',
            'n=len(g);k=': 'Redondear hacia abajo dentro de este mes; no se calcula el 20% sobre el total de varios meses.',
            "data.loc[ordered.index,'puesto_mensual']": 'Guardar el puesto de todas las reservas facilita auditar tanto alertas como no alertas.',
            "data.loc[ordered.index[:k],'alerta']": 'Marcar exactamente las primeras k filas del ranking de ambos hoteles juntos.',
            'cutoff=float': 'Guardar el score límite solo para auditoría; no convertirlo en un umbral fijo para otro mes.',
        },
        'final_evaluation': {
            "if receipt['estado']=='completada'": 'Un recibo completo activa lectura de resultados: esta rama no vuelve a predecir prueba.',
            "receipt.update(estado='predicciones_congeladas'": 'Confirmar scores y decisiones antes de abrir las etiquetas evita cambiar la política según sus aciertos.',
            "receipt.setdefault('timestamp_primer_acceso_etiquetas_utc'": 'Registrar la primera consulta de y después de la congelación permite verificar el orden temporal.',
            'tn,fp,fn,tp=confusion_matrix': 'Mantener clases [0,1]: TN y FP pertenecen a no cancelaciones; FN y TP a cancelaciones.',
        },
        'optimization': {
            'order = sorted': 'Seleccionar por AP interna y usar ROC-AUC solo para desempatar, sin consultar prueba.',
        },
    }
    for i,line in enumerate(lines,1):
        for prefix,explanation in details.get(module,{}).items():
            if line.lstrip().startswith(prefix):add(i,explanation)
    output=['# EDICIÓN COMENTADA PARA LECTURA. Las fuentes ejecutadas y selladas permanecen en la raíz.\n',f'# {header}\n','# Solo se añaden comentarios: no se han ejecutado instrucciones de esta copia.\n']
    count=3
    for i,line in enumerate(lines,1):
        indent=re.match(r'[ \t]*',line).group(0)
        for explanation in insertions.get(i,[]):
            output.append(indent+'# '+explanation+'\n');count+=1
        output.append(line)
    result=''.join(output)
    assert syntax(text)==syntax(result),module
    return result,count

def main():
    DEST.mkdir(exist_ok=True)
    records=[]
    sources=[*sorted((ROOT/'src').glob('*.py')),*sorted((ROOT/'tests').glob('*.py')),*sorted((ROOT/'entrega_final/fuentes').glob('*.py'))]
    for source in sources:
        relative=source.relative_to(ROOT);destination=DEST/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        module=source.stem;header=MODULES.get(module,'Pruebas de '+module.removeprefix('test_').replace('_',' ')+'.')
        text=source.read_text(encoding='utf-8-sig');commented,n=annotate(text,module,header)
        destination.write_text(commented,encoding='utf-8',newline='\n')
        records.append({'original':relative.as_posix(),'comentado':destination.relative_to(ROOT).as_posix(),'sha256_original':sha(source),'sha256_comentado':sha(destination),'comentarios_nuevos':n,'AST_identico':True})
    for source in sorted((ROOT/'notebooks').glob('*.ipynb')):
        nb=json.loads(source.read_text(encoding='utf-8'));original=json.loads(source.read_text(encoding='utf-8'));step=0;count=0
        explanations=NOTEBOOKS[source.stem]
        for i,cell in enumerate(nb['cells']):
            if cell['cell_type']!='code':continue
            code=''.join(cell['source']);commented,n=annotate(code,source.stem,explanations[step]);step+=1
            cell['source']=commented.splitlines(keepends=True);count+=n
            assert cell.get('outputs')==original['cells'][i].get('outputs')
            assert cell.get('execution_count')==original['cells'][i].get('execution_count')
        assert step==len(explanations),source
        destination=DEST/'notebooks'/source.name;destination.parent.mkdir(exist_ok=True)
        destination.write_text(json.dumps(nb,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
        records.append({'original':source.relative_to(ROOT).as_posix(),'comentado':destination.relative_to(ROOT).as_posix(),'sha256_original':sha(source),'sha256_comentado':sha(destination),'comentarios_nuevos':count,'AST_celdas_identico':True,'salidas_originales_conservadas':True,'ejecutado':False})
    # JavaScript editorial: se insertan comentarios completos entre líneas.
    # El comprobador independiente contrasta tokens y sintaxis de estos archivos.
    for source in sorted((ROOT/'entrega_final/fuentes').glob('*.mjs')):
        header={'crear_presentacion':'Crear las 15 diapositivas, notas y objetos editables desde tablas guardadas.', 'renderizar_presentacion':'Importar el PowerPoint final y exportar vistas para revisión visual sin modificarlo.'}[source.stem]
        comments={'const RUNTIME':'Localizar las bibliotecas editoriales separadas del entorno de modelado.', 'const ROOT':'Resolver el proyecto y las rutas de salida para la construcción editorial.', 'const presentation':'Crear un lienzo de 16:9 para todas las diapositivas.', 'function text':'Añadir texto editable con posición y tipografía explícitas.', 'function slide':'Crear una diapositiva y registrar sus notas y fuentes.', 'function body':'Distribuir las ideas con espacio suficiente para lectura durante la exposición.', 'function table':'Construir tablas nativas editables, conservando cifras y encabezados.', 'function chart':'Crear gráficos nativos desde valores guardados; el redondeo es solo de representación.', 'let s=slide':'Iniciar portada e identificar el alcance retrospectivo y la autoría pendiente.', 's=slide':'Desarrollar la siguiente diapositiva con cifras y limitaciones de la fase indicada.', 'await fs.writeFile':'Exportar las notas para poder preparar la exposición sin abrir PowerPoint.', 'for(let i':'Renderizar todas las diapositivas para revisar legibilidad y distribución.', 'const candidate':'Exportar un borrador separado antes de validar el archivo final.', 'const result':'Validar estructura, fuentes, tablas y gráficos antes de entregar el PowerPoint.', 'const p=await':'Cargar únicamente el archivo de presentación final para su inspección.'}
        text=source.read_text(encoding='utf-8-sig');output=['// EDICIÓN COMENTADA PARA LECTURA. No modifica la fuente editorial original.\n','// '+header+'\n'];count=2
        for line in text.splitlines(keepends=True):
            for needle,explanation in comments.items():
                if line.startswith(needle):output.append('// '+explanation+'\n');count+=1;break
            output.append(line)
        destination=DEST/source.relative_to(ROOT);destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(''.join(output),encoding='utf-8')
        records.append({'original':source.relative_to(ROOT).as_posix(),'comentado':destination.relative_to(ROOT).as_posix(),'sha256_original':sha(source),'sha256_comentado':sha(destination),'comentarios_nuevos':count,'solo_insercion_comentarios_linea':True})
    manifest={'alcance':'Edición didáctica separada de las fuentes congeladas; sin ejecución ni cambios funcionales.','archivos':records,'n_archivos':len(records),'comentarios_nuevos':sum(r['comentarios_nuevos'] for r in records)}
    (DEST/'verificacion_comentarios.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='archivos'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
