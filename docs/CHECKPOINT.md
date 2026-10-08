# RaceCoach Checkpoint

**Date:** 2026-10-08
**Branch:** `momentum-recovery`
**Production baseline:** `ed54353 Add RaceChrono gate-based course calibration`

## Current State

RaceCoach has a working end-to-end event pipeline for RaceChrono-based autocross analysis.

The current workflow is:

Course walk -> create RaceChrono track and named station gates -> Run 1 upload -> automatic course calibration -> fixed segment geometry -> reference establishment -> Runs 2-N -> segment comparison -> coaching -> report generation -> Drupal publication.

## Course Calibration

For an unconfigured event, RaceCoach can use a RaceChrono `.rcz` track and the first valid timed run to create the course segmentation automatically.

The calibration process:

- extracts Start, Finish, and intermediate RaceChrono gates
- intersects intermediate gates with the Run-1 GPS trajectory
- determines station distances in actual driving order
- generates contiguous named segments
- generates `course_trace.png`
- persists the calibrated geometry in `segments.yaml`

After calibration, the segment boundaries are fixed. Subsequent runs do not recalibrate against their own trajectories.

## Safety and Validation

RaceCoach fails closed when course geometry cannot be established confidently.

Current protections include:

- incomplete segment coverage detection
- gap and overlap detection
- nonzero course-start detection
- timed-lap distance validation
- GPS course-geometry validation against a reference
- missing RCZ rejection
- multiple RCZ rejection
- malformed RCZ rejection
- missing Start or Finish rejection
- missing intermediate-gate crossing rejection
- ambiguous multiple-crossing rejection
- atomic calibrated `segments.yaml` persistence

The focused regression suite currently passes 43 tests.

## Historical Event Validation

The RaceChrono calibration workflow was validated with the October 3, 2026 LPR Crows Landing event.

Run 1 calibrated nine segments covering approximately 0.0-1679.3 m.

Run 2 reused the Run-1 boundaries without recalibration.

Run 3 was processed through the normal upload watcher and successfully completed:

- timed-lap selection
- GPS geometry validation
- fixed-segment comparison
- report generation
- grid report generation
- Drupal publication

Run 3 was faster than Run 1 in all nine segments.

## Reference and Reporting Pipeline

The live workflow currently supports:

- event-based directories
- `active_event.txt`
- event preparation
- automatic upload watching
- timed-lap selection
- reference selection
- clean/provisional reference handling
- reference-change report rebuilding
- Markdown and HTML reports
- grid reports
- Drupal publication
- fail-closed data-quality reporting

## Current Development Boundary

The course-definition and run-comparison infrastructure is now sufficiently reliable to return development focus to coaching quality.

The October 3 validation showed that correct segment comparisons can still produce weak or misleading coaching text.

Example:

When Run 3 was faster than Run 1 in all nine segments, RaceCoach reported:

`No high-confidence opportunities detected. Check segment definitions and reference run.`

The first sentence was reasonable. The second was misleading because the segment definitions and reference pipeline had already validated successfully.

## Next Development Target

Improve coaching logic and report language while preserving the validated telemetry, segmentation, reference, and watcher infrastructure.

Primary goals:

1. Distinguish "no detected problem" from "analysis may be invalid."
2. Reinforce improvements when a run is faster across multiple segments.
3. Produce a useful next-run focus even when no high-confidence loss diagnosis exists.
4. Avoid suggesting telemetry or segment-definition problems unless validation actually found one.
5. Keep coaching concise and actionable between runs.

Do not weaken the existing fail-closed course and telemetry validation to improve coaching output.

## Repository Notes

The following working-tree items are not part of the RaceChrono calibration implementation or this documentation update and should not be committed accidentally:

- `publish_reports.sh`
- historical/untracked event directories
- `racecoach/analyze_run.py.pre_rcz_integration`

The RaceChrono implementation itself is already committed and pushed at `ed54353`.
