# EDICIÓN COMENTADA PARA LECTURA. Las fuentes ejecutadas y selladas permanecen en la raíz.
# Pruebas de temporal protocol.
# Solo se añaden comentarios: no se han ejecutado instrucciones de esta copia.
"""Fronteras y protección de prueba del protocolo aproximado v2."""
import unittest
import pandas as pd

from src.splitting import add_status_availability, temporal_split, temporal_split_legacy


# Auxiliar de test_temporal_protocol.
def synthetic():
    metadata = pd.DataFrame({"meta_row_id": range(6), "meta_duplicate_group": list("abcdef"),
        "meta_booking_date_proxy": ["2016-06-29", "2016-06-30", "2016-07-01", "2016-07-01", "2017-01-01", "2017-01-02"],
        "meta_label_available_after": ["2016-08-01", "2016-08-01", "2017-02-01", "2017-02-01", "2017-10-01", "2017-10-01"]})
    status = pd.Series(["2016-06-29", "2016-06-30", "2016-12-30", "2016-12-31", "2017-08-31", "2017-08-30"])
    return metadata, status


# Agrupar las comprobaciones relacionadas para verificar el contrato de esta parte del proyecto.
class TemporalProtocolTests(unittest.TestCase):
    # Prueba del contrato exact cut boundaries and test maturity: datos controlados y resultado esperado.
    def test_exact_cut_boundaries_and_test_maturity(self):
        metadata, status = synthetic()
        result = temporal_split(add_status_availability(metadata, status), as_of_date="2017-09-01")
        self.assertEqual(result.tolist(), ["entrenamiento", "no_madura_entrenamiento", "validacion",
            "no_madura_validacion", "no_madura_prueba", "prueba_reservada"])

    # Prueba del contrato early recorded outcome does not wait for planned departure: datos controlados y resultado esperado.
    def test_early_recorded_outcome_does_not_wait_for_planned_departure(self):
        metadata, status = synthetic()
        old = temporal_split_legacy(metadata)
        new = temporal_split(add_status_availability(metadata, status))
        self.assertEqual(old.iloc[0], "no_madura_entrenamiento")
        self.assertEqual(new.iloc[0], "entrenamiento")
        self.assertEqual(new.iloc[2], "validacion")

    # Prueba del contrato missing status and unaligned rows fail: datos controlados y resultado esperado.
    def test_missing_status_and_unaligned_rows_fail(self):
        metadata, status = synthetic()
        status.iloc[0] = None
        with self.assertRaises(ValueError):
            add_status_availability(metadata, status)
        with self.assertRaises(ValueError):
            add_status_availability(metadata, status.set_axis(range(10, 16)))
        with self.assertRaises(ValueError):
            temporal_split(metadata)

    # Prueba: comprobar el tratamiento o rechazo de duplicados según el contrato de esta función.
    def test_duplicate_group_cannot_cross_new_partitions(self):
        metadata, status = synthetic()
        metadata.loc[5, "meta_duplicate_group"] = "a"
        with self.assertRaisesRegex(ValueError, "duplicado"):
            temporal_split(add_status_availability(metadata, status))

    # Prueba del contrato input immutable and deterministic: datos controlados y resultado esperado.
    def test_input_immutable_and_deterministic(self):
        metadata, status = synthetic()
        before = metadata.copy(deep=True)
        enriched = add_status_availability(metadata, status)
        pd.testing.assert_frame_equal(metadata, before)
        first, second = temporal_split(enriched), temporal_split(enriched)
        pd.testing.assert_series_equal(first, second)
        self.assertEqual(len(first), len(metadata))

    # Prueba del contrato close must follow test and availability follow booking: datos controlados y resultado esperado.
    def test_close_must_follow_test_and_availability_follow_booking(self):
        metadata, status = synthetic()
        with self.assertRaises(ValueError):
            temporal_split(add_status_availability(metadata, status), as_of_date="2017-01-01")
        status.iloc[0] = "2016-06-01"
        with self.assertRaises(ValueError):
            temporal_split(add_status_availability(metadata, status))


# Ejecutar la entrada principal solo al invocar este archivo como script.
if __name__ == "__main__":
    unittest.main(verbosity=2)
