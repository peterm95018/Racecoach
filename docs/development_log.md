2026-06 GPS Investigation

Goal

Understand why segment timing did not match official autocross timing.

Findings

Crows Landing 2026-03-01

Run labeled Lap 4 showed:

* Minimum speed = 2.4 mph
* Time below 5 mph = 1.46 sec

Initially suspected data corruption.

Further investigation showed telemetry was internally consistent.

GGLC 2025-11-01

Re-exported RaceChrono data.

Official times:

Run 4 = 30.035
Run 5 = 29.875

Segment timing still failed to reconcile.

GPS Discovery

Raw CSV headers contain:

* latitude
* longitude

RaceCoach normalization was discarding GPS coordinates.

Support added to preserve:

* latitude
* longitude

GPS coordinates verified to be consistent across runs.

Current Hypothesis

Distance traveled is not a stable representation of physical course position.

Future development should investigate GPS-based segment definitions.

GPS Anchor Experiment

Date: 2026-06

Goal

Determine whether GPS coordinates can replace distance-based segmentation.

Method

* Preserved latitude and longitude from RaceChrono exports.
* Built nearest-point GPS anchor comparison.
* Tested GGLC 2025-11-01 Lap 4 vs Lap 5.

Result

GPS anchor matching was highly accurate:

* Typical anchor error: 0–1.1 meters.

However, timing deltas did not reconcile with official run times.

Example:

Official:

* Lap 4 = 30.035
* Lap 5 = 29.875
* Difference = -0.160 sec

GPS anchor segments produced cumulative differences far larger than official timing.

Conclusion

Nearest-GPS-point matching is insufficient for segment timing.

Likely next approach:

Reference-path projection.

A reference lap will be treated as the course centerline. Other laps will be projected onto that path to produce a stable course-position coordinate.