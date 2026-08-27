import unittest

import pandas as pd

from racecoach.data_quality import (
    DataQualityError,
    validate_segment_coverage,
)


class SegmentCoverageTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "distance": [0.0, 200.0, 400.0, 600.0, 748.0],
            }
        )
        self.segments = [
            {
                "name": "Opening",
                "start_distance": 0,
                "end_distance": 250,
            },
            {
                "name": "Middle",
                "start_distance": 250,
                "end_distance": 500,
            },
            {
                "name": "Finish",
                "start_distance": 500,
                "end_distance": 748,
            },
        ]

    def test_complete_contiguous_coverage_passes(self):
        result = validate_segment_coverage(
            self.df,
            self.segments,
            label="lap9",
        )

        self.assertEqual(result.lap_distance_m, 748.0)
        self.assertEqual(result.configured_finish_m, 748.0)

    def test_incomplete_course_coverage_is_rejected(self):
        segments = [
            {
                "name": "Opening",
                "start_distance": 0,
                "end_distance": 250,
            },
            {
                "name": "Finish",
                "start_distance": 250,
                "end_distance": 520,
            },
        ]

        with self.assertRaisesRegex(
            DataQualityError,
            "227.5m short|228.0m short",
        ):
            validate_segment_coverage(self.df, segments, label="lap9")

    def test_gap_between_segments_is_rejected(self):
        segments = [dict(segment) for segment in self.segments]
        segments[1]["start_distance"] = 260

        with self.assertRaisesRegex(DataQualityError, "10.0m gap"):
            validate_segment_coverage(self.df, segments)

    def test_overlap_between_segments_is_rejected(self):
        segments = [dict(segment) for segment in self.segments]
        segments[1]["start_distance"] = 240

        with self.assertRaisesRegex(DataQualityError, "10.0m overlap"):
            validate_segment_coverage(self.df, segments)

    def test_nonzero_course_start_is_rejected(self):
        segments = [dict(segment) for segment in self.segments]
        segments[0]["start_distance"] = 20

        with self.assertRaisesRegex(
            DataQualityError,
            "starts at 20.0m",
        ):
            validate_segment_coverage(self.df, segments)

    def test_small_finish_distance_variation_passes(self):
        segments = [dict(segment) for segment in self.segments]
        segments[-1]["end_distance"] = 735

        result = validate_segment_coverage(self.df, segments)

        self.assertEqual(result.configured_finish_m, 735.0)

    def test_numbered_lap_distance_cannot_be_hidden_by_trim(self):
        df = pd.DataFrame(
            {
                "distance": [0.0, 130.0, 260.0, 390.0, 520.0],
            }
        )
        segments = [
            {
                "name": "First half",
                "start_distance": 0,
                "end_distance": 260,
            },
            {
                "name": "Second half",
                "start_distance": 260,
                "end_distance": 520,
            },
        ]

        with self.assertRaisesRegex(
            DataQualityError,
            "timed lap is 748.0m",
        ):
            validate_segment_coverage(
                df,
                segments,
                label="trimmed numbered lap",
                timed_lap_distance_m=748.0,
            )

if __name__ == "__main__":
    unittest.main()