# Pruebas de v3: elegibilidad independiente del resultado y seguimiento por cohorte.
"""Elegibilidad ajena a resultado, embargos y seguimiento de bloques completos."""
import unittest
from pathlib import Path
import tempfile
import pandas as pd
import numpy as np
from src.splitting import temporal_split_v3,audit_followup_v3
from src.temporal_bias_v3 import read_rows,metrics_for


# Agrupar las comprobaciones relacionadas para verificar el contrato de esta parte del proyecto.
class V3Tests(unittest.TestCase):
    # Bloquear las entradas históricas que sobrescribirían los resultados activos v3.
    def test_old_entries_refuse_overwriting_active_v3(self):
        import json
        from src.comparison import load_development
        from src.temporal_protocol import build_protocol
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root=Path(directory);(root/'reports').mkdir()
            (root/'reports/estado_protocolo.json').write_text(json.dumps({'vigente':'v3_cohortes_llegada_retrospectivo'}),encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError,'histórica v2'):load_development(root)
            with self.assertRaisesRegex(RuntimeError,'sobrescribir'):build_protocol(root)

    # Crear metadatos artificiales con fechas conocidas para probar elegibilidad y seguimiento.
    def metadata(self):
        return pd.DataFrame({'meta_row_id':range(8),'meta_duplicate_group':list('abcdefgh'),
            'meta_arrival_date':['2015-07-01','2016-06-30','2016-07-01','2016-08-31','2016-09-01','2016-12-31','2017-01-01','2017-03-01']})

    # Asignar cada fila una sola vez y respetar las fronteras de train, embargos, validación y prueba.
    def test_boundaries_and_unique_assignment(self):
        m=self.metadata();a=temporal_split_v3(m)
        self.assertEqual(a.tolist(),['entrenamiento','entrenamiento','embargo_train_validacion','embargo_train_validacion',
            'validacion','validacion','embargo_validacion_prueba','prueba_reservada'])
        self.assertEqual(len(a),len(m))

    # Cambiar etiqueta y estado artificialmente para comprobar que v3 asigna solo por llegada.
    def test_outcome_and_status_do_not_change_eligibility(self):
        m=self.metadata();before=m.copy(deep=True)
        # Asignar cohortes por llegada sin seleccionar filas según su desenlace individual.
        first=temporal_split_v3(m.assign(is_canceled=0,reservation_status_date='2015-01-01'))
        # Asignar cohortes por llegada sin seleccionar filas según su desenlace individual.
        second=temporal_split_v3(m.assign(is_canceled=1,reservation_status_date='2099-12-31'))
        pd.testing.assert_series_equal(first,second);pd.testing.assert_frame_equal(m,before)

    # Prueba: comprobar que el remuestreo respeta bloques temporales y es reproducible.
    def test_late_outcome_blocks_cohort_does_not_drop_row(self):
        m=self.metadata();a=temporal_split_v3(m);dev=a.isin(['entrenamiento','validacion'])
        m=m.loc[dev];a=a.loc[dev]
        statuses=pd.Series(['2015-07-02','2016-07-02','2016-09-02','2017-01-02'],index=m.index)
        nights=pd.Series([1]*len(m),index=m.index)
        # Auditar el seguimiento de cohortes completas; si falla una fila no se rescatan las demás.
        result=audit_followup_v3(m,a,statuses,nights)
        self.assertEqual(int(result.registros.sum()),len(m))
        statuses.iloc[1]='2016-08-31'  # +1 = corte exclusivo; bloquea TODO train
        with self.assertRaisesRegex(ValueError,'bloquear el bloque completo'):
            # Auditar el seguimiento de cohortes completas; si falla una fila no se rescatan las demás.
            audit_followup_v3(m,a,statuses,nights)
        # Asignar cohortes por llegada sin seleccionar filas según su desenlace individual.
        pd.testing.assert_series_equal(temporal_split_v3(m),a)

    # Rechazar etiquetas de prueba en una auditoría limitada a los bloques de desarrollo.
    def test_auditing_test_labels_is_rejected(self):
        m=self.metadata();a=temporal_split_v3(m)
        with self.assertRaisesRegex(ValueError,'prueba'):
            # Auditar el seguimiento de cohortes completas; si falla una fila no se rescatan las demás.
            audit_followup_v3(m,a,pd.Series(['2018-01-01']*len(m)),pd.Series([1]*len(m)))

    # Prueba: comprobar el tratamiento o rechazo de duplicados según el contrato de esta función.
    def test_duplicates_and_missing_dates_rejected(self):
        m=self.metadata();m.loc[4,'meta_duplicate_group']='a'
        with self.assertRaisesRegex(ValueError,'duplicado'):temporal_split_v3(m)
        m=self.metadata();m.loc[0,'meta_arrival_date']=None
        with self.assertRaises(ValueError):temporal_split_v3(m)

    # Prueba: contrastar las métricas con los recuentos esperados de aciertos y errores.
    def test_selective_label_read_and_single_class_metrics(self):
        # Temporal dentro del workspace para evitar restricciones del sandbox Windows.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            path=Path(directory)/'labels.csv'
            pd.DataFrame({'is_canceled':[0,1,'NO_LEER',0],'secret':['x']*4}).to_csv(path,index=False)
            result=read_rows(path,['is_canceled'],[0,1,3])
            self.assertEqual(result.is_canceled.tolist(),[0,1,0])
            self.assertEqual(result.index.tolist(),[0,1,3])
        m=metrics_for([0,0],[.2,.8]);self.assertEqual(m['recall'],0);self.assertIsNone(m['roc_auc'])
