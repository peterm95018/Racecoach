from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from racecoach.run_status import (
    load_run_status,
    set_run_status,
)


class RunStatusTests(unittest.TestCase):
    def test_missing_status_file_returns_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)

            status, is_clean = load_run_status(
                event_dir,
                "lap1",
            )

            self.assertEqual(status, "unknown")
            self.assertIsNone(is_clean)

    def test_clean_status_is_written_and_loaded(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)

            status_path = set_run_status(
                event_dir,
                "lap2",
                " CLEAN ",
            )
            status, is_clean = load_run_status(
                event_dir,
                "lap2",
            )

            self.assertTrue(status_path.exists())
            self.assertEqual(status, "clean")
            self.assertTrue(is_clean)
            self.assertFalse(
                (event_dir / ".run_status.yaml.tmp").exists()
            )

    def test_nonclean_statuses_are_classified_false(self):
        for run_status in ("cone", "dnf", "off_course"):
            with self.subTest(status=run_status):
                with tempfile.TemporaryDirectory() as temp_dir:
                    event_dir = Path(temp_dir)

                    set_run_status(
                        event_dir,
                        "lap3",
                        run_status,
                    )
                    status, is_clean = load_run_status(
                        event_dir,
                        "lap3",
                    )

                    self.assertEqual(status, run_status)
                    self.assertFalse(is_clean)

    def test_updating_status_preserves_other_yaml_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            status_path = event_dir / "run_status.yaml"
            status_path.write_text(
                yaml.safe_dump(
                    {
                        "notes": "event classifications",
                        "runs": {
                            "lap1": {
                                "status": "clean",
                                "cones": 0,
                            },
                        },
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            set_run_status(
                event_dir,
                "lap2",
                "cone",
            )

            data = yaml.safe_load(
                status_path.read_text(encoding="utf-8")
            )

            self.assertEqual(
                data["notes"],
                "event classifications",
            )
            self.assertEqual(
                data["runs"]["lap1"]["status"],
                "clean",
            )
            self.assertEqual(
                data["runs"]["lap1"]["cones"],
                0,
            )
            self.assertEqual(
                data["runs"]["lap2"]["status"],
                "cone",
            )

    def test_invalid_status_is_rejected_without_writing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)

            with self.assertRaisesRegex(
                ValueError,
                "Invalid run status",
            ):
                set_run_status(
                    event_dir,
                    "lap4",
                    "maybe",
                )

            self.assertFalse(
                (event_dir / "run_status.yaml").exists()
            )

    def test_invalid_yaml_structure_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            status_path = event_dir / "run_status.yaml"
            status_path.write_text(
                "- not\n- a\n- mapping\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "Invalid run-status document",
            ):
                load_run_status(
                    event_dir,
                    "lap1",
                )


if __name__ == "__main__":
    unittest.main()
