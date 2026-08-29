from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from racecoach import cli
from racecoach.run_status import load_run_status
from types import SimpleNamespace
from unittest.mock import patch

class ClassifyCommandTests(unittest.TestCase):
    def test_parser_accepts_run_classification(self):
        parser = cli.build_parser()

        args = parser.parse_args(
            [
                "classify",
                "lap2",
                "clean",
            ]
        )

        self.assertEqual(args.command, "classify")
        self.assertEqual(args.run, "lap2")
        self.assertEqual(args.status, "clean")
        self.assertTrue(args.reprocess)

    def test_classify_command_writes_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            output = io.StringIO()

            with redirect_stdout(output):
                cli.classify_command(
                    event_dir,
                    "lap3",
                    "cone",
                    reprocess=False,
                )

            status, is_clean = load_run_status(
                event_dir,
                "lap3",
            )

            self.assertEqual(status, "cone")
            self.assertFalse(is_clean)
            self.assertIn(
                "Classified lap3 as cone.",
                output.getvalue(),
            )
            self.assertIn(
                "run_status.yaml",
                output.getvalue(),
            )

    def test_parser_accepts_no_reprocess(self):
        parser = cli.build_parser()

        args = parser.parse_args(
            [
                "classify",
                "lap2",
                "clean",
                "--no-reprocess",
            ]
        )

        self.assertFalse(args.reprocess)

    def test_classification_rebuilds_then_publishes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            reference_path = event_dir / "reference.csv"
            reference_path.write_text(
                "reference telemetry",
                encoding="utf-8",
            )

            candidate = SimpleNamespace(
                run_name="lap3",
                duration_s=37.0,
            )
            call_order = []

            with (
                patch.object(
                    cli,
                    "load_candidates",
                    return_value=[candidate],
                ) as load_mock,
                patch.object(
                    cli,
                    "reconcile_live_reference",
                    return_value=(candidate, False),
                ) as reconcile_mock,
                patch.object(
                    cli,
                    "rebuild_event",
                    side_effect=lambda *args: call_order.append(
                        "rebuild"
                    ),
                ) as rebuild_mock,
                patch.object(
                    cli,
                    "publish_command",
                    side_effect=lambda *args: call_order.append(
                        "publish"
                    ),
                ) as publish_mock,
            ):
                cli.classify_command(
                    event_dir,
                    "lap3",
                    "clean",
                )

            status, is_clean = load_run_status(
                event_dir,
                "lap3",
            )

            self.assertEqual(status, "clean")
            self.assertTrue(is_clean)
            self.assertEqual(load_mock.call_count, 2)
            reconcile_mock.assert_called_once_with(
                event_dir,
                [candidate],
            )
            rebuild_mock.assert_called_once_with(
                event_dir,
                reference_path,
            )
            publish_mock.assert_called_once_with(event_dir)
            self.assertEqual(
                call_order,
                ["rebuild", "publish"],
            )


    def test_failed_rebuild_restores_status_and_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            reference_path = event_dir / "reference.csv"
            metadata_path = (
                event_dir / "reference_selection.json"
            )

            cli.set_run_status(
                event_dir,
                "lap3",
                "cone",
            )
            reference_path.write_text(
                "old reference",
                encoding="utf-8",
            )
            metadata_path.write_text(
                '{"run": "lap1"}',
                encoding="utf-8",
            )

            candidate = SimpleNamespace(
                run_name="lap3",
                duration_s=37.0,
            )

            def change_reference(*args):
                reference_path.write_text(
                    "new reference",
                    encoding="utf-8",
                )
                metadata_path.write_text(
                    '{"run": "lap3"}',
                    encoding="utf-8",
                )
                return candidate, True

            with (
                patch.object(
                    cli,
                    "load_candidates",
                    return_value=[candidate],
                ),
                patch.object(
                    cli,
                    "reconcile_live_reference",
                    side_effect=change_reference,
                ),
                patch.object(
                    cli,
                    "rebuild_event",
                    side_effect=RuntimeError("rebuild failed"),
                ),
                patch.object(
                    cli,
                    "publish_command",
                ) as publish_mock,
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "rebuild failed",
                ):
                    cli.classify_command(
                        event_dir,
                        "lap3",
                        "clean",
                    )

            status, is_clean = load_run_status(
                event_dir,
                "lap3",
            )

            self.assertEqual(status, "cone")
            self.assertFalse(is_clean)
            self.assertEqual(
                reference_path.read_text(encoding="utf-8"),
                "old reference",
            )
            self.assertEqual(
                metadata_path.read_text(encoding="utf-8"),
                '{"run": "lap1"}',
            )
            publish_mock.assert_not_called()

    def test_unknown_run_is_rejected_without_writing_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)

            with patch.object(
                cli,
                "load_candidates",
                return_value=[],
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "no analyzed run was found",
                ):
                    cli.classify_command(
                        event_dir,
                        "lap99",
                        "clean",
                    )

            self.assertFalse(
                (event_dir / "run_status.yaml").exists()
            )

if __name__ == "__main__":
    unittest.main()