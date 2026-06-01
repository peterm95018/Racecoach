from pathlib import Path
import sys
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from racecoach.analyze_run import read_racechrono_csv, normalize_columns


def haversine_m(lat1, lon1, lat2, lon2):
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


def main():
    csv = Path(
        "events/gglc_2025-11-01/uploads/session_20251101_121758_gglc_11012025_lap5_v3.csv"
    )

    df = normalize_columns(read_racechrono_csv(csv))

    total = 0.0

    for i in range(1, len(df)):
        total += haversine_m(
            df.iloc[i - 1]["latitude"],
            df.iloc[i - 1]["longitude"],
            df.iloc[i]["latitude"],
            df.iloc[i]["longitude"],
        )

    print(f"Samples: {len(df)}")
    print(f"GPS path length: {total:.1f} m")
    print(f"Average spacing: {total / len(df):.3f} m")


if __name__ == "__main__":
    main()