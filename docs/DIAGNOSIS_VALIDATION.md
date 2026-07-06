# RaceCoach Diagnosis Validation

## Purpose

Track known run comparisons and expected diagnoses so coaching logic can be tested against real data.

---

## Validation Cases

| Event | Reference | Analysis | Segment | Expected Diagnosis | Notes |
|---|---|---|---|---|---|
| GGLC 2025-11-01 | Lap 3 | Lap 5 | Middle course | Weak Exit | Exit speed -10.4 mph |
| GGLC 2025-11-01 | Lap 6 | Lap 8 | Finish section | No Clear Diagnosis | Time loss but speed metrics better/neutral |
| GGLC 2025-11-01 | Lap 3 | Lap 5 | Finish section | Momentum Loss | Average speed -5.2 mph |

---

## Rule

When diagnosis logic changes, rerun these cases before committing.
