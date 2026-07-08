from __future__ import annotations

import json
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
    
def load_summaries(reports_dir: Path):
    summaries = []
    for path in sorted(reports_dir.glob("*_summary.json")):
        data = json.loads(path.read_text())
        summaries.append((path, data))
    return summaries


def main():
    event_dir = Path("events") / Path("active_event.txt").read_text().strip()
    reports_dir = event_dir / "reports"

    summaries = load_summaries(reports_dir)

    rows = []
    by_segment = defaultdict(list)

    for path, data in summaries:
        source = data.get("source", path.name)
        for m in data.get("metrics", []):
            row = {
                "run": short_run_name(source),
                "segment": m.get("name"),
                "time_delta": m.get("time_delta"),
                "exit_delta": m.get("exit_speed_delta_mph"),
                "min_delta": m.get("min_speed_delta_mph"),
                "avg_delta": m.get("avg_speed_delta_mph"),
                "throttle_delta": m.get("throttle_commit_delay_delta_s"),
                "brake_delta": m.get("brake_start_delta_s"),
            }
            rows.append(row)
            by_segment[row["segment"]].append(row)

    gains = sorted(
        [r for r in rows if r["time_delta"] is not None and r["time_delta"] < -0.15],
        key=lambda r: r["time_delta"],
    )[:5]

    losses = sorted(
        [r for r in rows if r["time_delta"] is not None and r["time_delta"] > 0.25],
        key=lambda r: r["time_delta"],
        reverse=True,
    )[:5]

    best_gain = gains[0] if gains else None
    best_loss = losses[0] if losses else None
    
    recurring_losses = []
    for segment, seg_rows in by_segment.items():
        loss_rows = [
            r for r in seg_rows
            if r["time_delta"] is not None and r["time_delta"] > 0.15
        ]
        if len(loss_rows) >= 2:
            avg_loss = sum(r["time_delta"] for r in loss_rows) / len(loss_rows)
            recurring_losses.append((segment, len(loss_rows), avg_loss))

    recurring_losses.sort(key=lambda x: (x[1], x[2]), reverse=True)

    lines = []
    lines.append("# Session Summary")
    lines.append("")
    lines.append(f"Event: `{event_dir.name}`")
    lines.append(f"Runs analyzed: {len(summaries)}")
    lap_list = ", ".join(
        short_run_name(data.get("source", path.name))
        for path, data in summaries
    )

    lines.append(f"Runs included: {lap_list}")
    lines.append("")

    lines.append("")
    lines.append("## Session Scorecard")
    lines.append("")

    if best_gain:
        lines.append(
            f"- Biggest improvement: **{best_gain['segment']}** "
            f"({best_gain['time_delta']:+.2f}s, {best_gain['run']})"
        )
    else:
        lines.append("- Biggest improvement: None detected")

    if best_loss:
        lines.append(
            f"- Biggest loss: **{best_loss['segment']}** "
            f"({best_loss['time_delta']:+.2f}s, {best_loss['run']})"
        )
    else:
        lines.append("- Biggest loss: None detected")

    if recurring_losses:
        segment, count, avg_loss = recurring_losses[0]
        lines.append(
            f"- Recurring loss: **{segment}** "
            f"({count} times, avg {avg_loss:+.2f}s)"
        )
    else:
        lines.append("- Recurring loss: None detected")

    lines.append("")
    lines.append("## Biggest Segment Gains")
    lines.append("")
    if gains:
        for r in gains:
            lines.append(
                f"- **{r['segment']}**: {fmt(r['time_delta'], 's')} "
                f"({r['run']})"
            )
    else:
        lines.append("No segment gains above threshold.")
    lines.append("")

    lines.append("## Biggest Segment Losses")
    lines.append("")
    if losses:
        for r in losses:
            lines.append(
                f"- **{r['segment']}**: {fmt(r['time_delta'], 's')}, "
                f"exit {fmt(r['exit_delta'], ' mph')} "
                f"({r['run']})"
            )
    else:
        lines.append("No major segment losses above threshold.")
    lines.append("")

    lines.append("## Recurring Loss Segments")
    lines.append("")
    if recurring_losses:
        for segment, count, avg_loss in recurring_losses:
            lines.append(
                f"- **{segment}**: {count} losses, avg {avg_loss:+.2f}s"
            )
    else:
        lines.append("No recurring loss segment detected.")
    lines.append("")

    lines.append("## Driver Trend")
    lines.append("")
    if recurring_losses:
        segment, count, avg_loss = recurring_losses[0]
        lines.append(
            f"Most repeated opportunity: **{segment}** "
            f"({count} times, avg {avg_loss:+.2f}s)."
        )
    elif gains:
        lines.append(
            f"Session trend: strongest repeatable gain appears in "
            f"**{gains[0]['segment']}**."
        )
    else:
        lines.append("Session was consistent with no major repeated weakness.")
    lines.append("")

    out = reports_dir / "session_summary.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
