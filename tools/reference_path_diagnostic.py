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


def add_gps_path_position(df):
    positions = [0.0]
    total = 0.0

    for i in range(1, len(df)):
        total += haversine_m(
            df.iloc[i - 1]["latitude"],
            df.iloc[i - 1]["longitude"],
            df.iloc[i]["latitude"],
            df.iloc[i]["longitude"],
        )
        positions.append(total)

    df = df.copy()
    df["gps_path_m"] = positions
    return df


def nearest_reference_position(ref_df, lat, lon):
    best_idx = None
    best_dist = float("inf")

    for idx, row in ref_df.iterrows():
        d = haversine_m(lat, lon, row["latitude"], row["longitude"])
        if d < best_dist:
            best_idx = idx
            best_dist = d

    return float(ref_df.loc[best_idx, "gps_path_m"]), best_dist


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

    print(f"Reference samples: {len(ref)}")
    print(f"Reference GPS path length: {ref['gps_path_m'].iloc[-1]:.1f} m")

    lap4 = project_lap_to_reference(lap4, ref)

    total = ref["gps_path_m"].iloc[-1]
    bins = [
        ("0-25%", 0, total * 0.25),
        ("25-50%", total * 0.25, total * 0.50),
        ("50-75%", total * 0.50, total * 0.75),
        ("75-100%", total * 0.75, total),
    ]

    print()
    print("| Segment | Lap4 Dur | Lap5 Dur | Δ Time | Lap4 Min | Lap5 Min | Avg GPS Err |")
    print("|---|---:|---:|---:|---:|---:|---:|")

    for name, start, end in bins:
        seg4 = lap4[(lap4["ref_pos_m"] >= start) & (lap4["ref_pos_m"] <= end)]
        seg5 = ref[(ref["gps_path_m"] >= start) & (ref["gps_path_m"] <= end)]

        dur4 = seg4["time_s"].iloc[-1] - seg4["time_s"].iloc[0]
        dur5 = seg5["time_s"].iloc[-1] - seg5["time_s"].iloc[0]

        print(
            f"| {name} | "
            f"{dur4:.3f} | "
            f"{dur5:.3f} | "
            f"{dur4 - dur5:+.3f} | "
            f"{seg4['speed_mph'].min():.1f} | "
            f"{seg5['speed_mph'].min():.1f} | "
            f"{seg4['ref_error_m'].mean():.2f} |"
        )

        def project_lap_to_reference(lap_df, ref_df):
            projected = []

            for _, row in lap_df.iterrows():
                ref_pos, err = nearest_reference_position(
                    ref_df,
                    row["latitude"],
                    row["longitude"],
                )
                projected.append((ref_pos, err))

            lap_df = lap_df.copy()
            lap_df["ref_pos_m"] = [x[0] for x in projected]
            lap_df["ref_error_m"] = [x[1] for x in projected]
            return lap_df

        print(
            f"{label:<12} -> ref_pos={ref_pos:7.1f} m, "
            f"nearest_error={err:5.2f} m, "
            f"lap4_time={row['time_s']:6.3f}, "
            f"lap4_speed={row['speed_mph']:5.1f}"
        )


if __name__ == "__main__":
    main()