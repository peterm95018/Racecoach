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

    def test_main_forwards_timing_runs_option(self):
        event_dir = Path("/tmp/test-event")
        args = SimpleNamespace(
            command="timing",
            event=event_dir,
            show_runs=True,
        )

        with (
            patch.object(cli, "build_parser") as build_parser,
            patch.object(
                cli,
                "resolve_event",
                return_value=event_dir,
            ),
            patch.object(cli, "timing_command") as timing_command,
        ):
            build_parser.return_value.parse_args.return_value = args
            cli.main()

        timing_command.assert_called_once_with(
            event_dir,
            show_runs=True,
        )

    def test_parser_accepts_timing_runs(self):
        parser = cli.build_parser()
        args = parser.parse_args(["timing", "--runs"])

        self.assertEqual(args.command, "timing")
        self.assertTrue(args.show_runs)

    def test_timing_command_displays_driver_runs(self):
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
            result = SimpleNamespace(
                car_number="353",
                car_class="P-05",
                car_name="2013 Porsche Carrera S",
                runs=(
                    SimpleNamespace(
                        index=1,
                        time_s=38.653,
                        adjusted_time_s=38.653,
                        status="clean",
                    ),
                    SimpleNamespace(
                        index=2,
                        time_s=38.016,
                        adjusted_time_s=39.016,
                        status="cone",
                    ),
                ),
            )

            with (
                patch.object(
                    cli,
                    "load_event_timing",
                    return_value=timing,
                ),
                patch.object(
                    cli,
                    "fetch_driver_result",
                    return_value=result,
                ) as fetch,
                redirect_stdout(output),
            ):
                cli.timing_command(
                    event_dir,
                    show_runs=True,
                )

            fetch.assert_called_once_with(
                timing.results_url,
                "353",
            )

            text = output.getvalue()
            self.assertIn("Car: 353", text)
            self.assertIn("Class: P-05", text)
            self.assertIn("38.653", text)
            self.assertIn("clean", text)
            self.assertIn("39.016", text)
            self.assertIn("cone", text)

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
