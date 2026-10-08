import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import yaml

from racecoach.analyze_run import analyze


class RaceChronoIntegrationTests(unittest.TestCase):
    def make_event(self, root: Path, configured: bool) -> Path:
        event_dir = root / "event"
        reports_dir = event_dir / "reports"
        event_dir.mkdir(parents=True)
        reports_dir.mkdir()

        (event_dir / "event.yaml").write_text(
            "organizer: test\n",
            encoding="utf-8",
        )

        (event_dir / "segments.yaml").write_text(
            yaml.safe_dump(
                {
                    "configured": configured,
                    "segments": [
                        {
                            "name": "Start -> Finish",
                            "start_distance": 0.0,
                            "end_distance": 100.0,
                        }
                    ],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        return event_dir

    def make_df(self) -> pd.DataFrame:
        df = pd.DataFrame(
            {
                "time_s": [0.0, 1.0, 2.0, 3.0, 4.0],
                "distance": [0.0, 25.0, 50.0, 75.0, 100.0],
                "speed_mph": [20.0, 30.0, 35.0, 30.0, 20.0],
                "long_g": [0.0] * 5,
                "lat_g": [0.0] * 5,
                "throttle": [0.0, 50.0, 100.0, 50.0, 0.0],
                "latitude": [
                    37.0000,
                    37.0002,
                    37.0004,
                    37.0006,
                    37.0008,
                ],
                "longitude": [-121.0] * 5,
            }
        )
        df.attrs["numbered_timed_lap_selected"] = True
        return df

    def test_unconfigured_run_invokes_racechrono_calibration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = self.make_event(root, configured=False)
            csv_path = root / "lap1.csv"
            csv_path.write_text("test", encoding="utf-8")

            df = self.make_df()

            generated_segments = [
                {
                    "name": "Start -> Finish",
                    "start_distance": 0.0,
                    "end_distance": 100.0,
                }
            ]

            def fake_calibration(event, source, run_df):
                config = {
                    "configured": True,
                    "source": "racechrono",
                    "track_file": "track.rcz",
                    "calibrated_from": source.name,
                    "segments": generated_segments,
                }
                (event / "segments.yaml").write_text(
                    yaml.safe_dump(config, sort_keys=False),
                    encoding="utf-8",
                )
                return generated_segments

            with (
                patch(
                    "racecoach.analyze_run.read_racechrono_csv",
                    return_value=pd.DataFrame(),
                ),
                patch(
                    "racecoach.analyze_run.select_timed_lap_rows",
                    return_value=pd.DataFrame(),
                ),
                patch(
                    "racecoach.analyze_run.normalize_columns",
                    return_value=df,
                ),
                patch(
                    "racecoach.analyze_run.trim_prestart_staging",
                    return_value=df,
                ),
                patch(
                    "racecoach.analyze_run.calibrate_course_from_racechrono",
                    side_effect=fake_calibration,
                ) as calibrate_mock,
            ):
                result_df, metrics, findings = analyze(
                    csv_path,
                    event_dir,
                    csv_path,
                )

            calibrate_mock.assert_called_once()

            config = yaml.safe_load(
                (event_dir / "segments.yaml").read_text()
            )

            self.assertTrue(config["configured"])
            self.assertEqual(config["source"], "racechrono")
            self.assertEqual(
                config["calibrated_from"],
                "lap1.csv",
            )
            self.assertEqual(len(metrics), 1)
            self.assertEqual(len(result_df), 5)

    def test_configured_run_does_not_recalibrate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = self.make_event(root, configured=True)
            csv_path = root / "lap2.csv"
            csv_path.write_text("test", encoding="utf-8")

            df = self.make_df()

            with (
                patch(
                    "racecoach.analyze_run.read_racechrono_csv",
                    return_value=pd.DataFrame(),
                ),
                patch(
                    "racecoach.analyze_run.select_timed_lap_rows",
                    return_value=pd.DataFrame(),
                ),
                patch(
                    "racecoach.analyze_run.normalize_columns",
                    return_value=df,
                ),
                patch(
                    "racecoach.analyze_run.trim_prestart_staging",
                    return_value=df,
                ),
                patch(
                    "racecoach.analyze_run.calibrate_course_from_racechrono",
                ) as calibrate_mock,
            ):
                result_df, metrics, findings = analyze(
                    csv_path,
                    event_dir,
                    csv_path,
                )

            calibrate_mock.assert_not_called()
            self.assertEqual(len(metrics), 1)
            self.assertEqual(len(result_df), 5)


    def test_missing_rcz_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = self.make_event(root, configured=False)
            csv_path = root / "lap1.csv"
            csv_path.write_text("test", encoding="utf-8")

            df = self.make_df()

            from racecoach.analyze_run import (
                DataQualityError,
                calibrate_course_from_racechrono,
            )

            with self.assertRaisesRegex(
                DataQualityError,
                "no RaceChrono track file",
            ):
                calibrate_course_from_racechrono(
                    event_dir,
                    csv_path,
                    df,
                )

            config = yaml.safe_load(
                (event_dir / "segments.yaml").read_text()
            )
            self.assertFalse(config["configured"])

    def test_multiple_rcz_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = self.make_event(root, configured=False)
            csv_path = root / "lap1.csv"
            csv_path.write_text("test", encoding="utf-8")

            (event_dir / "track1.rcz").write_bytes(b"test")
            (event_dir / "track2.rcz").write_bytes(b"test")

            df = self.make_df()

            from racecoach.analyze_run import (
                DataQualityError,
                calibrate_course_from_racechrono,
            )

            with self.assertRaisesRegex(
                DataQualityError,
                "multiple RaceChrono track files",
            ):
                calibrate_course_from_racechrono(
                    event_dir,
                    csv_path,
                    df,
                )

            config = yaml.safe_load(
                (event_dir / "segments.yaml").read_text()
            )
            self.assertFalse(config["configured"])

    def test_calibration_error_is_data_quality_failure_and_stays_unconfigured(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = self.make_event(root, configured=False)
            csv_path = root / "lap1.csv"
            csv_path.write_text("test", encoding="utf-8")
            (event_dir / "track.rcz").write_bytes(b"test")

            df = self.make_df()

            from racecoach.analyze_run import (
                DataQualityError,
                calibrate_course_from_racechrono,
            )
            from racecoach.racechrono_track import TrackCalibrationError

            with patch(
                "racecoach.analyze_run.load_racechrono_track",
                side_effect=TrackCalibrationError("bad track"),
            ):
                with self.assertRaisesRegex(
                    DataQualityError,
                    "RaceChrono course calibration failed: bad track",
                ):
                    calibrate_course_from_racechrono(
                        event_dir,
                        csv_path,
                        df,
                    )

            config = yaml.safe_load(
                (event_dir / "segments.yaml").read_text()
            )
            self.assertFalse(config["configured"])

if __name__ == "__main__":
    unittest.main()
