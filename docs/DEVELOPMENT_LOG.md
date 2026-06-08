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

## 2026-06-05 — Average Speed Diagnostics

### Problem

Several reports contained large segment time losses that were not explained by:

- Minimum speed
- Exit speed
- Coast time
- Throttle pickup timing

Example:

text Finish section: +1.54s slower  Min speed: +0.4 mph Exit speed: +1.3 mph 

The telemetry suggested a significant loss, but the reported metrics did not explain it.

### Investigation

Added average segment speed calculations.

Testing against GGLC 2025-11-01 data showed:

text Finish section  Entry speed: -3.5 mph Average speed: -5.2 mph Minimum speed: +0.4 mph Exit speed: +1.3 mph 

This revealed that the segment was compromised before the apex and remained slower throughout the segment.

### Changes Implemented

#### Metrics

Added:

- Average speed
- Average speed delta

#### Coaching Logic

Added coaching rule:

text Average speed significantly lower than reference AND Exit speed does not explain the loss 

Resulting coaching:

text The loss developed through the segment rather than at the apex. Look earlier in the course for the mistake that carried into this section. 

#### Report Summary

Run Summary now prefers:

- Average speed delta
- Entry speed delta

when they explain the largest segment loss better than minimum speed or exit speed.

### Additional Improvements

Implemented over-driving detection:

text Higher minimum speed Lower exit speed Slower segment 

Coaching:

text Give up a little entry speed, rotate once, and protect the exit. 

### Outcome

Reports now better distinguish between:

1. Entry/setup problems
2. Over-driving
3. Exit-speed losses
4. Segment-wide speed deficits

This represents a significant improvement in coaching quality compared with earlier versions.

### Next Development Item

Momentum Recovery metric:

- Locate minimum-speed point
- Measure acceleration recovery after minimum speed
- Compare against reference lap
- Generate coaching based on recovery rate and timing

## 2026-06-08 — Momentum Recovery Foundation

### Added

- `recovery_speed_1s_mph`
- `reference_recovery_speed_1s_mph`
- `recovery_speed_delta_mph`

### Purpose

Measure how much speed is recovered one second after the minimum-speed point in a segment.

### Initial Finding

In the GGLC lap 5 vs lap 3 test, the Middle Course showed:

```text
Recovery speed (+1s): 3.0 vs 3.6 mph (-0.5)
