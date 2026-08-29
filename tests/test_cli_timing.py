from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from racecoach import cli


class TimingCommandTests(unittest.TestCase):
    def test_parser_accepts_timing_command(self):
        parser = cli.build_parser()
        args = parser.parse_args(["timing"])

        self.assertEqual(args.command, "timing")

    def test_timing_command_displays_resolved_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            output = io.StringIO()
            timing = SimpleNamespace(
                organizer="lpr",
                profile="lpr",
                provider="clokkr",
                driver_number="353",
                results_url=(
                    "https://app.clokkr.com/results/lpr-autocross"
                ),
            )

            with (
                patch.object(
                    cli,
                    "load_event_timing",
                    return_value=timing,
                ),
                redirect_stdout(output),
            ):
                cli.timing_command(event_dir)

            text = output.getvalue()

            self.assertIn("Organizer: lpr", text)
            self.assertIn("Profile: lpr", text)
            self.assertIn("Provider: clokkr", text)
            self.assertIn("Driver number: 353", text)
            self.assertIn(
                "https://app.clokkr.com/results/lpr-autocross",
                text,
            )

    def test_timing_command_handles_unconfigured_event(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            output = io.StringIO()

            with (
                patch.object(
                    cli,
                    "load_event_timing",
                    return_value=None,
                ),
                redirect_stdout(output),
            ):
                cli.timing_command(event_dir)

            self.assertIn(
                "No live-timing configuration is available.",
                output.getvalue(),
            )


if __name__ == "__main__":
    unittest.main()
