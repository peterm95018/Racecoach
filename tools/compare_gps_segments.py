from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from racecoach.analyze_run import read_racechrono_csv, normalize_columns
from racecoach.gps_segments import load_gps_anchors, segment_between_anchors


def summarize_segment(df):
    n = max(3, len(df) // 10)

    return {
        "duration": float(df["time_s"].iloc[-1] - df["time_s"].iloc[0]),
        "entry_speed": float(df.iloc[:n]["speed_mph"].mean()),
        "min_speed": float(df["speed_mph"].min()),
        "exit_speed": float(df.iloc[-n:]["speed_mph"].mean()),
    }


def main():
    event = Path("events/gglc_2025-11-01")
    uploads = event / "uploads"

    lap4 = normalize_columns(
        read_racechrono_csv(
            uploads / "session_20251101_120901_gglc_11012025_lap4_v3.csv"
        )
    )

    lap5 = normalize_columns(
        read_racechrono_csv(
            uploads / "session_20251101_121758_gglc_11012025_lap5_v3.csv"
        )
    )

    anchors = load_gps_anchors(event / "gps_anchors.yaml")

    gps_segments = [
        ("Launch", "launch_start", "quarter_course"),
        ("Middle", "quarter_course", "half_course"),
        ("Late middle", "half_course", "three_quarter_course"),
        ("Finish", "three_quarter_course", "finish"),
    ]

    print("| Segment | Lap4 Dur | Lap5 Dur | Δ Time | Lap4 Min | Lap5 Min | Lap4 Exit | Lap5 Exit |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")

    for name, start_anchor, end_anchor in gps_segments:
        seg4 = segment_between_anchors(lap4, anchors, start_anchor, end_anchor)
        seg5 = segment_between_anchors(lap5, anchors, start_anchor, end_anchor)

        s4 = summarize_segment(seg4)
        s5 = summarize_segment(seg5)

        print(
            f"| {name} | "
            f"{s4['duration']:.3f} | "
            f"{s5['duration']:.3f} | "
            f"{s4['duration'] - s5['duration']:+.3f} | "
            f"{s4['min_speed']:.1f} | "
            f"{s5['min_speed']:.1f} | "
            f"{s4['exit_speed']:.1f} | "
            f"{s5['exit_speed']:.1f} |"
        )


if __name__ == "__main__":
    main()