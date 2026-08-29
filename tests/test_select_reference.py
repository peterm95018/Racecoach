from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from racecoach.select_reference import (
    ReferenceCandidate,
    canonical_duration,
    load_candidates,
    promote_reference,
    rebuild_event,
    reconcile_live_reference,
    select_clean_reference,
    select_reference,
    update_live_reference,
    write_selection_metadata,
)

from racecoach.run_status import set_run_status
from unittest.mock import patch

class SelectReferenceTests(unittest.TestCase):
    def candidate(
        self,
        run_name: str,
        duration_s: float,
        is_clean: bool | None,
    ) -> ReferenceCandidate:
        return ReferenceCandidate(
            run_name=run_name,
            source=f"{run_name}.csv",
            csv_path=Path(f"{run_name}.csv"),
            duration_s=duration_s,
            is_clean=is_clean,
        )

    def test_live_selection_uses_fastest_clean_run(self):
        candidates = [
            self.candidate("lap1", 36.5, False),
            self.candidate("lap2", 37.4, True),
            self.candidate("lap3", 37.1, True),
            self.candidate("lap4", 36.8, None),
        ]

        selected = select_clean_reference(candidates)

        self.assertIsNotNone(selected)
        self.assertEqual(selected.run_name, "lap3")

    def test_live_selection_returns_none_without_clean_run(self):
        candidates = [
            self.candidate("lap1", 37.0, None),
            self.candidate("lap2", 36.8, False),
        ]

        selected = select_clean_reference(candidates)

        self.assertIsNone(selected)

    def test_canonical_duration_prefers_final_segment_end(self):
        data = {
            "run": {
                "analyzed_duration_s": 40.0,
            },
            "metrics": [
                {"end_time": 10.0},
                {"end_time": 37.5},
            ],
        }

        self.assertEqual(canonical_duration(data), 37.5)

    def test_canonical_duration_falls_back_to_run_duration(self):
        data = {
            "run": {
                "analyzed_duration_s": 38.25,
            },
            "metrics": [],
        }

        self.assertEqual(canonical_duration(data), 38.25)

    def test_fastest_clean_wins_over_faster_nonclean_run(self):
        candidates = [
            self.candidate("lap1", 36.0, False),
            self.candidate("lap2", 37.5, True),
            self.candidate("lap3", 37.0, None),
        ]

        selected, rule = select_reference(candidates)

        self.assertEqual(selected.run_name, "lap2")
        self.assertEqual(rule, "fastest_clean")

    def test_fastest_of_multiple_clean_runs_is_selected(self):
        candidates = [
            self.candidate("lap1", 38.0, True),
            self.candidate("lap2", 37.2, True),
            self.candidate("lap3", 37.6, True),
        ]

        selected, rule = select_reference(candidates)

        self.assertEqual(selected.run_name, "lap2")
        self.assertEqual(rule, "fastest_clean")

    def test_fastest_analyzed_is_fallback_without_clean_run(self):
        candidates = [
            self.candidate("lap1", 38.0, None),
            self.candidate("lap2", 37.1, False),
            self.candidate("lap3", 37.5, None),
        ]

        selected, rule = select_reference(candidates)

        self.assertEqual(selected.run_name, "lap2")
        self.assertEqual(rule, "fastest_analyzed_fallback")

    def test_no_candidates_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "No valid reference candidates",
        ):
            select_reference([])

    def test_load_candidates_uses_current_run_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            reports_dir = event_dir / "reports"
            uploads_dir = event_dir / "uploads"
            reports_dir.mkdir()
            uploads_dir.mkdir()

            source = uploads_dir / "lap1.csv"
            source.write_text("lap one", encoding="utf-8")

            summary = {
                "source": source.name,
                "run": {
                    "name": "lap1",
                    "analyzed_duration_s": 38.0,
                    "is_clean": None,
                },
                "metrics": [],
            }

            (reports_dir / "lap1_summary.json").write_text(
                json.dumps(summary),
                encoding="utf-8",
            )

            set_run_status(event_dir, "lap1", "clean")

            candidates = load_candidates(event_dir)

            self.assertEqual(len(candidates), 1)
            self.assertTrue(candidates[0].is_clean)

    def test_load_candidates_skips_missing_source_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            reports_dir = event_dir / "reports"
            uploads_dir = event_dir / "uploads"
            reports_dir.mkdir()
            uploads_dir.mkdir()

            (uploads_dir / "lap1.csv").write_text(
                "lap one",
                encoding="utf-8",
            )

            valid_summary = {
                "source": "lap1.csv",
                "run": {
                    "name": "lap1",
                    "analyzed_duration_s": 38.0,
                    "is_clean": True,
                },
                "metrics": [],
            }
            missing_summary = {
                "source": "lap2.csv",
                "run": {
                    "name": "lap2",
                    "analyzed_duration_s": 37.0,
                    "is_clean": True,
                },
                "metrics": [],
            }

            (reports_dir / "lap1_summary.json").write_text(
                json.dumps(valid_summary),
                encoding="utf-8",
            )
            (reports_dir / "lap2_summary.json").write_text(
                json.dumps(missing_summary),
                encoding="utf-8",
            )

            candidates = load_candidates(event_dir)

            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0].run_name, "lap1")

    def test_promotion_and_metadata_are_written(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            uploads_dir = event_dir / "uploads"
            uploads_dir.mkdir()

            source = uploads_dir / "lap4.csv"
            source.write_text("telemetry", encoding="utf-8")

            selected = ReferenceCandidate(
                run_name="lap4",
                source="lap4.csv",
                csv_path=source,
                duration_s=37.25,
                is_clean=True,
            )

            reference_path = promote_reference(
                event_dir,
                selected,
            )
            metadata_path = write_selection_metadata(
                event_dir,
                selected,
                "fastest_clean",
            )

            self.assertEqual(
                reference_path.read_text(encoding="utf-8"),
                "telemetry",
            )

            metadata = json.loads(
                metadata_path.read_text(encoding="utf-8")
            )

            self.assertEqual(metadata["run"], "lap4")
            self.assertEqual(metadata["source"], "lap4.csv")
            self.assertEqual(metadata["duration_s"], 37.25)
            self.assertEqual(
                metadata["selection_rule"],
                "fastest_clean",
            )

    def test_live_update_bootstraps_unknown_provisional_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            uploads_dir = event_dir / "uploads"
            uploads_dir.mkdir()

            source = uploads_dir / "lap1.csv"
            source.write_text("lap one", encoding="utf-8")

            candidate = ReferenceCandidate(
                run_name="lap1",
                source="lap1.csv",
                csv_path=source,
                duration_s=38.0,
                is_clean=None,
            )

            selected, changed = update_live_reference(
                event_dir,
                [candidate],
                allow_provisional=True,
            )

            self.assertEqual(selected, candidate)
            self.assertTrue(changed)
            self.assertEqual(
                (event_dir / "reference.csv").read_text(
                    encoding="utf-8"
                ),
                "lap one",
            )

            metadata = json.loads(
                (event_dir / "reference_selection.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                metadata["selection_rule"],
                "first_valid_provisional",
            )
            self.assertTrue(metadata["provisional"])
            self.assertIsNone(metadata["is_clean"])

    def test_live_update_never_bootstraps_nonclean_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            uploads_dir = event_dir / "uploads"
            uploads_dir.mkdir()

            source = uploads_dir / "lap1.csv"
            source.write_text("cone run", encoding="utf-8")

            candidate = ReferenceCandidate(
                run_name="lap1",
                source="lap1.csv",
                csv_path=source,
                duration_s=36.0,
                is_clean=False,
            )

            selected, changed = update_live_reference(
                event_dir,
                [candidate],
                allow_provisional=True,
            )

            self.assertIsNone(selected)
            self.assertFalse(changed)
            self.assertFalse(
                (event_dir / "reference.csv").exists()
            )
            self.assertFalse(
                (event_dir / "reference_selection.json").exists()
            )

    def test_reconcile_replaces_disqualified_reference_with_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            uploads_dir = event_dir / "uploads"
            uploads_dir.mkdir()

            old_source = uploads_dir / "lap1.csv"
            old_source.write_text(
                "disqualified run",
                encoding="utf-8",
            )
            new_source = uploads_dir / "lap2.csv"
            new_source.write_text(
                "unknown valid run",
                encoding="utf-8",
            )

            reference_path = event_dir / "reference.csv"
            reference_path.write_text(
                "disqualified run",
                encoding="utf-8",
            )

            disqualified = ReferenceCandidate(
                run_name="lap1",
                source="lap1.csv",
                csv_path=old_source,
                duration_s=36.0,
                is_clean=False,
            )
            provisional = ReferenceCandidate(
                run_name="lap2",
                source="lap2.csv",
                csv_path=new_source,
                duration_s=38.0,
                is_clean=None,
            )

            selected, changed = reconcile_live_reference(
                event_dir,
                [disqualified, provisional],
            )

            self.assertEqual(selected, provisional)
            self.assertTrue(changed)
            self.assertEqual(
                reference_path.read_text(encoding="utf-8"),
                "unknown valid run",
            )

    def test_reconcile_retires_disqualified_reference_without_replacement(
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            uploads_dir = event_dir / "uploads"
            uploads_dir.mkdir()

            source = uploads_dir / "lap1.csv"
            source.write_text(
                "disqualified run",
                encoding="utf-8",
            )

            reference_path = event_dir / "reference.csv"
            reference_path.write_text(
                "disqualified run",
                encoding="utf-8",
            )
            metadata_path = event_dir / "reference_selection.json"
            metadata_path.write_text(
                '{"run": "lap1"}',
                encoding="utf-8",
            )

            disqualified = ReferenceCandidate(
                run_name="lap1",
                source="lap1.csv",
                csv_path=source,
                duration_s=36.0,
                is_clean=False,
            )

            selected, changed = reconcile_live_reference(
                event_dir,
                [disqualified],
            )

            self.assertIsNone(selected)
            self.assertTrue(changed)
            self.assertFalse(reference_path.exists())
            self.assertFalse(metadata_path.exists())


    def test_unknown_run_does_not_replace_existing_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            uploads_dir = event_dir / "uploads"
            uploads_dir.mkdir()

            reference_path = event_dir / "reference.csv"
            reference_path.write_text(
                "existing reference",
                encoding="utf-8",
            )

            source = uploads_dir / "lap2.csv"
            source.write_text("unknown faster run", encoding="utf-8")

            candidate = ReferenceCandidate(
                run_name="lap2",
                source="lap2.csv",
                csv_path=source,
                duration_s=35.0,
                is_clean=None,
            )

            selected, changed = update_live_reference(
                event_dir,
                [candidate],
                allow_provisional=False,
            )

            self.assertIsNone(selected)
            self.assertFalse(changed)
            self.assertEqual(
                reference_path.read_text(encoding="utf-8"),
                "existing reference",
            )

    def test_clean_run_replaces_existing_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            uploads_dir = event_dir / "uploads"
            uploads_dir.mkdir()

            reference_path = event_dir / "reference.csv"
            reference_path.write_text(
                "old reference",
                encoding="utf-8",
            )

            source = uploads_dir / "lap3.csv"
            source.write_text("clean faster run", encoding="utf-8")

            candidate = ReferenceCandidate(
                run_name="lap3",
                source="lap3.csv",
                csv_path=source,
                duration_s=37.0,
                is_clean=True,
            )

            selected, changed = update_live_reference(
                event_dir,
                [candidate],
                allow_provisional=False,
            )

            self.assertEqual(selected, candidate)
            self.assertTrue(changed)
            self.assertEqual(
                reference_path.read_text(encoding="utf-8"),
                "clean faster run",
            )

            metadata = json.loads(
                (event_dir / "reference_selection.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                metadata["selection_rule"],
                "fastest_clean",
            )
            self.assertFalse(metadata["provisional"])
            self.assertTrue(metadata["is_clean"])

    def test_rebuild_event_includes_existing_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            uploads_dir = event_dir / "uploads"
            uploads_dir.mkdir()

            source = uploads_dir / "lap1.csv"
            source.write_text("telemetry", encoding="utf-8")
            reference_path = event_dir / "reference.csv"
            reference_path.write_text(
                "telemetry",
                encoding="utf-8",
            )

            with patch(
                "racecoach.select_reference.subprocess.run"
            ) as run_mock:
                rebuild_event(event_dir, reference_path)

            analyze_command = run_mock.call_args_list[0].args[0]

            self.assertIn("--reference", analyze_command)
            self.assertIn(
                str(reference_path),
                analyze_command,
            )

    def test_rebuild_event_omits_missing_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            event_dir = Path(temp_dir)
            uploads_dir = event_dir / "uploads"
            uploads_dir.mkdir()

            source = uploads_dir / "lap1.csv"
            source.write_text("telemetry", encoding="utf-8")

            with patch(
                "racecoach.select_reference.subprocess.run"
            ) as run_mock:
                rebuild_event(event_dir, None)

            analyze_command = run_mock.call_args_list[0].args[0]

            self.assertNotIn("--reference", analyze_command)

if __name__ == "__main__":
    unittest.main()