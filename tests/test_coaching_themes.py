import tempfile
import unittest
from pathlib import Path

from racecoach.coaching_themes import load_coaching_themes


class CoachingThemesLoaderTests(unittest.TestCase):
    def test_missing_file_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)

            self.assertIsNone(
                load_coaching_themes(project_dir)
            )

    def test_themes_load(self):
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

secondary:
  name: Preserve Momentum
  status: emerging
  priority: 2

completed:
  - name: Driver Consistency
""".strip(),
                encoding="utf-8",
            )

            data = load_coaching_themes(project_dir)

            self.assertEqual(
                data["primary"]["name"],
                "Earlier Throttle Commitment",
            )
            self.assertEqual(
                data["primary"]["status"],
                "active",
            )
            self.assertEqual(
                data["secondary"]["status"],
                "emerging",
            )
            self.assertEqual(
                data["completed"][0]["name"],
                "Driver Consistency",
            )

    def test_invalid_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            driver_dir = project_dir / "driver"
            driver_dir.mkdir()

            (driver_dir / "coaching_themes.yaml").write_text(
                """
primary:
  name: Test Theme
  status: unknown
""".strip(),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_coaching_themes(project_dir)


if __name__ == "__main__":
    unittest.main()
