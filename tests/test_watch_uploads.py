import json
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
    def test_failed_rebuild_restores_reference_and_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = root / "event"
            uploads_dir = event_dir / "uploads"
            reports_dir = event_dir / "reports"
            processed_dir = event_dir / "processed"
            uploads_dir.mkdir(parents=True)
            reports_dir.mkdir(parents=True)

            reference_path = event_dir / "reference.csv"
            reference_path.write_text(
                "old reference",
                encoding="utf-8",
            )

            metadata_path = (
                event_dir / "reference_selection.json"
            )
            old_metadata = '{"run": "lap1"}\n'
            metadata_path.write_text(
                old_metadata,
                encoding="utf-8",
            )

            source = uploads_dir / "lap2.csv"
            source.write_text(
                "new clean run",
                encoding="utf-8",
            )

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

            selected = SimpleNamespace(
                run_name="lap2",
                source="lap2.csv",
                duration_s=37.0,
                is_clean=True,
                csv_path=source,
            )

            with (
                patch(
                    "racecoach.watch_uploads.time.sleep"
                ),
                patch(
                    "racecoach.watch_uploads.analyze",
                    return_value=(df, [], []),
                ),
                patch(
                    "racecoach.watch_uploads.write_report",
                    return_value=(
                        reports_dir / "lap2_report.md",
                        reports_dir / "lap2_summary.json",
                    ),
                ),
                patch(
                    "racecoach.watch_uploads.load_candidates",
                    return_value=[selected],
                ),
                patch(
                    "racecoach.watch_uploads.rebuild_event",
                    side_effect=RuntimeError("rebuild failed"),
                ),
                patch(
                    "racecoach.watch_uploads."
                    "publish_reports_to_drupal"
                ) as publish_mock,
                patch(
                    "racecoach.watch_uploads."
                    "traceback.print_exc"
                ),
            ):
                handler.on_created(event)

            self.assertEqual(
                reference_path.read_text(encoding="utf-8"),
                "old reference",
            )
            self.assertEqual(
                metadata_path.read_text(encoding="utf-8"),
                old_metadata,
            )
            publish_mock.assert_not_called()

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
            source.write_text(
                "valid test data",
                encoding="utf-8",
            )

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

            def write_report_side_effect(*args, **kwargs):
                summary_path.write_text(
                    json.dumps(
                        {
                            "source": source.name,
                            "run": {
                                "name": "lap1",
                                "analyzed_duration_s": 1.0,
                                "is_clean": None,
                            },
                            "metrics": [],
                            "findings": [],
                        }
                    ),
                    encoding="utf-8",
                )
                return report_path, summary_path

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
                    side_effect=write_report_side_effect,
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
                reference_path.read_text(encoding="utf-8"),
                source.read_text(encoding="utf-8"),
            )

            metadata = json.loads(
                (
                    event_dir / "reference_selection.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                metadata["selection_rule"],
                "first_valid_provisional",
            )
            self.assertTrue(metadata["provisional"])

            analyze_mock.assert_called_once_with(
                source,
                event_dir,
                source,
            )
            publish_mock.assert_called_once()

    def test_changed_clean_reference_rebuilds_before_publish(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = root / "event"
            uploads_dir = event_dir / "uploads"
            reports_dir = event_dir / "reports"
            processed_dir = event_dir / "processed"
            uploads_dir.mkdir(parents=True)
            reports_dir.mkdir(parents=True)

            reference_path = event_dir / "reference.csv"
            reference_path.write_text(
                "old reference",
                encoding="utf-8",
            )

            source = uploads_dir / "lap2.csv"
            source.write_text(
                "new clean run",
                encoding="utf-8",
            )

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

            selected = SimpleNamespace(
                run_name="lap2",
                duration_s=37.0,
                csv_path=source,
            )
            call_order = []

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
                    return_value=(
                        reports_dir / "lap2_report.md",
                        reports_dir / "lap2_summary.json",
                    ),
                ),
                patch(
                    "racecoach.watch_uploads.load_candidates",
                    return_value=[selected],
                ),
                patch(
                    "racecoach.watch_uploads."
                    "update_live_reference",
                    return_value=(selected, True),
                ) as update_mock,
                patch(
                    "racecoach.watch_uploads.rebuild_event",
                    side_effect=lambda *args: call_order.append(
                        "rebuild"
                    ),
                ) as rebuild_mock,
                patch(
                    "racecoach.watch_uploads."
                    "publish_reports_to_drupal",
                    side_effect=lambda *args: call_order.append(
                        "publish"
                    ),
                ),
            ):
                handler.on_created(event)

            analyze_mock.assert_called_once_with(
                source,
                event_dir,
                reference_path,
            )
            update_mock.assert_called_once_with(
                event_dir,
                [selected],
                allow_provisional=False,
            )
            rebuild_mock.assert_called_once_with(
                event_dir,
                reference_path,
            )
            self.assertEqual(
                call_order,
                ["rebuild", "publish"],
            )

if __name__ == "__main__":
    unittest.main()