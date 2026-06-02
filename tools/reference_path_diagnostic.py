from pathlib import Path
import sys
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from racecoach.analyze_run import read_racechrono_csv, normalize_columns


    from racecoach.reference_path import (
        add_gps_path_position,
        project_lap_to_reference,
    )

    lap_df = lap_df.copy()
    lap_df["ref_pos_m"] = [x[0] for x in projected]
    lap_df["ref_error_m"] = [x[1] for x in projected]
    return lap_df


def segment_summary(df, pos_col, start, end):
    seg = df[(df[pos_col] >= start) & (df[pos_col] <= end)].copy()

    if len(seg) < 5:
        return None

    return {
        "duration": float(seg["time_s"].iloc[-1] - seg["time_s"].iloc[0]),
        "min_speed": float(seg["speed_mph"].min()),
        "exit_speed": float(seg.iloc[-max(3, len(seg) // 10):]["speed_mph"].mean()),
        "avg_error": float(seg["ref_error_m"].mean()) if "ref_error_m" in seg else 0.0,
    }


def main():
    uploads = Path("events/gglc_2025-11-01/uploads")

    ref = normalize_columns(
        read_racechrono_csv(
            uploads / "session_20251101_121758_gglc_11012025_lap5_v3.csv"
        )
    )

    lap4 = normalize_columns(
        read_racechrono_csv(
            uploads / "session_20251101_120901_gglc_11012025_lap4_v3.csv"
        )
    )

    ref = add_gps_path_position(ref)
    lap4 = project_lap_to_reference(lap4, ref)

    total = float(ref["gps_path_m"].iloc[-1])

    print(f"Reference samples: {len(ref)}")
    print(f"Reference GPS path length: {total:.1f} m")
    print()

    bins = [
        ("0-25%", 0, total * 0.25),
        ("25-50%", total * 0.25, total * 0.50),
        ("50-75%", total * 0.50, total * 0.75),
        ("75-100%", total * 0.75, total),
    ]

    print("| Segment | Lap4 Dur | Lap5 Dur | Δ Time | Lap4 Min | Lap5 Min | Lap4 Exit | Lap5 Exit | Avg GPS Err |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    for name, start, end in bins:
        s4 = segment_summary(lap4, "ref_pos_m", start, end)
        s5 = segment_summary(ref, "gps_path_m", start, end)

        if s4 is None or s5 is None:
            continue

        print(
            f"| {name} | "
            f"{s4['duration']:.3f} | "
            f"{s5['duration']:.3f} | "
            f"{s4['duration'] - s5['duration']:+.3f} | "
            f"{s4['min_speed']:.1f} | "
            f"{s5['min_speed']:.1f} | "
            f"{s4['exit_speed']:.1f} | "
            f"{s5['exit_speed']:.1f} | "
            f"{s4['avg_error']:.2f} |"
        )


if __name__ == "__main__":
    main()