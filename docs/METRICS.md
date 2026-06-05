# RaceCoach Metrics Roadmap

## Current Metrics

- Segment time delta
- Entry speed
- Average speed
- Minimum speed
- Exit speed
- Coast time
- Brake timing
- Throttle pickup timing

---

### Coaching Priority

RaceCoach currently prioritizes telemetry indicators in approximately this order:

1. Segment time delta
2. Exit speed
3. Average speed
4. Throttle pickup timing
5. Brake timing
6. Minimum speed
7. Coast time

Average speed was added after analysis of GGLC 2025-11-01 data revealed several cases where significant time loss could not be explained by minimum speed, exit speed, or coast time alone. Average speed provided a better explanation of speed deficits that developed across an entire segment.

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

- Average speed