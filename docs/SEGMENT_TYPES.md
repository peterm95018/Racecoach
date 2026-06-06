# Segment Type Taxonomy

## Purpose

Define common autocross segment types so RaceCoach can apply different coaching logic depending on the feature being analyzed.

## Segment Types

| Type | Description | Most Important Metrics |
|---|---|---|
| Start | Launch and first acceleration zone | Reaction, throttle pickup, exit speed |
| Slalom | Repeated cone transitions | Average speed, path efficiency, speed decay |
| Sweeper | Sustained cornering section | Average speed, lateral load, exit speed |
| Hairpin | Tight low-speed corner | Minimum speed, rotation, throttle pickup, momentum recovery |
| Turnaround | 180-degree direction change | Entry control, rotation, exit speed, momentum recovery |
| Transition | Connector between major elements | Average speed, path length, setup speed |
| Finish | Final acceleration or final complex | Exit speed, average speed, commitment |

## Coaching Priority by Segment

### Start

Prioritize:

1. Clean launch
2. Early throttle
3. Speed at first feature

### Slalom

Prioritize:

1. Rhythm
2. Average speed
3. Path efficiency
4. Speed preservation

### Sweeper

Prioritize:

1. Average speed
2. Exit speed
3. Line discipline
4. Avoiding early throttle lift

### Hairpin / Turnaround

Prioritize:

1. Rotation
2. Momentum recovery
3. Throttle pickup
4. Exit speed
5. Minimum speed

### Transition

Prioritize:

1. Setup for next feature
2. Path efficiency
3. Average speed

### Finish

Prioritize:

1. Commitment
2. Exit speed
3. Average speed
4. Avoiding unnecessary lift

## Design Note

RaceCoach should avoid using one universal coaching rule for all segment types. A slalom loss and a turnaround loss may both show time loss, but they usually require different driving corrections.
