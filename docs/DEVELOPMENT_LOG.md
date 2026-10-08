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

```
---

## 2026-09-13 — Crows Landing Segment Coverage Failure

### Goal

Use RaceCoach for between-run coaching on the unusually long LPR Crows Landing autocross course.

The event was an important live test because the course was approximately two minutes long and substantially longer than the courses used during earlier development.

### Failure

RaceCoach received valid RaceChrono telemetry, but analysis failed with a segment-coverage error.

The configured segment definitions ended at approximately 520 meters while the actual timed course was much longer.

The failure exposed a dangerous assumption in the event setup process: a generic or placeholder segment file could appear structurally valid while describing only a small portion of the actual course.

### Investigation

Independent validation of Run 1 showed that the telemetry itself was valid and represented a complete long autocross run.

The problem was therefore not the RaceChrono export. It was the relationship between the configured segment geometry and the actual timed course.

This led to several hardening requirements:

- Segment coverage must represent the complete timed course.
- Gaps, overlaps, nonzero starts, and materially incomplete finishes must fail validation.
- Trimming or preprocessing must not hide a mismatch between the original timed-lap distance and the configured course.
- RaceCoach must not produce coaching from telemetry that cannot be mapped confidently to the configured course.
- GPS course geometry should be checked against the reference when a separate reference run exists.

### Design Principle

RaceCoach should fail closed when course identity or course coverage is uncertain.

Producing no coaching is preferable to producing apparently precise coaching against incorrect segment geometry.

### Outcome

Course-readiness, segment-coverage, preprocessing, and GPS-geometry validation were strengthened.

This solved an important class of silent-analysis failures, but it did not yet solve how correct segment boundaries would be created at an event.
---

## 2026-10-03 to 2026-10-08 — RaceChrono Gate-Based Course Calibration

### Problem Exposed at the October 3 Event

The October 3 LPR Crows Landing event exposed the remaining weakness in the course-segmentation workflow.

RaceCoach expected the event's segment distances to be configured before useful analysis could begin. That requirement was not operationally realistic.

During a course walk, the driver can identify meaningful physical features such as boxes, offsets, turnaround entry and exit, slaloms, jogs, and the finish approach. The driver does not, however, know their telemetry distances in meters.

Manually determining or editing those distances during course preparation is incompatible with the intended RaceCoach event-day workflow.

### Key Insight

RaceChrono Pro already provides a practical way to describe the physical course during the course walk.

A RaceChrono track can contain:

- one Start gate
- one Finish gate
- intermediate gates placed at recognizable course stations

The intermediate gates can be named during the walk without knowing their eventual RaceCoach distances.

This changed the segmentation problem from:

"Determine all segment distances before driving"

to:

"Identify physical stations during the walk, then determine their distances from the first timed run."

### Architecture Decision

RaceCoach now uses the RaceChrono `.rcz` track as the event's physical station definition.

For an unconfigured event:

1. RaceCoach reads the RaceChrono track.
2. Start, Finish, and intermediate gates are extracted.
3. The first valid timed run provides the actual driven GPS trajectory.
4. Each intermediate gate is intersected with that trajectory.
5. Gate crossings are converted to distances along the timed run.
6. Crossings are sorted in actual driving order.
7. Adjacent boundaries become contiguous RaceCoach segments.
8. The calibrated segments are persisted in `segments.yaml`.
9. A `course_trace.png` is generated as a human-readable calibration check.

The RaceChrono file therefore defines physical stations while Run 1 establishes their distance coordinates.

### Fixed-Boundary Rule

Calibration occurs only while the event is unconfigured.

After Run 1 calibration, Runs 2 through N use the persisted Run-1 boundaries. Later runs do not recalibrate the stations from their own GPS trajectories.

This is a critical invariant because run-to-run coaching requires every run to be measured against the same physical segmentation.

### Course-Walk Gate Placement

During the course walk, place each intermediate RaceChrono gate at the intended station marker and near the expected driven line.

Gate widths may be reduced when necessary to prevent nearby RaceChrono gates from overlapping.

The driver needs to identify the physical station correctly; the driver does not need to determine its distance.

### Fail-Closed Behavior

Automatic calibration is rejected when RaceCoach cannot establish the course confidently.

Examples include:

- no RaceChrono track
- multiple RaceChrono track files
- malformed track data
- missing Start or Finish
- an intermediate gate not crossed by Run 1
- an intermediate gate crossed ambiguously more than once
- boundaries that cannot be placed in a strict driven order
- invalid or incomplete GPS data
- failure to generate the calibration trace

Calibration artifacts are generated before the event is marked configured.

`segments.yaml` is written through a temporary file and atomically replaced so an interrupted write cannot leave a partially configured event.
### Historical Validation

The new architecture was tested against the October 3 Crows Landing data.

Run 1 produced nine contiguous segments:

1. Start -> Box 1
2. Box 1 -> Outbound offsets
3. Outbound offsets -> Turnaround entry
4. Turnaround entry -> Turnaround exit
5. Turnaround exit -> Station 4 box 2
6. Station 4 box 2 -> Full width offsets
7. Full width offsets -> Slalom across to jog
8. Slalom across to jog -> Decreasing radius to finish
9. Decreasing radius to finish -> Finish

The calibrated course extended from 0.0 m to approximately 1679.3 m.

All eight intermediate gates were crossed exactly once. The resulting gate offsets from the driven trajectory also validated the interpretation of the RaceChrono gate geometry.

### Subsequent-Run Validation

Run 2 successfully reused the Run-1 segment boundaries rather than recalibrating them.

Run 3 was then uploaded through the normal watcher workflow.

RaceCoach successfully:

- detected the upload
- selected the timed lap
- validated course geometry
- reused the fixed RaceChrono-derived segments
- compared all nine segments against the Run-1 reference
- generated the run report
- generated the grid report
- published the reports to Drupal

Run 3 was faster than Run 1 in all nine segments.

This demonstrated that the segmentation, reference, watcher, reporting, and publication pipeline was operating correctly. Later review identified the coaching text itself as the next area requiring improvement.

### Automated Validation

Regression coverage included:

- RaceChrono unit conversion
- gate calibration in driven order
- reverse-course ordering
- missing-gate rejection
- ambiguous multiple-crossing rejection
- contiguous full-lap segment generation
- automatic calibration of an unconfigured event
- prevention of recalibration for a configured event
- missing RCZ fail-closed behavior
- multiple RCZ fail-closed behavior
- calibration-error handling
- course readiness
- segment coverage
- preprocessing
- diagnosis regression
- watcher behavior

The final focused regression suite completed 43 tests successfully.

### Production Checkpoint

The implementation was committed as:

`ed54353 Add RaceChrono gate-based course calibration`

The work was fast-forwarded into `momentum-recovery` and pushed to `origin/momentum-recovery`.

### Outcome

The September and October failures established two complementary requirements:

1. RaceCoach must reject incorrect or incomplete course geometry.
2. RaceCoach must provide a realistic event-day method for creating correct course geometry.

The RaceChrono gate-calibration workflow satisfies both.

The intended event-day model is now:

Course walk -> create RaceChrono track and station gates -> Run 1 -> automatic station calibration -> persist fixed segment geometry -> establish reference -> Runs 2-N -> fixed-segment comparison -> coaching -> report publication.

This removes manual segment-distance calculation from the driver's course-walk responsibilities while preserving stable physical segments for the remainder of the event.
