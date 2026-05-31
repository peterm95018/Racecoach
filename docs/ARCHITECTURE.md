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
