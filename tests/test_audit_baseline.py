# Pruebas de auditoría: umbrales, bandas de calibración y escenarios temporales.
"""Pruebas auxiliares sin ajuste de modelos o acceso al conjunto de prueba real."""
import unittest
import numpy as np
import pandas as pd

from src.audit_baseline import threshold_table, reliability_table, timing_scenarios


# Agrupar las comprobaciones relacionadas para verificar el contrato de esta parte del proyecto.
class AuditBaselineTests(unittest.TestCase):
    # Comprobar cómo se resuelve la igualdad con el umbral y cómo cambian FP y FN.
    def test_threshold_tie_and_error_counts(self):
        target = np.array([0, 0, 1, 1])
        probabilities = np.array([.1, .5, .5, .9])
        result = threshold_table(target, probabilities, [0, .5, 1])
        middle = result.loc[result.umbral.eq(.5)].iloc[0]
        self.assertEqual(middle.falsos_positivos, 1)
        self.assertEqual(middle.falsos_negativos, 0)
        self.assertEqual(middle.alertas, 3)
        self.assertEqual(result.iloc[-1].alertas, 0)
        np.testing.assert_array_equal(probabilities, [.1, .5, .5, .9])
        with self.assertRaises(ValueError):
            threshold_table(target, [0, 0, 0, 1.1])

    # Incluir scores 0 y 1 en las bandas y conservar el total de observaciones.
    def test_reliability_includes_zero_one_and_preserves_totals(self):
        result = reliability_table([0, 1, 0, 1], [0, .1, .5, 1])
        self.assertEqual(result.registros.sum(), 4)
        self.assertEqual(result.cancelaciones.sum(), 2)
        self.assertEqual(result.iloc[0].registros, 2)
        self.assertAlmostEqual(float((result.registros * result.probabilidad_media).sum()), 1.6)

    # Aplicar cierres estrictos de auditoría sin trasladar reservas entre particiones.
    def test_temporal_scenarios_are_strict_and_do_not_reassign(self):
        status = pd.Series(["2017-08-31", "2017-09-01"])
        maturity = pd.Series(["2017-09-01", "2017-09-02"])
        before = maturity.copy(deep=True)
        result = timing_scenarios(status, maturity, {"hipotetico": "2017-09-01"})
        self.assertEqual(result.iloc[0].fecha_estado_en_o_despues_del_corte, 1)
        self.assertEqual(result.iloc[0].no_cumple_regla_madurez, 2)
        pd.testing.assert_series_equal(before, maturity)


# Ejecutar la entrada principal solo al invocar este archivo como script.
if __name__ == "__main__":
    unittest.main(verbosity=2)
