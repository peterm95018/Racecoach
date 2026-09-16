import tempfile
import unittest
from pathlib import Path

from racecoach.analyze_run import course_segments_configured


class CourseReadinessTests(unittest.TestCase):
    def write_segments(self, event_dir: Path, text: str) -> None:
        event_dir.mkdir(parents=True, exist_ok=True)
        (event_dir / "segments.yaml").write_text(
            text,
            encoding="utf-8",
        )

    def test_placeholder_course_is_not_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir) / "event"
            self.write_segments(
                event_dir,
                "configured: false\nsegments: []\n",
            )

            self.assertFalse(
                course_segments_configured(event_dir)
            )

    def test_explicitly_configured_course_is_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir) / "event"
            self.write_segments(
                event_dir,
                "configured: true\nsegments: []\n",
            )

            self.assertTrue(
                course_segments_configured(event_dir)
            )

    def test_legacy_course_without_flag_remains_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir) / "event"
            self.write_segments(
                event_dir,
                "segments: []\n",
            )

            self.assertTrue(
                course_segments_configured(event_dir)
            )


if __name__ == "__main__":
    unittest.main()
