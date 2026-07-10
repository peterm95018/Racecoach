RaceCoach Diagnosis Model

Purpose

RaceCoach should diagnose driving behavior, not merely report telemetry differences.

Telemetry describes what happened. The diagnosis model determines the most likely driving cause and converts it into one actionable change for the next run.

⸻

Diagnosis Structure

Each diagnosis contains five components:

1. Diagnosis — Classification of the primary driving issue.
2. Evidence — Telemetry supporting the diagnosis.
3. Conflicting Evidence — Telemetry that weakens or contradicts the diagnosis.
4. Confidence — Strength of the conclusion.
5. Action and Cue — The recommended adjustment and a short mental reminder.

The coaching engine should reason in this order:

Segment time difference
        ↓
Telemetry evidence
        ↓
Conflicting evidence
        ↓
Diagnosis
        ↓
Confidence
        ↓
Action
        ↓
Mental cue

Telemetry supports the diagnosis. It is not the diagnosis.

⸻

Current Diagnoses

Late to Power

Evidence

* Throttle commitment is later than the reference.
* Exit speed is lower.
* Recovery speed is lower after minimum speed.
* Segment time loss develops after the rotation point.

Conflicting Evidence

* Throttle commitment is earlier.
* Exit speed is equal or better.
* Recovery speed is equal or better.

Prescription

Complete rotation sooner and commit to throttle as soon as the car is pointed.

Mental Cue

Point, then power.

⸻

Over-Driving

Evidence

* Entry speed is higher than the reference.
* Exit speed is lower.
* Throttle commitment is delayed.
* Average speed is lower through the segment.
* Recovery after minimum speed is weak.

Conflicting Evidence

* Exit speed is equal or better.
* Recovery speed is equal or better.
* The segment is faster despite the higher entry speed.

Prescription

Give up a small amount of entry speed so the car can rotate and accelerate cleanly.

Mental Cue

Slow hands, fast exit.

⸻

Over-Slowing

Evidence

* Minimum speed is lower than the reference.
* Average speed is lower.
* Braking begins earlier or is stronger.
* Lower minimum speed does not produce a meaningful exit-speed benefit.

Conflicting Evidence

* Exit speed is substantially better.
* Earlier braking produces a faster segment.
* Lower minimum speed supports a cleaner and earlier throttle application.

Prescription

Reduce unnecessary braking and preserve more speed through the element.

Mental Cue

Protect momentum.

⸻

Momentum Loss

Evidence

* Coast time is longer.
* Multiple throttle lifts occur.
* Average speed is lower.
* The loss develops gradually through the segment.
* No single braking or throttle event fully explains the loss.

Conflicting Evidence

* Exit speed is strong.
* Coast time is brief and intentional.
* A clearer braking, throttle, or line-related diagnosis explains the loss.

Prescription

Remain connected to either brake or throttle and reduce unnecessary neutral time.

Mental Cue

Stay connected.

⸻

Weak Exit

Evidence

* Exit speed is lower than the reference.
* Segment time is slower.
* Recovery speed remains lower after the minimum-speed point.

Conflicting Evidence

* Exit speed is equal or better.
* The segment is faster despite a small exit-speed deficit.
* The exit boundary does not represent a meaningful acceleration point.

Prescription

Prioritize rotation and acceleration before protecting entry speed.

Mental Cue

Build the exit.

⸻

Execution Error

Evidence

* Lift before the finish.
* Abrupt throttle reduction near the timing lights.
* Missed element, cone avoidance, or one-time correction.
* Driver notes or video confirm a discrete mistake.

Conflicting Evidence

* The behavior appears repeatedly across multiple runs.
* The loss reflects a broader technique problem rather than a single mistake.

Prescription

Correct the isolated mistake without changing the broader driving approach.

Mental Cue

Finish the run.

⸻

No Clear Diagnosis

Evidence

* Segment time is slower, but telemetry differences are small.
* No single metric adequately explains the loss.
* Several possible causes have similar support.

Prescription

Review the segment without making a major technique change.

Mental Cue

Observe before changing.

⸻

Low Confidence

Low confidence is not a driving diagnosis. It is a qualification applied when the evidence is insufficient or contradictory.

Indicators

* Segment time is slower while speed metrics are equal or better.
* Telemetry signals conflict.
* Differences are below meaningful thresholds.
* Segment boundaries or GPS projection may explain the result.
* The diagnosis score is only marginally stronger than alternatives.

Prescription

Do not change technique based on this result alone. Seek confirmation from another run, video, GPS trace, or driver notes.

Mental Cue

Verify before changing.

⸻

Confidence Model

High Confidence

A diagnosis is high confidence when:

* Multiple telemetry indicators support the same explanation.
* Conflicting evidence is minimal.
* The metric differences exceed established thresholds.
* The diagnosis clearly explains the segment time loss.

Medium Confidence

A diagnosis is medium confidence when:

* The primary evidence is meaningful.
* Some conflicting evidence exists.
* More than one explanation remains plausible.

Low Confidence

A diagnosis is low confidence when:

* Differences are small.
* Telemetry is contradictory.
* GPS or segment alignment may affect the result.
* No diagnosis clearly explains the time difference.

Low-confidence segments may remain visible in detailed tables but should not drive the primary coaching recommendation.

⸻

Coaching Output

Grid Report

The Grid Report is designed for the driver between runs.

It should include:

* One primary diagnosis.
* One supporting piece of evidence.
* One action.
* One mental cue.
* One successful technique to repeat.

It should not include:

* Internal scores.
* Threshold calculations.
* Competing diagnoses.
* Detailed confidence math.
* Long telemetry explanations.

The driver needs a clear coaching instruction, not an explanation of the algorithm.

⸻

Full Report

The Full Report may include:

* Diagnosis.
* Supporting telemetry.
* Conflicting evidence.
* Confidence.
* Detailed action.
* Additional opportunities.

Its purpose is to explain why the coaching recommendation was made.

⸻

Developer Validation Report

A future developer-focused report should expose the internal reasoning used to tune the diagnosis engine.

It should include:

* All diagnosis scores.
* Winning and runner-up diagnoses.
* Score gap.
* Evidence contributions.
* Conflicting evidence.
* Threshold behavior.
* Expected and actual validation result.

This information is useful for development but should remain separate from event-day coaching.

⸻

Design Rules

* Diagnose the driving behavior, not just the telemetry symptom.
* Prefer one strong diagnosis over several weak possibilities.
* Do not coach from timing differences alone.
* Use conflicting evidence to reduce confidence.
* Reinforce gains as well as correcting losses.
* Keep the recommended action specific and executable.
* Keep the mental cue short enough to remember on grid.

⸻

Future Diagnosis: Inefficient Path

Problem

A segment may be slower even when minimum speed and exit speed are equal or better than the reference.

In these cases, the car may have been fast but traveled a longer or less efficient path.

Possible Telemetry Signature

* Segment time is slower.
* Minimum speed is equal or higher.
* Exit speed is equal or higher.
* Average speed is neutral or higher.
* Throttle commitment is not meaningfully delayed.
* No clear over-slowing or weak-exit signature exists.

Likely Causes

* Extra distance.
* Wider line.
* Late apex.
* Excess steering.
* Floating beyond the efficient path.
* Poor setup from the preceding element.

Prescription

Review GPS trace or video before changing braking or throttle technique.

Mental Cue

Shorter and cleaner.

Validation Case

GGLC 2026-06-20, Run 4 compared with Run 5, Finish section:

* Time loss: +0.32 s
* Minimum speed: +2.5 mph
* Exit speed: +4.6 mph

This case should not be classified as Weak Exit, Late to Power, or Over-Slowing.

⸻

Related Documentation

* METRICS.md
* COACHING_PHILOSOPHY.md
* REPORT_INTERPRETATION.md
* ARCHITECTURE.md