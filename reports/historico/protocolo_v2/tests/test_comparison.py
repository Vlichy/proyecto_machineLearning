"""Aislamiento de fit y frontera train/validación con datos sintéticos."""
import unittest
import numpy as np
import pandas as pd
from sklearn.base import clone
from src.comparison import model_factories, fit_one
from src.features import FEATURES, NUMERIC_FEATURES, CATEGORICAL_FEATURES


class ComparisonTests(unittest.TestCase):
    def data(self):
        x = pd.DataFrame({c: np.arange(40, dtype=float) % 7 for c in NUMERIC_FEATURES})
        for c in CATEGORICAL_FEATURES:
            x[c] = ['A', 'B'] * 20
        x.loc[0, 'children'] = np.nan
        y = pd.Series([0, 1] * 20)
        val = x.iloc[:8].copy().set_axis(range(100, 108))
        val['country'] = 'SOLO_VALIDACION'
        val['lead_time'] = 10000.
        return x[FEATURES], y, val[FEATURES], pd.Series([0,1]*4,index=val.index)

    def test_all_algorithms_train_only_unknown_and_reproducible(self):
        x,y,v,z = self.data()
        for name, pipeline in model_factories().items():
            with self.subTest(model=name):
                if name != 'regresion_logistica':
                    params = pipeline.named_steps['classifier'].get_params()
                    if 'n_estimators' in params: pipeline.set_params(classifier__n_estimators=3)
                original = clone(pipeline)
                metrics,p,_ = fit_one(pipeline,x,y,v,z)
                _,q,_ = fit_one(original,x,y,v,z)
                np.testing.assert_allclose(p,q,rtol=1e-12,atol=1e-12)
                encoder = pipeline.named_steps['preprocessor'].named_transformers_['categorical'].named_steps['encoder']
                self.assertNotIn('SOLO_VALIDACION',encoder.categories_[CATEGORICAL_FEATURES.index('country')])
                self.assertEqual(sum(metrics[k] for k in ['tn','fp','fn','tp']),len(v))

    def test_reject_overlap(self):
        x,y,v,z = self.data()
        with self.assertRaises(ValueError):
            fit_one(model_factories()['arbol_decision'],x,y,x.iloc[:8],y.iloc[:8])
