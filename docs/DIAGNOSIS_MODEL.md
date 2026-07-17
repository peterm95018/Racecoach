\# RaceCoach Diagnosis Model

## Purpose

RaceCoach exists to diagnose driving behavior—not merely report telemetry differences.

Telemetry measures what happened.

Diagnosis explains why it happened.

Coaching tells the driver what to do next.

The objective is not to explain every difference between two runs. The objective is to identify the highest-confidence driving behavior that, if improved, will make the driver faster on the next run.

---

## Diagnosis Pipeline

RaceCoach follows a consistent reasoning process:

```
Telemetry
      ↓
Measurements
      ↓
Supporting Evidence
      ↓
Diagnosis
      ↓
Confidence
      ↓
Coaching
      ↓
Driver Improvement
```

Each diagnosis contains five components:

1. Diagnosis
2. Supporting Evidence
3. Conflicting Evidence
4. Confidence
5. Coaching and Mental Cue

Telemetry supports the diagnosis.

It is not the diagnosis.

---

## How RaceCoach Chooses a Diagnosis

Several diagnoses may fit the same telemetry.

RaceCoach selects the diagnosis that:

- Best explains the segment time.
- Has the strongest supporting evidence.
- Has the least conflicting evidence.
- Produces the clearest coaching recommendation.

RaceCoach intentionally reports only **one primary diagnosis** to avoid overwhelming the driver.

---

# Diagnosis Catalog

## Late to Power

### Supporting Evidence

- Throttle commitment is later than the reference.
- Exit speed is lower.
- Recovery speed is lower after minimum speed.
- Segment time loss develops after the rotation point.

### Conflicting Evidence

- Throttle commitment is earlier.
- Exit speed is equal or better.
- Recovery speed is equal or better.

### Coaching

Complete rotation sooner and commit to throttle as soon as the car is pointed.

### Mental Cue

> Point, then power.

---

## Over-Driving

### Supporting Evidence

- Entry speed is higher than the reference.
- Exit speed is lower.
- Throttle commitment is delayed.
- Average speed is lower through the segment.
- Recovery after minimum speed is weak.

### Conflicting Evidence

- Exit speed is equal or better.
- Recovery speed is equal or better.
- The segment is faster despite the higher entry speed.

### Coaching

Give up a small amount of entry speed so the car can rotate and accelerate cleanly.

### Mental Cue

> Slow hands, fast exit.

---

## Over-Slowing

### Supporting Evidence

- Minimum speed is lower than the reference.
- Average speed is lower.
- Braking begins earlier or is stronger.
- Lower minimum speed does not produce a meaningful exit-speed benefit.

### Conflicting Evidence

- Exit speed is substantially better.
- Earlier braking produces a faster segment.
- Lower minimum speed supports earlier throttle commitment.

### Coaching

Reduce unnecessary braking and preserve more speed through the element.

### Mental Cue

> Protect momentum.

---

## Momentum Loss

### Supporting Evidence

- Coast time is longer.
- Multiple throttle lifts occur.
- Average speed is lower.
- The loss develops gradually through the segment.
- No single braking or throttle event fully explains the loss.

### Conflicting Evidence

- Exit speed is strong.
- Coast time is brief and intentional.
- A clearer diagnosis better explains the segment.

### Coaching

Remain connected to either brake or throttle and reduce unnecessary neutral time.

### Mental Cue

> Stay connected.

---

## Weak Exit

### Supporting Evidence

- Exit speed is lower than the reference.
- Segment time is slower.
- Recovery speed remains lower after the minimum-speed point.

### Conflicting Evidence

- Exit speed is equal or better.
- The segment is faster despite a small exit-speed deficit.
- The exit boundary does not represent a meaningful acceleration point.

### Coaching

Prioritize rotation and acceleration before protecting entry speed.

### Mental Cue

> Build the exit.

---

## Execution Error

### Supporting Evidence

- Lift before the finish.
- Abrupt throttle reduction near the timing lights.
- Missed element or cone avoidance.
- Driver notes or video confirm a discrete mistake.

### Conflicting Evidence

- The behavior appears repeatedly across multiple runs.
- The loss reflects a broader technique problem.

### Coaching

Correct the isolated mistake without changing the overall driving approach.

### Mental Cue

> Finish the run.

---

## No Clear Diagnosis

### Supporting Evidence

- Segment time is slower but telemetry differences are small.
- No single metric adequately explains the loss.
- Several diagnoses have similar support.

### Coaching

Review the segment before making a significant technique change.

### Mental Cue

> Observe before changing.

---

# Confidence Model

Confidence reflects how strongly the available evidence supports a diagnosis.

## High Confidence

A diagnosis is high confidence when:

- Multiple telemetry indicators support the same explanation.
- Conflicting evidence is minimal.
- Metric differences exceed meaningful thresholds.
- The diagnosis clearly explains the segment time.

RaceCoach should provide direct coaching.

---

## Medium Confidence

A diagnosis is medium confidence when:

- The primary evidence is meaningful.
- Some conflicting evidence exists.
- More than one explanation remains plausible.

RaceCoach should coach cautiously.

---

## Low Confidence

A diagnosis is low confidence when:

- Metric differences are small.
- Telemetry signals conflict.
- GPS alignment or segment boundaries may affect the result.
- No diagnosis clearly explains the time difference.

Low-confidence observations may remain visible in detailed reports but should not drive the primary coaching recommendation.

When confidence is low, RaceCoach prefers no diagnosis over an incorrect diagnosis.

---

# Reinforcement Coaching

Not every report should identify a mistake.

When no significant losses exist, RaceCoach should reinforce successful driving behavior.

Example:

> Your gains came from executing the whole course cleanly.
>
> Repeat the same rhythm—don't search for extra speed.

Drivers improve by repeating successful habits as much as correcting mistakes.

---

# Coaching Output

## Grid Report

The Grid Report supports the driver between runs.

It should contain:

- One primary diagnosis.
- One supporting piece of evidence.
- One coaching recommendation.
- One mental cue.
- One successful technique to repeat.

It should **not** contain:

- Internal scores.
- Threshold calculations.
- Competing diagnoses.
- Confidence math.
- Long telemetry explanations.

The driver needs a clear coaching instruction—not an explanation of the algorithm.

---

## Full Report

The Full Report explains why the recommendation was made.

It may include:

- Diagnosis.
- Supporting evidence.
- Conflicting evidence.
- Confidence.
- Coaching recommendation.
- Additional opportunities.

---

## Developer Validation

A future developer-oriented report should expose the reasoning used to tune the diagnosis engine.

Possible contents include:

- Diagnosis scores.
- Winning and runner-up diagnoses.
- Score gaps.
- Evidence contributions.
- Conflicting evidence.
- Threshold behavior.
- Validation results.

This information is valuable for development but should remain separate from event-day coaching.

---

# Design Rules

- Diagnose driving behavior—not telemetry symptoms.
- Coach causes, not measurements.
- Prefer one strong diagnosis over several weak possibilities.
- Never coach from timing differences alone.
- Use conflicting evidence to reduce confidence.
- Reinforce successful driving.
- Keep coaching specific and executable.
- Keep mental cues short enough to remember on grid.
- Prefer silence over speculation.

---

# Future Diagnosis

## Inefficient Path

### Problem

A segment may be slower even when minimum speed and exit speed are equal or better than the reference.

The driver may have maintained speed while traveling a longer or less efficient path.

### Possible Evidence

- Segment time is slower.
- Minimum speed is equal or higher.
- Exit speed is equal or higher.
- Average speed is neutral or higher.
- Throttle commitment is not meaningfully delayed.
- No clear Over-Slowing, Weak Exit, or Late to Power signature exists.

### Likely Causes

- Extra distance.
- Wider line.
- Late apex.
- Excess steering.
- Floating beyond the efficient path.
- Poor setup from the previous element.

### Coaching

Review the GPS trace or video before changing braking or throttle technique.

### Mental Cue

> Shorter and cleaner.

### Validation Case

**GGLC 2026-06-20**

Run 4 compared with Run 5 — Finish section

- Time loss: +0.32 s
- Minimum speed: +2.5 mph
- Exit speed: +4.6 mph

This case should not be classified as Weak Exit, Late to Power, or Over-Slowing.

---

# Related Documentation

- `COACHING_PHILOSOPHY.md`
- `REPORT_INTERPRETATION.md`
- `METRICS.md`
- `USER_GUIDE.md`
- `ARCHITECTURE.md`