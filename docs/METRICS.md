# RaceCoach Metrics

## Purpose

RaceCoach converts raw telemetry into performance metrics that support diagnosis and coaching.

Metrics describe **what happened** during a run.

They do **not** determine the coaching recommendation by themselves.

RaceCoach evaluates multiple metrics together before identifying the most likely driving behavior and producing a coaching recommendation.

---

# Metric Hierarchy

Not all metrics are equally important.

When evaluating a segment, RaceCoach generally prioritizes metrics in the following order:

1. Segment Time
2. Exit Speed
3. Throttle Commitment
4. Average Speed
5. Recovery Metrics
6. Brake Timing
7. Minimum Speed
8. Coast Time

The diagnosis engine may adjust this order depending on the driving situation.

---

# Primary Performance Metrics

## Segment Time

**Definition**

Elapsed time through the segment compared with the reference lap.

**Why it matters**

Segment time is the primary measure of performance.

Every other metric exists to help explain why the segment became faster or slower.

**Interpretation**

- Negative values indicate a faster segment.
- Positive values indicate a slower segment.

---

## Exit Speed

**Definition**

Vehicle speed at the end of the segment.

**Why it matters**

Exit speed is usually the strongest predictor of maintaining momentum into the following segment.

RaceCoach places significant weight on exit speed when diagnosing performance.

---

## Session Scorecard Metrics Updated

The Session Scorecard has been improved so that consistency metrics now reflect **only clean runs** when run classifications are available.

### Previous Behavior

All analyzed runs were included in consistency calculations, including:

- DNF runs
- Cone runs
- Off-course runs

This could distort:

- Best Repeat
- Top-3 Spread
- Run Standard Deviation

For example, a DNF run would artificially inflate the standard deviation and make repeatability appear worse than the driver's actual clean performance.

---

### New Behavior

Each run now carries metadata:

```json
"run": {
  "status": "clean",
  "is_clean": true
}
```

When at least one clean run exists:

- Fastest analyzed run is selected from clean runs.
- Best repeat is selected from clean runs.
- Top-3 spread is calculated from clean runs.
- Run standard deviation is calculated from clean runs.

If no clean classifications are available, RaceCoach automatically falls back to using all analyzed runs.

---

### New Session Metric

The Session Scorecard now reports:

- Clean-run percentage

Example:

```
Clean-run percentage: 75.0% (3 of 4 classified runs)
```

This measures execution quality across the session and separates driving consistency from outright pace.

---

### Example

Before:

```
Fastest analyzed run: lap4 (27.488s)
Best repeat: lap2 (+1.906s)
Standard deviation: 1.005s
```

With run classifications:

- lap1 = DNF
- lap2 = Clean
- lap3 = Clean
- lap4 = Clean

Now:

```
Fastest analyzed run: lap4 (27.488s)
Best repeat: lap3 (+0.508s)
Top-3 spread: 1.906s
Analyzed-run standard deviation: 0.806s
Clean-run percentage: 75.0% (3 of 4 classified runs)
```

The revised metrics better represent repeatable driving performance by excluding non-representative runs while still reporting the driver's overall execution rate.



---

# Supporting Speed Metrics

## Entry Speed

**Definition**

Vehicle speed at the beginning of the segment.

**Why it matters**

Provides context for how the segment was approached and helps explain setup into complex elements.

---

## Average Speed

**Definition**

Average vehicle speed throughout the segment.

**Why it matters**

Helps identify gradual momentum losses that occur across an entire segment rather than at a single point.

---

## Minimum Speed

**Definition**

Lowest speed reached within the segment.

**Why it matters**

Useful for understanding braking and rotation.

Higher minimum speed is **not** always faster.

RaceCoach interprets minimum speed together with exit speed and throttle commitment.

---

# Driver Input Metrics

## Throttle Commitment

**Definition**

Time between minimum speed and meaningful throttle application.

**Why it matters**

Represents how quickly the driver commits to acceleration after completing rotation.

Earlier throttle commitment generally produces stronger exits and lower segment times.

---

## Brake Start Distance

**Definition**

Distance from the beginning of the segment where braking begins.

**Why it matters**

Allows braking points to be compared between runs.

---

## Brake Timing

**Definition**

Time at which braking begins relative to the reference lap.

**Why it matters**

Helps identify unnecessary early braking or delayed braking.

---

## Peak Deceleration

**Definition**

Maximum braking force recorded during the segment.

**Why it matters**

Helps distinguish aggressive braking from gradual speed reduction.

---

# Momentum Metrics

## Coast Time

**Definition**

Time spent with neither brake nor throttle applied.

**Why it matters**

Long coast times often indicate hesitation or unnecessary loss of momentum.

---

## Recovery Gain (+1 s)

**Definition**

Difference in vehicle speed one second after the minimum-speed point.

**Why it matters**

Measures how quickly momentum is rebuilt after rotation.

---

## Recovery Gain (+2 s)

**Definition**

Difference in vehicle speed two seconds after the minimum-speed point.

**Why it matters**

Provides a longer view of acceleration and recovery.

Recovery metrics continue to evolve and currently play a supporting role in diagnosis.

---

# Interpreting Metrics Together

Individual metrics rarely tell the complete story.

RaceCoach evaluates combinations of metrics before forming a diagnosis.

Common combinations include:

| Metric Combination | Typical Interpretation |
|-------------------|------------------------|
| Segment Time + Exit Speed | Primary performance assessment |
| Minimum Speed + Exit Speed | Over-driving vs. over-slowing |
| Exit Speed + Recovery | Quality of acceleration after rotation |
| Brake Timing + Exit Speed | Effectiveness of corner setup |
| Coast Time + Throttle Commitment | Hesitation or delayed commitment |

---

# Design Principles

Metrics are evidence.

They are not coaching.

A metric should never be interpreted in isolation.

RaceCoach combines multiple measurements before identifying the most likely driving behavior.

---

# Related Documentation

- `COACHING_PHILOSOPHY.md`
- `DIAGNOSIS_MODEL.md`
- `REPORT_INTERPRETATION.md`
- `USER_GUIDE.md`
- `ARCHITECTURE.md`