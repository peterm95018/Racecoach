#!/usr/bin/env python3

"""
Extract a regression fixture from a RaceCoach summary.

Typical usage:

    python3 -m tools.extract_fixture \
        events/.../session_summary.json \
        "Finish section"

"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from racecoach.analyze_run import (
    SegmentMetric,
    diagnose_segment,
)


def load_summary(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Unable to read summary: {path}: {exc}") from exc


def find_metric(summary: dict, segment_name: str) -> dict:
    metrics = summary.get("metrics") or []

    matches = [
        metric
        for metric in metrics
        if metric.get("name") == segment_name
    ]

    if not matches:
        available = sorted(
            metric.get("name", "<unnamed>")
            for metric in metrics
        )

        print(f"Segment not found: {segment_name}")
        print()
        print("Available segments:")
        for name in available:
            print(f"  {name}")

        raise SystemExit(1)

    if len(matches) > 1:
        raise SystemExit(
            f"Multiple metrics found for segment: {segment_name}"
        )

    return matches[0]


def build_fixture(
    summary_path: Path,
    summary: dict,
    metric_data: dict,
) -> dict:
    metric = SegmentMetric(**metric_data)
    diagnosis = diagnose_segment(metric)

    source_run = (
        summary.get("run", {}).get("name")
        or summary.get("source")
        or summary_path.stem
    )

    fixture = {
        "name": f"{source_run} — {metric.name}",
        "source": {
            "event": summary_path.parent.parent.name,
            "summary": summary_path.name,
            "run": source_run,
            "segment": metric.name,
        },
        "metric": metric_data,
        "expected": {
            "diagnosis": diagnosis.name,
            "confidence": diagnosis.confidence,
            "evidence": diagnosis.evidence,
            "cue": diagnosis.cue,
            "action": diagnosis.action,
        },
    }

    return fixture


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Extract a historical RaceCoach diagnosis fixture "
            "from a summary JSON file."
        )
    )

    parser.add_argument(
        "summary",
        type=Path,
        help="Path to *_summary.json",
    )

    parser.add_argument(
        "segment",
        help="Exact segment name",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write fixture JSON to this path instead of stdout",
    )

    args = parser.parse_args()

    summary = load_summary(args.summary)
    metric_data = find_metric(summary, args.segment)

    fixture = build_fixture(
        args.summary,
        summary,
        metric_data,
    )

    text = json.dumps(
        fixture,
        indent=2,
        sort_keys=False,
    ) + "\n"

    if args.output:
        args.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.output.write_text(
            text,
            encoding="utf-8",
        )
        print(f"Wrote: {args.output}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
