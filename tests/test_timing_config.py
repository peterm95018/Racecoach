from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from racecoach.timing_config import (
    load_event_timing,
    load_timing_profiles,
)


class TimingConfigTests(unittest.TestCase):
    def write_event(
        self,
        event_dir: Path,
        contents: str,
    ) -> None:
        (event_dir / "event.yaml").write_text(
            contents,
            encoding="utf-8",
        )

    def test_bundled_pca_profiles_are_available(self):
        profiles = load_timing_profiles()

        self.assertEqual(
            profiles["ggr"]["results_url"],
            "https://app.clokkr.com/results/ggr-autocross",
        )
        self.assertEqual(
            profiles["lpr"]["results_url"],
            "https://app.clokkr.com/results/lpr-autocross",
        )
        self.assertEqual(
            profiles["ggr"]["driver_number"],
            353,
        )
        self.assertEqual(
            profiles["lpr"]["driver_number"],
            353,
        )

    def test_organizer_selects_shared_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            self.write_event(
                event_dir,
                "organizer: ggr\n",
            )

            timing = load_event_timing(event_dir)

            self.assertIsNotNone(timing)
            self.assertEqual(timing.profile, "ggr")
            self.assertEqual(timing.provider, "clokkr")
            self.assertEqual(timing.driver_number, "353")

    def test_explicit_profile_is_supported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            self.write_event(
                event_dir,
                """
organizer: pca
timing:
  profile: lpr
""".lstrip(),
            )

            timing = load_event_timing(event_dir)

            self.assertEqual(timing.profile, "lpr")
            self.assertEqual(
                timing.results_url,
                "https://app.clokkr.com/results/lpr-autocross",
            )

    def test_event_specific_timing_is_supported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            self.write_event(
                event_dir,
                """
organizer: gglc
timing:
  provider: clokkr
  results_url: https://app.clokkr.com/results/example-event
  driver_number: 355
""".lstrip(),
            )

            timing = load_event_timing(event_dir)

            self.assertIsNone(timing.profile)
            self.assertEqual(timing.organizer, "gglc")
            self.assertEqual(timing.driver_number, "355")

    def test_event_can_override_profile_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            self.write_event(
                event_dir,
                """
organizer: ggr
timing:
  driver_number: 999
""".lstrip(),
            )

            timing = load_event_timing(event_dir)

            self.assertEqual(timing.profile, "ggr")
            self.assertEqual(timing.driver_number, "999")

    def test_event_without_timing_returns_none(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)

            timing = load_event_timing(event_dir)

            self.assertIsNone(timing)

    def test_unknown_profile_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            self.write_event(
                event_dir,
                """timing:
                profile: missing
                """.lstrip(),
            )

            with self.assertRaisesRegex(
                ValueError,
                "unknown timing profile",
            ):
                load_event_timing(event_dir)


if __name__ == "__main__":
    unittest.main()