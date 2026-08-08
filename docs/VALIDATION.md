# RaceCoach Validation

## Purpose

RaceCoach validation ensures that telemetry processing, performance metrics, diagnosis, and coaching remain technically correct, behaviorally accurate, and useful to the driver.

Validation is intended to answer four questions:

1. Did RaceCoach correctly measure what happened?
2. Did it identify the most likely driving cause?
3. Did it communicate that cause with appropriate confidence?
4. Did it produce coaching that the driver can immediately apply?

A mathematically correct report is not necessarily a useful coaching report. Validation therefore extends beyond numerical correctness to the complete reasoning chain.

```text
Telemetry
    ↓
Preprocessing
    ↓
Segment Metrics
    ↓
Reference Comparison
    ↓
Diagnosis
    ↓
Confidence
    ↓
Coaching
    ↓
Driver Action
```

---

# Validation Philosophy

## Validate Behavior, Not Just Calculations

Metric calculations are necessary but not sufficient.

RaceCoach exists to improve driver performance. Validation therefore emphasizes whether the diagnosis reflects what actually occurred on course rather than whether a single metric appears reasonable.

A valid diagnosis should agree with multiple independent sources whenever available:

- Telemetry
- GPS trace
- Video
- Driver observations
- Course layout
- Event results
- Repeated behavior across multiple runs

The strongest diagnoses are supported by multiple independent observations rather than a single metric.

---

## Prefer No Diagnosis Over a False Diagnosis

RaceCoach intentionally allows uncertain conclusions.

Producing no diagnosis is preferable to producing an incorrect diagnosis with high confidence.

Low-confidence filtering is therefore considered a core safety feature of the coaching engine.

---

## Historical Consistency Matters

Every improvement should preserve previously validated behavior.

Whenever diagnosis logic, telemetry processing, or metric calculations change, RaceCoach should continue producing reasonable results for previously accepted historical cases.

Regression testing is intended to prevent improvements in one area from degrading another.

---

# Validation Levels

RaceCoach validation occurs at four progressively broader levels.

## Level 0 — Static Validation

Confirms that the codebase is internally consistent.

Typical checks include:

```bash
python3 -m py_compile racecoach/analyze_run.py

git diff --check
```

These checks detect syntax errors, merge artifacts, whitespace issues, and similar implementation problems before behavioral validation begins.

---

## Level 1 — Automated Regression Tests

Automated regression tests validate individual components independently of complete reports.

Current coverage includes:

### Diagnosis Engine

- Weak Exit
- Late to Power
- Over Slowing
- Momentum Loss
- Low Confidence
- No Clear Diagnosis
- Contradictory telemetry handling

### Telemetry Preprocessing

- Normal recordings remain unchanged
- Pre-start staging detection
- Time and distance re-zeroing
- Brake timing normalization

Run the complete suite with:

```bash
python3 -m unittest discover -s tests -v
```

Expected result:

```text
Ran 10 tests

OK
```

These tests should pass before any diagnosis, telemetry preprocessing, or metric changes are merged.

---

## Level 2 — Historical Regression

Automated tests verify algorithms.

Historical telemetry verifies behavior.

RaceCoach maintains representative historical comparisons that exercise the diagnosis engine using real RaceChrono recordings.

Historical regression should include:

- Weak Exit
- Late to Power
- Over Slowing
- Momentum Loss
- Low Confidence
- No Clear Diagnosis
- Reinforcement-only coaching
- Contradictory telemetry
- Successful faster runs
- Known telemetry edge cases

Historical regression confirms that diagnosis, confidence, evidence, and coaching remain stable across real driving situations.

---

## Level 3 — Driver Validation

The final validation level compares RaceCoach output with actual driving.

Useful evidence includes:

- Video review
- Driver observations
- GPS traces
- Course maps
- Event results
- Instructor feedback
- Repeatability across multiple runs

The objective is to determine whether the coaching would have helped the driver improve on the next run.

---

# Validation Workflow

## 1. Static Validation

Run:

```bash
python3 -m py_compile racecoach/analyze_run.py

git diff --check
```

Correct any implementation problems before continuing.

---

## 2. Automated Regression

Execute:

```bash
python3 -m unittest discover -s tests -v
```

All tests must pass.

---

## 3. Representative Event Validation

Select representative historical events that cover different course types and diagnoses.

Examples include:

- PCA events
- GGLC events
- Crows Landing
- Salinas
- Different segment layouts
- Different telemetry conditions

Regenerate reports using the current code.

---

## 4. Review Reports

Review both:

- Full Report
- Grid Report

Confirm that:

- primary diagnosis is reasonable
- confidence matches available evidence
- coaching is actionable
- low-confidence cases remain suppressed
- successful runs receive reinforcement rather than unnecessary criticism

---

## 5. Investigate Differences

A changed diagnosis is not automatically a regression.

For every changed result determine:

- Did telemetry preprocessing change?
- Did metric calculations change?
- Did diagnosis scoring change?
- Is the new result more accurate?
- Is confidence still appropriate?

Only accepted improvements should replace previous behavior.

---

# Regression Assets

RaceCoach currently maintains several forms of regression protection.

## Static Checks

```bash
python3 -m py_compile

git diff --check
```

---

## Automated Tests

```text
tests/
```

Current coverage:

- Diagnosis engine
- Telemetry preprocessing

These tests execute automatically and should remain deterministic.

---

## Historical Telemetry

Historical RaceChrono recordings serve as end-to-end behavioral validation.

Representative events should exercise:

- Launches
- Sweepers
- Hairpins
- Slaloms
- Finish sections
- Fast courses
- Tight courses
- Clean runs
- Edge cases

Historical telemetry provides confidence that real-world coaching remains consistent.

---

# Validation Criteria

Every diagnosis should satisfy four independent questions.

## Measurement

Were the telemetry metrics calculated correctly?

Examples include:

- segment duration
- entry speed
- minimum speed
- exit speed
- average speed
- braking
- throttle timing
- recovery metrics

---

## Diagnosis

Did the scoring engine select the best explanation?

Alternative diagnoses should lose for understandable reasons.

---

## Confidence

Does the reported confidence accurately reflect the available evidence?

High confidence requires multiple supporting metrics.

Conflicting telemetry should reduce confidence.

---

## Coaching

The coaching should be:

- technically correct
- concise
- immediately actionable
- consistent with the RaceCoach coaching philosophy

---

# Regression Requirements

Before merging significant changes to telemetry processing, metrics, diagnosis scoring, or coaching:

Complete:

```text
✓ py_compile

✓ git diff --check

✓ automated regression tests

✓ representative historical report generation

✓ review changed coaching

✓ investigate changed diagnoses

✓ confirm low-confidence behavior

✓ confirm reinforcement behavior
```

No diagnosis change should be accepted solely because it improves one historical case.

The entire regression suite should continue producing behavior that is at least as accurate as previous releases.

---

# Future Validation

The validation framework is expected to expand over time.

Planned improvements include:

- JSON/YAML regression fixtures
- Automated historical comparison tools
- Full event regression command
- Report snapshot comparison
- Confidence calibration testing
- Path-analysis validation
- Reference selection regression
- Session summary regression
- Publishing regression tests

These additions will allow RaceCoach to validate complete event processing automatically while preserving coaching quality across future development.

---

# Related Documentation

- ARCHITECTURE.md
- DIAGNOSIS_MODEL.md
- METRICS.md
- COACHING_PHILOSOPHY.md
- REPORT_INTERPRETATION.md
- OPERATIONS.md
- BACKLOG.md