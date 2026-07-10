RaceCoach Metrics

Purpose

RaceCoach converts raw telemetry into a set of performance metrics used by the diagnosis and coaching engines.

These metrics describe what happened during a run. They do not, by themselves, determine the coaching recommendation. Interpretation is handled by the Diagnosis Engine.

⸻

Speed Metrics

Segment Time

Definition

Elapsed time for a segment compared to the reference lap.

Why it matters

This is the primary measure of performance.

Interpretation

* Negative values indicate a faster segment.
* Positive values indicate a slower segment.

⸻

Entry Speed

Definition

Vehicle speed at the beginning of the segment.

Why it matters

Provides context for the remainder of the segment and helps explain setup into complex course elements.

⸻

Average Speed

Definition

Average vehicle speed throughout the segment.

Why it matters

Helps identify speed losses that occur across an entire segment rather than at a single point.

⸻

Minimum Speed

Definition

Lowest speed reached within the segment.

Why it matters

Useful for understanding braking and rotation.

Higher minimum speed is not always faster.

⸻

Exit Speed

Definition

Vehicle speed at the end of the segment.

Why it matters

The strongest predictor of maintaining momentum into the next segment.

⸻

Braking Metrics

Brake Start Distance

Definition

Distance from the segment start where braking begins.

Why it matters

Allows comparison of braking points between runs.

⸻

Brake Timing

Definition

Time at which braking begins relative to the reference lap.

Why it matters

Identifies early or late braking tendencies.

⸻

Peak Deceleration

Definition

Maximum braking force recorded during the segment.

Why it matters

Helps distinguish aggressive braking from gradual speed reduction.

⸻

Throttle Metrics

Throttle Commitment

Definition

Time between minimum speed and meaningful throttle application.

Why it matters

Represents how quickly the driver commits to acceleration after rotation.

⸻

Momentum Metrics

Coast Time

Definition

Time spent with neither brake nor throttle applied.

Why it matters

Long coast times frequently indicate lost momentum.

⸻

Experimental Metrics

Recovery Gain (+1 s)

Difference in vehicle speed one second after minimum speed.

⸻

Recovery Gain (+2 s)

Difference in vehicle speed two seconds after minimum speed.

These metrics are currently experimental and are displayed for evaluation but are not heavily weighted in coaching recommendations.

⸻

Coaching Priority

When multiple indicators disagree, RaceCoach generally prioritizes metrics in this order:

1. Segment Time
2. Exit Speed
3. Average Speed
4. Throttle Commitment
5. Brake Timing
6. Minimum Speed
7. Coast Time

The diagnosis engine may adjust this priority based on the driving situation.

⸻

Related Documentation

* DIAGNOSIS_MODEL.md
* REPORT_INTERPRETATION.md
* ARCHITECTURE.md