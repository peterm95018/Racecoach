import unittest

import pandas as pd

from racecoach.analyze_run import (
    metrics_for_segment,
    normalize_columns,
    select_timed_lap_rows,
    trim_prestart_staging,
)


class PreprocessingRegressionTests(unittest.TestCase):
    def test_normal_run_is_unchanged(self):
        df = pd.DataFrame(
            {
                "time_s": [0, 1, 2, 3, 4, 5],
                "distance": [0, 10, 20, 30, 40, 50],
                "speed_mph": [5, 10, 15, 20, 25, 30],
                "throttle": [10, 20, 30, 40, 50, 60],
                "long_g": [0, 0, 0, 0, 0, 0],
            }
        )

        trimmed = trim_prestart_staging(df)

        pd.testing.assert_frame_equal(
            trimmed.reset_index(drop=True),
            df.reset_index(drop=True),
        )

    def test_ambiguous_multiple_laps_are_rejected(self):
        df = pd.DataFrame(
            {
                "lap_number": [1] * 5 + [2] * 5,
            }
        )

        with self.assertRaisesRegex(ValueError, "Multiple timed laps"):
            select_timed_lap_rows(df, "reference.csv")

    def test_filename_lap_mismatch_is_rejected(self):
        df = pd.DataFrame(
            {
                "lap_number": [2] * 5,
            }
        )

        with self.assertRaisesRegex(ValueError, "requests lap 3"):
            select_timed_lap_rows(df, "session_event_lap3_v3.csv")

    def test_extended_staging_is_trimmed_and_rezeroed(self):
        rows = []

        # Early movement.
        for i in range(10):
            rows.append(
                {
                    "time_s": float(i),
                    "distance": float(i),
                    "speed_mph": 2.0,
                    "throttle": 10.0,
                    "long_g": 0.0,
                }
            )

        # Long staging stop.
        for i in range(10, 41):
            rows.append(
                {
                    "time_s": float(i),
                    "distance": 10.0,
                    "speed_mph": 0.0,
                    "throttle": 10.0,
                    "long_g": 0.0,
                }
            )

        # Competitive launch.
        for i in range(41, 61):
            rows.append(
                {
                    "time_s": float(i),
                    "distance": 10.0 + (i - 40) * 5.0,
                    "speed_mph": 10.0,
                    "throttle": 80.0,
                    "long_g": 0.1,
                }
            )

        df = pd.DataFrame(rows)

        trimmed = trim_prestart_staging(df)

        self.assertLess(len(trimmed), len(df))
        self.assertEqual(trimmed.iloc[0]["time_s"], 0.0)
        self.assertEqual(trimmed.iloc[0]["distance"], 0.0)
        self.assertGreater(trimmed.iloc[-1]["distance"], 0.0)

    def test_numbered_lap_is_selected_and_rezeroed(self):
        df = pd.DataFrame(
            {
                "lap_number": [None, 9, 9, 9, 9, 9, None],
                "elapsed_time": [180, 187, 188, 189, 190, 191, 230],
                "distance_traveled": [0, 100, 110, 120, 130, 140, 900],
                "speed": [0, 10, 11, 12, 13, 14, 5],
            }
        )

        selected = select_timed_lap_rows(
            df,
            "session_event_lap9_v3.csv",
        )
        normalized = normalize_columns(selected)

        self.assertEqual(len(normalized), 5)
        self.assertEqual(normalized.iloc[0]["time_s"], 0.0)
        self.assertEqual(normalized.iloc[0]["distance"], 0.0)
        self.assertEqual(normalized.iloc[-1]["time_s"], 4.0)
        self.assertEqual(normalized.iloc[-1]["distance"], 40.0)

    def test_filename_selects_lap_when_multiple_are_present(self):
        df = pd.DataFrame(
            {
                "lap_number": [1] * 5 + [2] * 5,
                "marker": list(range(10)),
            }
        )

        selected = select_timed_lap_rows(
            df,
            "session_event_lap2_v3.csv",
        )

        self.assertEqual(selected["marker"].tolist(), list(range(5, 10)))

    def test_single_available_lap_is_used_for_reference_file(self):
        df = pd.DataFrame(
            {
                "lap_number": [None, 4, 4, 4, 4, 4, None],
                "marker": list(range(7)),
            }
        )

        selected = select_timed_lap_rows(df, "reference.csv")

        self.assertEqual(len(selected), 5)
        self.assertTrue((selected["lap_number"] == 4).all())

    def test_export_without_lap_markers_is_unchanged(self):
        df = pd.DataFrame(
            {
                "elapsed_time": [0, 1, 2, 3, 4],
                "distance_traveled": [0, 10, 20, 30, 40],
            }
        )

        selected = select_timed_lap_rows(df, "legacy.csv")

        pd.testing.assert_frame_equal(selected, df)

    def test_brake_start_time_is_segment_relative(self):
        df = pd.DataFrame(
            {
                "time_s": [
                    100.0,
                    100.5,
                    101.0,
                    101.5,
                    102.0,
                    102.5,
                ],
                "distance": [0, 20, 40, 60, 80, 100],
                "speed_mph": [40, 38, 34, 30, 32, 35],
                "throttle": [0, 0, 0, 20, 40, 50],
                "long_g": [-0.1, -0.3, -0.5, -0.2, 0.0, 0.1],
            }
        )

        seg = {
            "name": "Test braking segment",
            "type": "hairpin",
            "start_distance": 0,
            "end_distance": 100,
        }

        metric = metrics_for_segment(df, seg)

        self.assertIsNotNone(metric)
        self.assertAlmostEqual(
            metric.brake_start_time,
            0.5,
            places=6,
        )


if __name__ == "__main__":
    unittest.main()
