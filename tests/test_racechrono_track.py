from pathlib import Path
from tempfile import TemporaryDirectory
import json
import zipfile
import unittest

import pandas as pd

from racecoach.racechrono_track import (
    RaceChronoGate,
    TrackCalibrationError,
    TRAP_START,
    TRAP_FINISH,
    TRAP_INTERMEDIATE,
    load_racechrono_track,
    calibrate_boundaries,
    boundaries_to_segments,
)


class RaceChronoTrackTests(unittest.TestCase):
    def make_run(self):
        # Straight northbound trajectory, approximately 111.32 m long.
        return pd.DataFrame(
            {
                "latitude": [
                    37.0000,
                    37.0002,
                    37.0004,
                    37.0006,
                    37.0008,
                    37.0010,
                ],
                "longitude": [-121.0] * 6,
                "distance": [0.0, 22.264, 44.528, 66.792, 89.056, 111.320],
            }
        )

    def gate(self, name, trap_type, latitude, width=30.0):
        # Bearing 0 degrees means travel direction / gate normal is north.
        return RaceChronoGate(
            name=name,
            trap_type=trap_type,
            latitude=latitude,
            longitude=-121.0,
            bearing_deg=0.0,
            width_m=width,
            unidirectional=True,
        )

    def test_calibrates_intermediate_gates_in_driving_order(self):
        df = self.make_run()

        # Deliberately supply stations out of file/order sequence.
        gates = [
            self.gate("Start", TRAP_START, 37.0000),
            self.gate("Station 3", TRAP_INTERMEDIATE, 37.00075),
            self.gate("Station 1", TRAP_INTERMEDIATE, 37.00025),
            self.gate("Finish", TRAP_FINISH, 37.0010),
            self.gate("Station 2", TRAP_INTERMEDIATE, 37.00050),
        ]

        boundaries = calibrate_boundaries(df, gates)

        self.assertEqual(
            [boundary.name for boundary in boundaries],
            [
                "Start",
                "Station 1",
                "Station 2",
                "Station 3",
                "Finish",
            ],
        )

        self.assertAlmostEqual(boundaries[0].distance_m, 0.0)
        self.assertAlmostEqual(boundaries[-1].distance_m, 111.320)

    def test_reverse_course_uses_actual_driving_order(self):
        df = self.make_run()

        gates = [
            self.gate("Start", TRAP_START, 37.0000),
            self.gate("Station 6", TRAP_INTERMEDIATE, 37.00025),
            self.gate("Station 5", TRAP_INTERMEDIATE, 37.00050),
            self.gate("Station 4", TRAP_INTERMEDIATE, 37.00075),
            self.gate("Finish", TRAP_FINISH, 37.0010),
        ]

        boundaries = calibrate_boundaries(df, gates)

        self.assertEqual(
            [boundary.name for boundary in boundaries],
            [
                "Start",
                "Station 6",
                "Station 5",
                "Station 4",
                "Finish",
            ],
        )

    def test_missing_intermediate_gate_fails_closed(self):
        df = self.make_run()

        gates = [
            self.gate("Start", TRAP_START, 37.0000),
            RaceChronoGate(
                name="Station 1",
                trap_type=TRAP_INTERMEDIATE,
                latitude=37.0005,
                longitude=-121.0010,
                bearing_deg=0.0,
                width_m=10.0,
                unidirectional=True,
            ),
            self.gate("Finish", TRAP_FINISH, 37.0010),
        ]

        with self.assertRaisesRegex(
            TrackCalibrationError,
            "was not crossed",
        ):
            calibrate_boundaries(df, gates)

    def test_multiple_crossings_fail_closed(self):
        # North, south, then north across the same gate.
        df = pd.DataFrame(
            {
                "latitude": [
                    37.0000,
                    37.0006,
                    37.0002,
                    37.0008,
                    37.0010,
                ],
                "longitude": [-121.0] * 5,
                "distance": [0.0, 60.0, 100.0, 160.0, 180.0],
            }
        )

        gates = [
            self.gate("Start", TRAP_START, 37.0000),
            self.gate("Station 1", TRAP_INTERMEDIATE, 37.0004),
            self.gate("Finish", TRAP_FINISH, 37.0010),
        ]

        with self.assertRaisesRegex(
            TrackCalibrationError,
            "ambiguous crossings",
        ):
            calibrate_boundaries(df, gates)

    def test_segments_are_contiguous_and_cover_lap(self):
        df = self.make_run()

        gates = [
            self.gate("Start", TRAP_START, 37.0000),
            self.gate("Station 1", TRAP_INTERMEDIATE, 37.0003),
            self.gate("Station 2", TRAP_INTERMEDIATE, 37.0007),
            self.gate("Finish", TRAP_FINISH, 37.0010),
        ]

        boundaries = calibrate_boundaries(df, gates)
        segments = boundaries_to_segments(boundaries)

        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0]["start_distance"], 0.0)
        self.assertAlmostEqual(
            segments[-1]["end_distance"],
            111.320,
            places=3,
        )

        for previous, current in zip(segments, segments[1:]):
            self.assertEqual(
                previous["end_distance"],
                current["start_distance"],
            )

    def test_loads_rcz_units_correctly(self):
        payload = {
            "track": {
                "traps": [
                    {
                        "name": "Start",
                        "type": 1,
                        "centerLatitude": 222000000,
                        "centerLongitude": -726000000,
                        "bearing": 321000,
                        "width": 25000,
                        "uniDirectional": True,
                    },
                    {
                        "name": "Station 1",
                        "type": 4,
                        "centerLatitude": 222003000,
                        "centerLongitude": -726003000,
                        "bearing": 123456,
                        "width": 30000,
                        "uniDirectional": True,
                    },
                    {
                        "name": "Finish",
                        "type": 2,
                        "centerLatitude": 222006000,
                        "centerLongitude": -726006000,
                        "bearing": 180000,
                        "width": 50000,
                        "uniDirectional": True,
                    },
                ]
            }
        }

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "track.rcz"

            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(
                    "trackId.json",
                    json.dumps(payload),
                )

            gates = load_racechrono_track(path)

        self.assertEqual(len(gates), 3)

        station = gates[1]

        self.assertEqual(station.name, "Station 1")
        self.assertEqual(station.trap_type, TRAP_INTERMEDIATE)
        self.assertAlmostEqual(station.latitude, 37.0005)
        self.assertAlmostEqual(station.longitude, -121.0005)
        self.assertAlmostEqual(station.bearing_deg, 123.456)
        self.assertAlmostEqual(station.width_m, 30.0)


if __name__ == "__main__":
    unittest.main()
