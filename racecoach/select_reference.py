from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", type=Path, required=True)
    args = parser.parse_args()

    candidates = load_candidates(args.event)
    selected, selection_rule = select_reference(candidates)

    print(f"Selected run: {selected.run_name}")
    print(f"Source CSV: {selected.csv_path}")
    print(f"Duration: {selected.duration_s:.3f}s")
    print(f"Selection rule: {selection_rule}")


if __name__ == "__main__":
    main()
    