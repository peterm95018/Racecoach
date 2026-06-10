## Momentum Recovery Summary

Purpose:
Measure how quickly speed is rebuilt after minimum speed.

Inputs:
- Minimum speed point
- Throttle pickup time
- Speed at +1 second
- Speed at +2 seconds

Reference comparison:
- Recovery delay
- Recovery rate
- Speed gained after apex

Coaching examples:
- Recovered speed 0.4s later than reference.
- Carried speed into the corner but rebuilt speed more slowly.
- Early throttle but weak acceleration recovery.

Coaching Rule Catalog

Purpose

Define telemetry patterns that RaceCoach should translate into driving advice.

Rules

Pattern	Interpretation	Coaching
Higher minimum speed + lower exit speed + time loss	Over-driving entry	Give up a little entry speed, rotate once, protect the exit
Lower average speed + similar or better exit speed + time loss	Segment compromised before apex	Look earlier in the course; the loss developed through the whole segment
Lower exit speed + similar minimum speed	Poor exit commitment	Prioritize exit line and earlier throttle
Later throttle pickup + time loss	Delayed commitment	Pick up throttle earlier after rotation
More coast time + time loss	Waiting between brake and throttle	Make a decision: brake, rotate, or accelerate
Lower entry speed + lower average speed	Upstream setup loss	Focus on the previous segment or transition
Higher entry speed + lower exit speed	Entry over-attack	Slow hands, finish rotation, protect exit
Similar speed metrics + time loss	Possible path inefficiency	Review GPS trace or path length
Large time loss with contradictory speed metrics	Segment or timing anomaly	Validate segment boundaries and course position

Priority Order

RaceCoach should generally prioritize explanations in this order:

1. Time loss
2. Exit speed deficit
3. Average speed deficit
4. Over-driving pattern
5. Throttle pickup delay
6. Coast time
7. Brake timing
8. Minimum speed alone

Notes

Minimum speed should rarely be used as the primary coaching conclusion by itself. It is most useful when combined with exit speed, average speed, and time delta.

# Momentum Recovery Metric

## Purpose

Measure how quickly the car rebuilds speed after the slowest point in a segment.

## Problem It Solves

RaceCoach has found repeated cases where:

- Minimum speed is higher than reference
- Exit speed is lower than reference
- Segment time is slower

This usually means the driver carried speed into the corner but failed to convert it into exit speed.

## Measurements

For each segment:

- Minimum speed
- Time of minimum speed
- Speed 1.0 second after minimum speed
- Speed 2.0 seconds after minimum speed
- Speed gained after minimum speed
- Distance traveled before speed recovery
- Throttle pickup time after minimum speed, when available

## Reference Comparison

Compare analysis lap against reference lap:

- Recovery time delta
- Recovery speed delta
- Recovery distance delta
- Throttle-after-minimum-speed delta

## Coaching Examples

- Recovered speed later than reference.
- Carried speed into the corner but rebuilt speed more slowly.
- Higher minimum speed did not produce better exit speed.
- Earlier rotation needed before throttle commitment.
- Protect the exit instead of carrying more entry speed.

## Report Use

Momentum Recovery should help explain patterns like:

Minimum speed: +1.1 mph
Exit speed: -10.4 mph
Segment time: +0.36s

Interpretation:

The driver carried speed into the corner but did not rebuild speed after the apex as effectively as the reference lap. Focus on earlier rotation and earlier throttle commitment rather than carrying additional entry speed.
