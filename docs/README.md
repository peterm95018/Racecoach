# RaceCoach

RaceCoach is a telemetry-driven coaching system for autocross and track drivers.

Rather than overwhelming drivers with telemetry, RaceCoach identifies the **single driving behavior** most likely to improve the next run.

Telemetry is evidence.

Coaching is the product.

---

# How RaceCoach Works

RaceCoach follows a simple coaching workflow:

1. Record telemetry using RaceChrono Pro.
2. Upload the completed run.
3. Compare the run to a reference lap.
4. Diagnose the largest opportunity for improvement.
5. Generate coaching for the next run.

As additional runs are recorded, RaceCoach also identifies recurring strengths, recurring weaknesses, and long-term development trends.

---

## RaceCoach CLI

Common commands:

```bash
racecoach status
```
Show the current event status.

```bash
racecoach today
```
Display the active event dashboard.

```bash
racecoach doctor
```
Validate the RaceCoach installation and current event.

```bash
racecoach validate
```
Run automated regression validation, including unit tests and historical regression fixtures.

```bash
racecoach reference --promote --rebuild
```
Promote the selected reference run and rebuild the event.

```bash
racecoach finalize
```
Complete end-of-event processing by selecting the best reference and rebuilding reports.
```
---

# Reports

## Grid Report

Designed for the short break between runs.

Provides:

- One high-priority coaching objective
- One behavior to repeat
- A quick segment summary

Typical reading time is less than 30 seconds.

---

## Full Report

Provides a detailed comparison against the reference lap, including:

- Run Summary
- Next Run Focus
- Segment analysis
- Opportunity analysis
- Supporting telemetry

---

## Session Summary

Summarizes an entire event rather than a single run.

Identifies:

- Recurring strengths
- Recurring weaknesses
- Biggest improvements
- Development priorities before the next event

---

# Documentation

## New Users

Start here:

- `USER_GUIDE.md` — Using RaceCoach during an event
- `REPORT_INTERPRETATION.md` — Understanding RaceCoach reports

---

## Driver Coaching

- `COACHING_PHILOSOPHY.md`
- `DIAGNOSIS_MODEL.md`
- `METRICS.md`

---

## Developers

- `ARCHITECTURE.md`
- `OPERATIONS.md` -- Event-day operational procedures
- `CLI.md` -- Command reference and event workflow
- `TODO.md`
- `BACKLOG.md`
- `CHANGELOG.md`

---

# Project Philosophy

RaceCoach is designed to answer one question:

> **What is the one thing I should do differently on my next run?**

Every report, every diagnosis, and every metric exists to answer that question.


---

# Project Status

RaceCoach is under active development.

Current development focuses on:

- Improving coaching quality
- Better session-level analysis
- Long-term driver development across multiple events
- Clearer coaching language
- Higher-confidence diagnoses