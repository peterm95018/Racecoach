# RaceCoach Metrics Roadmap

## Current Metrics

- Segment time delta
- Entry speed
- Minimum speed
- Exit speed
- Coast time
- Brake timing
- Throttle pickup timing

---

## Planned Metrics

### Momentum Recovery

Definition:
Time and distance required to recover speed after a minimum-speed point.

Outputs:
- Time to +10 mph
- Time to +20 mph
- Distance to +10 mph
- Distance to +20 mph

Why:
Fast autocross laps are often won by accelerating sooner after rotation.

---

### Path Length

Definition:
Actual driven distance through a segment.

Outputs:
- Segment path length
- Delta vs reference

Why:
Detect inefficient lines and overdriving.

---

### Path Efficiency

Definition:
Time lost per extra foot traveled.

Outputs:
- Extra distance
- Estimated time impact

---

### Overdriving Detection

Indicators:
- Similar min speed
- Lower exit speed
- Later throttle
- Longer path

Outputs:
Low / Medium / High confidence overdriving flag.

## Known Findings

### GGLC 2025-11-01

An early version of the segment definitions ended at distance 600 while laps extended beyond 609-613.

This caused segment deltas to overstate losses because the final portion of the course was not included in analysis.

Lesson:
Segment definitions must extend through the entire timed course.