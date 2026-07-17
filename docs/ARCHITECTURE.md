# RaceCoach Architecture

## Purpose

RaceCoach transforms telemetry into coaching.

Telemetry provides evidence.

Diagnosis explains performance.

Coaching tells the driver what to improve on the next run.

RaceCoach analyzes RaceChrono telemetry from autocross events and transforms measurable performance differences into actionable coaching. Rather than simply reporting telemetry, the system attempts to answer one question:

**Why was this run faster or slower, and what should the driver change next?**

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

RaceCoach consists of five major components:

1. Telemetry Import
2. Metrics Engine
3. Diagnosis Engine
4. Coaching Engine
5. Report Generation

Each component has a single responsibility and passes structured information to the next stage.

---

# Processing Pipeline

```
RaceChrono CSV
        │
        ▼
Telemetry Import
        │
        ▼
Reference Path Projection
        │
        ▼
Segment Assignment
        │
        ▼
Metric Calculation
        │
        ▼
Diagnosis Engine
        │
        ▼
Confidence Evaluation
        │
        ▼
Coaching Selection
        │
        ▼
Report Generation
        │
        ▼
HTML / Markdown / JSON
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

# Design Principles

The architecture follows several guiding principles.

## Coach the Driver, Not the Telemetry

Telemetry exists to explain driving behavior, not simply present numbers.

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