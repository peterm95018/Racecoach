import json
import unittest
from pathlib import Path

from racecoach.analyze_run import (
    SegmentMetric,
    build_findings,
    diagnose_segment,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "diagnosis"


def metric(**overrides) -> SegmentMetric:
    """Create a SegmentMetric with neutral defaults."""
    values = {
        "name": "Test segment",
        "type": "segment",
        "start_time": 0.0,
        "end_time": 5.0,
        "duration": 5.0,
        "entry_speed_mph": 40.0,
        "min_speed_mph": 30.0,
        "exit_speed_mph": 40.0,
        "avg_speed_mph": 35.0,
        "peak_decel_g": -0.5,
        "coast_time_s": 0.0,
        "throttle_pickup_time": None,
        "segment_distance": 100.0,
        "brake_start_time": None,
    }

    values.update(overrides)
    return SegmentMetric(**values)


class DiagnosisRegressionTests(unittest.TestCase):
    def test_diagnosis_fixtures(self):
        fixture_paths = sorted(FIXTURE_DIR.glob("*.json"))

        self.assertTrue(
            fixture_paths,
            "No diagnosis regression fixtures found",
        )

        for path in fixture_paths:
            with self.subTest(fixture=path.name):
                data = json.loads(path.read_text())

                m = metric(**data["metric"])
                diagnosis = diagnose_segment(m)
                expected = data["expected"]

                self.assertEqual(
                    diagnosis.name,
                    expected["diagnosis"],
                )
                self.assertEqual(
                    diagnosis.confidence,
                    expected["confidence"],
                )

                evidence_contains = expected.get(
                    "evidence_contains"
                )
                if evidence_contains:
                    self.assertIn(
                        evidence_contains.lower(),
                        diagnosis.evidence[0].lower(),
                    )

                expected_cue = expected.get("cue")
                if expected_cue:
                    self.assertEqual(
                        diagnosis.cue,
                        expected_cue,
                    )

    def test_low_confidence_loss_is_not_a_finding(self):
        m = metric(
            time_delta=0.20,
            entry_speed_delta_mph=-0.2,
            min_speed_delta_mph=-0.2,
            exit_speed_delta_mph=-0.2,
            avg_speed_delta_mph=-0.2,
        )

        findings = build_findings([m])

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
