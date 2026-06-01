from pathlib import Path
import sys
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from racecoach.analyze_run import read_racechrono_csv, normalize_columns


def main():
    csv_path = Path(
        "events/gglc_2025-11-01/uploads/session_20251101_121758_gglc_11012025_lap5_v3.csv"
    )
    out_path = Path("events/gglc_2025-11-01/gps_anchors.yaml")

    df = normalize_columns(read_racechrono_csv(csv_path))

    anchors = {
        "launch_start": df.iloc[0],
        "quarter_course": df.iloc[len(df) // 4],
        "half_course": df.iloc[len(df) // 2],
        "three_quarter_course": df.iloc[(3 * len(df)) // 4],
        "finish": df.iloc[-1],
    }

    data = {
        "reference_csv": csv_path.name,
        "anchors": {
            name: {
                "time_s": float(row["time_s"]),
                "distance": float(row["distance"]),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
            }
            for name, row in anchors.items()
        },
    }

    out_path.write_text(yaml.safe_dump(data, sort_keys=False))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
