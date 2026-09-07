# RaceCoach User Guide

RaceCoach is a driver coaching system that analyzes telemetry from each run and identifies the single driving behavior most likely to improve your next run.

Its purpose is simple:

> **What is the one thing I should do differently on my next run?**

RaceCoach is designed around the rhythm of an autocross day—from course walk to final results.

---

# Event Workflow

## Before Leaving Home

Prepare your equipment before arriving at the event.

### Equipment Checklist

- Charge iPhone
- Charge RaceBox GPS
- Charge GoPro (if used)
- Pack OBDLink
- Pack tire gauge and inflator
- Pack helmet and autocross equipment

### RaceCoach Checklist

- Verify the correct event is active.
- Confirm the upload service is running.
- Open the Grid Report URL once to verify connectivity.

---

## At the Event

### 1. Prepare the Event

Create a new RaceCoach event if necessary.

Review course map if available and try to create meaningful driving segments.

Walk the course carefully and create a RaceChrono Pro track marking traps with driving segments.

Good segment definitions produce better coaching.

---

### 2. Record a Run

Record telemetry using:

- RaceChrono Pro
- RaceBox GPS
- OBDLink (recommended)
- GoPro (optional)

Complete the run as normal.

---

### 3. Upload the Run

Export the completed run from RaceChrono.

Upload the CSV to the RaceCoach server.

RaceCoach automatically:

- Imports the run
- Compares it to the reference lap
- Updates the Grid Report
- Updates the Full Report

No additional analysis is normally required.

---

### 4. Review the Grid Report

During the break between runs, open the Grid Report.

Spend no more than **30 seconds** reviewing it.

Focus only on:

- Next Run
- Keep
- Quick Segment Check

Ignore the remaining details unless additional time is available.

The objective is to leave the grid with **one clear improvement** for the next run.

Do not attempt to fix multiple problems simultaneously.

---

### 5. Drive the Next Run

Trust the coaching.

Commit to the selected improvement.

Avoid changing driving style in multiple places on the course.

Repeat successful techniques while applying one new adjustment.

---

## After the Event

Review the Full Report after returning to paddock or at home.

Use it to understand:

- Where time was gained
- Where time was lost
- Why those differences occurred
- Which techniques consistently worked
- Which habits should become permanent

If available, review the Session Summary to identify patterns across the entire event rather than individual runs.

---

# Best Practices

RaceCoach is most effective when used consistently.

Follow these principles:

- Focus on one improvement per run.
- Reinforce successful techniques.
- Trust repeated patterns over isolated laps.
- Do not chase small timing differences.
- Let confidence determine how much weight to give each recommendation.

Remember:

> The objective is not to drive a perfect run.

> The objective is to drive a better run than the previous one.

---

# Typical Event Timeline

1. Prepare the event.
2. Walk the course; create a track map with segments.
3. Record a run.
4. Upload telemetry.
5. Review the Grid Report.
6. Drive the next run.
7. Repeat throughout the event.
8. Review the Full Report and Session Summary after the event.

---

# Related Documentation

- `REPORT_INTERPRETATION.md` — Understanding RaceCoach reports
- `COACHING_PHILOSOPHY.md` — Coaching principles and design philosophy
- `METRICS.md` — Definitions of telemetry metrics
- `DIAGNOSIS_MODEL.md` — How RaceCoach forms coaching recommendations
- `OPERATIONS.md` — Installation, event management, and system administration
- `ARCHITECTURE.md` — Software architecture and implementation
