# RaceCoach Architecture

## Purpose

RaceCoach transforms telemetry into coaching.

Telemetry provides evidence.

Diagnosis explains performance.

Coaching tells the driver what to improve on the next run.

RaceCoach analyzes RaceChrono telemetry from autocross events and transforms measurable performance differences into actionable coaching. Rather than simply reporting telemetry, the system attempts to answer one question:

**Why was this run faster or slower, and what should the driver change next?**

---

## Event Structure

Each RaceCoach event is self-contained under:

```text
events/<event-name>/
├── uploads/
├── reports/
├── segments.yaml
├── run_status.yaml
├── reference.csv
└── reference_selection.json
```

Each event contains everything required to reproduce the analysis independently of other events. This self-contained structure allows events to be archived, rebuilt, or reviewed without affecting any other event.


## Upload Processing

The `watch_uploads` module provides RaceCoach's real-time event processing. It monitors the active event's `uploads/` directory for newly exported RaceChrono CSV files and automatically analyzes each run against the current `reference.csv`. For every uploaded run, it generates the Full Report, Grid Report, and summary JSON, then publishes the latest reports for driver review. The upload watcher intentionally does not modify the session reference. Reference selection and event rebuilding are intentionally separate post-session workflows.

## Analysis Engine

The `analyze_run` module is the core telemetry analysis engine within RaceCoach. It analyzes a single RaceChrono CSV file against a single reference lap. During analysis it imports and normalizes telemetry, projects samples onto the reference path when enabled, computes segment-level performance metrics, evaluates diagnostic evidence, determines the highest-confidence coaching recommendation, and generates the Full Report, Grid Report, and summary JSON for that run.

The module is intentionally stateless. It analyzes one run against one explicit reference and does not manage session state, select reference laps, rebuild events, or publish reports. Those responsibilities belong to the orchestration modules that coordinate the overall event workflow.

## Session Summary

The `session_summary` module provides RaceCoach's session-level analysis. Rather than analyzing raw telemetry, it consumes the summary JSON produced for each run and evaluates performance across the entire event. It identifies the fastest clean run, measures driver repeatability using metrics such as best repeat, top-three spread, standard deviation, and clean-run percentage, highlights recurring segment losses, and generates `session_summary.md`. By operating entirely on run summary JSON rather than raw telemetry, the module remains independent of the telemetry analysis engine while providing a consolidated view of driver consistency and session-level performance.

## Report Publishing

The report publishing layer makes RaceCoach analysis available to the driver without participating in telemetry analysis. After each run is analyzed, the latest Grid Report and Full Report are converted into the published artifacts used during the event, while completed event reports remain preserved in the event directory. By separating publishing from analysis, RaceCoach can regenerate, republish, or switch between events without changing the underlying telemetry, diagnostics, or coaching results.


## Reference Selection

The `select_reference` module manages session reference optimization.

Responsibilities:

- Load analyzed run summaries.
- Select the fastest clean run, falling back to the fastest analyzed run when no clean run is available.
- Promote the selected CSV to `reference.csv`.
- Record the selection in `reference_selection.json`.
- Optionally rebuild the entire event.

This module operates independently of the upload watcher, allowing reference optimization to occur after all runs have been classified.



---

# Design Goals

RaceCoach is designed around several architectural principles:

- Coaching-first rather than telemetry-first.
- Modular components with clear responsibilities.
- Repeatable analysis using a reference lap.
- Reproducible reports from identical input data.
- Simple event-day operation.
- Extensible diagnostic framework.

---

# System Overview

RaceCoach has two architectural layers.

**Operational orchestration**

- Upload Processing
- Reference Selection
- Event Rebuild
- Session Summary
- Report Publishing

**Telemetry analysis**

- Telemetry Import
- Reference Path Projection
- Metrics
- Diagnosis
- Coaching
- Report Generation

The orchestration layer manages events, references, reports, and publishing. The telemetry analysis layer transforms a single run into coaching recommendations.


```markdown
The command-line interface (`racecoach`) provides the public entry point to these components. It orchestrates operational workflows such as status reporting, reference management, session summaries, and event finalization while delegating telemetry analysis to the underlying modules.


---

# Processing Pipeline

```
CSV Upload
      ↓
Analyze Against Current Reference
      ↓
Report Generation
      ↓
Summary JSON
      ↓
(Session Continues)

──────── End of Session ────────

Run Classification
      ↓
Reference Selection
      ↓
Reference Promotion
      ↓
Event Rebuild
      ↓
Final Reports
```

---

# Data Flow

The information flowing through the system becomes progressively more meaningful.

```
Telemetry Samples
        ↓
Segment Metrics
        ↓
Supporting Evidence
        ↓
Diagnosis
        ↓
Confidence
        ↓
Coaching Recommendation
        ↓
Reports
```

Each stage builds upon the previous one.

Telemetry measures.

Metrics summarize.

Diagnosis explains.

Coaching guides improvement.

---

# Major Components

## Telemetry Import

Imports RaceChrono CSV files and normalizes telemetry collected from GPS, OBD-II, and RaceChrono calculated channels.

The output of this stage is a consistent telemetry dataset suitable for analysis.

---

## Reference Path Projection

Projects telemetry samples onto the reference lap.

Each event maintains a `reference.csv` used for comparative analysis. The first uploaded run initializes the reference. After the session, RaceCoach can automatically select a better reference (currently the fastest clean run) and rebuild the event so every report uses the same optimized reference.

Using the reference path allows segment boundaries to follow the actual driven line instead of relying solely on cumulative distance, improving repeatability when drivers take different paths through the course.

---

## Metrics Engine

Calculates performance measurements for each segment, including:

- Segment time
- Entry speed
- Average speed
- Minimum speed
- Exit speed
- Brake timing
- Brake start distance
- Peak deceleration
- Coast time
- Throttle commitment
- Recovery metrics

These measurements form the evidence used by the diagnosis engine.

---

## Diagnosis Engine

Evaluates telemetry differences to determine the most likely explanation for changes in segment performance.

Possible diagnoses include:

- Late to Power
- Over-Driving
- Over-Slowing
- Momentum Loss
- Weak Exit
- Execution Error
- No Clear Diagnosis

The diagnosis engine combines multiple telemetry measurements rather than relying on individual metrics.

---

## Confidence Evaluation

Every diagnosis is evaluated for confidence.

Confidence reflects:

- Strength of supporting evidence.
- Amount of conflicting evidence.
- Magnitude of telemetry differences.
- Ability of the diagnosis to explain the observed time difference.

Low-confidence diagnoses are intentionally filtered to reduce incorrect coaching recommendations.

---

## Coaching Engine

Converts diagnoses into driver coaching.

The coaching engine prioritizes recommendations that:

- Are strongly supported by telemetry.
- Have high diagnostic confidence.
- Can be applied on the very next run.
- Reinforce successful techniques as well as correcting mistakes.

The coaching engine is responsible for transforming analysis into actionable advice.

---

## Report Generation

RaceCoach produces multiple views of the same analysis.

These include:

- Grid Report
- Full Report
- Session Summary
- Markdown reports
- HTML reports
- JSON summaries

Each report presents the same underlying analysis while varying the level of detail for its intended audience.

---

# Component Boundaries

RaceCoach separates responsibilities between modules.

- `watch_uploads` processes newly uploaded runs.
- `select_reference` chooses and promotes references.
- `analyze_run` analyzes one run against one reference.
- `session_summary` aggregates summary JSON files.
- Publishing exposes reports without changing analysis.

These boundaries separate event orchestration from telemetry analysis. Keeping each module focused on a single responsibility makes RaceCoach easier to validate, test, and extend without introducing unintended coupling between components.

---

# Design Principles

The architecture follows several guiding principles.

## Coach the Driver, Not the Telemetry

Telemetry exists to explain driving behavior, not simply present numbers.

---

## Preserve Explicit Workflows

RaceCoach avoids hidden state changes.

Operations that affect historical analysis—such as run classification, reference promotion, and event rebuilding—are explicit user actions rather than automatic side effects.

This preserves reproducibility, keeps event processing predictable, and clearly separates real-time coaching from post-session optimization.

---

## Diagnose Before Coaching

Metrics become evidence.

Evidence supports diagnosis.

Diagnosis produces coaching.

---

## Prefer Confidence Over Certainty

When telemetry does not clearly explain a result, RaceCoach intentionally suppresses coaching rather than speculate.

---

## Reinforce Success

Repeatable gains deserve coaching attention just as much as mistakes.

---

## Keep the Driver Focused

Between runs, drivers should receive one clear coaching priority rather than a large collection of observations.

---

# Future Architecture

Future enhancements may include:

- Automated reference selection strategies.
- Richer GPS path analysis.
- Inefficient path detection.
- Driver-specific learning.
- Adaptive diagnostic thresholds.
- Multi-run trend analysis.
- Machine-assisted diagnosis.
- Live coaching support.

These enhancements should preserve the core coaching-first philosophy while improving diagnostic accuracy.

---

# Related Documentation

- `README.md`
- `USER_GUIDE.md`
- `COACHING_PHILOSOPHY.md`
- `DIAGNOSIS_MODEL.md`
- `METRICS.md`
- `REPORT_INTERPRETATION.md`
- `OPERATIONS.md`