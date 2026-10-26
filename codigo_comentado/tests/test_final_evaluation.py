# EDICIÓN COMENTADA PARA LECTURA. Las fuentes ejecutadas y selladas permanecen en la raíz.
# Pruebas de final evaluation.
# Solo se añaden comentarios: no se han ejecutado instrucciones de esta copia.
"""Verificación final sin entrenar ningún algoritmo y sin inferencia real repetida."""
from pathlib import Path
import unittest
from unittest.mock import patch
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from src.final_evaluation import measure,moving_day_indices,uncertainty,predict_without_fit,verify_partitions
from src.decision_policy import apply_frozen_policy


# Agrupar las comprobaciones relacionadas para verificar el contrato de esta parte del proyecto.
class FinalEvaluationTests(unittest.TestCase):
    # Prueba: contrastar las métricas con los recuentos esperados de aciertos y errores.
    def test_matrix_and_metrics_reconcile(self):
        policy,global_metrics=measure([0,0,1,1],[.1,.9,.2,.8],[False,True,False,True])
        self.assertEqual(policy['matriz_confusion'],[[1,1],[1,1]])
        self.assertEqual(policy['precision'],.5);self.assertEqual(policy['recall'],.5)
        self.assertEqual(policy['f1'],.5);self.assertEqual(policy['priorizadas'],2)
        self.assertAlmostEqual(global_metrics['brier'],(.01+.81+.64+.04)/4)
        self.assertAlmostEqual(global_metrics['probabilidad_media'],.5)

    # Prueba del contrato actual manifest integrity without targets: datos controlados y resultado esperado.
    def test_actual_manifest_integrity_without_targets(self):
        root=Path(__file__).resolve().parents[1]
        # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
        manifest=pd.read_csv(root/'reports/particiones_temporales.csv')
        # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
        metadata=pd.read_csv(root/'data/processed/hotel_bookings_prepared.csv',usecols=['meta_row_id','meta_arrival_date','meta_duplicate_group'])
        verified=verify_partitions(manifest,metadata)
        self.assertEqual(int(verified.eq('prueba_reservada').sum()),32829)
        broken=manifest.copy();broken.loc[0,'particion']='prueba_reservada'
        with self.assertRaises(ValueError):verify_partitions(broken,metadata)

    # Prueba: comprobar que el remuestreo respeta bloques temporales y es reproducible.
    def test_predict_guard_blocks_training(self):
        # Agrupar las comprobaciones relacionadas para verificar el contrato de esta parte del proyecto.
        class BadEstimator:
            # Auxiliar de test_final_evaluation.
            def predict_proba(self,x):
                # Aprender los parámetros con el entrenamiento recibido; validación se reserva para medir rendimiento.
                LogisticRegression().fit([[0.],[1.]],[0,1])
                raise AssertionError('No debe llegar aquí')
        with self.assertRaisesRegex(RuntimeError,'Reentrenamiento prohibido'):
            predict_without_fit(BadEstimator(),[[0.]])
        # Agrupar las comprobaciones relacionadas para verificar el contrato de esta parte del proyecto.
        class InferenceOnly:
            # Auxiliar de test_final_evaluation.
            def __init__(self):self.calls=0
            # Auxiliar de test_final_evaluation.
            def predict_proba(self,x):self.calls+=1;return np.array([[.8,.2],[.1,.9]])
        model=InferenceOnly();p=predict_without_fit(model,[[0.],[1.]])
        self.assertEqual(model.calls,1);np.testing.assert_array_equal(p,[.2,.9])

    # Prueba: comprobar que el remuestreo respeta bloques temporales y es reproducible.
    def test_daily_blocks_keep_whole_days_and_are_reproducible(self):
        dates=pd.DatetimeIndex(np.repeat(pd.date_range('2017-03-01',periods=8),2))
        first=list(moving_day_indices(dates,3,10,42));second=list(moving_day_indices(dates,3,10,42))
        for a,b in zip(first,second):
            np.testing.assert_array_equal(a,b)
            self.assertEqual(len(a),16)
            counts=np.bincount(a,minlength=16)
            for day in range(8):self.assertEqual(counts[day*2],counts[day*2+1])

    # Prueba: comprobar las restricciones del ajuste y la conservación de parámetros aprendidos.
    def test_descriptive_intervals_reproduce_without_predict_or_fit(self):
        dates=np.repeat(pd.date_range('2017-03-01',periods=20),2)
        data=pd.DataFrame({'fecha_llegada':dates,'is_canceled':[0,1]*20,
            'score':[.2,.8]*20,'alerta':[False,True]*20})
        a,ai=uncertainty(data,repetitions=10,block_days=4,seed=42)
        b,bi=uncertainty(data,repetitions=10,block_days=4,seed=42)
        pd.testing.assert_frame_equal(a,b);pd.testing.assert_frame_equal(ai,bi)

    # Prueba: comprobar que se aplica la especificación congelada y se rechazan contratos incompatibles.
    def test_frozen_policy_exact_monthly_quota_and_shuffle(self):
        root=Path(__file__).resolve().parents[1]
        spec=json.loads((root/'reports/seleccion_8_especificacion_congelada.json').read_text(encoding='utf-8'))
        ids=np.arange(33);months=np.array(['2017-03']*17+['2017-04']*16);scores=np.ones(33)*.5
        a,b=apply_frozen_policy(spec,scores,ids,months)
        self.assertEqual(b.k.tolist(),[3,3])
        order=np.random.default_rng(9).permutation(33)
        c,_=apply_frozen_policy(spec,scores[order],ids[order],months[order])
        self.assertEqual(set(a.loc[a.alerta,'meta_row_id']),set(c.loc[c.alerta,'meta_row_id']))

    # Prueba: comprobar que se aplica la especificación congelada y se rechazan contratos incompatibles.
    def test_originals_and_frozen_artifacts_match_specification(self):
        from src.comparison import sha
        root=Path(__file__).resolve().parents[1]
        spec=json.loads((root/'reports/seleccion_8_especificacion_congelada.json').read_text(encoding='utf-8'))
        for path,expected in spec['huellas_entradas'].items():self.assertEqual(sha(root/path),expected)
        self.assertEqual(sha(root/spec['artefacto_modelo']),spec['artefacto_sha256'])
