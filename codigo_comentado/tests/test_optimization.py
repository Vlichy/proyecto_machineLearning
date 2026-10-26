# EDICIÓN COMENTADA PARA LECTURA. Las fuentes ejecutadas y selladas permanecen en la raíz.
# Pruebas de optimization.
# Solo se añaden comentarios: no se han ejecutado instrucciones de esta copia.
"""Fronteras temporales, muestreo reproducible y análisis posterior sintético."""
import unittest
import json
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from src.optimization import (make_folds, candidate_parameters, threshold_table,
                              reliability_table, scenario_table, audit_preprocessor, json_write)
from src.comparison import model_factories
from src.preprocessing import build_preprocessor
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from src.features import NUMERIC_FEATURES, CATEGORICAL_FEATURES


# Agrupar las comprobaciones relacionadas para verificar el contrato de esta parte del proyecto.
class OptimizationTests(unittest.TestCase):
    # Prueba del contrato json preserves nan default as explicit metadata: datos controlados y resultado esperado.
    def test_json_preserves_nan_default_as_explicit_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'parameters.json'
            json_write(path,{'missing':np.nan,'none':None,'n':np.int64(42)})
            value=json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(value,{'missing':'NaN','none':None,'n':42})

    # Auxiliar de test_optimization.
    def metadata(self):
        booking=['2015-08-01','2015-08-02','2015-09-01','2015-10-01','2015-10-02',
                 '2015-11-01','2015-12-01','2016-01-01','2016-01-02',
                 '2016-02-01','2016-04-01','2016-04-02']
        available=['2015-08-02','2015-08-03','2015-10-01','2015-10-02','2015-10-03',
                   '2016-01-01','2016-01-02','2016-01-02','2016-01-03',
                   '2016-04-01','2016-04-02','2016-04-03']
        return pd.DataFrame({'meta_row_id':range(12),'meta_duplicate_group':[str(i) for i in range(12)],
                             'meta_booking_date_proxy':booking,'meta_label_available_proxy':available}),pd.Series([0,1]*6)

    # Prueba del contrato strict availability and booking boundaries: datos controlados y resultado esperado.
    def test_strict_availability_and_booking_boundaries(self):
        m,y=self.metadata(); folds,summary=make_folds(m,y)
        first_train,first_val=folds[0]
        self.assertNotIn(2,first_train)  # disponibilité exactamente en inicio
        self.assertIn(3,first_val)       # alta exactamente en inicio
        self.assertNotIn(5,first_val)   # disponibilidad exactamente en fin
        self.assertNotIn(7,first_val)   # alta en fin pertenece a ventana siguiente
        self.assertEqual(len(summary),3)
        self.assertFalse(set(first_train)&set(first_val))

    # Prueba: comprobar el tratamiento o rechazo de duplicados según el contrato de esta función.
    def test_reject_external_rows_duplicates_and_overlapping_windows(self):
        m,y=self.metadata()
        bad=m.copy();bad.loc[0,'meta_label_available_proxy']='2016-07-01'
        with self.assertRaises(ValueError): make_folds(bad,y)
        bad=m.copy();bad.loc[3,'meta_duplicate_group']=bad.loc[0,'meta_duplicate_group']
        with self.assertRaises(ValueError): make_folds(bad,y)
        with self.assertRaises(ValueError):
            make_folds(m,y,[('2015-10-01','2016-02-01'),('2016-01-01','2016-07-01')])

    # Prueba del contrato candidates reproduce and include initial: datos controlados y resultado esperado.
    def test_candidates_reproduce_and_include_initial(self):
        models=model_factories()
        for name in ['xgboost','lightgbm']:
            first=candidate_parameters(name,models[name])
            self.assertEqual(first,candidate_parameters(name,models[name]))
            self.assertEqual(len(first),9)
            self.assertEqual(len({str(sorted(p.items())) for p in first}),9)
            for key,value in first[0].items(): self.assertEqual(value,models[name].get_params()[key])

    # Prueba del contrato thresholds costs and probability one bin: datos controlados y resultado esperado.
    def test_thresholds_costs_and_probability_one_bin(self):
        y=pd.Series([0,1,0,1]);p=pd.DataFrame({'modelo':[.1,.4,.6,1.]})
        table=threshold_table(y,p,[.4,.5,1.])
        self.assertEqual(table.iloc[0].alertas,3)
        self.assertEqual((int(table.iloc[1].fp),int(table.iloc[1].fn)),(1,1))
        self.assertEqual(table.iloc[2].porcentaje_alto_riesgo,25)
        bins,calibration=reliability_table(y,p)
        self.assertEqual(int(bins.n.sum()),4)
        self.assertEqual(int(bins.loc[bins.bin.eq(9),'n'].iloc[0]),1)
        self.assertAlmostEqual(calibration.iloc[0].brier,(.01+.36+.36+0)/4)
        scenarios=scenario_table(table)
        row=scenarios[(scenarios.umbral==.5)&(scenarios.coste_fn_supuesto==5)].iloc[0]
        self.assertEqual(row.carga_relativa_errores,6)

    # Prueba: comprobar las restricciones del ajuste y la conservación de parámetros aprendidos.
    def test_preprocessing_audit_detects_full_dataset_fit(self):
        train=pd.DataFrame({c:[1.,2.,3.,4.] for c in NUMERIC_FEATURES})
        for c in CATEGORICAL_FEATURES: train[c]=['A','B','A','B']
        model=Pipeline([('preprocessor',build_preprocessor(False)),('classifier',DecisionTreeClassifier())])
        # Aprender los parámetros con el entrenamiento recibido; validación se reserva para medir rendimiento.
        model.fit(train,[0,1,0,1]);audit_preprocessor(model,train)
        forbidden=train.copy();forbidden['country']='FUTURO';forbidden['lead_time']=999
        # Aprender los parámetros con el entrenamiento recibido; validación se reserva para medir rendimiento.
        model.fit(pd.concat([train,forbidden]),[0,1,0,1]*2)
        with self.assertRaises(AssertionError): audit_preprocessor(model,train)
