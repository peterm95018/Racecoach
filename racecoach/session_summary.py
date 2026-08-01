from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path


def fmt(value, suffix=""):
    if value is None:
        return ""
    return f"{value:+.2f}{suffix}"


def short_run_name(source: str) -> str:
    stem = Path(source).stem
    parts = stem.split("_")

    for part in parts:
        if part.startswith("lap"):
            return part

    return stem


def analyzed_duration(data: dict) -> float | None:
    metrics = data.get("metrics", [])

    if metrics:
        end_time = metrics[-1].get("end_time")

        if end_time is not None:
            return float(end_time)

    run = data.get("run") or {}
    duration = run.get("analyzed_duration_s")

    if duration is not None:
        return float(duration)

    return None


def segment_durations(data: dict) -> dict[str, float]:
    durations = {}

    for metric in data.get("metrics", []):
        name = metric.get("name")
        duration = metric.get("duration")

        if name and duration is not None:
            durations[name] = float(duration)

    return durations


def consistency_interpretation(
    best_repeat_gap: float | None,
    top_three_spread: float | None,
) -> str:
    if best_repeat_gap is None:
        return "Not enough analyzed runs to assess repeatability."

    if (
        best_repeat_gap <= 0.20
        and (top_three_spread is None or top_three_spread <= 0.50)
    ):
        return "Strong repeatability near the session best."

    if (
        best_repeat_gap <= 0.50
        and (top_three_spread is None or top_three_spread <= 1.00)
    ):
        return (
            "Good repeatability, with some remaining variation between "
            "the quickest runs."
        )

    return (
        "The session best was not yet repeatable; prioritize reproducing "
        "the fastest run before adding more pace."
    )


def load_summaries(reports_dir: Path):
    summaries = []

    for path in sorted(reports_dir.glob("*_summary.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        summaries.append((path, data))

    return summaries


def main():
    active_event_file = Path("active_event.txt")

    if not active_event_file.exists():
        raise SystemExit("active_event.txt not found")

    active_event = active_event_file.read_text(encoding="utf-8").strip()

    if not active_event:
        raise SystemExit("active_event.txt is empty")

    event_dir = Path("events") / active_event
    reports_dir = event_dir / "reports"

    if not reports_dir.exists():
        raise SystemExit(f"Reports directory not found: {reports_dir}")

    summaries = load_summaries(reports_dir)

    if not summaries:
        raise SystemExit(f"No summary JSON files found in {reports_dir}")

    run_times = []

    for path, data in summaries:
        source = data.get("source", path.name)
        duration = analyzed_duration(data)

        if duration is not None:
            run_times.append(
                {
                    "run": short_run_name(source),
                    "duration": duration,
                    "segments": segment_durations(data),
                }
            )

    run_times.sort(key=lambda item: item["duration"])

    fastest_run = run_times[0] if run_times else None
    best_repeat = run_times[1] if len(run_times) >= 2 else None

    best_repeat_gap = (
        best_repeat["duration"] - fastest_run["duration"]
        if fastest_run and best_repeat
        else None
    )

    repeatability_gaps = []

    if fastest_run and best_repeat:
        fastest_segments = fastest_run["segments"]
        repeat_segments = best_repeat["segments"]

        for segment, repeat_duration in repeat_segments.items():
            fastest_duration = fastest_segments.get(segment)

            if fastest_duration is None:
                continue

            gap = repeat_duration - fastest_duration

            if gap > 0:
                repeatability_gaps.append(
                    {
                        "segment": segment,
                        "gap": gap,
                    }
                )

    repeatability_gaps.sort(
        key=lambda item: item["gap"],
        reverse=True,
    )

    top_three_spread = None

    if len(run_times) >= 3:
        top_three_spread = (
            run_times[2]["duration"] - run_times[0]["duration"]
        )

    duration_stddev = (
        statistics.pstdev(item["duration"] for item in run_times)
        if len(run_times) >= 2
        else None
    )

    consistency_text = consistency_interpretation(
        best_repeat_gap,
        top_three_spread,
    )

    classified_runs = []

    for _, data in summaries:
        run = data.get("run") or {}
        is_clean = run.get("is_clean")

        if isinstance(is_clean, bool):
            classified_runs.append(is_clean)

    clean_run_count = sum(classified_runs)
    classified_run_count = len(classified_runs)

    clean_run_percentage = (
        clean_run_count / classified_run_count * 100.0
        if classified_run_count
        else None
    )

    rows = []
    by_segment = defaultdict(list)

    for path, data in summaries:
        source = data.get("source", path.name)

        for metric in data.get("metrics", []):
            segment = metric.get("name")

            if not segment:
                continue

            row = {
                "run": short_run_name(source),
                "segment": segment,
                "time_delta": metric.get("time_delta"),
                "exit_delta": metric.get("exit_speed_delta_mph"),
                "min_delta": metric.get("min_speed_delta_mph"),
                "avg_delta": metric.get("avg_speed_delta_mph"),
                "throttle_delta": metric.get(
                    "throttle_commit_delay_delta_s"
                ),
                "brake_delta": metric.get("brake_start_delta_s"),
            }

            rows.append(row)
            by_segment[segment].append(row)

    gains = sorted(
        [
            row
            for row in rows
            if row["time_delta"] is not None
            and row["time_delta"] < -0.15
        ],
        key=lambda row: row["time_delta"],
    )[:5]

    losses = sorted(
        [
            row
            for row in rows
            if row["time_delta"] is not None
            and row["time_delta"] > 0.25
        ],
        key=lambda row: row["time_delta"],
        reverse=True,
    )[:5]

    best_gain = gains[0] if gains else None
    best_loss = losses[0] if losses else None

    recurring_losses = []

    for segment, segment_rows in by_segment.items():
        loss_rows = [
            row
            for row in segment_rows
            if row["time_delta"] is not None
            and row["time_delta"] > 0.15
        ]

        if len(loss_rows) >= 2:
            avg_loss = (
                sum(row["time_delta"] for row in loss_rows)
                / len(loss_rows)
            )

            recurring_losses.append(
                {
                    "segment": segment,
                    "count": len(loss_rows),
                    "avg_loss": avg_loss,
                }
            )

    recurring_losses.sort(
        key=lambda item: (item["count"], item["avg_loss"]),
        reverse=True,
    )

    lines = [
        "# Session Summary",
        "",
        f"Event: `{event_dir.name}`",
        f"Runs analyzed: {len(summaries)}",
    ]

    lap_list = ", ".join(
        short_run_name(data.get("source", path.name))
        for path, data in summaries
    )

    lines.extend(
        [
            f"Runs included: {lap_list}",
            "",
            "## Session Scorecard",
            "",
        ]
    )

    if fastest_run:
        lines.append(
            f"- Fastest analyzed run: **{fastest_run['run']}** "
            f"({fastest_run['duration']:.3f}s)"
        )
    else:
        lines.append("- Fastest analyzed run: Not available")

    if best_repeat and best_repeat_gap is not None:
        lines.append(
            f"- Best repeat: **{best_repeat['run']}** "
            f"({best_repeat['duration']:.3f}s, "
            f"+{best_repeat_gap:.3f}s)"
        )
    else:
        lines.append("- Best repeat: Not enough analyzed runs")

    if top_three_spread is not None:
        lines.append(f"- Top-3 spread: {top_three_spread:.3f}s")
    else:
        lines.append("- Top-3 spread: Not enough analyzed runs")

    if duration_stddev is not None:
        lines.append(
            f"- Analyzed-run standard deviation: {duration_stddev:.3f}s"
        )
    else:
        lines.append(
            "- Analyzed-run standard deviation: Not enough analyzed runs"
        )

    if clean_run_percentage is not None:
        lines.append(
            f"- Clean-run percentage: {clean_run_percentage:.1f}% "
            f"({clean_run_count} of {classified_run_count} classified runs)"
        )
    else:
        lines.append(
            "- Clean-run percentage: Not available; no runs classified"
        )

    lines.append(
        f"- Consistency interpretation: {consistency_text}"
    )

    if repeatability_gaps:
        top_gaps = repeatability_gaps[:2]

        gap_text = " and ".join(
            f"**{item['segment']}** ({item['gap']:.2f}s)"
            for item in top_gaps
        )

        lines.append(
            f"- Repeatability gap: {best_repeat['run']} lost the most "
            f"to {fastest_run['run']} in {gap_text}."
        )
    else:
        lines.append(
            "- Repeatability gap: No comparable segment-duration gaps available."
        )

    lines.extend(
        [
            "",
            "## Session Findings",
            "",
        ]
    )

    if best_gain:
        lines.append(
            f"- Biggest segment gain vs. reference: "
            f"**{best_gain['segment']}** "
            f"({best_gain['time_delta']:+.2f}s, "
            f"{best_gain['run']})"
        )
    else:
        lines.append(
            "- Biggest segment gain vs. reference: None detected"
        )

    if best_loss:
        lines.append(
            f"- Biggest segment loss vs. reference: "
            f"**{best_loss['segment']}** "
            f"({best_loss['time_delta']:+.2f}s, "
            f"{best_loss['run']})"
        )
    else:
        lines.append(
            "- Biggest segment loss vs. reference: None detected"
        )

    if recurring_losses:
        recurring = recurring_losses[0]

        lines.append(
            f"- Recurring loss: **{recurring['segment']}** "
            f"({recurring['count']} times, "
            f"avg {recurring['avg_loss']:+.2f}s)"
        )
    else:
        lines.append("- Recurring loss: None detected")

    lines.extend(
        [
            "",
            "## Biggest Segment Gains",
            "",
        ]
    )

    if gains:
        for row in gains:
            lines.append(
                f"- **{row['segment']}**: "
                f"{fmt(row['time_delta'], 's')} "
                f"({row['run']})"
            )
    else:
        lines.append("No segment gains above threshold.")

    lines.extend(
        [
            "",
            "## Biggest Segment Losses",
            "",
        ]
    )

    if losses:
        for row in losses:
            lines.append(
                f"- **{row['segment']}**: "
                f"{fmt(row['time_delta'], 's')}, "
                f"exit {fmt(row['exit_delta'], ' mph')} "
                f"({row['run']})"
            )
    else:
        lines.append("No major segment losses above threshold.")

    lines.extend(
        [
            "",
            "## Recurring Loss Segments",
            "",
        ]
    )

    if recurring_losses:
        for recurring in recurring_losses:
            lines.append(
                f"- **{recurring['segment']}**: "
                f"{recurring['count']} losses, "
                f"avg {recurring['avg_loss']:+.2f}s"
            )
    else:
        lines.append("No recurring loss segment detected.")

    lines.extend(
        [
            "",
            "## Driver Trend",
            "",
        ]
    )

    if recurring_losses:
        recurring = recurring_losses[0]

        lines.append(
            f"Most repeated opportunity: "
            f"**{recurring['segment']}** "
            f"({recurring['count']} times, "
            f"avg {recurring['avg_loss']:+.2f}s)."
        )
    elif gains:
        lines.append(
            "Session trend: strongest repeatable gain appears in "
            f"**{gains[0]['segment']}**."
        )
    else:
        lines.append(
            "Session was consistent with no major repeated weakness."
        )

    lines.append("")

    output_path = reports_dir / "session_summary.md"
    output_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
