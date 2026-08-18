import tempfile
import unittest
from pathlib import Path

from racecoach.preparation import build_preparation_brief


class PreparationTests(unittest.TestCase):
    def test_brief_combines_themes_and_reflection(self):
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
  reinforcement_cue: Point, then power.

secondary:
  name: Preserve Momentum
  status: emerging
""".strip(),
                encoding="utf-8",
            )

            event_dir = project_dir / "events" / "test_event"
            event_dir.mkdir(parents=True)

            (event_dir / "event_reflection.yaml").write_text(
                """
schema_version: 1

preparation:
  visualization: true
  limited_grid_analysis: true

performance:
  focus: good

observations:
  - Stayed focused on rhythm.

breakthrough: One coaching theme helped execution.
""".strip(),
                encoding="utf-8",
            )

            brief = build_preparation_brief(project_dir)

            self.assertEqual(
                brief["primary_theme"]["name"],
                "Earlier Throttle Commitment",
            )
            self.assertEqual(
                brief["secondary_theme"]["name"],
                "Preserve Momentum",
            )
            self.assertEqual(
                brief["reflection_event"],
                "test_event",
            )
            self.assertTrue(
                brief["preparation"]["visualization"]
            )
            self.assertEqual(
                brief["performance"]["focus"],
                "good",
            )
            self.assertEqual(
                brief["breakthrough"],
                "One coaching theme helped execution.",
            )

    def test_brief_handles_missing_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)

            brief = build_preparation_brief(project_dir)

            self.assertIsNone(
                brief["primary_theme"]
            )
            self.assertIsNone(
                brief["reflection_event"]
            )
            self.assertEqual(
                brief["observations"],
                [],
            )


if __name__ == "__main__":
    unittest.main()
