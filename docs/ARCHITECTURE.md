# RaceCoach Architecture

## Purpose

RaceCoach analyzes RaceChrono telemetry from autocross events and produces coaching-oriented reports focused on measurable performance differences between runs.

## Production Data Source

RaceCoach is designed around:

- RaceChrono Pro
- RaceBox GPS
- OBDLink MX+

RaceChrono CSV exports are the canonical input format.

## Workflow

text RaceChrono CSV     ↓ uploads/     ↓ watch_uploads.py     ↓ analyze_run.py     ↓ reports/ 

## Event Structure

text events/<event>/ ├── uploads/ ├── processed/ ├── reports/ ├── segments.yaml └── reference.csv 

## Core Components

### prep_event

Creates event structure and sets active event.

### watch_uploads.py

Monitors uploads folder and automatically analyzes new CSV files.

### analyze_run.py

Calculates segment metrics and compares against the reference lap.

## Current Metrics

- Segment time delta
- Entry speed
- Average speed
- Minimum speed
- Exit speed
- Coast time
- Brake timing
- Throttle pickup timing

## Coaching Priority

RaceCoach currently prioritizes telemetry indicators in approximately this order:

1. Segment time delta
2. Exit speed
3. Average speed
4. Throttle pickup timing
5. Brake timing
6. Minimum speed
7. Coast time

## Current Segment Method

Segments are currently defined using:

yaml segments:   - name: Start     start_distance: 0     end_distance: 200 

Distance-based segmentation is currently the production method.

## Future Direction

Planned improvements:

- Momentum Recovery metric
- GPS anchor segments
- Reference path projection
- Path efficiency analysis
- Automatic segment discovery
- Video synchronization
- Grid coaching summaries
```
:::

Then keep ARCHITECTURE_COMPLETE.md as the detailed engineering history and design rationale document. That's where all the distance-vs-GPS discussion, average-speed diagnostics rationale, and future segmentation research belong.

## Low-Confidence Loss Filtering

Purpose:
Reduce false-positive coaching recommendations.

Implementation:
- classify_loss() can return "unexplained timing loss"
- low_confidence_loss() identifies segments with slower time but no meaningful telemetry degradation
- Such segments are excluded from:
  - Run Summary
  - Next Run Focus
  - Top Opportunities

They remain visible in:
  - Segment Time vs Reference Lap
  - Segment Table

This prevents coaching recommendations based solely on timing differences when entry speed, minimum speed, average speed, exit speed, braking, and throttle metrics do not indicate a clear driving error.