import unittest

from racecoach.analyze_run import (
    SegmentMetric,
    build_findings,
    diagnose_segment,
)


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
    def test_over_slowing_high_confidence(self):
        # Based on LPR AM lap2 Finish section.
        m = metric(
            name="Finish section",
            time_delta=0.65,
            entry_speed_delta_mph=-5.8,
            min_speed_delta_mph=-7.4,
            exit_speed_delta_mph=-4.0,
            avg_speed_delta_mph=-4.6,
        )

        diagnosis = diagnose_segment(m)

        self.assertEqual(diagnosis.name, "Over Slowing")
        self.assertEqual(diagnosis.confidence, "High")
        self.assertIn("Minimum speed", diagnosis.evidence[0])
        self.assertEqual(
            diagnosis.cue,
            "You over-slowed the car.",
        )

    def test_late_to_power_high_confidence(self):
        m = metric(
            name="Launch / first element",
            time_delta=0.50,
            throttle_commit_delay_delta_s=0.96,
            exit_speed_delta_mph=-1.0,
            min_speed_delta_mph=0.0,
            avg_speed_delta_mph=-0.5,
        )

        diagnosis = diagnose_segment(m)

        self.assertEqual(diagnosis.name, "Late to Power")
        self.assertEqual(diagnosis.confidence, "High")
        self.assertIn("Power commitment", diagnosis.evidence[0])
        self.assertEqual(
            diagnosis.cue,
            "You waited too long to get back to power.",
        )

    def test_weak_exit_high_confidence(self):
        # Based on the historical Crows Finish acceleration pattern.
        m = metric(
            name="Finish acceleration",
            time_delta=1.42,
            entry_speed_delta_mph=3.0,
            min_speed_delta_mph=-1.5,
            exit_speed_delta_mph=-8.9,
            avg_speed_delta_mph=-4.3,
        )

        diagnosis = diagnose_segment(m)

        self.assertEqual(diagnosis.name, "Weak Exit")
        self.assertEqual(diagnosis.confidence, "High")
        self.assertIn("Exit speed", diagnosis.evidence[0])
        self.assertEqual(
            diagnosis.cue,
            "You gave away speed on the exit.",
        )

    def test_momentum_loss_medium_confidence(self):
        m = metric(
            name="Flowing section",
            time_delta=0.50,
            entry_speed_delta_mph=-1.0,
            min_speed_delta_mph=-1.0,
            exit_speed_delta_mph=0.0,
            avg_speed_delta_mph=-5.2,
        )

        diagnosis = diagnose_segment(m)

        self.assertEqual(diagnosis.name, "Momentum Loss")
        self.assertEqual(diagnosis.confidence, "Medium")
        self.assertIn("Average speed", diagnosis.evidence[0])
        self.assertEqual(
            diagnosis.cue,
            "You lost speed through the whole section.",
        )

    def test_no_clear_diagnosis_is_low_confidence(self):
        m = metric(
            time_delta=0.20,
            entry_speed_delta_mph=-0.2,
            min_speed_delta_mph=-0.2,
            exit_speed_delta_mph=-0.2,
            avg_speed_delta_mph=-0.2,
            throttle_commit_delay_delta_s=0.05,
            brake_start_delta_s=0.05,
        )

        diagnosis = diagnose_segment(m)

        self.assertEqual(diagnosis.name, "No Clear Diagnosis")
        self.assertEqual(diagnosis.confidence, "Low")

    def test_contradictory_timing_loss_is_low_confidence(self):
        m = metric(
            time_delta=0.40,
            entry_speed_delta_mph=1.0,
            min_speed_delta_mph=1.0,
            exit_speed_delta_mph=1.0,
            avg_speed_delta_mph=1.0,
        )

        diagnosis = diagnose_segment(m)

        self.assertEqual(diagnosis.name, "Low Confidence")
        self.assertEqual(diagnosis.confidence, "Low")
        self.assertIn(
            "conflict",
            diagnosis.evidence[0].lower(),
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
