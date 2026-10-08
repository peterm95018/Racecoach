from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd


RACECHRONO_COORD_SCALE = 6_000_000.0

TRAP_START = 1
TRAP_FINISH = 2
TRAP_INTERMEDIATE = 4


class TrackCalibrationError(ValueError):
    """RaceChrono track geometry cannot be calibrated safely."""


@dataclass(frozen=True)
class RaceChronoGate:
    name: str
    trap_type: int
    latitude: float
    longitude: float
    bearing_deg: float
    width_m: float
    unidirectional: bool


@dataclass(frozen=True)
class CalibratedBoundary:
    name: str
    trap_type: int
    distance_m: float
    offset_from_center_m: float | None = None


def load_racechrono_track(path: Path) -> list[RaceChronoGate]:
    """Read RaceChrono gates from an RCZ track export."""
    path = Path(path)

    try:
        with zipfile.ZipFile(path) as archive:
            payload = json.loads(archive.read("trackId.json"))
    except (OSError, KeyError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        raise TrackCalibrationError(
            f"Could not read RaceChrono track file: {path}"
        ) from exc

    try:
        traps = payload["track"]["traps"]
    except (KeyError, TypeError) as exc:
        raise TrackCalibrationError(
            f"RaceChrono track has no trap definitions: {path}"
        ) from exc

    gates = []

    for trap in traps:
        try:
            gate = RaceChronoGate(
                name=str(trap["name"]).strip(),
                trap_type=int(trap["type"]),
                latitude=float(trap["centerLatitude"])
                / RACECHRONO_COORD_SCALE,
                longitude=float(trap["centerLongitude"])
                / RACECHRONO_COORD_SCALE,
                bearing_deg=float(trap["bearing"]) / 1000.0,
                width_m=float(trap["width"]) / 1000.0,
                unidirectional=bool(trap.get("uniDirectional", False)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise TrackCalibrationError(
                f"Invalid RaceChrono gate definition in {path}"
            ) from exc

        if gate.trap_type in (
            TRAP_START,
            TRAP_FINISH,
            TRAP_INTERMEDIATE,
        ):
            gates.append(gate)

    if not gates:
        raise TrackCalibrationError(
            f"RaceChrono track contains no usable gates: {path}"
        )

    starts = [g for g in gates if g.trap_type == TRAP_START]
    finishes = [g for g in gates if g.trap_type == TRAP_FINISH]

    if len(starts) != 1:
        raise TrackCalibrationError(
            f"Expected exactly one Start gate; found {len(starts)}"
        )

    if len(finishes) != 1:
        raise TrackCalibrationError(
            f"Expected exactly one Finish gate; found {len(finishes)}"
        )

    return gates


def _finite_gate_crossings(
    df: pd.DataFrame,
    gate: RaceChronoGate,
) -> list[tuple[float, float]]:
    """
    Return (run distance, lateral offset) for finite gate crossings.

    RaceChrono bearing describes the gate normal / direction through
    the gate. The finite timing line is perpendicular to that bearing.
    """
    required = {"latitude", "longitude", "distance"}
    missing = required - set(df.columns)

    if missing:
        raise TrackCalibrationError(
            "Run data missing required columns: "
            + ", ".join(sorted(missing))
        )

    if len(df) < 2:
        raise TrackCalibrationError(
            "Run data has too few samples for gate calibration"
        )

    lat = df["latitude"].to_numpy(dtype=float)
    lon = df["longitude"].to_numpy(dtype=float)
    distance = df["distance"].to_numpy(dtype=float)

    if not (
        np.isfinite(lat).all()
        and np.isfinite(lon).all()
        and np.isfinite(distance).all()
    ):
        raise TrackCalibrationError(
            "Run data contains nonfinite GPS or distance values"
        )

    origin_lat = float(np.mean(lat))
    origin_lon = float(np.mean(lon))

    meters_lat = 111_320.0
    meters_lon = 111_320.0 * math.cos(math.radians(origin_lat))

    x = (lon - origin_lon) * meters_lon
    y = (lat - origin_lat) * meters_lat

    cx = (gate.longitude - origin_lon) * meters_lon
    cy = (gate.latitude - origin_lat) * meters_lat

    theta = math.radians(gate.bearing_deg)

    # RaceChrono bearing is normal to the finite gate line.
    nx = math.sin(theta)
    ny = math.cos(theta)

    # Unit vector along the gate line.
    gx = ny
    gy = -nx

    signed = (x - cx) * nx + (y - cy) * ny
    half_width = gate.width_m / 2.0

    crossings = []

    for i in range(len(df) - 1):
        a = signed[i]
        b = signed[i + 1]

        if a == 0.0:
            t = 0.0
        elif a * b > 0.0:
            continue
        else:
            denominator = a - b
            if abs(denominator) < 1e-12:
                continue
            t = a / denominator

        ix = x[i] + t * (x[i + 1] - x[i])
        iy = y[i] + t * (y[i + 1] - y[i])

        along = (ix - cx) * gx + (iy - cy) * gy

        if abs(along) > half_width:
            continue

        crossing_distance = (
            distance[i]
            + t * (distance[i + 1] - distance[i])
        )

        crossings.append(
            (float(crossing_distance), float(along))
        )

    return crossings


def calibrate_boundaries(
    df: pd.DataFrame,
    gates: list[RaceChronoGate],
) -> list[CalibratedBoundary]:
    """
    Calibrate RaceChrono gates against a timed Run 1 trajectory.

    Start and Finish are fixed to the timed-lap endpoints because a
    RaceChrono timed-lap export is already clipped at those timing gates.
    Intermediate gates must have exactly one finite-line crossing.
    """
    if df.empty:
        raise TrackCalibrationError("Run data is empty")

    lap_distance = float(df["distance"].max())

    if not math.isfinite(lap_distance) or lap_distance <= 0:
        raise TrackCalibrationError(
            f"Invalid timed-lap distance: {lap_distance!r}"
        )

    starts = [g for g in gates if g.trap_type == TRAP_START]
    finishes = [g for g in gates if g.trap_type == TRAP_FINISH]

    if len(starts) != 1 or len(finishes) != 1:
        raise TrackCalibrationError(
            "Calibration requires exactly one Start and one Finish"
        )

    boundaries = [
        CalibratedBoundary(
            name=starts[0].name,
            trap_type=TRAP_START,
            distance_m=0.0,
        )
    ]

    for gate in gates:
        if gate.trap_type != TRAP_INTERMEDIATE:
            continue

        crossings = _finite_gate_crossings(df, gate)

        if len(crossings) == 0:
            raise TrackCalibrationError(
                f"Gate {gate.name!r} was not crossed by Run 1"
            )

        if len(crossings) > 1:
            distances = ", ".join(
                f"{distance:.1f}m"
                for distance, _ in crossings
            )
            raise TrackCalibrationError(
                f"Gate {gate.name!r} has ambiguous crossings: "
                f"{distances}"
            )

        crossing_distance, offset = crossings[0]

        boundaries.append(
            CalibratedBoundary(
                name=gate.name,
                trap_type=gate.trap_type,
                distance_m=crossing_distance,
                offset_from_center_m=offset,
            )
        )

    boundaries.sort(key=lambda boundary: boundary.distance_m)

    boundaries.append(
        CalibratedBoundary(
            name=finishes[0].name,
            trap_type=TRAP_FINISH,
            distance_m=lap_distance,
        )
    )

    for previous, current in zip(boundaries, boundaries[1:]):
        if current.distance_m <= previous.distance_m:
            raise TrackCalibrationError(
                "RaceChrono boundaries are not strictly ordered: "
                f"{previous.name}={previous.distance_m:.1f}m, "
                f"{current.name}={current.distance_m:.1f}m"
            )

    return boundaries


def boundaries_to_segments(
    boundaries: list[CalibratedBoundary],
) -> list[dict]:
    """Build contiguous RaceCoach segments between calibrated boundaries."""
    if len(boundaries) < 2:
        raise TrackCalibrationError(
            "At least two boundaries are required"
        )

    segments = []

    for start, finish in zip(boundaries, boundaries[1:]):
        segments.append(
            {
                "name": f"{start.name} -> {finish.name}",
                "start_distance": round(start.distance_m, 3),
                "end_distance": round(finish.distance_m, 3),
            }
        )

    return segments


def render_course_trace(
    df: pd.DataFrame,
    boundaries: list[CalibratedBoundary],
    output_path: Path,
    *,
    title: str = "RaceCoach Course Trace",
) -> Path:
    """
    Render the driven GPS trajectory with calibrated station markers.

    Intermediate stations are numbered in actual driving order, independent
    of their names or order in the RaceChrono RCZ file.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    required = {"latitude", "longitude", "distance"}
    missing = required - set(df.columns)

    if missing:
        raise TrackCalibrationError(
            "Run data missing required columns for course trace: "
            + ", ".join(sorted(missing))
        )

    if len(df) < 2:
        raise TrackCalibrationError(
            "Run data has too few samples for course trace"
        )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lat = df["latitude"].to_numpy(dtype=float)
    lon = df["longitude"].to_numpy(dtype=float)
    distance = df["distance"].to_numpy(dtype=float)

    if not (
        np.isfinite(lat).all()
        and np.isfinite(lon).all()
        and np.isfinite(distance).all()
    ):
        raise TrackCalibrationError(
            "Run data contains nonfinite values for course trace"
        )

    origin_lat = float(np.mean(lat))
    origin_lon = float(np.mean(lon))

    meters_lat = 111_320.0
    meters_lon = 111_320.0 * math.cos(math.radians(origin_lat))

    x = (lon - origin_lon) * meters_lon
    y = (lat - origin_lat) * meters_lat

    fig, ax = plt.subplots(figsize=(8, 10))

    # Actual Run 1 driven path.
    ax.plot(x, y, linewidth=2.0)

    ordered = sorted(
        boundaries,
        key=lambda boundary: boundary.distance_m,
    )

    intermediate_number = 0

    for boundary in ordered:
        target = boundary.distance_m
        index = int(np.argmin(np.abs(distance - target)))

        px = x[index]
        py = y[index]

        if boundary.trap_type == TRAP_START:
            label = "START"
        elif boundary.trap_type == TRAP_FINISH:
            label = "FINISH"
        else:
            intermediate_number += 1
            label = str(intermediate_number)

        ax.scatter([px], [py], s=55, zorder=3)

        ax.annotate(
            label,
            (px, py),
            xytext=(7, 7),
            textcoords="offset points",
            fontsize=10,
            fontweight="bold",
            zorder=4,
        )

    # Direction cue near the beginning of the competitive path.
    if len(x) >= 3:
        cue_index = min(max(len(x) // 40, 1), len(x) - 2)

        ax.annotate(
            "",
            xy=(x[cue_index + 1], y[cue_index + 1]),
            xytext=(x[cue_index - 1], y[cue_index - 1]),
            arrowprops={"arrowstyle": "->", "linewidth": 1.5},
        )

    ax.set_title(title)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("East / West (m)")
    ax.set_ylabel("North / South (m)")
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)

    return output_path
