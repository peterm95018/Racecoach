import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from racecoach import cli


class ThemesCommandTests(unittest.TestCase):
    def test_themes_command_displays_driver_themes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            driver_dir = project_dir / "driver"
            driver_dir.mkdir()

            (driver_dir / "coaching_themes.yaml").write_text(
                """
schema_version: 1

primary:
  name: Earlier Throttle Commitment
  status: active
  priority: 1
  started: 2026-08-17
  practice_objective: Commit earlier.
  reinforcement_cue: Point, then power.

secondary:
  name: Preserve Momentum
  status: emerging
  priority: 2

completed:
  - name: Driver Consistency
    completed: 2026-07-12

future_candidates:
  - Protect Exit Speed
""".strip(),
                encoding="utf-8",
            )

            output = io.StringIO()

            with patch.object(
                cli,
                "project_root",
                return_value=project_dir,
            ):
                with redirect_stdout(output):
                    cli.themes_command()

            text = output.getvalue()

            self.assertIn(
                "Earlier Throttle Commitment",
                text,
            )
            self.assertIn(
                "Preserve Momentum",
                text,
            )
            self.assertIn(
                "Driver Consistency",
                text,
            )
            self.assertIn(
                "Protect Exit Speed",
                text,
            )
            self.assertIn(
                "Point, then power.",
                text,
            )

    def test_themes_command_handles_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            output = io.StringIO()

            with patch.object(
                cli,
                "project_root",
                return_value=project_dir,
            ):
                with redirect_stdout(output):
                    cli.themes_command()

            self.assertIn(
                "No driver/coaching_themes.yaml found.",
                output.getvalue(),
            )


if __name__ == "__main__":
    unittest.main()
