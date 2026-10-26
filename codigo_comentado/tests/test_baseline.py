# EDICIÓN COMENTADA PARA LECTURA. Las fuentes ejecutadas y selladas permanecen en la raíz.
# Pruebas de baseline.
# Solo se añaden comentarios: no se han ejecutado instrucciones de esta copia.
"""Verifica fronteras temporales, conservación, grupos y métricas conocidas."""
import unittest

import pandas as pd

from src.splitting import temporal_split_legacy as temporal_split
from src.baseline import evaluate_predictions


# Auxiliar de test_baseline.
def synthetic_metadata():
    return pd.DataFrame({
        "meta_row_id": range(7), "meta_duplicate_group": list("abcdefg"),
        "meta_booking_date_proxy": ["2016-06-30", "2016-06-30", "2016-07-01", "2016-12-31",
                                    "2017-01-01", "2016-08-01", "2016-06-29"],
        "meta_label_available_after": ["2016-06-30", "2016-07-01", "2016-07-02", "2017-01-01",
                                       "2017-01-02", "2016-12-31", "2016-07-02"],
    })


# Agrupar las comprobaciones relacionadas para verificar el contrato de esta parte del proyecto.
class BaselineTests(unittest.TestCase):
    # Prueba del contrato dates and maturity boundaries: datos controlados y resultado esperado.
    def test_dates_and_maturity_boundaries(self):
        # Primera fila usa proxy anterior a madurez, respetando la regla semántica.
        meta = synthetic_metadata()
        meta.loc[0, "meta_booking_date_proxy"] = "2016-06-29"
        actual = temporal_split(meta).tolist()
        self.assertEqual(actual, ["entrenamiento", "no_madura_entrenamiento", "validacion",
                                  "no_madura_validacion", "prueba_reservada", "validacion",
                                  "no_madura_entrenamiento"])
        self.assertEqual(len(actual), len(meta))

    # Prueba: comprobar el tratamiento o rechazo de duplicados según el contrato de esta función.
    def test_duplicate_group_cannot_cross_partitions(self):
        meta = synthetic_metadata()
        meta.loc[0, "meta_booking_date_proxy"] = "2016-06-29"
        meta.loc[4, "meta_duplicate_group"] = "a"
        with self.assertRaisesRegex(ValueError, "duplicado"):
            temporal_split(meta)

    # Prueba del contrato invalid dates and cut order fail: datos controlados y resultado esperado.
    def test_invalid_dates_and_cut_order_fail(self):
        meta = synthetic_metadata()
        with self.assertRaises(ValueError):
            temporal_split(meta, validation_start="2017-01-01", test_start="2016-01-01")
        with self.assertRaises(ValueError):
            temporal_split(meta)  # Madurez <= proxy de la primera fila.

    # Prueba del contrato confusion orientation and trivial auc: datos controlados y resultado esperado.
    def test_confusion_orientation_and_trivial_auc(self):
        result = evaluate_predictions([0, 0, 1, 1], [0, 1, 0, 1], [.1, .7, .2, .8])
        self.assertEqual(result["matriz_confusion"], [[1, 1], [1, 1]])
        self.assertEqual(result["precision"], .5)
        self.assertEqual(result["recall"], .5)
        trivial = evaluate_predictions([0, 0, 1, 1], [0, 0, 0, 0], [0., 0., 0., 0.])
        self.assertEqual(trivial["roc_auc"], .5)
        self.assertEqual(trivial["recall"], 0.)


# Ejecutar la entrada principal solo al invocar este archivo como script.
if __name__ == "__main__":
    unittest.main(verbosity=2)
