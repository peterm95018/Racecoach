from __future__ import annotations

import math

import pandas as pd


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


def add_gps_path_position(df: pd.DataFrame) -> pd.DataFrame:
    positions = [0.0]
    total = 0.0

    for i in range(1, len(df)):
        total += haversine_m(
            float(df.iloc[i - 1]["latitude"]),
            float(df.iloc[i - 1]["longitude"]),
            float(df.iloc[i]["latitude"]),
            float(df.iloc[i]["longitude"]),
        )
        positions.append(total)

    out = df.copy()
    out["gps_path_m"] = positions
    return out


def nearest_reference_position(
    ref_df: pd.DataFrame,
    lat: float,
    lon: float,
) -> tuple[float, float]:
    best_idx = None
    best_dist = float("inf")

    for idx, row in ref_df.iterrows():
        d = haversine_m(
            lat,
            lon,
            float(row["latitude"]),
            float(row["longitude"]),
        )

        if d < best_dist:
            best_idx = idx
            best_dist = d

    if best_idx is None:
        raise ValueError("Reference path is empty.")

    return float(ref_df.loc[best_idx, "gps_path_m"]), best_dist


def project_lap_to_reference(
    lap_df: pd.DataFrame,
    ref_df: pd.DataFrame,
    downsample: int = 20,
) -> pd.DataFrame:
    if "gps_path_m" not in ref_df.columns:
        ref_df = add_gps_path_position(ref_df)

    ref_search = ref_df.iloc[::downsample].copy()

    projected = []

    for _, row in lap_df.iterrows():
        ref_pos, err = nearest_reference_position(
            ref_search,
            float(row["latitude"]),
            float(row["longitude"]),
        )
        projected.append((ref_pos, err))

    out = lap_df.copy()
    out["ref_pos_m"] = [x[0] for x in projected]
    out["ref_error_m"] = [x[1] for x in projected]
    return out


def segment_by_reference_position(
    df: pd.DataFrame,
    start_m: float,
    end_m: float,
    position_col: str = "ref_pos_m",
) -> pd.DataFrame:
    part = df[(df[position_col] >= start_m) & (df[position_col] <= end_m)].copy()

    if len(part) < 5:
        raise ValueError(
            f"Not enough samples in reference segment {start_m:.1f}-{end_m:.1f}m"
        )

    return part