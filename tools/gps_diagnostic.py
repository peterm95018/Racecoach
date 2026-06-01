from pathlib import Path
import sys
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from racecoach.analyze_run import read_racechrono_csv, normalize_columns


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearest_sample(df, lat, lon):
    distances = df.apply(
        lambda row: haversine_m(row["latitude"], row["longitude"], lat, lon),
        axis=1,
    )
    idx = distances.idxmin()
    row = df.loc[idx]
    return row, distances.loc[idx]


def main():
    uploads = Path("events/gglc_2025-11-01/uploads")

    lap4 = normalize_columns(
        read_racechrono_csv(uploads / "session_20251101_120901_gglc_11012025_lap4_v3.csv")
    )
    lap5 = normalize_columns(
        read_racechrono_csv(uploads / "session_20251101_121758_gglc_11012025_lap5_v3.csv")
    )

    # Start with Lap 5 finish as a known GPS anchor.
    anchor = lap5.iloc[-1]
    lat = anchor["latitude"]
    lon = anchor["longitude"]

    print(f"Anchor lat/lon: {lat:.7f}, {lon:.7f}")

    for name, df in [("lap4", lap4), ("lap5", lap5)]:
        row, err_m = nearest_sample(df, lat, lon)
        print(f"\n{name}")
        print(f"nearest error: {err_m:.2f} m")
        print(f"time: {row['time_s']:.3f}")
        print(f"distance: {row['distance']:.2f}")
        print(f"speed: {row['speed_mph']:.1f} mph")
        print(f"throttle: {row['throttle']:.1f}")


if __name__ == "__main__":
    main()