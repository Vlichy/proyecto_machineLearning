# Interpretación de resultados guardados, sin cargar ni ejecutar el modelo.
"""Lectura de resultados ya congelados. No importa ni ejecuta el modelo."""
from pathlib import Path
import json


# Añadir la interpretación de las cifras ya guardadas sin volver a evaluar el modelo.
def add_narrative(root):
    root=Path(root);out=root/'reports'
    result=json.loads((out/'evaluacion_9_metricas.json').read_text(encoding='utf-8'))
    receipt=json.loads((out/'evaluacion_9_recibo.json').read_text(encoding='utf-8'))
    if receipt['estado']!='completada' or receipt['llamadas_predict_proba']!=1:
        raise ValueError('Interpretar solo resultados congelados completos')
    path=out/'fase_9_evaluacion_final.md'
    text=path.read_text(encoding='utf-8')
    marker='<!-- lectura_resultados_fase9 -->'
    if marker in text:return
    p=result['politica'];g=result['modelo_global']
    summary=(f"**Resultado final:** {p['priorizadas']} prioridades de {p['n']} reservas, "
             f"precision {p['precision']:.2%}, recall {p['recall']:.2%}, F1 {p['f1']:.4f}, "
             f"ROC-AUC {g['roc_auc']:.4f} y AP {g['average_precision']:.4f}. "
             "El rendimiento es inferior al de validación; modelo y política permanecen sin cambios.\n\n")
    text=text.replace('## 1. Verificaciones',summary+'## 1. Verificaciones',1)
    narrative='''<!-- lectura_resultados_fase9 -->
## 4.1. Lectura de los resultados observados, sin reajustes

La precision de seguimiento baja de 85,60% a 81,35% (−4,25 puntos porcentuales), y recall de 45,01% a 40,65% (−4,35 puntos). F1 baja de 0,58996 a 0,54213; ROC-AUC de 0,79459 a 0,78019 y AP de 0,76216 a 0,74160. Brier empeora de 0,17238 a 0,18534. Los indicadores muestran deterioro descriptivo fuera de la validación seleccionada; no se modifica nada para compensarlo.

La prevalencia aumenta de 38,02% a 40,01% (+1,99 puntos). La caída de precision/AP no se explica simplemente por haber menos positivos: hay mayor proporción de cancelaciones, pero también distinta capacidad de ordenación y composición. No se realiza una descomposición causal. La media predicha es 35,21%, unos 4,81 puntos por debajo de la observada; la selección top-k no requiere calibración para ordenar, pero sus scores no deben tratarse como frecuencias fiables. No se ajusta un calibrador con prueba.

Por meses, los volúmenes son de 4925 a 6313 filas: no se trata de fluctuaciones en grupos de unas pocas reservas, pero las observaciones siguen pudiendo estar relacionadas. La precision alcanza 93,90% en mayo, baja a 68,17% en julio y 58,68% en agosto; recall pasa de 47,79% en marzo a 31,83% en agosto. ROC-AUC es 0,833 en abril y cae a 0,674 en agosto. No hay deterioro monótono desde marzo: los últimos meses son especialmente difíciles y coinciden con otra temporada. No se separa el efecto temporal de cambios comerciales o de selección de datos con este diseño.

La mezcla de hoteles cambia poco: City representa 68,76% en validación y 68,66% en prueba. Por tanto, ese reparto agregado por sí solo no explica el deterioro. Sí cambia el mercado: Online TA pasa de 49,48% a 56,45% y Offline TA/TO de 21,03% a 15,26%; Transient sube de 79,69% a 83,30% y Transient-Party baja de 19,19% a 14,29%. La mediana de antelación pasa de 66 a 103 días, mientras su percentil 90 baja de 313 a 264: no es un desplazamiento uniforme de toda la distribución. Son posibles factores asociados, no causas demostradas del cambio.

City recibe 5349 prioridades (23,73% de sus reservas), con precision 82,99% y recall 45,88%. Resort recibe 1215 (11,81%), con precision 74,16% y recall 26,04%. La cuota es conjunta; esta diferencia no es un fallo de cálculo ni se corrige repartiendo alertas después de ver etiquetas. La infrapredicción media es mayor en Resort (8,56 puntos, frente a 3,09 en City). Cualquier política distinta por hotel requeriría otro estudio autorizado, nunca reajustar esta evaluación final.

Los percentiles de remuestreo para precision son aproximadamente 75,47%–88,76%; para recall, 37,24%–43,62%; para AUC, 0,7478–0,8102. Son intervalos descriptivos condicionados a decisiones originales y bloques escogidos, no una garantía de rendimiento futuro ni una prueba formal de diferencia con validación. No cubren incertidumbre de selección/entrenamiento ni sesgos del protocolo.

'''
    text=text.replace('## 5. Meses de prueba',narrative+'## 5. Meses de prueba',1)
    path.write_text(text,encoding='utf-8')
