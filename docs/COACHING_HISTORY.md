RaceCoach Coaching History

Purpose

This document records why RaceCoach shifted from telemetry reporting toward diagnosis-based coaching.

The goal is to preserve the reasoning behind recent changes so future development stays aligned with the project direction.

⸻

Original Problem

RaceCoach was producing useful telemetry, but some report language was still too engineering-focused.

Examples:

* Minimum speed
* Throttle after min speed
* Throttle pickup
* Exit speed delta
* Average speed delta

These terms are useful internally but not always useful to a driver sitting on grid.

The driver needs to know:

* What happened?
* Why did it matter?
* What should I do next run?

⸻

Coaching Philosophy Shift

We decided that RaceCoach should not primarily report metrics.

RaceCoach should diagnose driving behavior.

New preferred structure:

1. Diagnosis
2. Evidence
3. Action

Example:

Before:

Why: Momentum Loss -5.2 mph

After:

Diagnosis: Momentum Loss
Evidence: Average speed -5.2 mph
Do this: Look for excess steering, early braking, or extra distance.

⸻

Key Design Principle

RaceCoach should coach driving behavior, not telemetry labels.

Telemetry remains important, but it should support the diagnosis rather than being the headline.

⸻

Late to Power Language

We replaced confusing throttle language such as:

Throttle pickup was later after minimum speed.

with driver-facing language:

You waited 0.32 s too long to get back to power.

Preferred coaching cue:

Commit to throttle as soon as the car is pointed.

Reason:

“After minimum speed” is an implementation detail. The driver experiences this as hesitation after the car is ready to accelerate.

⸻

Low-Confidence Fallback

We improved cases where RaceCoach could detect a time loss but could not identify a strong telemetry cause.

Before:

Repeat the reference technique.

After:

Small loss with no clear telemetry fault. Do not chase a setup change.

Reason:

When evidence is weak or conflicting, RaceCoach should prevent overreaction. The correct advice may be to drive cleanly rather than change technique.

⸻

Diagnosis Names in Grid Report

We changed Grid Report language from telemetry-first labels to diagnosis names.

Examples:

* Weak Exit
* Late to Power
* Over Slowing
* Momentum Loss
* Low Confidence
* No Clear Diagnosis

Reason:

The Grid Report should read like a coach’s summary, not a telemetry table.

⸻

Diagnosis vs Evidence Separation

We separated diagnosis from evidence.

Before:

Why: Weak Exit -10.4 mph

After:

Diagnosis: Weak Exit
Evidence: Exit speed -10.4 mph

Reason:

A diagnosis is the interpretation. Evidence is the measurement supporting it. Mixing them made the report harder to scan and less coach-like.

⸻

Current Direction

RaceCoach is evolving into four layers:

1. Telemetry
2. Metrics
3. Diagnosis
4. Coaching

The next architectural step should be a structured diagnosis object, likely something like:

Diagnosis(
    name="Weak Exit",
    confidence="High",
    evidence=[
        "Exit speed -10.4 mph",
    ],
    action="Unwind earlier and protect exit speed.",
    cue="Point, then power."
)

This would reduce duplication across:

* classify_loss()
* primary_cause()
* primary_evidence()
* primary_action()
* driver_translation()
* coach_text()

⸻

Why This Matters

The July 11–12 Porsche Club Salinas events are intended to field-test RaceCoach as a between-run coaching tool.

The objective is not more data.

The objective is one useful instruction before the next run.

## July 2026 — Separation of Driver Coaching and Developer Validation

### Problem

As the diagnosis engine matured, the grid report began exposing internal scoring details such as diagnosis scores, competing diagnoses, and score contributions.

While useful during development, these details created unnecessary cognitive load for the driver and could be mistaken for telemetry values or timing data.

### Decision

Separate RaceCoach into two audiences.

#### Driver (Grid Report)

Designed for use on grid between runs.

The report should answer only:

- What happened?
- Why did it happen?
- What should I do differently?

The driver should never need to understand the diagnosis algorithm.

#### Developer (Validation Report)

Designed for post-event analysis and algorithm tuning.

This report will include:

- All diagnosis scores
- Winning and runner-up diagnoses
- Confidence calculations
- Score contributions
- Conflicting evidence
- Threshold decisions
- Validation against expected outcomes

### Coaching Philosophy

RaceCoach should coach like an experienced instructor.

The driver receives a simple coaching cue.

The software performs the complex reasoning behind the scenes.

### Design Principle

Telemetry → Diagnosis → Coaching

Not

Telemetry → Algorithm → Driver

The diagnosis engine exists to translate telemetry into language that helps the driver improve, not to expose its internal implementation.