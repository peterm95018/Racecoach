from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    )

    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def load_gps_anchors(path: Path) -> dict[str, dict[str, float]]:
    data = yaml.safe_load(path.read_text())

    if not data or "anchors" not in data:
        raise ValueError(f"Missing anchors in {path}")

    return data["anchors"]


def nearest_sample(df: pd.DataFrame, lat: float, lon: float) -> tuple[int, float]:
    best_idx = -1
    best_dist = float("inf")

    for idx, row in df.iterrows():
        d = haversine_m(
            float(row["latitude"]),
            float(row["longitude"]),
            lat,
            lon,
        )

        if d < best_dist:
            best_idx = idx
            best_dist = d

    return best_idx, best_dist


def segment_between_anchors(
    df: pd.DataFrame,
    anchors: dict[str, dict[str, float]],
    start_anchor: str,
    end_anchor: str,
    max_anchor_error_m: float = 5.0,
) -> pd.DataFrame:
    start = anchors[start_anchor]
    end = anchors[end_anchor]

    start_idx, start_err = nearest_sample(
        df,
        float(start["latitude"]),
        float(start["longitude"]),
    )

    end_idx, end_err = nearest_sample(
        df,
        float(end["latitude"]),
        float(end["longitude"]),
    )

    if start_err > max_anchor_error_m:
        raise ValueError(
            f"Start anchor {start_anchor} error too large: {start_err:.2f}m"
        )

    if end_err > max_anchor_error_m:
        raise ValueError(
            f"End anchor {end_anchor} error too large: {end_err:.2f}m"
        )

    if end_idx <= start_idx:
        raise ValueError(
            f"End anchor {end_anchor} occurs before start anchor {start_anchor}"
        )

    return df.loc[start_idx:end_idx].copy()