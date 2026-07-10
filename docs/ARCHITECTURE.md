RaceCoach Architecture

Purpose

RaceCoach analyzes RaceChrono telemetry from autocross events and transforms measurable performance differences into actionable driver coaching.

Rather than simply reporting telemetry, RaceCoach attempts to answer:

Why was this run faster or slower, and what should the driver change next?

⸻

System Overview

RaceCoach consists of five major layers:

1. Telemetry Import
2. Analysis Engine
3. Diagnosis Engine
4. Coaching Engine
5. Report Generation

Each layer has a single responsibility and passes structured information to the next stage.

⸻

Processing Pipeline

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
Driver Diagnosis
        │
        ▼
Opportunity Ranking
        │
        ▼
Report Generation
        │
        ▼
HTML / Markdown / JSON

⸻

Core Modules

Telemetry Import

Imports RaceChrono CSV files and normalizes telemetry channels from GPS, OBD-II, and calculated RaceChrono values.

⸻

Reference Path

Projects each analysis sample onto the reference lap.

This allows segment boundaries to follow the actual driven path instead of relying solely on cumulative distance.

⸻

Metrics Engine

Calculates performance metrics including:

* Segment time
* Entry speed
* Average speed
* Minimum speed
* Exit speed
* Brake timing
* Brake start distance
* Coast time
* Throttle commitment
* Recovery metrics

⸻

Diagnosis Engine

Evaluates telemetry differences to determine why a segment gained or lost time.

The diagnosis engine attempts to identify:

* Late throttle commitment
* Weak exit speed
* Excess braking
* Excess coasting
* Overslowing
* Over-driving
* Low-confidence timing losses

⸻

Coaching Engine

Converts diagnostic results into coaching recommendations.

The coaching engine prioritizes advice that:

* is supported by telemetry,
* has high confidence,
* can be applied on the next run,
* reinforces successful techniques as well as correcting mistakes.

⸻

Report Generator

Produces:

* Grid Report
* Full Report
* JSON Summary
* Session Summary (under development)

Reports are generated from a common analysis pipeline to ensure consistency.

⸻

Driver Input Selection

RaceCoach automatically selects the best available throttle source.

Preferred order:

1. accelerator_pos
2. relative_throttle_pos
3. throttle_pos

The selected source is recorded in the generated report.

⸻

Low-Confidence Filtering

RaceCoach intentionally suppresses coaching recommendations when telemetry does not clearly explain a time loss.

Segments may still appear in timing summaries but are excluded from coaching sections when no meaningful driving difference can be identified.

This reduces false-positive coaching recommendations.

⸻

Design Principles

RaceCoach is built around five principles.

Coach the Driver, Not the Telemetry

Telemetry exists to explain driving behavior, not simply to present numbers.

Provide Actionable Advice

Every recommendation should help improve the next run.

Ignore Low-Confidence Conclusions

Avoid coaching when the data does not support a clear explanation.

Reinforce Success

Repeatable gains are just as valuable as identifying mistakes.

Keep the Driver Focused

The Grid Report emphasizes a single improvement between runs rather than overwhelming the driver with data.

⸻

Current Limitations

Current limitations include:

* Segment definitions remain event-specific.
* Coaching quality depends on telemetry quality.
* Recovery metrics continue to be refined.
* Driver diagnosis is primarily rule-based.
* Some advanced path-analysis concepts remain under development.

⸻

Related Documentation

* USER_GUIDE.md
* OPERATIONS.md
* METRICS.md
* DIAGNOSIS_MODEL.md
* REPORT_INTERPRETATION.md
* COACHING_PHILOSOPHY.md