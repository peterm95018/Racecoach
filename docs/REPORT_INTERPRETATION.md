# RaceCoach Report Interpretation Guide

RaceCoach produces several reports throughout an autocross event. Each report serves a different purpose and is intended to answer a different coaching question.

This guide explains when to use each report, how to interpret the information it contains, and which sections deserve the most attention.

Detailed descriptions of individual telemetry metrics are provided in `METRICS.md`.

---

## Report Types

### Grid Report

**Purpose**

Provide immediate coaching for the next run.

**When to read**

During the short break between runs.

**Typical reading time**

Less than 30 seconds.

**Focus on**

- Next Run
- Keep
- Quick Segment Check

Ignore the remaining details unless you have additional time.

The objective is to leave the grid with **one clear improvement** to execute on the next run.

---

### Full Report

**Purpose**

Explain why a run was faster or slower than the selected reference lap.

**When to read**

After returning to paddock or after the event.

Use the report to understand:

- Where time was gained.
- Where time was lost.
- Why those differences occurred.
- Which techniques should be repeated.

---

### Session Summary

**Purpose**

Summarize an entire event rather than a single run.

The Session Summary identifies:

- Recurring strengths.
- Recurring weaknesses.
- Improvement across multiple runs.
- Coaching priorities before the next event.

Unlike the Grid Report, which focuses on the next run, the Session Summary focuses on long-term improvement throughout the event.

---

## Reading the Full Report

### Run Summary

Read this section first.

It provides a high-level overview of the run, including:

- Biggest gain
- Biggest loss
- Overall performance differences

---

### Next Run Focus

This is the most important coaching section.

Recommendations are ordered by expected impact.

Choose **one improvement** and commit to it during the next run.

Trying to fix multiple problems simultaneously usually produces inconsistent driving.

---

### Segment Time vs Reference

This is the primary performance comparison.

Everything else in the report attempts to explain why each segment became faster or slower.

- Negative values indicate a faster segment.
- Positive values indicate a slower segment.

---

### Top Opportunities

These sections explain why RaceCoach believes time was lost.

Common diagnoses include:

- Late throttle commitment
- Weak exit speed
- Excess coasting
- Over-driving
- Over-slowing
- Early braking

Only opportunities supported by sufficient confidence are presented.

---

### Segment Table

The segment table provides a concise comparison of every analyzed segment.

Look for recurring patterns rather than isolated values.

Repeated losses usually deserve more attention than a single slow segment.

---

## Interpreting the Metrics

Telemetry metrics should never be interpreted in isolation.

RaceCoach combines multiple measurements before reaching a coaching recommendation.

Common combinations include:

- Exit Speed + Coast Time
- Minimum Speed + Exit Speed
- Brake Timing + Exit Speed
- Throttle Commitment + Segment Time

Detailed definitions are available in `METRICS.md`.

---

## Common Interpretation Patterns

### Higher Minimum Speed + Lower Exit Speed

Often indicates over-driving the corner entry.

---

### Lower Minimum Speed + Higher Exit Speed

Often indicates sacrificing entry speed to produce a stronger exit.

---

### Longer Coast Time

Usually indicates hesitation or delayed throttle commitment.

---

### Earlier Brake Point + Better Exit

May indicate a more effective corner setup.

---

### Faster Segment + Similar Metrics

Occasionally RaceCoach cannot confidently explain a time difference.

Small gains and losses are not always accompanied by measurable telemetry changes.

Low-confidence conclusions are intentionally filtered to avoid speculative coaching.

---

## Coaching Philosophy

RaceCoach is designed to improve the driver's next run—not simply explain the previous one.

When reviewing a report:

- Focus on one improvement at a time.
- Reinforce successful techniques.
- Repeat what worked.
- Trust consistent trends over isolated laps.
- Favor high-confidence coaching over speculative analysis.

Telemetry is evidence.

Coaching is the product.

---

## Related Documentation

- `USER_GUIDE.md`
- `COACHING_PHILOSOPHY.md`
- `DIAGNOSIS_MODEL.md`
- `METRICS.md`