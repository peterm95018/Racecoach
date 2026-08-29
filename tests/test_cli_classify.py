from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from racecoach import cli
from racecoach.run_status import load_run_status


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

    def test_classify_command_writes_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            output = io.StringIO()

            with redirect_stdout(output):
                cli.classify_command(
                    event_dir,
                    "lap3",
                    "cone",
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


if __name__ == "__main__":
    unittest.main()