from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ReferenceCandidate:
    run_name: str
    source: str
    csv_path: Path
    duration_s: float
    is_clean: bool | None


def canonical_duration(data: dict) -> float | None:
    """
    Return the timed course duration represented by the summary.

    Prefer the final segment end time so summaries from different analyzer
    versions remain comparable. Fall back to the run-level duration only when
    segment timing is unavailable.
    """
    metrics = data.get("metrics") or []

    if metrics:
        end_time = metrics[-1].get("end_time")

        if end_time is not None:
            return float(end_time)

    run = data.get("run") or {}
    duration = run.get("analyzed_duration_s")

    if duration is not None:
        return float(duration)

    return None


def load_candidates(event_dir: Path) -> list[ReferenceCandidate]:
    reports_dir = event_dir / "reports"
    uploads_dir = event_dir / "uploads"

    candidates = []

    for summary_path in sorted(reports_dir.glob("*_summary.json")):
        data = json.loads(summary_path.read_text(encoding="utf-8"))

        source = data.get("source")
        run = data.get("run") or {}
        duration = canonical_duration(data)

        if not source or duration is None:
            continue

        csv_path = uploads_dir / source

        if not csv_path.exists():
            continue

        candidates.append(
            ReferenceCandidate(
                run_name=str(run.get("name") or Path(source).stem),
                source=source,
                csv_path=csv_path,
                duration_s=duration,
                is_clean=run.get("is_clean"),
            )
        )

    return candidates


def select_reference(
    candidates: list[ReferenceCandidate],
) -> tuple[ReferenceCandidate, str]:
    if not candidates:
        raise ValueError("No valid reference candidates found")

    clean_candidates = [
        candidate
        for candidate in candidates
        if candidate.is_clean is True
    ]

    if clean_candidates:
        selected = min(
            clean_candidates,
            key=lambda candidate: candidate.duration_s,
        )
        return selected, "fastest_clean"

    selected = min(
        candidates,
        key=lambda candidate: candidate.duration_s,
    )
    return selected, "fastest_analyzed_fallback"

def promote_reference(
    event_dir: Path,
    selected: ReferenceCandidate,
) -> Path:
    reference_path = event_dir / "reference.csv"
    shutil.copy2(selected.csv_path, reference_path)
    return reference_path


def write_selection_metadata(
    event_dir: Path,
    selected: ReferenceCandidate,
    selection_rule: str,
) -> Path:
    metadata_path = event_dir / "reference_selection.json"

    metadata = {
        "run": selected.run_name,
        "source": selected.source,
        "duration_s": selected.duration_s,
        "selection_rule": selection_rule,
        "selected_at": datetime.now(timezone.utc).isoformat(),
    }

    metadata_path.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    return metadata_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument(
        "--promote",
        action="store_true",
        help="Copy the selected run to event/reference.csv",
    )
    args = parser.parse_args()

    candidates = load_candidates(args.event)
    selected, selection_rule = select_reference(candidates)

    print(f"Selected run: {selected.run_name}")
    print(f"Source CSV: {selected.csv_path}")
    print(f"Duration: {selected.duration_s:.3f}s")
    print(f"Selection rule: {selection_rule}")

    if args.promote:
        reference_path = promote_reference(args.event, selected)
        metadata_path = write_selection_metadata(
            args.event,
            selected,
            selection_rule,
        )

        print(f"Updated reference: {reference_path}")
        print(f"Wrote selection metadata: {metadata_path}")
    else:
        print("Dry run only; reference.csv was not changed.")


if __name__ == "__main__":
    main()

