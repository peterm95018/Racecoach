import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from racecoach.data_quality import DataQualityError
from racecoach.watch_uploads import (
    UploadHandler,
    write_data_quality_failure_reports,
)


class WatchUploadTests(unittest.TestCase):
    def test_failure_report_replaces_latest_and_grid_coaching(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = Path(temp_dir)
            source = reports_dir / "lap2.csv"
            error = DataQualityError(
                "segment coverage ends at 520.0m "
                "but timed lap is 748.0m"
            )

            latest_path, grid_path = (
                write_data_quality_failure_reports(
                    source,
                    reports_dir,
                    error,
                )
            )

            self.assertTrue(latest_path.exists())
            self.assertTrue(grid_path.exists())
            self.assertIn(
                "No coaching generated",
                latest_path.read_text(),
            )
            self.assertIn(
                "segment coverage ends at 520.0m",
                latest_path.read_text(),
            )
            self.assertIn(
                "Do not use coaching from the previous run",
                grid_path.read_text(),
            )
            self.assertTrue(
                (reports_dir / "latest_report.html").exists()
            )
            self.assertTrue(
                (reports_dir / "grid_report.html").exists()
            )

    def test_invalid_first_upload_does_not_become_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = root / "event"
            uploads_dir = event_dir / "uploads"
            reports_dir = event_dir / "reports"
            processed_dir = event_dir / "processed"
            uploads_dir.mkdir(parents=True)

            source = uploads_dir / "lap1.csv"
            source.write_text("invalid test data")

            handler = UploadHandler(
                event_dir,
                reports_dir,
                processed_dir,
            )
            event = SimpleNamespace(
                is_directory=False,
                src_path=str(source),
            )

            error = DataQualityError(
                "segment coverage is incomplete"
            )

            with (
                patch(
                    "racecoach.watch_uploads.time.sleep"
                ),
                patch(
                    "racecoach.watch_uploads.analyze",
                    side_effect=error,
                ) as analyze_mock,
                patch(
                    "racecoach.watch_uploads."
                    "publish_reports_to_drupal"
                ) as publish_mock,
            ):
                handler.on_created(event)

            self.assertFalse(
                (event_dir / "reference.csv").exists()
            )
            self.assertIn(
                "DATA INVALID",
                (reports_dir / "grid_report.md").read_text(),
            )
            analyze_mock.assert_called_once_with(
                source,
                event_dir,
                source,
            )
            publish_mock.assert_called_once()

    def test_valid_first_upload_becomes_reference_after_analysis(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = root / "event"
            uploads_dir = event_dir / "uploads"
            reports_dir = event_dir / "reports"
            processed_dir = event_dir / "processed"
            uploads_dir.mkdir(parents=True)
            reports_dir.mkdir(parents=True)

            source = uploads_dir / "lap1.csv"
            source.write_text("valid test data")

            handler = UploadHandler(
                event_dir,
                reports_dir,
                processed_dir,
            )
            event = SimpleNamespace(
                is_directory=False,
                src_path=str(source),
            )

            df = pd.DataFrame(
                {
                    "time_s": [0.0, 1.0],
                }
            )
            df.attrs["driver_input_source"] = "accelerator_pos"

            report_path = reports_dir / "lap1_report.md"
            summary_path = reports_dir / "lap1_summary.json"

            with (
                patch(
                    "racecoach.watch_uploads.time.sleep"
                ),
                patch(
                    "racecoach.watch_uploads.analyze",
                    return_value=(df, [], []),
                ) as analyze_mock,
                patch(
                    "racecoach.watch_uploads.write_report",
                    return_value=(report_path, summary_path),
                ),
                patch(
                    "racecoach.watch_uploads."
                    "publish_reports_to_drupal"
                ) as publish_mock,
            ):
                handler.on_created(event)

            reference_path = event_dir / "reference.csv"

            self.assertTrue(reference_path.exists())
            self.assertEqual(
                reference_path.read_text(),
                source.read_text(),
            )
            analyze_mock.assert_called_once_with(
                source,
                event_dir,
                source,
            )
            publish_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()