# RaceCoach Test Suite

## Purpose

The `tests/` directory contains fast regression tests that verify RaceCoach behavior without requiring full event processing.

These tests are intended to detect unintended changes to telemetry preprocessing, diagnosis logic, and coaching behavior during development.

## Test Organization

```
tests/
├── fixtures/
│   └── diagnosis/
├── test_diagnosis_regression.py
└── test_preprocessing_regression.py
```

### Diagnosis Regression

Diagnosis regression tests use JSON fixtures.

Each fixture represents a known telemetry pattern and the expected diagnosis produced by the scoring engine.

These tests verify:

- diagnosis
- confidence
- evidence
- coaching cue

To add a diagnosis regression:

1. Create a new JSON fixture in `fixtures/diagnosis/`.
2. Run the test suite.
3. Confirm the fixture passes.

### Telemetry Preprocessing

Preprocessing tests validate telemetry normalization before segment analysis.

Current coverage includes:

- normal recordings remain unchanged
- pre-start staging removal
- brake timing normalization

## Running Tests

Run the complete suite:

```bash
python3 -m unittest discover -s tests -v
```

## Philosophy

Tests should verify behavior rather than implementation.

Diagnosis fixtures represent stable coaching expectations.

Preprocessing tests verify telemetry correctness.

Historical event validation is documented separately in `docs/VALIDATION.md`.
