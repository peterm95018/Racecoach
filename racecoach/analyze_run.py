from __future__ import annotations

import os
import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml
import markdown
from racecoach.event_config import load_event_config

from racecoach.reference_path import (
    add_gps_path_position,
    project_lap_to_reference,
)

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
    avg_speed_mph: float
    peak_decel_g: float
    coast_time_s: float
    throttle_pickup_time: Optional[float]
    segment_distance: float

    coast_time_s: float
    throttle_pickup_time: Optional[float]
    brake_start_time: Optional[float]
    brake_start_distance: Optional[float]
    segment_distance: float
    recovery_speed_1s_mph: Optional[float] = None

    reference_duration: Optional[float] = None
    reference_entry_speed_mph: Optional[float] = None
    reference_min_speed_mph: Optional[float] = None
    reference_exit_speed_mph: Optional[float] = None
    reference_avg_speed_mph: Optional[float] = None
    reference_peak_decel_g: Optional[float] = None
    reference_coast_time_s: Optional[float] = None
    reference_throttle_pickup_time: Optional[float] = None
    reference_brake_start_time: Optional[float] = None

    throttle_pickup_delta_s: Optional[float] = None
    brake_start_delta_s: Optional[float] = None
    reference_recovery_speed_1s_mph: Optional[float] = None
    recovery_speed_delta_mph: Optional[float] = None

    brake_start_distance: Optional[float] = None
    reference_brake_start_distance: Optional[float] = None
    brake_start_distance_delta: Optional[float] = None

    time_delta: Optional[float] = None
    entry_speed_delta_mph: Optional[float] = None
    min_speed_delta_mph: Optional[float] = None
    exit_speed_delta_mph: Optional[float] = None
    avg_speed_delta_mph: Optional[float] = None
    peak_decel_delta_g: Optional[float] = None
    coast_time_delta_s: Optional[float] = None

    recovery_speed_1s_mph: float | None = None
    recovery_speed_2s_mph: float | None = None
    recovery_gain_1s_mph: float | None = None
    recovery_gain_2s_mph: float | None = None

    recovery_gain_1s_delta_mph: float | None = None
    recovery_gain_2s_delta_mph: float | None = None

    throttle_commit_delay_s: Optional[float] = None
    reference_throttle_commit_delay_s: Optional[float] = None

    throttle_commit_delay_s: Optional[float] = None
    reference_throttle_commit_delay_s: Optional[float] = None
    throttle_commit_delay_delta_s: Optional[float] = None


@dataclass
class Diagnosis:
    name: str
    confidence: str
    evidence: list[str]
    action: str
    cue: str
    confidence_reason: str

@dataclass
class DiagnosisScore:
    name: str
    score: int
    evidence: list[str]
    contributions: list[str]


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
    throttle_col = pick_existing(df, ["accelerator_pos", "relative_throttle_pos", "throttle_pos"])

    out.attrs["driver_input_source"] = throttle_col or "none"
    if throttle_col:
        print(f"Using driver input channel: {throttle_col}")
        

    lat_col = pick_existing(df, ["latitude"])
    lon_col = pick_existing(df, ["longitude"])
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
    out["latitude"] = parse_numeric(df[lat_col]) if lat_col else np.nan
    out["longitude"] = parse_numeric(df[lon_col]) if lon_col else np.nan
    out = out.replace([np.inf, -np.inf], np.nan)
    for col in ["time_s", "distance", "speed_mph", "long_g", "lat_g", "throttle", "latitude", "longitude"]:
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

def load_segment_config(event_dir: Path):
    segments_file = event_dir / "segments.yaml"
    if not segments_file.exists():
        raise FileNotFoundError(f"Missing segments file: {segments_file}")
    return yaml.safe_load(segments_file.read_text())


def load_segments(event_dir: Path):
    return load_segment_config(event_dir)["segments"]


VALID_RUN_STATUSES = {
    "clean",
    "cone",
    "dnf",
    "off_course",
    "unknown",
}


def load_run_status(
    event_dir: Path,
    run_name: str,
) -> tuple[str, bool | None]:
    status_file = event_dir / "run_status.yaml"

    if not status_file.exists():
        return "unknown", None

    data = yaml.safe_load(
        status_file.read_text(encoding="utf-8")
    ) or {}

    run_data = (data.get("runs") or {}).get(run_name) or {}
    status = str(run_data.get("status", "unknown")).strip().lower()

    if status not in VALID_RUN_STATUSES:
        raise ValueError(
            f"Invalid run status {status!r} for {run_name} "
            f"in {status_file}"
        )

    if status == "clean":
        return status, True

    if status in {"cone", "dnf", "off_course"}:
        return status, False

    return "unknown", None


def metrics_for_segment(df: pd.DataFrame, seg: dict) -> Optional[SegmentMetric]:
    if "start_distance" not in seg or "end_distance" not in seg:
        return None

    start_distance = float(seg["start_distance"])
    end_distance = float(seg["end_distance"])

    part = df[
        (df["distance"] >= start_distance) &
        (df["distance"] <= end_distance)
    ].copy()

    debug_segments = bool(df.attrs.get("debug_segments", False))
    segment_name = str(seg.get("name", "Unnamed segment"))

    if debug_segments:
        print(
            f"SEGMENT DEBUG: {segment_name}: "
            f"range={start_distance:.1f}-{end_distance:.1f}, "
            f"samples={len(part)}"
        )

    if len(part) < 5:
        if debug_segments:
            print(f"SEGMENT DEBUG: {segment_name}: skipped, not enough samples")
        return None

    if debug_segments:
        duration_debug = float(part.iloc[-1]["time_s"] - part.iloc[0]["time_s"])
        msg = (
            f"SEGMENT DEBUG: {segment_name}: "
            f"time={float(part.iloc[0]['time_s']):.2f}-{float(part.iloc[-1]['time_s']):.2f}s, "
            f"duration={duration_debug:.2f}s"
        )
        msg += (
            f", projected_range={float(part['distance'].min()):.1f}-"
            f"{float(part['distance'].max()):.1f}m"
        )
        if "ref_error_m" in part.columns:
            msg += (
                f", ref_error_avg={float(part['ref_error_m'].mean()):.2f}m, "
                f"ref_error_max={float(part['ref_error_m'].max()):.2f}m"
            )
        print(msg)

    n = max(3, len(part) // 10)
    entry = part.iloc[:n]["speed_mph"].mean()
    exit_ = part.iloc[-n:]["speed_mph"].mean()
    avg_speed = part["speed_mph"].mean()
    min_speed = part["speed_mph"].min()
    peak_decel = part["long_g"].min()
    if part["throttle"].notna().any():
        coast_mask = (part["throttle"] < 5) & (part["long_g"] > -0.10)
    else:
        coast_mask = (part["long_g"] > -0.10) & (part["long_g"] < 0.05)
    dt = part["time_s"].diff().fillna(0).clip(lower=0, upper=1)
    coast_time = float(dt[coast_mask].sum())
    throttle_pickup_time = None
    min_idx = part["speed_mph"].idxmin()
    min_speed_time = float(part.loc[min_idx, "time_s"])
    min_time = float(part.loc[min_idx, "time_s"])
    min_speed = float(part.loc[min_idx, "speed_mph"])

    recovery_speed_1s_mph = None
    recovery_speed_2s_mph = None
    recovery_gain_1s_mph = None
    recovery_gain_2s_mph = None

    recovery_1s = part[part["time_s"] >= (min_time + 1.0)]
    if len(recovery_1s):
        recovery_speed_1s_mph = float(recovery_1s.iloc[0]["speed_mph"])
        recovery_gain_1s_mph = recovery_speed_1s_mph - min_speed

    recovery_2s = part[part["time_s"] >= (min_time + 2.0)]
    if len(recovery_2s):
        recovery_speed_2s_mph = float(recovery_2s.iloc[0]["speed_mph"])
        recovery_gain_2s_mph = recovery_speed_2s_mph - min_speed

    if part["throttle"].notna().any():
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
    brake_start_distance = None

    min_idx = part["speed_mph"].idxmin()
    before_min = part.loc[:min_idx]
    braking = before_min[before_min["long_g"] < -0.20]

    if len(braking):
        brake_start_time = float(braking.iloc[0]["time_s"])
        brake_start_distance = float(braking.iloc[0]["distance"])




    throttle_commit_delay_s = None
    if throttle_pickup_time is not None:
        throttle_commit_delay_s = throttle_pickup_time - min_speed_time

    return SegmentMetric(
        name=str(seg["name"]),
        type=str(seg.get("type", "segment")),
        start_time=float(part.iloc[0]["time_s"]),
        end_time=float(part.iloc[-1]["time_s"]),
        duration=float(part.iloc[-1]["time_s"] - part.iloc[0]["time_s"]),
        entry_speed_mph=float(entry),
        min_speed_mph=float(min_speed),
        exit_speed_mph=float(exit_),
        avg_speed_mph=float(avg_speed),
        peak_decel_g=float(peak_decel),
        coast_time_s=coast_time,
        throttle_pickup_time=throttle_pickup_time,
        throttle_commit_delay_s=throttle_commit_delay_s,
        brake_start_time=brake_start_time,
        brake_start_distance=brake_start_distance,
        segment_distance=float(part["distance"].iloc[-1] - part["distance"].iloc[0]),
        recovery_speed_1s_mph=recovery_speed_1s_mph,
        recovery_speed_2s_mph=recovery_speed_2s_mph,
        recovery_gain_1s_mph=recovery_gain_1s_mph,
        recovery_gain_2s_mph=recovery_gain_2s_mph,
    )


def attach_reference_metrics(metrics: list[SegmentMetric], ref_metrics: dict[str, SegmentMetric]) -> None:
    for m in metrics:
        r = ref_metrics.get(m.name)
        if not r:
            continue

        m.reference_duration = r.duration
        m.time_delta = m.duration - r.duration

        m.reference_entry_speed_mph = r.entry_speed_mph
        m.reference_min_speed_mph = r.min_speed_mph
        m.reference_exit_speed_mph = r.exit_speed_mph
        m.reference_avg_speed_mph = r.avg_speed_mph
        m.reference_peak_decel_g = r.peak_decel_g
        m.reference_coast_time_s = r.coast_time_s
        m.reference_throttle_pickup_time = r.throttle_pickup_time

        m.reference_throttle_commit_delay_s = r.throttle_commit_delay_s
        if (
            m.throttle_commit_delay_s is not None
            and r.throttle_commit_delay_s is not None
        ):
            m.throttle_commit_delay_delta_s = (
                m.throttle_commit_delay_s - r.throttle_commit_delay_s
            )

        m.reference_brake_start_time = r.brake_start_time
        m.reference_brake_start_distance = r.brake_start_distance
        m.reference_recovery_speed_1s_mph = r.recovery_speed_1s_mph

        m.recovery_gain_1s_delta_mph = (
            m.recovery_gain_1s_mph - r.recovery_gain_1s_mph
            if m.recovery_gain_1s_mph is not None and r.recovery_gain_1s_mph is not None
            else None
        )

        m.recovery_gain_2s_delta_mph = (
            m.recovery_gain_2s_mph - r.recovery_gain_2s_mph
            if m.recovery_gain_2s_mph is not None and r.recovery_gain_2s_mph is not None
            else None
        )

        m.entry_speed_delta_mph = m.entry_speed_mph - r.entry_speed_mph
        m.min_speed_delta_mph = m.min_speed_mph - r.min_speed_mph
        m.exit_speed_delta_mph = m.exit_speed_mph - r.exit_speed_mph
        m.avg_speed_delta_mph = m.avg_speed_mph - r.avg_speed_mph
        m.peak_decel_delta_g = m.peak_decel_g - r.peak_decel_g
        m.coast_time_delta_s = m.coast_time_s - r.coast_time_s

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

        m.brake_start_distance_delta = (
            m.brake_start_distance - r.brake_start_distance
            if m.brake_start_distance is not None and r.brake_start_distance is not None
            else None
        )

        m.recovery_speed_delta_mph = (
            m.recovery_speed_1s_mph - r.recovery_speed_1s_mph
            if m.recovery_speed_1s_mph is not None and r.recovery_speed_1s_mph is not None
            else None
        )


def analyze(csv_path: Path, event_dir: Path, reference_path: Path | None = None):
    df = normalize_columns(read_racechrono_csv(csv_path))

    config = load_event_config(event_dir)
    mode = config.get("segmentation_mode", "distance")

    print(f"Segmentation mode: {mode}")

    segments = load_segments(event_dir)
    segment_config = load_segment_config(event_dir)

    ref_path = reference_path or (event_dir / "reference.csv")

    if mode == "reference_path" and ref_path.exists():
        print("Using reference path segmentation.")

        ref_df = normalize_columns(read_racechrono_csv(ref_path))
        ref_df = add_gps_path_position(ref_df)

        max_ref_d = float(ref_df["gps_path_m"].max())
        max_lap_d = float(df["distance"].max())

        df["ref_pos_m"] = df["distance"] / max_lap_d * max_ref_d
        df["ref_error_m"] = 0.0

        debug_segments = os.environ.get("RACECOACH_DEBUG_SEGMENTS") == "1"

        df.attrs["debug_segments"] = debug_segments
        ref_df.attrs["debug_segments"] = debug_segments

        df["raw_distance"] = df["distance"]
        ref_df["raw_distance"] = ref_df["distance"]

        df["distance"] = df["ref_pos_m"]
        ref_df["distance"] = ref_df["gps_path_m"]

        df["time_s"] = df["time_s"] - df["time_s"].iloc[0]
        ref_df["time_s"] = ref_df["time_s"] - ref_df["time_s"].iloc[0]

        max_d = float(ref_df["distance"].max())

        # Reference-path v0:
        # If segments.yaml has named segments but no distance ranges,
        # split the reference path evenly across those named segments.
        if segments and all(
            "start_distance" not in seg or "end_distance" not in seg
            for seg in segments
        ):
            width = max_d / len(segments)
            generated_segments = []
            for i, seg in enumerate(segments):
                start = i * width
                end = max_d if i == len(segments) - 1 else (i + 1) * width
                generated_segments.append(
                    {
                        **seg,
                        "start_distance": start,
                        "end_distance": end,
                    }
                )
            print("Reference path generated segment ranges:")
            for seg in generated_segments:
                print(
                    f"  {seg['name']}: "
                    f"{float(seg['start_distance']):.1f}-"
                    f"{float(seg['end_distance']):.1f}m"
                )
            segments = generated_segments

    else:
        if mode == "reference_path":
            print("WARNING: Reference path mode selected but no reference path was found.")

        start_d = float(segment_config.get("timed_start_distance", 0))
        finish_d = float(segment_config.get("timed_finish_distance", df["distance"].max()))

        df = df[
            (df["distance"] >= start_d) &
            (df["distance"] <= finish_d)
        ].copy()

        df["time_s"] = df["time_s"] - df["time_s"].iloc[0]
        df["distance"] = df["distance"] - df["distance"].iloc[0]

        ref_df = None

    metrics = [m for seg in segments if (m := metrics_for_segment(df, seg))]

    if not metrics:
        print("WARNING: No valid segments found; using default Start/Middle/Finish segments.")
        max_d = float(df["distance"].max())
        segments = [
            {"name": "Start", "start_distance": 0, "end_distance": max_d * 0.25},
            {"name": "Middle course", "start_distance": max_d * 0.25, "end_distance": max_d * 0.75},
            {"name": "Finish section", "start_distance": max_d * 0.75, "end_distance": max_d},
        ]
        metrics = [m for seg in segments if (m := metrics_for_segment(df, seg))]

    if ref_path.exists():
        if mode != "reference_path":
            ref_df = normalize_columns(read_racechrono_csv(ref_path))

            start_d = float(segment_config.get("timed_start_distance", 0))
            finish_d = float(segment_config.get("timed_finish_distance", ref_df["distance"].max()))

            ref_df = ref_df[
                (ref_df["distance"] >= start_d) &
                (ref_df["distance"] <= finish_d)
            ].copy()

            ref_df["time_s"] = ref_df["time_s"] - ref_df["time_s"].iloc[0]
            ref_df["distance"] = ref_df["distance"] - ref_df["distance"].iloc[0]

        ref_metrics = {
            m.name: m
            for seg in segments
            if (m := metrics_for_segment(ref_df, seg))
        }
        attach_reference_metrics(metrics, ref_metrics)

    findings = build_findings(metrics)
    return df, metrics, findings

def build_findings(metrics: list[SegmentMetric]):
    findings = []

    for m in metrics:
        diagnosis = diagnose_segment(m)

        if diagnosis.confidence == "Low":
            continue

        score = 0.0
        reasons = []

        if m.coast_time_s > 0.45:
            score += min(3.0, m.coast_time_s * 2.0)
            reasons.append(f"coasted {m.coast_time_s:.2f}s")

        if (
            m.type in {"hairpin", "turnaround", "sweeper"}
            and m.peak_decel_g > -0.55
        ):
            score += 1.5
            reasons.append(
                f"peak braking only {m.peak_decel_g:.2f}G"
            )

        if (
            m.min_speed_delta_mph is not None
            and m.min_speed_delta_mph < -3
        ):
            score += abs(m.min_speed_delta_mph) * 0.4
            reasons.append(
                f"minimum speed "
                f"{abs(m.min_speed_delta_mph):.1f} mph "
                f"below reference"
            )

        if (
            m.exit_speed_delta_mph is not None
            and m.exit_speed_delta_mph < -3
        ):
            score += abs(m.exit_speed_delta_mph) * 0.35
            reasons.append(
                f"exit speed "
                f"{abs(m.exit_speed_delta_mph):.1f} mph "
                f"below reference"
            )

        if m.time_delta is not None and m.time_delta > 0.10:
            score += m.time_delta * 4.0
            reasons.append(
                f"{m.time_delta:.2f}s slower than reference"
            )

        if score > 0:
            findings.append(
                {
                    "score": score,
                    "segment": m,
                    "reasons": reasons,
                    "coaching": coach_text(m),
                    "diagnosis": diagnosis,
                }
            )

    return sorted(
        findings,
        key=lambda item: item["score"],
        reverse=True,
    )

def low_confidence_loss(m: SegmentMetric) -> bool:
    if m.time_delta is None or m.time_delta <= 0.10:
        return False

    min_delta = abs(m.min_speed_delta_mph or 0)
    exit_delta = abs(m.exit_speed_delta_mph or 0)
    avg_delta = abs(m.avg_speed_delta_mph or 0)

    throttle_delta = (
        abs(m.throttle_commit_delay_delta_s)
        if m.throttle_commit_delay_delta_s is not None
        else 0
    )

    brake_delta = (
        abs(m.brake_start_delta_s)
        if m.brake_start_delta_s is not None
        else 0
    )

    return (
        min_delta < 1.0
        and exit_delta < 1.0
        and avg_delta < 2.0
        and throttle_delta < 0.10
        and brake_delta < 0.20
    )


def classify_loss(m: SegmentMetric) -> Optional[str]:
    if m.time_delta is None or m.time_delta <= 0.05:
        return None

    if (
        m.time_delta is not None
        and m.time_delta > 0.30
        and m.entry_speed_delta_mph is not None
        and m.entry_speed_delta_mph > 1.0
        and m.min_speed_delta_mph is not None
        and m.min_speed_delta_mph > 1.0
        and m.exit_speed_delta_mph is not None
        and m.exit_speed_delta_mph > 1.0
        and m.avg_speed_delta_mph is not None
        and abs(m.avg_speed_delta_mph) < 1.0
    ):
        return "unexplained timing loss"

    if (
        m.entry_speed_delta_mph is not None
        and m.entry_speed_delta_mph > 2.0
        and m.avg_speed_delta_mph is not None
        and m.avg_speed_delta_mph < -2.0
    ):
        return "over-attacked entry"

    if (
        m.min_speed_delta_mph is not None
        and m.min_speed_delta_mph < -2.0
    ):
        return "overslowed middle"

    if (
        m.exit_speed_delta_mph is not None
        and m.exit_speed_delta_mph < -2.0
    ):
        return "weak exit"

    if (
        m.throttle_commit_delay_delta_s is not None
        and m.throttle_commit_delay_delta_s > 0.25
    ):
        return "late throttle"

    if (
        m.brake_start_distance_delta is not None
        and m.brake_start_distance_delta < -15
    ):
        return "early braking"

    if (
        m.avg_speed_delta_mph is not None
        and m.avg_speed_delta_mph < -2.0
    ):
        return "low average speed"

    return "unclear"


def coach_text(m: SegmentMetric) -> str:
    t = fmt_time(m.start_time)
    cause = classify_loss(m)

    if m.time_delta is not None and m.time_delta < -0.10:
        if (
            m.brake_start_delta_s is not None
            and m.brake_start_delta_s < -0.20
            and m.min_speed_delta_mph is not None
            and m.min_speed_delta_mph > 1
            and m.exit_speed_delta_mph is not None
            and m.exit_speed_delta_mph > 1
        ):
            return (
                f"{m.name} at {t}: this was a gain. You braked "
                f"{abs(m.brake_start_delta_s):.2f}s earlier, carried "
                f"{m.min_speed_delta_mph:+.1f} mph more minimum speed, "
                f"and exited {m.exit_speed_delta_mph:+.1f} mph faster. "
                "This suggests the earlier setup improved rotation and exit."
            )

        if (
            m.throttle_commit_delay_delta_s is not None
            and m.throttle_commit_delay_delta_s < -0.25
        ):
            return (
                f"{m.name} at {t}: this was a gain. You committed to throttle "
                f"{abs(m.throttle_commit_delay_delta_s):.2f}s earlier after min speed "
                f"and gained {abs(m.time_delta):.2f}s vs reference."
            )

        if m.min_speed_delta_mph is not None and m.min_speed_delta_mph > 1:
            return (
                f"{m.name} at {t}: this was a gain. You carried "
                f"{m.min_speed_delta_mph:+.1f} mph more minimum speed and gained "
                f"{abs(m.time_delta):.2f}s vs reference."
            )

        return (
            f"{m.name} at {t}: this segment gained "
            f"{abs(m.time_delta):.2f}s vs reference. Keep the approach."
        )

    if m.time_delta is not None and m.time_delta > 0.10:
        if low_confidence_loss(m):
            return (
                f"{m.name} at {t}: this was {m.time_delta:.2f}s slower, "
                "but entry speed, minimum speed, exit speed, throttle timing, "
                "and braking were all close to reference. Treat this as normal variation."
            )
        if cause == "unexplained timing loss":
            return (
                f"{m.name} at {t}: the segment was slower, but entry speed, "
                "minimum speed, and exit speed were all as good or better than reference. "
                "Review trace alignment or segment boundaries before changing driving technique."
            )
        if cause == "over-attacked entry":
            return (
                f"{m.name} at {t}: entered faster but carried less average speed through the segment. "
                "Back up the entry, reduce the initial attack, and keep the car flowing."
            )

        if cause == "overslowed middle":
            return (
                f"{m.name} at {t}: the main loss came from overslowing the middle of the segment. "
                "Carry more speed through the center without adding steering correction."
            )

        if cause == "weak exit":
            return (
                f"{m.name} at {t}: the loss is exit-speed related. "
                "Prioritize the exit line and unwind earlier."
            )

        if cause == "late throttle":
            return (
                f"{m.name} at {t}: throttle pickup was later than reference. "
                "Finish rotation sooner and commit to throttle earlier."
            )

        if cause == "early braking":
            return (
                f"{m.name} at {t}: braking started earlier than reference and average speed suffered. "
                "Brake later or release sooner; do not slow the car before it needs it."
            )

        if cause == "low average speed":
            return (
                f"{m.name} at {t}: average speed was lower through the segment. "
                "Look for excess steering, early braking, or a line that adds distance."
            )

        exit_down = (
            m.exit_speed_delta_mph is not None
            and m.exit_speed_delta_mph < -2
        )
        min_down = (
            m.min_speed_delta_mph is not None
            and m.min_speed_delta_mph < -2
        )
        min_up = (
            m.min_speed_delta_mph is not None
            and m.min_speed_delta_mph > 1
        )
        throttle_late = (
            m.throttle_commit_delay_delta_s is not None
            and m.throttle_commit_delay_delta_s > 0.20
        )

        if min_up and exit_down:
            return (
                f"{m.name} at {t}: the loss looks like over-driving entry. "
                f"You lost {m.time_delta:.2f}s, carried "
                f"{m.min_speed_delta_mph:+.1f} mph more minimum speed, but exited "
                f"{abs(m.exit_speed_delta_mph):.1f} mph slower than reference. "
                "Give up a little entry speed, rotate once, and protect the exit."
            )

        if throttle_late and exit_down:
            return (
                f"{m.name} at {t}: the loss is late to power. "
                f"You lost {m.time_delta:.2f}s because you waited "
                f"{m.throttle_commit_delay_delta_s:.2f}s too long to get back to power "
                f"and exited {abs(m.exit_speed_delta_mph):.1f} mph slower than reference. "
                "Commit to throttle as soon as the car is pointed."
            )

        if exit_down:
            return (
                f"{m.name} at {t}: the loss is exit-speed related. You lost "
                f"{m.time_delta:.2f}s and exited "
                f"{abs(m.exit_speed_delta_mph):.1f} mph slower than reference. "
                "Prioritize the exit line and throttle commitment."
            )

        if min_down:
            return (
                f"{m.name} at {t}: you lost {m.time_delta:.2f}s and carried "
                f"{abs(m.min_speed_delta_mph):.1f} mph less minimum speed. "
                "Focus on the setup that lets the car rotate without over-slowing."
            )

        if throttle_late:
            return (
                f"{m.name} at {t}: the loss is late to power. "
                f"You waited {m.throttle_commit_delay_delta_s:.2f}s too long "
                f"to get back to power, and the segment lost {m.time_delta:.2f}s. "
                "Commit to throttle as soon as the car is pointed."
            )

        if (
            m.avg_speed_delta_mph is not None
            and m.avg_speed_delta_mph < -3
        ):
            return (
                f"{m.name} at {t}: average speed was "
                f"{abs(m.avg_speed_delta_mph):.1f} mph below reference. "
                "The loss developed through the segment rather than at the apex. "
                "Look earlier in the course for the mistake that carried into this section."
            )

        return (
            f"{m.name} at {t}: this was {m.time_delta:.2f}s slower than reference. "
            "Check whether the loss came from setup, exit speed, or throttle delay."
        )

    return (
        f"{m.name} at {t}: no strong coaching conclusion. Review the deltas before "
        "changing the driving approach."
    )

def explain_delta(m: SegmentMetric) -> str:
    reasons = []

    if m.time_delta is not None:
        if m.time_delta > 0.05:
            reasons.append(f"lost {m.time_delta:.2f}s versus reference lap")
        elif m.time_delta < -0.05:
            reasons.append(f"gained {abs(m.time_delta):.2f}s versus reference lap")

    if m.brake_start_delta_s is not None:
        if m.brake_start_delta_s < -0.20:
            reasons.append(f"braked {abs(m.brake_start_delta_s):.2f}s earlier")
        elif m.brake_start_delta_s > 0.20:
            reasons.append(f"braked {m.brake_start_delta_s:.2f}s later")

    if m.throttle_commit_delay_delta_s is not None:
        if m.throttle_commit_delay_delta_s > 0.20:
            reasons.append(
                f"waited {m.throttle_commit_delay_delta_s:.2f}s too long to get back to power"
            )
        elif m.throttle_commit_delay_delta_s < -0.20:
            reasons.append(
                f"got back to power {abs(m.throttle_commit_delay_delta_s):.2f}s sooner"
            )

    if (
        m.avg_speed_delta_mph is not None
        and m.avg_speed_delta_mph < -3
        and (
            m.exit_speed_delta_mph is None
            or abs(m.exit_speed_delta_mph) < 3
        )
    ):
        reasons.append(
            f"average speed was {abs(m.avg_speed_delta_mph):.1f} mph lower through the segment"
        )
    else:
        if m.min_speed_delta_mph is not None and abs(m.min_speed_delta_mph) > 1:
            reasons.append(f"minimum speed changed by {m.min_speed_delta_mph:+.1f} mph")

        if m.exit_speed_delta_mph is not None and abs(m.exit_speed_delta_mph) > 1:
            reasons.append(f"exit speed changed by {m.exit_speed_delta_mph:+.1f} mph")
    if m.coast_time_delta_s is not None and abs(m.coast_time_delta_s) > 0.20:
        if m.coast_time_delta_s > 0:
            reasons.append(f"coasted {m.coast_time_delta_s:.2f}s longer")
        else:
            reasons.append(f"coasted {abs(m.coast_time_delta_s):.2f}s less")

    if not reasons:
        reasons.append("flagged by combined telemetry pattern; review speed, throttle, coast time, and braking together")

    return "; ".join(reasons)

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
    body = markdown.markdown(
        markdown_text,
        extensions=["tables"]
    )

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>RaceCoach Report</title>
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif;
    max-width: 1000px;
    margin: 20px auto;
    padding: 12px;
    line-height: 1.5;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}}

th, td {{
    border: 1px solid #ccc;
    padding: 6px 10px;
    text-align: left;
}}

th {{
    background: #f5f5f5;
}}

h1 {{
    border-bottom: 2px solid #ddd;
    padding-bottom: 6px;
}}

h2 {{
    margin-top: 1.5em;
}}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def contradictory_timing_loss(m: SegmentMetric) -> bool:
    return (
        m.time_delta is not None
        and m.time_delta > 0
        and m.avg_speed_delta_mph is not None
        and m.avg_speed_delta_mph > 0
        and m.exit_speed_delta_mph is not None
        and m.exit_speed_delta_mph > 0
    )

    
def primary_action(m: SegmentMetric) -> str:
    if contradictory_timing_loss(m):
        return "Verify segment boundary or line distance before changing driving."

    if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph < -2:
        return "Unwind earlier and protect exit speed."
    if (
        m.throttle_commit_delay_delta_s is not None
        and m.throttle_commit_delay_delta_s > 0.25
    ):
        return "Finish rotation sooner and commit to throttle earlier."
    if m.min_speed_delta_mph is not None and m.min_speed_delta_mph < -2:
        return "Carry more speed without adding steering."
    if m.avg_speed_delta_mph is not None and m.avg_speed_delta_mph < -3:
        return "Look for excess steering, early braking, or extra distance."
    return "Drive it clean; no single telemetry fault stands out."


def primary_cause(m: SegmentMetric) -> str:
    if contradictory_timing_loss(m):
        return "Low Confidence"

    if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph < -2:
        return f"Weak Exit"
    if (
        m.throttle_commit_delay_delta_s is not None
        and m.throttle_commit_delay_delta_s > 0.25
    ):
        return f"Late to Power"
    
    if m.min_speed_delta_mph is not None and m.min_speed_delta_mph < -2:
        return f"Over Slowing"
    
    if (
        m.avg_speed_delta_mph is not None
        and m.avg_speed_delta_mph < -2.0
    ):
        return "Momentum Loss"
    
    return "No Clear Diagnosis"


def primary_evidence(m: SegmentMetric) -> str:
    if contradictory_timing_loss(m):
        return "Speed metrics conflict with timing loss"

    if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph < -2:
        return f"Exit speed {m.exit_speed_delta_mph:+.1f} mph"

    if (
        m.throttle_commit_delay_delta_s is not None
        and m.throttle_commit_delay_delta_s > 0.25
    ):
        return f"Power commitment {m.throttle_commit_delay_delta_s:+.2f}s"

    if m.min_speed_delta_mph is not None and m.min_speed_delta_mph < -2:
        return f"Minimum speed {m.min_speed_delta_mph:+.1f} mph"

    if m.avg_speed_delta_mph is not None:
        return f"Average speed {m.avg_speed_delta_mph:+.1f} mph"

    return "No single telemetry cause"


def clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def score_weak_exit(m: SegmentMetric) -> DiagnosisScore:
    score = 0
    evidence = []
    contributions = []

    if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph < -2.0:
        points = min(70, abs(m.exit_speed_delta_mph) * 8)
        score += points
        evidence.append(f"Exit speed {m.exit_speed_delta_mph:+.1f} mph")
        contributions.append(f"+{int(round(points))} exit speed down")

    if m.time_delta is not None and m.time_delta > 0.10:
        points = min(20, m.time_delta * 10)
        score += points
        contributions.append(f"+{int(round(points))} time loss")

    if m.min_speed_delta_mph is not None and m.min_speed_delta_mph > 0:
        score += 5
        contributions.append("+5 minimum speed maintained")

    return DiagnosisScore("Weak Exit", clamp_score(score), evidence, contributions)


def score_late_to_power(m: SegmentMetric) -> DiagnosisScore:
    score = 0
    evidence = []
    contributions = []

    if (
        m.throttle_commit_delay_delta_s is not None
        and m.throttle_commit_delay_delta_s > 0.25
    ):
        delay = m.throttle_commit_delay_delta_s
        points = min(75, delay * 150)
        score += points
        evidence.append(f"Power commitment {delay:+.2f}s")
        contributions.append(f"+{int(round(points))} delayed power commitment")

    if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph < -2.0:
        points = min(20, abs(m.exit_speed_delta_mph) * 2)
        score += points
        contributions.append(f"+{int(round(points))} exit speed down")

    if m.time_delta is not None and m.time_delta > 0.10:
        points = min(10, m.time_delta * 5)
        score += points
        contributions.append(f"+{int(round(points))} time loss")

    return DiagnosisScore("Late to Power", clamp_score(score), evidence, contributions)


def score_over_slowing(m: SegmentMetric) -> DiagnosisScore:
    score = 0
    evidence = []
    contributions = []

    if m.min_speed_delta_mph is not None and m.min_speed_delta_mph < -2.0:
        points = min(70, abs(m.min_speed_delta_mph) * 10)
        score += points
        evidence.append(f"Minimum speed {m.min_speed_delta_mph:+.1f} mph")
        contributions.append(f"+{int(round(points))} minimum speed down")

    if m.avg_speed_delta_mph is not None and m.avg_speed_delta_mph < -1.0:
        points = min(20, abs(m.avg_speed_delta_mph) * 4)
        score += points
        contributions.append(f"+{int(round(points))} average speed down")

    if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph > 1.0:
        score -= 10
        contributions.append("-10 exit speed improved")

    return DiagnosisScore("Over Slowing", clamp_score(score), evidence, contributions)


def score_momentum_loss(m: SegmentMetric) -> DiagnosisScore:
    score = 0
    evidence = []
    contributions = []

    if m.avg_speed_delta_mph is not None and m.avg_speed_delta_mph < -2.0:
        points = min(75, abs(m.avg_speed_delta_mph) * 10)
        score += points
        evidence.append(f"Average speed {m.avg_speed_delta_mph:+.1f} mph")
        contributions.append(f"+{int(round(points))} average speed down")

    if m.time_delta is not None and m.time_delta > 0.25:
        points = min(20, m.time_delta * 8)
        score += points
        contributions.append(f"+{int(round(points))} time loss")

    if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph < -2.0:
        score -= 15
        contributions.append("-15 exit speed suggests weak exit instead")

    return DiagnosisScore("Momentum Loss", clamp_score(score), evidence, contributions)


def score_diagnoses(m: SegmentMetric) -> list[DiagnosisScore]:
    scores = [
        score_weak_exit(m),
        score_late_to_power(m),
        score_over_slowing(m),
        score_momentum_loss(m),
    ]
    return sorted(scores, key=lambda item: item.score, reverse=True)


def diagnose_segment(m: SegmentMetric) -> Diagnosis:
    scores = score_diagnoses(m)
    winner = scores[0]
    runner_up = scores[1] if len(scores) > 1 else DiagnosisScore("None", 0, [], [])

    if contradictory_timing_loss(m):
        diagnosis = "Low Confidence"
        evidence = "Speed metrics conflict with timing loss"
        confidence = "Low"
        confidence_reason = "Timing loss conflicts with speed metrics."
    elif low_confidence_loss(m):
        diagnosis = "No Clear Diagnosis"
        evidence = "No telemetry metric clearly explains the loss"
        confidence = "Low"
        confidence_reason = "Telemetry is close to reference; no strong fault stands out."
    elif winner.score < 35:
        diagnosis = "No Clear Diagnosis"
        evidence = "No telemetry metric clearly explains the loss"
        confidence = "Low"
        confidence_reason = "No telemetry metric clearly explains the time loss."
    else:
        diagnosis = winner.name
        evidence = winner.evidence[0] if winner.evidence else primary_evidence(m)

        score_gap = winner.score - runner_up.score
        if winner.score >= 70 and score_gap >= 25:
            confidence = "High"
        elif winner.score >= 50:
            confidence = "Medium"
        else:
            confidence = "Low"

        contribution_text = "; ".join(winner.contributions) if winner.contributions else "no scoring details"
        confidence_reason = (
            f"{winner.name} scored {winner.score}; next closest was "
            f"{runner_up.name} at {runner_up.score}. "
            f"Scoring: {contribution_text}."
        )

    return Diagnosis(
        name=diagnosis,
        confidence=confidence,
        evidence=[evidence],
        action=primary_action(m),
        cue=driver_translation(m),
        confidence_reason=confidence_reason,
    )


def driver_translation(m: SegmentMetric) -> str:
    if contradictory_timing_loss(m):
        return "Timing loss conflicts with speed metrics; treat this as low confidence."

    if (
        m.exit_speed_delta_mph is not None
        and m.exit_speed_delta_mph < -8
        and m.throttle_commit_delay_delta_s is not None
        and m.throttle_commit_delay_delta_s > 0.30
    ):
        return "You were late getting the car pointed and late getting back to power."

    if (
        m.exit_speed_delta_mph is not None
        and m.exit_speed_delta_mph < -8
    ):
        return "You protected entry but gave away the exit."

    if (
        m.min_speed_delta_mph is not None
        and m.min_speed_delta_mph < -3
    ):
        return "You over-slowed the car."
    
    if m.avg_speed_delta_mph is not None and m.avg_speed_delta_mph < -2:
        return "You lost speed through the whole section. Clean up the line and keep the car flowing."

    return "Small loss with no clear telemetry fault. Do not chase a setup change."


def write_grid_report(
    csv_path: Path,
    reference_path: Path | None,
    metrics: list[SegmentMetric],
    findings: list[dict],
    reports_dir: Path,
):
    reports_dir.mkdir(parents=True, exist_ok=True)

    grid_md_path = reports_dir / "grid_report.md"
    grid_html_path = reports_dir / "grid_report.html"

    losses = sorted(
        [
            m for m in metrics
            if m.time_delta is not None
            and m.time_delta >= 0.25
            and diagnose_segment(m).confidence != "Low"
        ],
        key=lambda x: x.time_delta,
        reverse=True,
    )

    gains = sorted(
        [m for m in metrics if m.time_delta is not None and m.time_delta < -0.10],
        key=lambda x: x.time_delta,
    )

    lines = [
        f"# Grid Mode — {csv_path.name}",
        "",
    ]

    if reference_path:
        lines += [
            f"Reference: {reference_path.name}",
            "",
        ]

    if losses:
        m = losses[0]
        d = diagnose_segment(m)

        lines += [
            "## ONE THING TO REMEMBER",
            "",
            d.cue,
            "",
        ]

        heading = "Check" if contradictory_timing_loss(m) else "Fix"

        lines += [
            "## NEXT RUN",
            "",
            f"### {heading}: {m.name}",
            "",
            f"**Loss:** {m.time_delta:+.2f}s",
            "",
            f"**Diagnosis:** {d.name}",
            "",
            f"**Confidence:** {d.confidence}",
            "",
            f"**Evidence:** {'; '.join(d.evidence)}",
            "",
            f"**Why confidence:** {d.confidence_reason}",
            "",
            f"**Do this:** {d.action}",
            "",
        ]

        if (
            len(losses) > 1
            and losses[1].time_delta is not None
            and losses[1].time_delta >= 0.25
        ):
            m2 = losses[1]
            d2 = diagnose_segment(m2)

            lines += [
                "## SECOND PRIORITY",
                "",
                f"### {m2.name}",
                "",
                f"**Loss:** {m2.time_delta:+.2f}s",
                "",
                f"**Diagnosis:** {d2.name}",
                "",
                f"**Confidence:** {d2.confidence}",
                "",
                f"**Evidence:** {'; '.join(d2.evidence)}",
                "",
                f"**Why confidence:** {d2.confidence_reason}",
                "",
                f"**Do this:** {d2.action}",
                "",
            ]

    else:
        lines = [
            "## NEXT RUN",
            "",
            "Your gains came from executing the whole course cleanly.",
            "",
            "Repeat the same rhythm—don't search for extra speed.",
            "",
        ]
    if gains:
        g = gains[0]
        lines += [
            "## KEEP",
            "",
            f"### {g.name}",
            "",
            f"**Gain:** {g.time_delta:+.2f}s",
            "",
            "Repeat what worked here.",
            "",
        ]

    lines += [
        "---",
        "",
        "## Quick Segment Check",
        "",
        "| Segment | Δ Time | Exit Δ | Note |",
        "|---|---:|---:|---|",
    ]

    for m in metrics:
        note = ""
        if m.time_delta is not None and m.time_delta >= 0.25:
            note = "loss"
        elif m.time_delta is not None and m.time_delta <= -0.25:
            note = "gain"

        lines.append(
            f"| {m.name} | {delta_str(m.time_delta, 2)} | "
            f"{delta_str(m.exit_speed_delta_mph, 1)} | {note} |"
        )

    text = "\n".join(lines) + "\n"

    grid_md_path.write_text(text)
    grid_html_path.write_text(markdown_to_html(text))

    return grid_md_path, grid_html_path

def short_run_name(source: str) -> str:
    stem = Path(source).stem
    for part in stem.split("_"):
        if part.startswith("lap"):
            return part
    return stem


def write_report(
    csv_path: Path,
    reference_path: Path | None,
    metrics: list[SegmentMetric],
    findings: list[dict],
    reports_dir: Path,
    event_dir: Path,
    driver_input_source: str | None = None,
    analyzed_duration_s: float | None = None,
    sample_count: int | None = None,
):
    reports_dir.mkdir(parents=True, exist_ok=True)
    stem = csv_path.stem
    md_path = reports_dir / f"{stem}_report.md"
    json_path = reports_dir / f"{stem}_summary.json"
    has_reference = any(m.time_delta is not None for m in metrics)
    lines = [f"# RaceCoach Report — {csv_path.name}", ""]

    if reference_path:
        lines.extend([
            f"Reference Lap: {reference_path.name}",
            "",
        ])

    if driver_input_source:
        lines.extend([
            f"Driver Input Source: {driver_input_source}",
            "",
        ])

    lines.extend([
        '<p><strong>Help & Documentation</strong></p>',
        '<ul>',
        '<li><a href="https://github.com/peterm95018/racecoach/blob/momentum-recovery/docs/USER_GUIDE.md" target="_blank">User Guide</a></li>',
        '<li><a href="https://github.com/peterm95018/racecoach/blob/momentum-recovery/docs/ARCHITECTURE.md" target="_blank">Architecture</a></li>',
        '</ul>',
        '',
    ])
    
    if has_reference:
        gains = sorted(
            [m for m in metrics if m.time_delta is not None and m.time_delta < 0],
            key=lambda x: x.time_delta,
        )

        losses = sorted(
            [m for m in metrics if m.time_delta is not None and m.time_delta > 0],
            key=lambda x: x.time_delta,
            reverse=True,
        )



        summary_gains = [
            m for m in gains
            if m.name not in {"Start", "Launch"}
            and m.time_delta is not None
            and abs(m.time_delta) >= 0.10
        ]

        summary_losses = [
            m for m in losses
            if m.name not in {"Start", "Launch"}
            and m.time_delta is not None
            and m.time_delta >= 0.10
            and not low_confidence_loss(m)
            and classify_loss(m) != "unexplained timing loss"
        ]

        summary_added = False
        
        lines += ["## Run Summary", ""]

        if summary_gains:
            g = summary_gains[0]

            lines.append(
                f"Biggest gain: **{g.name}** ({g.time_delta:+.2f}s)"
            )
            lines.append("")
            
            if g.min_speed_delta_mph is not None:
                lines.append(
                    f"- Min speed: {g.min_speed_delta_mph:+.1f} mph vs reference lap"
                )

            if g.exit_speed_delta_mph is not None:
                lines.append(
                    f"- Exit speed: {g.exit_speed_delta_mph:+.1f} mph vs reference lap"
                )

            lines.append("")

        if summary_losses:
            l = summary_losses[0]

            lines.append(
                f"Biggest loss: **{l.name}** ({l.time_delta:+.2f}s)"
            )
            lines.append("")
            
            if (
                l.avg_speed_delta_mph is not None
                and l.avg_speed_delta_mph < -3
            ):

                lines.append(
                    f"- Average speed: {l.avg_speed_delta_mph:+.1f} mph vs reference lap"
                )

                if l.entry_speed_delta_mph is not None:
                    lines.append(
                        f"- Entry speed: {l.entry_speed_delta_mph:+.1f} mph vs reference lap"
                    )
            else:
                if l.min_speed_delta_mph is not None:
                    lines.append(
                        f"- Min speed: {l.min_speed_delta_mph:+.1f} mph vs reference lap"
                    )

                    if l.exit_speed_delta_mph is not None:
                        lines.append(
                            f"- Exit speed: {l.exit_speed_delta_mph:+.1f} mph vs reference lap"
                    )

            lines.append("")
            lines.append("")

        if not summary_gains and not summary_losses:
            small_gains = [
                m for m in gains
                if m.time_delta is not None
                and m.name not in {"Start", "Launch"}
            ]

            if small_gains:
                g = small_gains[0]
                lines.append("Small net improvement over reference lap.")
                lines.append("")
                lines.append(
                    f"Best small gain: **{g.name}** ({g.time_delta:+.2f}s)"
                )
                lines.append("")
                lines.append("No major losses detected.")
            else:
                lines.append("Your gains came from executing the whole course cleanly.")
                lines.append("")
                lines.append("Repeat the same rhythm—don't search for extra speed.")
                lines.append("")
                lines.append("Use the segment table to check small changes.")
                
        lines += [
            "",
            "### Next Run Focus",
            "",
        ]

        focus_items = []

        if summary_losses:
            l = summary_losses[0]
            name = l.name

            exit_down = (
                l.exit_speed_delta_mph is not None
                and l.exit_speed_delta_mph < -2
            )
            min_down = (
                l.min_speed_delta_mph is not None
                and l.min_speed_delta_mph < -2
            )
            min_up = (
                l.min_speed_delta_mph is not None
                and l.min_speed_delta_mph > 1
            )
            throttle_late = (
                l.throttle_commit_delay_delta_s is not None
                and l.throttle_commit_delay_delta_s > 0.20
            )
            coasting = l.coast_time_s is not None and l.coast_time_s > 0.30

            if min_up and exit_down:
                focus_items.append(f"{name}: slow the entry slightly and protect exit speed.")
                focus_items.append("Rotate once, then commit to throttle.")
            elif throttle_late and exit_down:
                focus_items.append(f"{name}: pick up throttle earlier.")
                focus_items.append("Prioritize exit speed over entry speed.")
            elif min_down:
                focus_items.append(f"{name}: carry more minimum speed.")
                focus_items.append("Brake less or release earlier.")
            elif coasting:
                focus_items.append(f"{name}: reduce coasting.")
                focus_items.append("Choose brake or throttle, not neutral.")
            elif exit_down:
                focus_items.append(f"{name}: recover exit speed.")
                focus_items.append("Look earlier and unwind sooner.")
            else:
                focus_items.append(f"{name}: reduce the biggest time loss.")
                focus_items.append("Review braking, rotation, and throttle timing.")

        if summary_gains:
            g = summary_gains[0]
            focus_items.append(f"Repeat what worked in {g.name}.")
        if not focus_items:
            focus_items.append("Protect the gains and continue building speed gradually.")

        for i, item in enumerate(focus_items[:3], start=1):
            lines.append(f"{i}. {item}")

        lines += ["", "---", ""]    
    if has_reference:
        gains = sorted([m for m in metrics if m.time_delta is not None and m.time_delta < 0], key=lambda x: x.time_delta)
        losses = sorted([m for m in metrics if m.time_delta is not None and m.time_delta > 0], key=lambda x: x.time_delta, reverse=True)
        lines += ["## Segment Time vs Reference Lap", ""]
        display_gains = [
            m for m in gains
            if m.name not in {"Start", "Launch", "Launch / first element"}
        ]

        if display_gains:
            for m in display_gains[:3]:
                gain_line = (
                    f"- **{m.name}**: {m.time_delta:+.2f}s, "
                    f"min speed {fmt_ref(m.min_speed_mph, m.reference_min_speed_mph, m.min_speed_delta_mph, 'mph')}, "
                    f"exit {fmt_ref(m.exit_speed_mph, m.reference_exit_speed_mph, m.exit_speed_delta_mph, 'mph')}"
                )

#                if (
#                    m.throttle_pickup_time is not None
#                    and m.reference_throttle_pickup_time is not None
#                ):
#                    gain_line += (
#                        f", throttle {fmt_optional(m.throttle_pickup_time)} vs "
#                        f"{fmt_optional(m.reference_throttle_pickup_time)} sec "
#                        f"({delta_str(m.throttle_pickup_delta_s, 2)})"
#                    )

                lines.append(gain_line)
        else:
            lines.append("- No faster segments vs reference lap.")

            lines += ["", "## Slower Segments vs Reference Lap", ""]

        coaching_losses = [
            m for m in losses
            if m.name not in {"Start", "Launch"}
        ]

        if coaching_losses:
            for m in coaching_losses[:3]:
                summary_line = (
                    f"- **{m.name}**: {m.time_delta:+.2f}s, "
                    f"min speed {fmt_ref(m.min_speed_mph, m.reference_min_speed_mph, m.min_speed_delta_mph, 'mph')}, "
                    f"exit {fmt_ref(m.exit_speed_mph, m.reference_exit_speed_mph, m.exit_speed_delta_mph, 'mph')}"
                )

                if (
                    m.throttle_pickup_time is not None
                    and m.reference_throttle_pickup_time is not None
                ):
                    summary_line += (
                        f", throttle {fmt_optional(m.throttle_pickup_time)} vs "
                        f"{fmt_optional(m.reference_throttle_pickup_time)} sec "
                        f"({delta_str(m.throttle_pickup_delta_s, 2)})"
                    )

                lines.append(summary_line)
        else:
            lines.append("- No slower segments vs reference lap.")

        lines.append("")

    lines += ["## Top Opportunities", ""]

    opportunities = [
        finding
        for finding in findings
        if finding["segment"].time_delta is not None
        and finding["segment"].time_delta > 0
        and finding["segment"].name not in {"Launch", "Start"}
    ]
    
    if not opportunities:
        lines.append("No high-confidence opportunities detected. Check segment definitions and reference run.")
    else:
        for i, f in enumerate(opportunities[:3], start=1):
            m = f["segment"]
            lines += [
                f"### {i}. {m.name} ({m.time_delta:+.2f}s)",
                "",
                f["coaching"],
                "",
                f"- Analysis: {explain_delta(m)}",
                "",
                "**Telemetry:**",
                "",
                f"- Duration: {fmt_ref(m.duration, m.reference_duration, m.time_delta, 'sec', 2)}",
                f"- Entry speed: {fmt_ref(m.entry_speed_mph, m.reference_entry_speed_mph, m.entry_speed_delta_mph, 'mph')}",
                f"- Average speed: {fmt_ref(m.avg_speed_mph, m.reference_avg_speed_mph, m.avg_speed_delta_mph, 'mph')}",
                f"- Minimum speed: {fmt_ref(m.min_speed_mph, m.reference_min_speed_mph, m.min_speed_delta_mph, 'mph')}",
                f"- Exit speed: {fmt_ref(m.exit_speed_mph, m.reference_exit_speed_mph, m.exit_speed_delta_mph, 'mph')}",
            ]

            if (
                m.brake_start_distance is not None
                and m.reference_brake_start_distance is not None
            ):
                lines.append(
                    f"- Brake start distance: "
                    f"{fmt_ref(m.brake_start_distance, m.reference_brake_start_distance, m.brake_start_distance_delta, 'ft', 1)}"
                )
            if (
                m.recovery_speed_1s_mph is not None
                and m.reference_recovery_speed_1s_mph is not None
            ):

                lines.append(
                    f"- Recovery speed (+1s): {fmt_ref(m.recovery_speed_1s_mph, m.reference_recovery_speed_1s_mph, m.recovery_speed_delta_mph, 'mph', 1)}"
                )


            if (
                m.recovery_gain_1s_mph is not None
                and m.recovery_gain_1s_delta_mph is not None
            ):
                lines.append(
                    f"- Recovery gain (+1s): "
                    f"{m.recovery_gain_1s_mph:.1f} mph "
                    f"({delta_str(m.recovery_gain_1s_delta_mph, 1)})"
                )

            if (
                m.recovery_gain_2s_mph is not None
                and m.recovery_gain_2s_delta_mph is not None
            ):
                lines.append(
                    f"- Recovery gain (+2s): "
                    f"{m.recovery_gain_2s_mph:.1f} mph "
                    f"({delta_str(m.recovery_gain_2s_delta_mph, 1)})"
                )

            lines += [
                f"- Peak braking/decel: {fmt_ref(m.peak_decel_g, m.reference_peak_decel_g, m.peak_decel_delta_g, 'G', 2)}",
                f"- Coast time: {fmt_ref(m.coast_time_s, m.reference_coast_time_s, m.coast_time_delta_s, 'sec', 2)}",
            ]

            if (
                m.throttle_commit_delay_s is not None
                and m.reference_throttle_commit_delay_s is not None
            ):
                lines += [
                    "",
                    "#### Throttle Commitment",
                    "",
                    f"- Throttle after min speed: {fmt_optional(m.throttle_commit_delay_s)} vs "
                    f"{fmt_optional(m.reference_throttle_commit_delay_s)} sec "
                    f"({delta_str(m.throttle_commit_delay_delta_s, 2)})",
                ]

            lines += [
                "",
                "#### Why Flagged",
                "",
            ]

            for reason in f["reasons"]:
                lines.append(f"- {reason}")

            lines.append("")
    lines.append("")

    lines += [
    "",
    "## Segment Table",
    "",
    "| Segment | Δ Time | Min Δ | Exit Δ | Rec+1 | Rec+2 | Notes |",
    "|---|---:|---:|---:|---:|---:|---|",
]

    for m in metrics:
        notes = []

        if m.throttle_commit_delay_delta_s is not None:
            notes.append(f"thrΔ={m.throttle_commit_delay_delta_s:+.2f}s")

        if m.time_delta is not None:
            if m.time_delta > 0.15:
                if classify_loss(m) == "unexplained timing loss":
                    notes.append("timing loss unexplained")
                else:
                    notes.append("loss")
            elif m.time_delta < -0.15:
                notes.append("gain")

        if m.exit_speed_delta_mph is not None and m.exit_speed_delta_mph < -2:
            notes.append("exit speed down")

        if m.brake_start_delta_s is not None:
            if m.brake_start_delta_s > 0.20:
                notes.append("braked later")
            elif m.brake_start_delta_s < -0.20:
                notes.append("braked earlier")

#        if m.throttle_pickup_delta_s is not None:
#            if abs(m.throttle_pickup_delta_s) > 2.0:
#                notes.append("throttle delta suspect")
#            elif m.throttle_pickup_delta_s > 0.25:
#                notes.append("throttle later")
#            elif m.throttle_pickup_delta_s < -0.25:
#                notes.append("earlier throttle commitment")

        lines.append(
            f"| {m.name} | "
            f"{delta_str(m.time_delta, 2)} | "
            f"{delta_str(m.min_speed_delta_mph, 1)} | "
            f"{delta_str(m.exit_speed_delta_mph, 1)} | "
            f"{delta_str(m.recovery_gain_1s_delta_mph, 1)} | "
            f"{delta_str(m.recovery_gain_2s_delta_mph, 1)} | "
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

    run_name = short_run_name(csv_path.name)
    run_status, is_clean = load_run_status(event_dir, run_name)

    summary = {
        "source": csv_path.name,
        "run": {
            "name": run_name,
            "analyzed_duration_s": analyzed_duration_s,
            "sample_count": sample_count,
            "driver_input_source": driver_input_source,
            "status": run_status,
            "is_clean": is_clean,
        },
        "metrics": [asdict(m) for m in metrics],
        "findings": [
            {
                "score": f["score"],
                "segment": f["segment"].name,
                "reasons": f["reasons"],
                "coaching": f["coaching"],
            }
            for f in findings
        ],
    }

    json_path.write_text(json.dumps(summary, indent=2))

    write_grid_report(
        csv_path,
        reference_path,
        metrics,
        findings,
        reports_dir,
    )

    return md_path, json_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--reports", type=Path, default=Path("reports"))
    args = parser.parse_args()
    df, metrics, findings = analyze(args.csv, args.event, args.reference)

    analyzed_duration_s = None
    if not df.empty and "time_s" in df.columns:
        analyzed_duration_s = float(df["time_s"].iloc[-1])

    md, js = write_report(
        args.csv,
        args.reference,
        metrics,
        findings,
        args.reports,
        args.event,
        driver_input_source=df.attrs.get("driver_input_source"),
        analyzed_duration_s=analyzed_duration_s,
        sample_count=len(df),
    )
    print(md.read_text())
    print(f"\nWrote: {md}")
    print(f"Wrote: {js}")

if __name__ == "__main__":
    main()
