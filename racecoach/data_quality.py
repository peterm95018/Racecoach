from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd


class DataQualityError(ValueError):
    """Raised when telemetry cannot safely produce coaching."""


@dataclass(frozen=True)
class SegmentCoverage:
    lap_distance_m: float
    configured_start_m: float
    configured_finish_m: float
    endpoint_difference_m: float
    tolerance_m: float


def validate_segment_coverage(
    df: pd.DataFrame,
    segments: list[dict],
    *,
    label: str = "run",
    timed_lap_distance_m: float | None = None,
    join_tolerance_m: float = 1.0,
    endpoint_tolerance_m: float = 10.0,
    endpoint_tolerance_ratio: float = 0.03,
) -> SegmentCoverage:
    if df.empty:
        raise DataQualityError(f"{label}: timed-lap data is empty")

    if "distance" not in df.columns:
        raise DataQualityError(f"{label}: distance data is missing")

    measured_distance = float(df["distance"].max())
    lap_distance = (
        measured_distance
        if timed_lap_distance_m is None
        else float(timed_lap_distance_m)
    )

    if not math.isfinite(lap_distance) or lap_distance <= 0:
        raise DataQualityError(
            f"{label}: invalid timed-lap distance {lap_distance!r}"
        )

    if not segments:
        raise DataQualityError(f"{label}: no segments are configured")

    ranges = []

    for index, segment in enumerate(segments, start=1):
        name = str(segment.get("name", f"segment {index}"))

        if (
            "start_distance" not in segment
            or "end_distance" not in segment
        ):
            raise DataQualityError(
                f"{label}: {name} is missing a distance boundary"
            )

        try:
            start = float(segment["start_distance"])
            finish = float(segment["end_distance"])
        except (TypeError, ValueError) as exc:
            raise DataQualityError(
                f"{label}: {name} has a nonnumeric distance boundary"
            ) from exc

        if not math.isfinite(start) or not math.isfinite(finish):
            raise DataQualityError(
                f"{label}: {name} has a nonfinite distance boundary"
            )

        if finish <= start:
            raise DataQualityError(
                f"{label}: {name} ends at {finish:.1f}m "
                f"but starts at {start:.1f}m"
            )

        ranges.append((name, start, finish))

    configured_start = ranges[0][1]
    configured_finish = ranges[-1][2]

    if abs(configured_start) > join_tolerance_m:
        raise DataQualityError(
            f"{label}: segment coverage starts at "
            f"{configured_start:.1f}m instead of 0.0m"
        )

    for previous, current in zip(ranges, ranges[1:]):
        previous_name, _, previous_finish = previous
        current_name, current_start, _ = current
        separation = current_start - previous_finish

        if separation > join_tolerance_m:
            raise DataQualityError(
                f"{label}: {separation:.1f}m gap between "
                f"{previous_name} and {current_name}"
            )

        if separation < -join_tolerance_m:
            raise DataQualityError(
                f"{label}: {-separation:.1f}m overlap between "
                f"{previous_name} and {current_name}"
            )

    tolerance = max(
        endpoint_tolerance_m,
        lap_distance * endpoint_tolerance_ratio,
    )
    difference = configured_finish - lap_distance

    if abs(difference) > tolerance:
        direction = "short" if difference < 0 else "long"
        raise DataQualityError(
            f"{label}: segment coverage ends at "
            f"{configured_finish:.1f}m but timed lap is "
            f"{lap_distance:.1f}m "
            f"({abs(difference):.1f}m {direction}; "
            f"tolerance {tolerance:.1f}m)"
        )

    return SegmentCoverage(
        lap_distance_m=lap_distance,
        configured_start_m=configured_start,
        configured_finish_m=configured_finish,
        endpoint_difference_m=difference,
        tolerance_m=tolerance,
    )