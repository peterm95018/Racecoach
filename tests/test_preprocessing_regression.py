import unittest

import pandas as pd

from racecoach.analyze_run import (
    metrics_for_segment,
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
