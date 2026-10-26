# Plan previo — Fase 8

Se conserva protocolo v3, los 14 predictores y las dos configuraciones iniciales. Solo se reentrenan logística y XGBoost con entrenamiento v3; se contrastan sus probabilidades con fase 7.1. No se ejecuta run_v3 ni se regenera el manifiesto. No se cargan objetivos o predictores de prueba para ajustar, comparar o decidir.

Antes de calcular resultados de capacidad/calibración se fija una **capacidad ilustrativa del 20% por mes de llegada**, con sensibilidad descriptiva del 10% y 30%. No representa recursos reales del hotel ni maximiza una función económica. Usar meses mantiene la misma unidad de planificación entre los cuatro meses de validación y los seis de prueba, evitando concentrar una capacidad global de todo el semestre en un único mes.

Para cada mes: k=floor(q*n), sin superar el porcentaje. Orden descendente de score; empates EXACTOS resueltos por SHA256 del texto UTF-8 `42|ID` ascendente y, de persistir, ID numérico ascendente. Los IDs son únicos y no son predictores; el hash evita usar directamente el orden original del CSV como desempate. No se redondean scores ni se usa y para empates. Se aplicará el mismo porcentaje, unidad mensual y algoritmo al bloque reservado, sin escoger un corte nuevo por sus resultados.

Es una política retrospectiva por lote mensual completo: presupone disponer de los scores de todas sus reservas y no simula una cola en tiempo real o intervención al crear una reserva. La factibilidad de contactar antes de un resultado requeriría snapshots y un calendario operativo no acreditados. Las etiquetas no participan en la aplicación de la política. Alerta significa prioridad de seguimiento humano, no cancelación asegurada ni penalización automática.

Se comparan precision/recall/F1/FP/FN con volumen mensual igual para ambos modelos; se registran tasas y empates en los bordes. ROC-AUC/AP globales apoyan discriminación, pero no sustituyen el análisis a capacidad fija. Se consideran simplicidad, estabilidad mensual y Brier, sin calibrar en validación. Si la mejora a capacidad fija no compensa complejidad se favorece logística; no se selecciona XGBoost por defecto. No se buscará una capacidad distinta tras observar resultados.

Los umbrales 0,1–0,9 se analizan solo como diagnósticos separados, no como alternativas para sustituir esta capacidad por el mejor F1. No se atribuyen beneficios o costes monetarios. Una transformación estrictamente creciente del score mantiene el ranking; transformaciones no estrictas pueden generar empates y alterar la selección bajo el desempate congelado.

Se congelará un modelo, su pipeline ajustado exclusivamente con entrenamiento v3, especificación, política mensual al 20%, versiones y hashes antes de abrir prueba. No se reentrenará con validación ni se recalibrará para evaluación final sin cambiar expresamente la especificación. Prueba sigue cerrada; no se hacen predicciones sobre ella en esta fase.
