from __future__ import annotations

import math
import numpy as np
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
    downsample: int = 50,
) -> pd.DataFrame:
    if "gps_path_m" not in ref_df.columns:
        ref_df = add_gps_path_position(ref_df)

    if downsample < 1:
        downsample = 1

    ref_search = ref_df.iloc[::downsample].copy()

    ref_lats = ref_search["latitude"].astype(float).to_numpy()
    ref_lons = ref_search["longitude"].astype(float).to_numpy()
    ref_pos = ref_search["gps_path_m"].astype(float).to_numpy()

    ref_lats_rad = np.radians(ref_lats)
    ref_lons_rad = np.radians(ref_lons)

    projected_pos = []
    projected_err = []

    earth_radius_m = 6371000.0

    for row in lap_df.itertuples(index=False):
        lat = float(getattr(row, "latitude"))
        lon = float(getattr(row, "longitude"))

        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        dlat = ref_lats_rad - lat_rad
        dlon = ref_lons_rad - lon_rad
        mean_lat = (ref_lats_rad + lat_rad) / 2.0

        x = dlon * np.cos(mean_lat)
        y = dlat
        dist_m = earth_radius_m * np.sqrt((x * x) + (y * y))

        best_i = int(np.argmin(dist_m))
        projected_pos.append(float(ref_pos[best_i]))
        projected_err.append(float(dist_m[best_i]))

    projected_pos = list(np.maximum.accumulate(projected_pos))

    out = lap_df.copy()

    out["ref_pos_m"] = projected_pos

    out["ref_error_m"] = projected_err
    
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