import unittest

import pandas as pd

from racecoach.data_quality import (
    DataQualityError,
    validate_course_geometry,
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


class CourseGeometryTests(unittest.TestCase):
    def setUp(self):
        self.reference = pd.DataFrame(
            {
                "latitude": [
                    36.66000, 36.66010, 36.66020, 36.66030, 36.66040,
                    36.66050, 36.66060, 36.66070, 36.66080, 36.66090,
                ],
                "longitude": [-121.61000] * 10,
                "distance": [
                    0.0, 11.1, 22.2, 33.3, 44.4,
                    55.5, 66.6, 77.7, 88.8, 99.9,
                ],
            }
        )

    def test_matching_course_geometry_passes(self):
        lap = self.reference.copy()
        lap["longitude"] = lap["longitude"] + 0.00001

        result = validate_course_geometry(
            lap,
            self.reference,
            label="matching lap",
            downsample=1,
        )

        self.assertLess(result.p95_error_m, 5.0)
        self.assertEqual(result.far_sample_ratio, 0.0)

    def test_course_subset_is_rejected(self):
        # Every point in this shorter lap lies exactly on the reference,
        # so a one-way lap-to-reference check would incorrectly pass it.
        lap = self.reference.iloc[:6].copy()

        with self.assertRaisesRegex(
            DataQualityError,
            "course geometry does not match",
        ):
            validate_course_geometry(
                lap,
                self.reference,
                label="shorter course",
                downsample=1,
                p95_error_limit_m=20.0,
                far_error_m=20.0,
                far_sample_ratio_limit=0.05,
            )

    def test_large_course_divergence_is_rejected(self):
        lap = self.reference.copy()

        lap.loc[8:, "longitude"] = (
            lap.loc[8:, "longitude"] + 0.00070
        )

        with self.assertRaisesRegex(
            DataQualityError,
            "course geometry does not match",
        ):
            validate_course_geometry(
                lap,
                self.reference,
                label="mismatched lap",
                downsample=1,
                p95_error_limit_m=20.0,
                far_error_m=20.0,
                far_sample_ratio_limit=0.05,
            )


if __name__ == "__main__":
    unittest.main()
