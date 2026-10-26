"""Capacidad, empates y aplicación de política sin información de resultados."""
import unittest
import hashlib
import numpy as np
from src.decision_policy import monthly_priority,apply_frozen_policy


class PolicyTests(unittest.TestCase):
    def test_per_month_floor_and_empty_extremes(self):
        p=np.linspace(.01,.99,13);ids=np.arange(13);months=['2016-09']*7+['2016-10']*6
        for q in [0,10,20,30,100]:
            allocation,borders=monthly_priority(p,ids,months,q)
            self.assertEqual(int(allocation.alerta.sum()),7*q//100+6*q//100)
            self.assertTrue((borders.k==borders.n*q//100).all())
        a,b=monthly_priority([],[],[],20);self.assertTrue(a.empty and b.empty)

    def test_ties_resolve_by_hash_and_ignore_input_order(self):
        ids=np.arange(20);scores=np.ones(20)*.5;months=np.array(['2016-09']*20)
        first,b=monthly_priority(scores,ids,months,20)
        expected=sorted(ids,key=lambda i:(hashlib.sha256(f'42|{i}'.encode()).hexdigest(),i))[:4]
        self.assertEqual(set(first.loc[first.alerta,'meta_row_id']),set(expected))
        order=np.random.default_rng(123).permutation(20)
        second,_=monthly_priority(scores[order],ids[order],months[order],20)
        self.assertEqual(set(second.loc[second.alerta,'meta_row_id']),set(expected))
        self.assertEqual(int(b.empate_total_en_corte.iloc[0]),20)
        self.assertEqual(int(b.empate_alertado_en_corte.iloc[0]),4)

    def test_strictly_increasing_transform_preserves_priority(self):
        ids=np.arange(20);p=np.linspace(.01,.99,20);months=['2016-09']*20
        a,_=monthly_priority(p,ids,months,30)
        b,_=monthly_priority(.1+.8*p,ids,months,30)
        np.testing.assert_array_equal(a.alerta,b.alerta)

    def test_duplicate_ids_invalid_scores_and_capacity_rejected(self):
        for scores,ids,months,q in [([.1,.2],[1,1],['2016-09']*2,20),
            ([np.nan],[1],['2016-09'],20),([1.2],[1],['2016-09'],20),
            ([.5],[1],['2016-13'],20),([.5],[1],['2016-09'],20.5),
            ([.5],[-1],['2016-09'],20),([.5],[1],['2016-09'],True)]:
            with self.assertRaises((ValueError,TypeError)):monthly_priority(scores,ids,months,q)

    def test_frozen_policy_uses_only_scores_ids_months(self):
        spec={'politica':{'tipo':'top_capacidad_mensual','version_algoritmo':1,'capacidad_pct':20,
            'clave_grupo':'mes_llegada_YYYY-MM','fraccion_redondeo':'floor','seed_desempate':42,
            'desempate':'score_desc_sha256(seed|ID)_asc_ID_asc_sin_redondear_score'}}
        a,_=apply_frozen_policy(spec,[.1,.2,.3,.4,.9],list(range(5)),['2016-09']*5)
        self.assertEqual(a.loc[a.alerta,'meta_row_id'].tolist(),[4])
        spec['politica']['version_algoritmo']=2
        with self.assertRaises(ValueError):apply_frozen_policy(spec,[.9],[0],['2016-09'])
