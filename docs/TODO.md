# RaceCoach Development Roadmap

This document defines the planned development path for RaceCoach.

It intentionally focuses on **future work** and the current production baseline. Historical implementation details are maintained separately in the design documentation.

---

Session Summary Enhancement

Goal

Develop session_summary into the primary end-of-day coaching report that summarizes an entire event rather than a single run.

Objectives

* Identify recurring strengths across all analyzed runs.
* Identify recurring opportunities that appear in multiple runs.
* Measure improvement by segment over the course of the day.
* Highlight the run with the biggest improvement in each segment.
* Detect persistent habits such as:
    * Late throttle commitment
    * Excess coasting
    * Early braking
    * Weak exit speed
* Produce an overall driver scorecard for the event.

Planned Report Sections

* Session Overview
* Driver Scorecard
* Biggest Improvements
* Recurring Opportunities
* Segment Trends
* Best Segment Performances
* Coaching Themes
* Next Event Focus

Future Enhancements

* Compare multiple events over time.
* Track driver improvement trends across the season.
* Build a personalized coaching history from recurring strengths and weaknesses.
* Generate season-long performance statistics by segment type.

# Current Stable Baseline

**Git Tag:** `reference-path-stable`

## Current Production Features

- Five named course segments
- Distance-normalized reference-path segmentation
- Stable Grid Report generation
- Markdown and HTML reports
- Session summaries
- Opportunity ranking and confidence filtering
- Debug segment logging (`RACECOACH_DEBUG_SEGMENTS`)
- Production-ready event analysis

## Current Limitations

- Reference position is derived from normalized lap distance rather than true GPS projection.
- Segment boundaries assume similar driving lines.
- Courses with significant shortcuts, alternate lines, or overlapping paths are not yet fully supported.

---

# Phase 1 — Event Organization

## 1. Course Variants (High Priority)

### Goal

Support multiple course layouts within a single event.

Example:

```text
events/
    ggr_2026-07-11/
        event.yaml

        morning/
            uploads/
            reports/
            course_segments.yaml
            reference_path.json

        afternoon/
            uploads/
            reports/
            course_segments.yaml
            reference_path.json
```

### Shared Event Data

- Event information
- Weather
- Tire pressure log
- Vehicle setup
- Driver notes

### Variant-Specific Data

- RaceChrono track
- Reference path
- Course segments
- Uploaded telemetry
- Reports
- Reference lap

### Future Enhancement

Automatically detect when a course has changed enough to recommend creating a new course variant.

---

## 2. Event Setup Wizard

Simplify event preparation.

Features:

- Create event
- Create course variant
- Import course segments
- Validate event configuration
- Select reference lap

---

## 3. Automatic Segment Validation

Automatically verify:

- Every segment receives telemetry samples
- No empty segments
- Reasonable segment durations
- Proper segment ordering

---

# Phase 2 — GPS Reference Projection

## Goal

Replace normalized-distance reference positioning with robust GPS reference-path projection.

The current normalized-distance implementation remains the production baseline until this phase meets all validation criteria.

## Required Capabilities

- Heading-aware nearest-point matching
- Forward-only progression
- Local search window
- Jump rejection
- Turnaround handling
- Overlapping path handling
- Projection confidence scoring

## Validation

The new implementation must perform at least as well as the current production baseline.

Primary validation case:

**GGLC 2026-06-20**

Reference Lap 1 → Analysis Lap 2

Success criteria:

- All expected segments populated
- Plausible segment timing
- No false large gains/losses
- Stable coaching output
- Equal or better coaching quality than the normalized-distance approach

---

# Phase 3 — Driver Coaching

## Opportunity Detection

Improve diagnosis of:

- Braking
- Throttle pickup
- Throttle commitment
- Coasting
- Line errors
- Momentum loss
- Confidence scoring

## Coaching Prioritization

Improve:

- Opportunity ranking
- Confidence metrics
- Detection of repeated mistakes
- "One Thing to Fix" recommendations

---

# Phase 4 — Reporting

## HTML Reports

- Improved formatting
- Responsive layout
- Interactive visualizations

## Visual Analysis

- Reference vs. analysis overlays
- Momentum visualizations
- Speed recovery charts
- Braking overlays

## Session Reports

- Session summaries
- Trend reports
- Improvement tracking
- Best run progression

---

# Phase 5 — Long-Term Analytics

- Multi-run trend analysis
- Driver improvement over a season
- AI-generated coaching summaries
- Racing-line comparison
- Video synchronization
- Cross-event performance tracking

---

# Documentation Improvements

## Architecture Decision Records (ADR)

Record significant design decisions.

Proposed structure:

```text
docs/
    ROADMAP.md
    ARCHITECTURE.md
    USER_GUIDE.md

    adr/
        0001-reference-path-segmentation.md
        0002-driver-coaching-metrics.md
        0003-course-variants.md
```

Each ADR should explain:

- The problem
- Alternatives considered
- Decision made
- Rationale
- Consequences

---

## Design Documentation

Implementation history and engineering notes should be maintained separately from the roadmap.

Example:

```text
docs/design/
    reference_path_segmentation.md
```

This keeps the roadmap focused on future development while preserving the reasoning behind past architectural decisions.

---

# Guiding Principles

RaceCoach development should prioritize:

1. Reliable coaching over experimental algorithms.
2. Stable production behavior before adding new features.
3. Improvements that provide actionable feedback between autocross runs.
4. Maintainable architecture that supports future analytics and visualization.
5. Validation against real event data before replacing production algorithms.


Diagnosis Model Validation

* Verify that current code produces the diagnoses documented in DIAGNOSIS_MODEL.md.
* Confirm that Low Confidence is implemented as a confidence state rather than a driving diagnosis.
* Add or validate the Weak Exit diagnosis.
* Standardize terminology across reports:
    * Throttle commitment
    * Over-driving
    * Over-slowing
    * Momentum loss
    * Weak exit
* Confirm that Grid Reports expose only one primary diagnosis, one action, and one mental cue.