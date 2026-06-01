from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml

MPS_TO_MPH = 2.2369362921

@dataclass
class SegmentMetric:
    name: str
    type: str
    start_time: float
    end_time: float
    duration: float
    entry_speed_mph: float
    min_speed_mph: float
    exit_speed_mph: float
    peak_decel_g: float
    coast_time_s: float
    throttle_pickup_time: Optional[float]
    segment_distance: float

    coast_time_s: float
    throttle_pickup_time: Optional[float]
    brake_start_time: Optional[float]
    segment_distance: float

    reference_duration: Optional[float] = None
    reference_entry_speed_mph: Optional[float] = None
    reference_min_speed_mph: Optional[float] = None
    reference_exit_speed_mph: Optional[float] = None
    reference_peak_decel_g: Optional[float] = None
    reference_coast_time_s: Optional[float] = None
    reference_throttle_pickup_time: Optional[float] = None
    reference_brake_start_time: Optional[float] = None

    throttle_pickup_delta_s: Optional[float] = None
    brake_start_delta_s: Optional[float] = None

    time_delta: Optional[float] = None
    entry_speed_delta_mph: Optional[float] = None
    min_speed_delta_mph: Optional[float] = None
    exit_speed_delta_mph: Optional[float] = None
    peak_decel_delta_g: Optional[float] = None
    coast_time_delta_s: Optional[float] = None

def read_racechrono_csv(csv_path: Path) -> pd.DataFrame:
    lines = csv_path.read_text(errors="replace").splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        low = line.lower()
        if low.startswith("timestamp,") and "elapsed_time" in low and "distance_traveled" in low:
            header_idx = i
            break
    if header_idx is None:
        for i, line in enumerate(lines):
            low = line.lower()
            if "timestamp" in low and "speed" in low and "distance" in low:
                header_idx = i
                break
    if header_idx is None:
        raise ValueError("Could not find RaceChrono data header row.")
    return pd.read_csv(csv_path, skiprows=[*range(header_idx), header_idx + 1, header_idx + 2])

def unique_columns(columns):
    seen = {}
    output = []
    for c in columns:
        if c not in seen:
            seen[c] = 0
            output.append(c)
        else:
            seen[c] += 1
            output.append(f"{c}.{seen[c]}")
    return output

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = unique_columns([str(c).strip() for c in df.columns])
    out = pd.DataFrame()
    time_col = pick_existing(df, ["elapsed_time", "timestamp"])
    dist_col = pick_existing(df, ["distance_traveled"])
    speed_col = pick_existing(df, ["speed"])
    longg_col = pick_existing(df, ["longitudinal_acc"])
    latg_col = pick_existing(df, ["lateral_acc"])
    throttle_col = pick_existing(df, ["relative_throttle_pos"])
    if time_col:
        out["time_s"] = parse_numeric(df[time_col])
        out["time_s"] = out["time_s"] - out["time_s"].iloc[0]
    else:
        out["time_s"] = np.arange(len(df)) / 25.0
    if dist_col:
        out["distance"] = parse_numeric(df[dist_col])
        out["distance"] = out["distance"] - out["distance"].iloc[0]
    else:
        out["distance"] = np.nan
    if speed_col:
        speed_raw = parse_numeric(df[speed_col])
        out["speed_mph"] = speed_raw * MPS_TO_MPH if speed_raw.max(skipna=True) < 90 else speed_raw
    else:
        out["speed_mph"] = np.nan
    if out["distance"].isna().all():
        speed_mps = out["speed_mph"] / MPS_TO_MPH
        dt = out["time_s"].diff().fillna(0).clip(lower=0, upper=1)
        out["distance"] = (speed_mps * dt).cumsum()
    if out["speed_mph"].isna().all():
        dt = out["time_s"].diff().replace(0, np.nan)
        dd = out["distance"].diff()
        out["speed_mph"] = (dd / dt * MPS_TO_MPH).replace([np.inf, -np.inf], np.nan).interpolate()
    if longg_col:
        out["long_g"] = parse_numeric(df[longg_col])
    else:
        speed_mps = out["speed_mph"] / MPS_TO_MPH
        dt = out["time_s"].diff().replace(0, np.nan)
        out["long_g"] = (speed_mps.diff() / dt / 9.80665).replace([np.inf, -np.inf], np.nan)
    out["lat_g"] = parse_numeric(df[latg_col]) if latg_col else np.nan
    out["throttle"] = parse_numeric(df[throttle_col]) if throttle_col else np.nan
    out = out.replace([np.inf, -np.inf], np.nan)
    for col in ["time_s", "distance", "speed_mph", "long_g", "lat_g", "throttle"]:
        out[col] = out[col].interpolate().ffill().bfill()
    return out.dropna(subset=["time_s", "distance", "speed_mph"]).reset_index(drop=True)

def pick_existing(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    cols = list(df.columns)
    lower_to_real = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in lower_to_real:
            return lower_to_real[cand.lower()]
    for cand in candidates:
        cand_l = cand.lower()
        for c in cols:
            if cand_l in c.lower():
                return c
    return None

def parse_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")

def load_segments(event_dir: Path):
    segments_file = event_dir / "segments.yaml"
    if not segments_file.exists():
        raise FileNotFoundError(f"Missing segments file: {segments_file}")
    return yaml.safe_load(segments_file.read_text())["segments"]

def metrics_for_segment(df: pd.DataFrame, seg: dict) -> Optional[SegmentMetric]:
    part = df[(df["distance"] >= float(seg["start_distance"])) & (df["distance"] <= float(seg["end_distance"]))].copy()
    if len(part) < 5:
        return None
    n = max(3, len(part) // 10)
    entry = part.iloc[:n]["speed_mph"].mean()
    exit_ = part.iloc[-n:]["speed_mph"].mean()
    min_speed = part["speed_mph"].min()
    peak_decel = part["long_g"].min()
    if part["throttle"].notna().any():
        coast_mask = (part["throttle"] < 5) & (part["long_g"] > -0.10)
    else:
        coast_mask = (part["long_g"] > -0.10) & (part["long_g"] < 0.05)
    dt = part["time_s"].diff().fillna(0).clip(lower=0, upper=1)
    coast_time = float(dt[coast_mask].sum())
    throttle_pickup_time = None
    if part["throttle"].notna().any():
        min_idx = part["speed_mph"].idxmin()
        after_min = part.loc[min_idx:].reset_index(drop=True)

        sustained_samples = 3
        throttle_threshold = 20

    for i in range(0, len(after_min) - sustained_samples + 1):
        window = after_min.iloc[i : i + sustained_samples]
        if (window["throttle"] > throttle_threshold).all():
            candidate_time = float(window.iloc[0]["time_s"])

            # Ignore pickups that occur very late in the segment.
            # These are usually finish-line artifacts or a second throttle event.
            segment_progress = (
                candidate_time - float(part.iloc[0]["time_s"])
            ) / max(float(part.iloc[-1]["time_s"] - part.iloc[0]["time_s"]), 0.001)

            if segment_progress <= 0.80:
                throttle_pickup_time = candidate_time
                break



















    brake_start_time = None
    braking = part[part["long_g"] < -0.20]

    if len(braking):
        brake_start_time = float(braking.iloc[0]["time_s"])

    return SegmentMetric(
        name=str(seg["name"]), type=str(seg.get("type", "segment")),
        start_time=float(part.iloc[0]["time_s"]), end_time=float(part.iloc[-1]["time_s"]),
        duration=float(part.iloc[-1]["time_s"] - part.iloc[0]["time_s"]),
        entry_speed_mph=float(entry), min_speed_mph=float(min_speed), exit_speed_mph=float(exit_),
        peak_decel_g=float(peak_decel),
        coast_time_s=coast_time,
        throttle_pickup_time=throttle_pickup_time,
        brake_start_time=brake_start_time,
        segment_distance=float(part["distance"].iloc[-1] - part["distance"].iloc[0]),
    )

def attach_reference_metrics(metrics: list[SegmentMetric], ref_metrics: dict[str, SegmentMetric]) -> None:
    for m in metrics:
        r = ref_metrics.get(m.name)
        if not r:
            continue
        m.reference_duration = r.duration
        m.reference_entry_speed_mph = r.entry_speed_mph
        m.reference_min_speed_mph = r.min_speed_mph
        m.reference_exit_speed_mph = r.exit_speed_mph
        m.reference_peak_decel_g = r.peak_decel_g
        m.reference_coast_time_s = r.coast_time_s
        m.reference_throttle_pickup_time = r.throttle_pickup_time
        m.reference_brake_start_time = r.brake_start_time
        m.throttle_pickup_delta_s = (
            m.throttle_pickup_time - r.throttle_pickup_time
            if m.throttle_pickup_time is not None and r.throttle_pickup_time is not None
            else None
        )
        m.brake_start_delta_s = (
            m.brake_start_time - r.brake_start_time
            if m.brake_start_time is not None and r.brake_start_time is not None
            else None
        )

        m.time_delta = m.duration - r.duration
        m.entry_speed_delta_mph = m.entry_speed_mph - r.entry_speed_mph
        m.min_speed_delta_mph = m.min_speed_mph - r.min_speed_mph
        m.exit_speed_delta_mph = m.exit_speed_mph - r.exit_speed_mph
        m.peak_decel_delta_g = m.peak_decel_g - r.peak_decel_g
        m.coast_time_delta_s = m.coast_time_s - r.coast_time_s

def analyze(csv_path: Path, event_dir: Path, reference_path: Path | None = None):
    df = normalize_columns(read_racechrono_csv(csv_path))
    segments = load_segments(event_dir)
    metrics = [m for seg in segments if (m := metrics_for_segment(df, seg))]
    ref_path = reference_path or (event_dir / "reference.csv")
    if ref_path.exists():
        ref_df = normalize_columns(read_racechrono_csv(ref_path))
        ref_metrics = {m.name: m for seg in segments if (m := metrics_for_segment(ref_df, seg))}
        attach_reference_metrics(metrics, ref_metrics)
    findings = build_findings(metrics)
    return df, metrics, findings

def build_findings(metrics: list[SegmentMetric]):
    findings = []
    MIN_OPPORTUNITY_DELTA = 0.10
    for m in metrics:
        score = 0.0
        reasons = []
        if m.coast_time_s > 0.45:
            score += min(3.0, m.coast_time_s * 2.0)
            reasons.append(f"coasted {m.coast_time_s:.2f}s")
        if m.type in {"hairpin", "turnaround", "sweeper"} and m.peak_decel_g > -0.55:
            score += 1.5
            reasons.append(f"peak braking only {m.peak_decel_g:.2f}G")
        if m.min_speed_delta_mph is not None and m.min_speed_delta_mph < -3:
            score += abs(m.min_speed_delta_mph) * 0.4
            reasons.append(f"minimum speed {(abs(m.min_speed_delta_mph) if m.min_speed_delta_mph is not None else 0):.1f} mph below reference")
        if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph < -3:
            score += abs(m.exit_speed_delta_mph) * 0.35
            reasons.append(f"exit speed {(abs(m.exit_speed_delta_mph) if m.exit_speed_delta_mph is not None else 0):.1f} mph below reference")
        if m.time_delta is not None and m.time_delta > 0.15:
            score += m.time_delta * 4.0
            reasons.append(f"{m.time_delta:.2f}s slower than reference")
        if score > 0 and m.time_delta is not None and abs(m.time_delta) >= MIN_OPPORTUNITY_DELTA:
            findings.append({"score": score, "segment": m, "reasons": reasons, "coaching": coach_text(m)})
    return sorted(findings, key=lambda x: x["score"], reverse=True)

def coach_text(m: SegmentMetric) -> str:
    t = fmt_time(m.start_time)
    if m.time_delta is not None and m.time_delta < -0.15:
        if m.min_speed_delta_mph is not None and m.min_speed_delta_mph > 2:
            return f"{m.name} at {t}: this was a gain. You carried {m.min_speed_delta_mph:+.1f} mph more minimum speed and gained {abs(m.time_delta):.2f}s vs reference. Keep this commitment."
        return f"{m.name} at {t}: this segment gained {abs(m.time_delta):.2f}s vs reference. Keep the approach."
    if m.time_delta is not None and m.time_delta > 0.15:
        if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph < -2:
            return f"{m.name} at {t}: largest opportunity is exit commitment. You lost {m.time_delta:.2f}s and exited {(abs(m.exit_speed_delta_mph) if m.exit_speed_delta_mph is not None else 0):.1f} mph slower than reference. Open the exit earlier and stay on throttle."
        if m.min_speed_delta_mph is not None and m.min_speed_delta_mph < -2:
            return f"{m.name} at {t}: you over-slowed by {(abs(m.min_speed_delta_mph) if m.min_speed_delta_mph is not None else 0):.1f} mph and lost {m.time_delta:.2f}s. Brake/lift more decisively, then carry more speed through the middle."
        return f"{m.name} at {t}: this was {m.time_delta:.2f}s slower than reference. Look for earlier throttle or less hesitation."
    if m.type in {"hairpin", "turnaround"}:
        return f"For the {m.name} at {t}, prioritize a cleaner V-shaped rotation: brake later with a firmer initial hit, get the car turned, then unwind and accelerate sooner."
    if m.type == "sweeper":
        return f"In the {m.name} at {t}, protect momentum. Use one decisive brake/lift, avoid over-slowing, and carry earlier maintenance throttle."
    if m.type == "slalom":
        return f"In the {m.name} at {t}, commit earlier to the first cone and reduce hesitation between transitions."
    if m.type == "finish":
        return f"In the {m.name} at {t}, stay committed and avoid unnecessary lift before timing."
    return f"At {m.name} around {t}, reduce hesitation and prioritize earlier throttle commitment."

def fmt_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    sec = seconds - 60 * minutes
    return f"{minutes:02d}:{sec:06.3f}"

def fmt_optional(value, precision=2):
    if value is None:
        return ""
    return f"{value:.{precision}f}"

def delta_str(value: Optional[float], precision: int = 2) -> str:
    return "" if value is None else f"{value:+.{precision}f}"

def fmt_ref(current: float, ref: Optional[float], delta: Optional[float], unit: str, precision: int = 1) -> str:
    if ref is None or delta is None:
        return f"{current:.{precision}f} {unit}"
    return f"{current:.{precision}f} vs {ref:.{precision}f} {unit} ({delta:+.{precision}f})"

def markdown_to_html(markdown_text: str) -> str:
    import html

    body = html.escape(markdown_text)

    body = body.replace("\n# ", "\n<h1>")
    body = body.replace("\n## ", "\n<h2>")
    body = body.replace("\n### ", "\n<h3>")

    body = body.replace("\n", "<br>\n")

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>RaceCoach Report</title>
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif;
    max-width: 900px;
    margin: 40px auto;
    line-height: 1.45;
}}
pre {{
    background: #f5f5f5;
    padding: 12px;
    overflow-x: auto;
}}
</style>
</head>
<body>
<pre>{body}</pre>
</body>
</html>
"""
def write_report(
    csv_path: Path,
    reference_path: Path | None,
    metrics: list[SegmentMetric],
    findings: list[dict],
    reports_dir: Path
):
    reports_dir.mkdir(parents=True, exist_ok=True)
    stem = csv_path.stem
    md_path = reports_dir / f"{stem}_report.md"
    json_path = reports_dir / f"{stem}_summary.json"
    has_reference = any(m.time_delta is not None for m in metrics)
    lines = [f"# RaceCoach Report — {csv_path.name}", ""]
    if reference_path:
        lines.extend([
            f"Reference Run: {reference_path.name}",
            ""
        ])
    if has_reference:
        gains = sorted(
            [m for m in metrics if m.time_delta is not None and m.time_delta < 0],
            key=lambda x: x.time_delta
        )

        losses = sorted(
            [m for m in metrics if m.time_delta is not None and m.time_delta > 0],
            key=lambda x: x.time_delta,
            reverse=True
        )

        lines += ["## Run Summary", ""]

        if gains:
            g = gains[0]

            lines.append(
                f"Biggest gain: **{g.name}** ({g.time_delta:+.2f}s)"
            )

            if g.min_speed_delta_mph is not None:
                lines.append(
                    f"- Min speed: {g.min_speed_delta_mph:+.1f} mph vs reference"
                )

            if g.exit_speed_delta_mph is not None:
                lines.append(
                    f"- Exit speed: {g.exit_speed_delta_mph:+.1f} mph vs reference"
                )

            lines.append("")

        if losses:
            l = losses[0]

            lines.append(
                f"Biggest loss: **{l.name}** ({l.time_delta:+.2f}s)"
            )

            if l.min_speed_delta_mph is not None:
                lines.append(
                    f"- Min speed: {l.min_speed_delta_mph:+.1f} mph vs reference"
                )

            if l.exit_speed_delta_mph is not None:
                lines.append(
                    f"- Exit speed: {l.exit_speed_delta_mph:+.1f} mph vs reference"
                )

            lines.append("")

        lines += [
            "### Next Run Focus",
            "",
        ]

        if losses:
            l = losses[0]

            if l.exit_speed_delta_mph is not None and l.exit_speed_delta_mph < -2:
                lines.append(
                    f"1. Recover exit speed in {l.name}."
                )

            elif l.min_speed_delta_mph is not None and l.min_speed_delta_mph < -2:
                lines.append(
                    f"1. Carry more minimum speed through {l.name}."
                )

            else:
                lines.append(
                    f"1. Reduce time loss in {l.name}."
                )

        if gains:
            g = gains[0]
            lines.append(
                f"2. Repeat the approach used in {g.name}."
            )

        lines.append(
            "3. Look for earlier throttle commitment after the slowest corner."
        )

        lines += ["", "---", ""]    
    if has_reference:
        gains = sorted([m for m in metrics if m.time_delta is not None and m.time_delta < 0], key=lambda x: x.time_delta)
        losses = sorted([m for m in metrics if m.time_delta is not None and m.time_delta > 0], key=lambda x: x.time_delta, reverse=True)
        lines += ["## Top Gains vs Reference", ""]
        if gains:
            for m in gains[:3]:
                lines.append(
                    f"- **{m.name}**: {m.time_delta:+.2f}s, "
                    f"min speed {fmt_ref(m.min_speed_mph, m.reference_min_speed_mph, m.min_speed_delta_mph, 'mph')}, "
                    f"exit {fmt_ref(m.exit_speed_mph, m.reference_exit_speed_mph, m.exit_speed_delta_mph, 'mph')}, "
                    f"throttle {fmt_optional(m.throttle_pickup_time)} vs {fmt_optional(m.reference_throttle_pickup_time)} sec "
                    f"({delta_str(m.throttle_pickup_delta_s, 2)})"
                )        
        else:
            lines.append("- No faster segments vs reference.")
        lines += ["", "## Top Losses vs Reference", ""]
        if losses:
            for m in losses[:3]:
                lines.append(
                f"- **{m.name}**: {m.time_delta:+.2f}s, "
                f"min speed {fmt_ref(m.min_speed_mph, m.reference_min_speed_mph, m.min_speed_delta_mph, 'mph')}, "
                f"exit {fmt_ref(m.exit_speed_mph, m.reference_exit_speed_mph, m.exit_speed_delta_mph, 'mph')}, "
                f"throttle {fmt_optional(m.throttle_pickup_time)} vs {fmt_optional(m.reference_throttle_pickup_time)} sec "
                f"({delta_str(m.throttle_pickup_delta_s, 2)})"
            )
        else:
            lines.append("- No slower segments vs reference.")
        lines.append("")
    lines += ["## Top 3 Opportunities", ""]
    if not findings:
        lines.append("No high-confidence opportunities detected. Check segment definitions and reference run.")
    else:
        for i, f in enumerate(findings[:3], start=1):
            m = f["segment"]
            lines += [
                f"### {i}. {m.name} — {fmt_time(m.start_time)}", "", f["coaching"], "", "**Telemetry:**",
                f"- Throttle pickup: {fmt_optional(m.throttle_pickup_time)} vs {fmt_optional(m.reference_throttle_pickup_time)} sec ({delta_str(m.throttle_pickup_delta_s, 2)})",
                f"- Duration: {fmt_ref(m.duration, m.reference_duration, m.time_delta, 'sec', 2)}",
                f"- Entry speed: {fmt_ref(m.entry_speed_mph, m.reference_entry_speed_mph, m.entry_speed_delta_mph, 'mph')}",
                f"- Minimum speed: {fmt_ref(m.min_speed_mph, m.reference_min_speed_mph, m.min_speed_delta_mph, 'mph')}",
                f"- Exit speed: {fmt_ref(m.exit_speed_mph, m.reference_exit_speed_mph, m.exit_speed_delta_mph, 'mph')}",
                f"- Peak braking/decel: {fmt_ref(m.peak_decel_g, m.reference_peak_decel_g, m.peak_decel_delta_g, 'G', 2)}",
                f"- Coast time: {fmt_ref(m.coast_time_s, m.reference_coast_time_s, m.coast_time_delta_s, 'sec', 2)}",
                f"- Why flagged: {', '.join(f['reasons'])}", "",
            ]
    lines += [
    "",
    "## Segment Table",
    "",
    "| Segment | Δ Time | Min Δ | Exit Δ | Brake Δ | Thr Δ | Notes |",
    "|---|---:|---:|---:|---:|---:|---|",
]
    for m in metrics:
        notes = []
            

        if m.throttle_pickup_time is not None:
            notes.append(f"thr={m.throttle_pickup_time:.1f}")
        
        if m.time_delta is not None and m.time_delta > 0:
            notes.append("loss")
        elif m.time_delta is not None and m.time_delta < 0:
            notes.append("gain")

        if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph < -2:
            notes.append("exit speed down")

        if m.brake_start_delta_s is not None:
            if m.brake_start_delta_s > 0.20:
                notes.append("braked later")
            elif m.brake_start_delta_s < -0.20:
                notes.append("braked earlier")

        if m.throttle_pickup_delta_s is not None:
            if abs(m.throttle_pickup_delta_s) > 2.0:
                notes.append("throttle delta suspect")
            elif m.throttle_pickup_delta_s > 0.25:
                notes.append("throttle later")
            elif m.throttle_pickup_delta_s < -0.25:
                notes.append("throttle earlier")

        lines.append(
            f"| {m.name} | "
            f"{delta_str(m.time_delta, 2)} | "
            f"{delta_str(m.min_speed_delta_mph, 1)} | "
            f"{delta_str(m.exit_speed_delta_mph, 1)} | "
            f"{delta_str(m.brake_start_delta_s, 2)} | "
            f"{delta_str(m.throttle_pickup_delta_s, 2)} | "
            f"{', '.join(notes)} |"
        )

        report_text = "\n".join(lines)

    md_path.write_text(report_text)

    html_path = reports_dir / f"{stem}_report.html"
    html_path.write_text(markdown_to_html(report_text))

    latest_path = reports_dir / "latest_report.md"
    latest_path.write_text(report_text)

    latest_html_path = reports_dir / "latest_report.html"
    latest_html_path.write_text(markdown_to_html(report_text))

    summary = {"source": csv_path.name, "metrics": [asdict(m) for m in metrics], "findings": [{"score": f["score"], "segment": f["segment"].name, "reasons": f["reasons"], "coaching": f["coaching"]} for f in findings]}
    json_path.write_text(json.dumps(summary, indent=2))

    return md_path, json_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--reports", type=Path, default=Path("reports"))
    args = parser.parse_args()
    _, metrics, findings = analyze(args.csv, args.event, args.reference)
    md, js = write_report(
    args.csv,
    args.reference,
    metrics,
    findings,
    args.reports
)
    print(md.read_text())
    print(f"\nWrote: {md}")
    print(f"Wrote: {js}")

if __name__ == "__main__":
    main()
