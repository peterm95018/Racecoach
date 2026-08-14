import tempfile
import unittest
from pathlib import Path

from racecoach.event_reflection import load_event_reflection


class EventReflectionTests(unittest.TestCase):
    def test_missing_reflection_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            event_dir = Path(tmp)

            reflection = load_event_reflection(event_dir)

            self.assertIsNone(reflection)

    def test_reflection_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            event_dir = Path(tmp)

            (event_dir / "event_reflection.yaml").write_text(
                """
schema_version: 1

preparation:
  visualization: true
  reviewed_video: true

performance:
  focus: good

observations:
  - Stayed focused on rhythm.

breakthrough: Better preparation helped execution.
""".strip(),
                encoding="utf-8",
            )

            reflection = load_event_reflection(event_dir)

            self.assertEqual(
                reflection["schema_version"],
                1,
            )
            self.assertTrue(
                reflection["preparation"]["visualization"]
            )
            self.assertEqual(
                reflection["performance"]["focus"],
                "good",
            )
            self.assertEqual(
                reflection["observations"],
                ["Stayed focused on rhythm."],
            )
            self.assertEqual(
                reflection["breakthrough"],
                "Better preparation helped execution.",
            )

    def test_empty_reflection_uses_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            event_dir = Path(tmp)

            (event_dir / "event_reflection.yaml").write_text(
                "",
                encoding="utf-8",
            )

            reflection = load_event_reflection(event_dir)

            self.assertEqual(
                reflection["schema_version"],
                1,
            )
            self.assertEqual(
                reflection["preparation"],
                {},
            )
            self.assertEqual(
                reflection["performance"],
                {},
            )
            self.assertEqual(
                reflection["observations"],
                [],
            )
            self.assertIsNone(
                reflection["breakthrough"]
            )

    def test_invalid_observations_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            event_dir = Path(tmp)

            (event_dir / "event_reflection.yaml").write_text(
                """
observations:
  note: This should have been a list.
""".strip(),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_event_reflection(event_dir)


if __name__ == "__main__":
    unittest.main()
