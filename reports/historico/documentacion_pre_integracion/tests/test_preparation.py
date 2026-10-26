"""Pruebas de fuga, integridad y transformadores con datos exclusivamente sintéticos."""
import unittest

import numpy as np
import pandas as pd
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted

from src.cleaning import clean
from src.features import (FEATURES, NUMERIC_FEATURES, CATEGORICAL_FEATURES, LEAKAGE_FEATURES,
                          UNCERTAIN_FEATURES, separate_model_data)
from src.preparation import prepare_data
from src.preprocessing import build_preprocessor


def synthetic_raw():
    """Esquema de hotel con valores inventados para verificar reglas, no resultados."""
    row = {"hotel": "City Hotel", "is_canceled": 0, "lead_time": 10,
           "arrival_date_year": 2016, "arrival_date_month": "January",
           "arrival_date_week_number": 2, "arrival_date_day_of_month": 10,
           "stays_in_weekend_nights": 1, "stays_in_week_nights": 2,
           "adults": 2, "children": 0., "babies": 0, "meal": "BB", "country": "PRT",
           "market_segment": "Direct", "distribution_channel": "Direct", "is_repeated_guest": 0,
           "previous_cancellations": 0, "previous_bookings_not_canceled": 0,
           "reserved_room_type": "A", "assigned_room_type": "A", "booking_changes": 0,
           "deposit_type": "No Deposit", "agent": np.nan, "company": np.nan,
           "days_in_waiting_list": 0, "customer_type": "Transient", "adr": 100.,
           "required_car_parking_spaces": 0, "total_of_special_requests": 0,
           "reservation_status": "Check-Out", "reservation_status_date": "2016-01-13"}
    data = pd.DataFrame([row.copy() for _ in range(3)])
    data["lead_time"] = [10, 20, 30]
    data["children"] = [0., 2., np.nan]
    data.loc[2, "country"] = np.nan
    return data


class PreparationTests(unittest.TestCase):
    def test_all_rows_and_duplicates_preserved_without_mutation(self):
        raw = synthetic_raw()
        raw = pd.concat([raw, raw.iloc[[0]]], ignore_index=True)
        before = raw.copy(deep=True)
        first, second = prepare_data(raw), prepare_data(raw)
        pd.testing.assert_frame_equal(raw, before)
        pd.testing.assert_frame_equal(first, second)
        self.assertEqual(len(first), len(raw))
        self.assertEqual(first.meta_duplicate_group.duplicated().sum(), 1)
        self.assertEqual(first.meta_row_id.tolist(), list(range(4)))

    def test_anomalies_and_unknowns_not_guessed(self):
        raw = synthetic_raw()
        raw.loc[0, "adr"] = -6.38
        raw.loc[1, "adr"] = 0
        raw.loc[1, ["adults", "children", "babies", "stays_in_week_nights", "stays_in_weekend_nights"]] = 0
        data = clean(raw)
        self.assertTrue(pd.isna(data.loc[0, "adr"]))
        self.assertEqual(data.loc[1, "adr"], 0)
        self.assertTrue(pd.isna(data.loc[2, "children"]))
        self.assertTrue(data.agent.isna().all())
        self.assertEqual(str(data.children.dtype), "Int64")
        prepared = prepare_data(raw)
        self.assertEqual(prepared.meta_adr_negative.sum(), 1)
        self.assertEqual(prepared.meta_zero_nights.sum(), 1)
        self.assertEqual(prepared.meta_zero_guests.sum(), 1)
        self.assertEqual(prepared.meta_guests_unknown.sum(), 1)

    def test_target_and_future_values_cannot_change_features(self):
        raw = synthetic_raw()
        baseline, _, _ = separate_model_data(prepare_data(raw))
        altered = raw.copy()
        altered["is_canceled"] = 1
        altered["reservation_status"] = "Canceled"
        altered["reservation_status_date"] = "2016-06-01"
        altered["adr"] = 9000
        altered["booking_changes"] = 999
        altered["deposit_type"] = "Non Refund"
        actual, target, metadata = separate_model_data(prepare_data(altered))
        pd.testing.assert_frame_equal(baseline, actual)
        self.assertTrue(target.eq(1).all())
        self.assertEqual(actual.columns.tolist(), FEATURES)
        self.assertFalse(set(actual.columns) & set(LEAKAGE_FEATURES + UNCERTAIN_FEATURES + ["is_canceled"]))
        self.assertFalse(any(c.startswith("meta_") for c in actual))
        self.assertIn("meta_label_available_after", metadata)

    def test_training_only_fit_unseen_categories_and_statistics(self):
        train, _, _ = separate_model_data(prepare_data(synthetic_raw()))
        future = train.iloc[[0]].copy()
        future.loc[:, "lead_time"] = 10000.
        future.loc[:, "children"] = np.nan
        future.loc[:, "country"] = "PAIS_NUEVO"
        future.loc[:, "hotel"] = "HOTEL_NUEVO"
        future.loc[:, "is_canceled"] = 1  # Resto no permitido: siempre se descarta.
        future.loc[:, "meta_booking_date_proxy"] = "2099-01-01"
        pipeline = build_preprocessor()
        with self.assertRaises(NotFittedError):
            check_is_fitted(pipeline)
        pipeline.fit(train)  # Solo tres registros inventados.
        imputer = pipeline.named_transformers_["numeric"].named_steps["imputer"]
        scaler = pipeline.named_transformers_["numeric"].named_steps["scaler"]
        encoder = pipeline.named_transformers_["categorical"].named_steps["encoder"]
        child_index = NUMERIC_FEATURES.index("children")
        self.assertEqual(imputer.statistics_[child_index], 1.)
        self.assertEqual(scaler.mean_[NUMERIC_FEATURES.index("lead_time")], 20.)
        before = scaler.mean_.copy()
        output = pipeline.transform(future)
        values = output.toarray() if hasattr(output, "toarray") else output
        self.assertTrue(np.isfinite(values).all())
        np.testing.assert_array_equal(scaler.mean_, before)
        self.assertNotIn("PAIS_NUEVO", encoder.categories_[CATEGORICAL_FEATURES.index("country")])
        self.assertTrue(all("meta_" not in name and "is_canceled" not in name for name in pipeline.get_feature_names_out()))
        with self.assertRaises(NotFittedError):
            check_is_fitted(build_preprocessor())  # La fábrica no comparte objetos ajustados.

    def test_no_scaling_option_and_temporal_metadata(self):
        prepared = prepare_data(synthetic_raw())
        x, _, meta = separate_model_data(prepared)
        pipeline = build_preprocessor(scale_numeric=False)
        pipeline.fit_transform(x)
        self.assertNotIn("scaler", pipeline.named_transformers_["numeric"].named_steps)
        self.assertEqual(meta.meta_booking_date_proxy.iloc[0], pd.Timestamp("2015-12-31"))
        self.assertTrue((meta.meta_label_available_after > meta.meta_arrival_date).all())


if __name__ == "__main__":
    unittest.main(verbosity=2)
