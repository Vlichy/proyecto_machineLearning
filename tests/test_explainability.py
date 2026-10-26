# Pruebas de explicabilidad: mapeo, reconstrucción SHAP y denominadores por segmento.
"""Correspondencia one-hot, aditividad SHAP y denominadores de errores."""
import unittest
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.special import expit
import shap
from xgboost import XGBClassifier
from src.features import NUMERIC_FEATURES, CATEGORICAL_FEATURES
from src.preprocessing import build_preprocessor
from src.explainability import feature_mapping,group_contributions,segment_metrics,calibration_bins,select_cases


# Agrupar las comprobaciones relacionadas para verificar el contrato de esta parte del proyecto.
class ExplainabilityTests(unittest.TestCase):
    # Relacionar dummies con variables originales sin romper nombres con guiones bajos y conservar la suma SHAP.
    def test_mapping_underscores_and_grouped_additivity(self):
        x=pd.DataFrame({c:[1.,2.,3.,4.] for c in NUMERIC_FEATURES})
        for c in CATEGORICAL_FEATURES:x[c]=['A_B','C_D']*2
        # Aprender los parámetros con el entrenamiento recibido; validación se reserva para medir rendimiento.
        pre=build_preprocessor(False).fit(x)
        mapping=feature_mapping(pre)
        self.assertEqual(mapping.original.eq('arrival_date_month').sum(),2)
        values=np.arange(2*len(mapping),dtype=float).reshape(2,-1)
        grouped=group_contributions(values,mapping)
        np.testing.assert_array_equal(grouped.sum(axis=1),values.sum(axis=1))
        with self.assertRaises(ValueError):group_contributions(values[:,:-1],mapping)

    # Comprobar la compatibilidad de SHAP con la matriz dispersa y reconstruir el margen del árbol.
    def test_sparse_shap_compatibility_reconstruction(self):
        x=sparse.csr_matrix(np.array([[0.,1.],[1.,0.],[1.,1.],[0.,0.]]*10))
        # Aprender los parámetros con el entrenamiento recibido; validación se reserva para medir rendimiento.
        model=XGBClassifier(n_estimators=3,n_jobs=1,random_state=42).fit(x,[0,1,1,0]*10)
        # Explicar este modelo de árboles y su población; las contribuciones no se trasladan a logística.
        explainer=shap.TreeExplainer(model,feature_perturbation='tree_path_dependent',model_output='raw')
        values=explainer.shap_values(x)
        margin=explainer.expected_value+values.sum(axis=1)
        np.testing.assert_allclose(margin,model.predict(x,output_margin=True),atol=1e-5)
        # Obtener scores con el pipeline ajustado, sin aprender parámetros de estas filas.
        np.testing.assert_allclose(expit(margin),model.predict_proba(x)[:,1],atol=1e-6)

    # Mantener denominadores explícitos y evitar un ROC-AUC indefinido en segmentos de una clase.
    def test_segments_single_class_and_denominators(self):
        data=pd.DataFrame({'hotel':['A']*4+['B']*2,'is_canceled':[0,0,1,1,0,0],
                           'probabilidad':[.1,.8,.2,.9,.1,1.]})
        rows=segment_metrics(data,['hotel']).set_index('grupo')
        self.assertEqual(rows.loc['A','fpr'],.5);self.assertEqual(rows.loc['A','fnr'],.5)
        self.assertTrue(pd.isna(rows.loc['B','roc_auc']))
        self.assertFalse(rows.suficiente_descriptivo.any())
        bins=calibration_bins(data)
        self.assertEqual(bins.loc[bins.hotel.eq('Todos'),'n'].sum(),6)
        self.assertEqual(bins.loc[bins.hotel.eq('B')&bins.bin.eq(9),'n'].iloc[0],1)

    # Elegir casos de los cuatro tipos de error de forma determinista.
    def test_cases_cover_four_outcomes_and_are_deterministic(self):
        y=np.array([1,0,0,1]*3);p=np.array([.9,.2,.8,.1]*3)
        cases=select_cases(y,p)
        self.assertEqual(cases,select_cases(y,p))
        self.assertEqual(set(cases),{'TP','TN','FP','FN'})
        for label,i in cases.items():
            expected=('T' if int(p[i]>=.5)==y[i] else 'F')+('P' if p[i]>=.5 else 'N')
            self.assertEqual(label,expected)
