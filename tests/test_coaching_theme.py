import unittest

from racecoach.coaching_theme import CoachingTheme


class CoachingThemeTests(unittest.TestCase):
    def test_active_theme_can_be_created(self):
        theme = CoachingTheme(
            name="Earlier Throttle Commitment",
            status="active",
            priority=1,
            occurrence_count=6,
            event_count=3,
            cumulative_opportunity_s=1.8,
        )

        self.assertEqual(
            theme.name,
            "Earlier Throttle Commitment",
        )
        self.assertEqual(theme.status, "active")
        self.assertEqual(theme.priority, 1)

    def test_new_theme_defaults_to_no_history(self):
        theme = CoachingTheme(
            name="Preserve Momentum",
            status="emerging",
        )

        self.assertEqual(theme.occurrence_count, 0)
        self.assertEqual(theme.event_count, 0)
        self.assertEqual(
            theme.cumulative_opportunity_s,
            0.0,
        )
        self.assertEqual(theme.evidence, [])

    def test_theme_evidence_is_not_shared(self):
        first = CoachingTheme(
            name="Earlier Throttle Commitment",
            status="active",
        )
        second = CoachingTheme(
            name="Protect Exit Speed",
            status="emerging",
        )

        first.evidence.append("Late to Power observed")

        self.assertEqual(second.evidence, [])


if __name__ == "__main__":
    unittest.main()