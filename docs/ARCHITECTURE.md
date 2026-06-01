# RaceCoach Architecture

## Purpose

RaceCoach analyzes RaceChrono telemetry from autocross events and produces coaching-oriented reports focused on measurable performance differences between runs.

## Current Workflow

### Event Setup

```text
./prep_event

events/<event>/
├── uploads/
├── processed/
├── reports/
├── segments.yaml
└── reference.csv
```

### Data Flow

```text
RaceChrono CSV
    ↓
FTPManager
    ↓
uploads/
    ↓
watch_uploads.py
    ↓
analyze_run.py
    ↓
reports/
```

## Core Components

### prep_event
Creates event structure and sets active event.

### watch_uploads.py
Monitors uploads folder and automatically analyzes new CSV files.

### analyze_run.py
Calculates segment metrics and compares against reference lap.

## Current Metrics

- Segment time
- Entry speed
- Minimum speed
- Exit speed
- Peak deceleration
- Coast time
- Throttle pickup timing
- Reference deltas

## Development Roadmap

### Completed

- Event management
- Auto analysis
- Reference lap comparison
- Git integration
- Throttle pickup timing
- Compact report format

### Next

- Improve throttle pickup detection
- Brake start timing
- Segment discovery tool
- Feature-based segments
- Video synchronization
- Grid coaching summaries



RaceCoach Architecture

Purpose

RaceCoach analyzes RaceChrono telemetry from autocross events and produces coaching-oriented reports focused on measurable performance differences between runs.

Current Workflow

Event Setup
./prep_event

events/<event>/
├── uploads/
├── processed/
├── reports/
├── segments.yaml
└── reference.csv

Data Flow

RaceChrono CSV
    ↓
FTPManager
    ↓
uploads/
    ↓
watch_uploads.py
    ↓
analyze_run.py
    ↓
reports/

Core Components

prep_event

Creates event structure and sets active event.

watch_uploads.py

Monitors uploads folder and automatically analyzes new CSV files.

analyze_run.py

Calculates segment metrics and compares against reference lap.

Current Metrics

* Segment time
* Entry speed
* Minimum speed
* Exit speed
* Peak deceleration
* Coast time
* Throttle pickup timing
* Reference deltas

Development Roadmap

Completed

* Event management
* Auto analysis
* Reference lap comparison
* Git integration
* Throttle pickup timing
* Compact report format

Next

* Improve throttle pickup detection
* Brake start timing
* Segment discovery tool
* Feature-based segments
* Video synchronization
* Grid coaching summaries


Telemetry Coordinate Systems

Original Approach

RaceCoach initially segmented autocross courses using RaceChrono’s distance_traveled field.

Example:
segments:
  - name: Launch
    start_distance: 0
    end_distance: 200

    The assumption was that distance represented a stable location on the course.

Investigation Findings

Multiple events were analyzed:

* Crows Landing 2026-03-01
* GGLC 2025-11-01

Results showed segment timing deltas that did not reconcile with official event timing.

Example:

Official:

* Run 4 = 30.035
* Run 5 = 29.875
* Delta = +0.160 sec

RaceCoach segment deltas:

* Launch = +0.23
* Middle = +0.06
* Finish = -1.11

Total = -0.82 sec

The sign of the result was opposite the official timing.

Discovery

Raw RaceChrono exports contain:

* latitude
* longitude
* speed
* distance_traveled
* OBD data
* accelerometer data

GPS coordinates are stable across runs.

Distance values vary significantly between runs on the same course.

Example:

Lap 4 max distance = 611.895
Lap 5 max distance = 609.456

GPS start and finish locations were nearly identical.

Conclusion:

Distance traveled should not be treated as a stable course coordinate.

Future Direction

Investigate GPS-position-based segmentation.

Potential approaches:

1. GPS anchor points
2. Reference path projection
3. Segment markers tied to GPS coordinates
4. RaceChrono split markers

Distance-based segmentation remains useful for initial experimentation but should not be considered authoritative.