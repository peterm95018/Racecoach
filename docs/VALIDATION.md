RaceCoach Validation

Purpose

RaceCoach validation determines whether the diagnosis and coaching engines produce conclusions that are consistent with telemetry, driver experience, video, course context, and known performance outcomes.

Validation answers four questions:

1. Did RaceCoach identify the correct performance difference?
2. Did it explain the most likely driving cause?
3. Did it avoid diagnoses contradicted by the telemetry?
4. Did it produce coaching that the driver could apply on the next run?

Validation is not limited to confirming that calculations execute correctly.

A report can be mathematically correct while still producing poor coaching.

The objective is to validate the complete reasoning chain:

Telemetry
    ↓
Metrics
    ↓
Supporting and Conflicting Evidence
    ↓
Diagnosis
    ↓
Confidence
    ↓
Coaching

⸻

Validation Principles

Validate Behavior, Not Just Numbers

Metric calculations should be tested independently, but RaceCoach must ultimately be validated against observed driving behavior.

A diagnosis is stronger when it agrees with multiple sources, including:

* Telemetry
* GPS trace
* Video
* Driver notes
* Course layout
* Run results
* Repeated behavior across multiple runs

⸻

Use Real Runs

Synthetic data is useful for unit testing thresholds and scoring rules.

Real event data is required to validate whether those rules reflect actual driving.

Historical runs provide the primary behavioral regression suite for RaceCoach.

⸻

Include Conflicting Cases

Validation should include more than obvious examples.

The test set should contain:

* Clear gains
* Clear losses
* Mixed telemetry
* Small timing differences
* Execution mistakes
* Strong speed with slower segment time
* Faster segments with apparently weaker individual metrics
* Cases where RaceCoach should produce no diagnosis

These cases are necessary to prevent the engine from overfitting to simple telemetry patterns.

⸻

Prefer No Diagnosis Over a False Diagnosis

A low-confidence or unexplained result is acceptable.

A confident but incorrect diagnosis is not.

Validation should reward the system for suppressing recommendations when evidence is insufficient or contradictory.

⸻

Preserve Historical Cases

Once a case has been reviewed and accepted, it should remain in the regression suite.

Changes to thresholds, metrics, segment logic, or diagnosis scoring should be tested against all accepted cases before being treated as production-ready.

⸻

Validation Levels

RaceCoach validation occurs at four levels.

Level 1 — Metric Validation

Confirms that individual metrics are calculated correctly.

Examples include:

* Segment time
* Entry speed
* Average speed
* Minimum speed
* Exit speed
* Brake start
* Peak deceleration
* Coast time
* Throttle commitment
* Recovery speed

Metric validation should compare calculated values against manually inspected telemetry or a trusted external source.

⸻

Level 2 — Diagnosis Validation

Confirms that the diagnosis engine selects the most appropriate explanation.

A diagnosis validation case should record:

* Analysis run
* Reference run
* Segment
* Metric differences
* Expected diagnosis
* Diagnoses that must not be selected
* Expected confidence
* Reasoning

⸻

Level 3 — Coaching Validation

Confirms that the selected diagnosis produces useful coaching.

The coaching should be:

* Specific
* Executable
* Appropriate to the diagnosed behavior
* Short enough to use between runs
* Consistent with the RaceCoach coaching philosophy

A technically accurate diagnosis can still fail validation if its coaching recommendation is vague or impractical.

⸻

Level 4 — Report Validation

Confirms that the correct information appears in the appropriate report.

The Grid Report should emphasize:

* One primary coaching priority
* One supporting observation
* One action
* One mental cue
* One successful behavior to repeat

The Full Report may expose more detail, including conflicting evidence and confidence.

Developer-only diagnostic details should not appear in event-day reports.

⸻

Validation Case Format

Each accepted case should use the following format.

## Case: Descriptive Name
**Status:** Proposed | Accepted | Needs Review | Rejected
**Event:** Event identifier  
**Analysis Run:** Run being evaluated  
**Reference Run:** Comparison run  
**Segment:** Segment name
### Context
Course, driver, weather, run order, or other information needed to interpret the result.
### Observed Differences
- Segment time:
- Entry speed:
- Average speed:
- Minimum speed:
- Exit speed:
- Brake timing:
- Coast time:
- Throttle commitment:
- Recovery:
### Expected Diagnosis
Diagnosis name.
### Expected Confidence
High, Medium, or Low.
### Diagnoses That Must Not Win
- Diagnosis
- Diagnosis
### Expected Coaching
Recommended driver action.
### Mental Cue
> Short cue.
### Validation Basis
Explanation of why this result is expected, including telemetry, video, driver notes, or repeat behavior.
### Regression Requirement
What must remain true after future changes.

Not every metric must be populated. Only include measurements relevant to the case.

⸻

Accepted and Candidate Validation Cases

Case: Faster Finish Through Stronger Recovery

Status: Accepted

Event: GGLC 2025-11-01
Analysis Run: Lap 9
Reference Run: Lap 8
Segment: Finish section

Context

The compared run produced a substantial gain in the finish section. The improved run carried more speed through the segment and accelerated much more effectively toward the finish.

Observed Differences

* Segment time: approximately -1.36 s to -1.96 s, depending on the report version and segment definition
* Minimum speed: higher
* Exit speed: substantially higher
* Recovery: stronger
* Throttle application: consistent with an earlier or more effective commitment to acceleration

Expected Diagnosis

Successful execution or strong exit.

This case should normally appear as reinforcement coaching rather than as a correction.

Expected Confidence

High.

Diagnoses That Must Not Win

* Weak Exit
* Over-Slowing
* Late to Power

Expected Coaching

Repeat the earlier commitment to acceleration and carry the same rhythm through the finish.

Mental Cue

Commit and finish.

Validation Basis

The improved run was faster while producing materially stronger exit speed. The gain is consistent with successful rotation, throttle commitment, and acceleration rather than a timing artifact.

Regression Requirement

Future diagnosis changes must continue to recognize this segment as a gain and must not produce corrective coaching based solely on any isolated weaker metric.

⸻

Case: Clear Finish-Section Loss

Status: Accepted

Event: GGLC 2026-06-20
Analysis Run: Historical slower run
Reference Run: Faster comparison run
Segment: Finish section

Context

The slower run lost substantial time in the final portion of the course. Earlier RaceCoach reports identified the finish as the largest loss and reported materially lower exit speed.

Observed Differences

* Segment time: approximately +0.61 s to +0.88 s in reviewed comparisons
* Exit speed: materially lower in the slower run
* Recovery: weaker
* Minimum speed: may not fully explain the loss

Expected Diagnosis

Weak Exit or Late to Power, depending on throttle and recovery evidence.

Expected Confidence

Medium to High.

Diagnoses That Must Not Win

* Over-Slowing based only on minimum speed
* Inefficient Path without supporting path evidence
* No Clear Diagnosis when throttle and exit evidence are strong

Expected Coaching

Complete rotation sooner and accelerate through the finish rather than waiting for the car to become perfectly straight.

Mental Cue

Point, then power.

Validation Basis

The time loss and lower exit speed support a failure to rebuild speed after the minimum-speed point. Throttle timing and recovery metrics should determine whether Late to Power or Weak Exit is the stronger diagnosis.

Regression Requirement

The diagnosis engine must use throttle and recovery evidence to choose between Late to Power and Weak Exit rather than selecting both or relying only on exit speed.

⸻

Case: Faster Speeds but Slower Segment

Status: Accepted

Event: GGLC 2026-06-20
Analysis Run: Run 4
Reference Run: Run 5
Segment: Finish section

Context

The analysis run was slower through the segment despite carrying more speed at key measured points.

Observed Differences

* Segment time: +0.32 s
* Minimum speed: +2.5 mph
* Exit speed: +4.6 mph
* Throttle commitment: not known to be materially worse
* Speed metrics: generally equal or stronger

Expected Diagnosis

No Clear Diagnosis until path analysis is available.

Inefficient Path is the leading future diagnosis.

Expected Confidence

Low.

Diagnoses That Must Not Win

* Weak Exit
* Late to Power
* Over-Slowing

Expected Coaching

Do not change braking or throttle technique based on this comparison alone. Review the GPS trace, driven distance, and video.

Mental Cue

Verify the path.

Validation Basis

The slower segment cannot be explained by minimum speed or exit speed because both are better than the reference. A longer path, wider line, segment projection issue, or other spatial factor is more plausible.

Regression Requirement

The engine must not generate a confident speed- or throttle-based diagnosis when the principal speed metrics contradict that conclusion.

When path-efficiency analysis is implemented, this case should be reevaluated as an Inefficient Path candidate.

⸻

Case: Late Return to Power

Status: Candidate

Event: GGLC 2025-11-01
Analysis Run: Lap 9 or another reviewed run with delayed commitment
Reference Run: Faster comparison lap
Segment: Middle course or finish section

Context

Historical RaceCoach output described the driver as being late getting the car pointed and late getting back to power.

Observed Differences

Expected evidence includes:

* Slower segment time
* Later throttle commitment
* Lower recovery speed
* Lower exit speed
* Loss developing after the minimum-speed point

Expected Diagnosis

Late to Power.

Expected Confidence

High when throttle commitment, recovery, and exit speed all agree.

Diagnoses That Must Not Win

* Over-Slowing when minimum speed is not the primary issue
* Momentum Loss when a discrete delayed throttle event explains the loss
* Weak Exit when throttle timing provides the more specific cause

Expected Coaching

Finish rotation sooner and commit to throttle as soon as the car is pointed.

Mental Cue

Point, then power.

Validation Basis

This case should be confirmed using the original telemetry files and current metric calculations before being promoted to Accepted status.

Regression Requirement

Late to Power should outrank the more general Weak Exit diagnosis when delayed throttle commitment directly explains weak recovery and exit speed.

⸻

Case: Momentum Loss Through Neutral Time

Status: Candidate

Event: To be selected
Analysis Run: To be selected
Reference Run: To be selected
Segment: Slalom, offsets, or linked elements

Context

This case should represent gradual loss across a segment rather than one clear braking or throttle mistake.

Observed Differences

Expected evidence includes:

* Longer coast time
* Multiple throttle lifts
* Lower average speed
* Gradual accumulation of time loss
* No single strong brake or throttle event explaining the result

Expected Diagnosis

Momentum Loss.

Expected Confidence

Medium to High.

Diagnoses That Must Not Win

* Late to Power if there is no single delayed throttle commitment
* Over-Slowing if minimum speed alone does not explain the loss
* Execution Error if the behavior repeats through the segment

Expected Coaching

Stay connected to either brake or throttle and reduce unnecessary neutral time.

Mental Cue

Stay connected.

Validation Basis

A suitable historical case must be identified from an event with linked slalom or offset elements.

Regression Requirement

Momentum Loss should require a distributed pattern of neutral time or repeated lifts. It should not become a generic fallback for every unexplained loss.

⸻

Case: Over-Driving Entry

Status: Candidate

Event: To be selected
Analysis Run: To be selected
Reference Run: To be selected
Segment: Sweeper, turnaround, or offset entry

Context

This case should represent a driver carrying excessive speed into an element and compromising rotation or acceleration.

Observed Differences

Expected evidence includes:

* Higher entry speed
* Delayed throttle commitment
* Lower exit speed
* Weak recovery
* Lower average speed or slower segment time

Expected Diagnosis

Over-Driving.

Expected Confidence

High when the higher entry speed is followed by weaker rotation, recovery, and exit.

Diagnoses That Must Not Win

* Over-Slowing
* Weak Exit when excessive entry speed is the more specific cause
* Late to Power when delayed throttle is a consequence of excessive entry speed

Expected Coaching

Give up a small amount of entry speed so the car can rotate and accelerate cleanly.

Mental Cue

Slow hands, fast exit.

Validation Basis

The selected case should be confirmed with telemetry and, when available, video showing delayed rotation or corrective steering.

Regression Requirement

Higher entry speed must not automatically trigger Over-Driving. The diagnosis requires evidence that the higher entry compromised the remainder of the segment.

⸻

Case: Over-Slowing Without Exit Benefit

Status: Candidate

Event: To be selected
Analysis Run: To be selected
Reference Run: To be selected
Segment: Turnaround or tight offset

Context

This case should represent excessive braking or unnecessary speed reduction that does not produce a better exit.

Observed Differences

Expected evidence includes:

* Lower minimum speed
* Lower average speed
* Earlier braking or stronger deceleration
* No meaningful exit-speed improvement
* Slower segment time

Expected Diagnosis

Over-Slowing.

Expected Confidence

High when braking, minimum speed, average speed, and segment time agree.

Diagnoses That Must Not Win

* Over-Driving
* Late to Power unless throttle commitment is independently delayed
* Weak Exit when excessive speed reduction is the more direct cause

Expected Coaching

Reduce unnecessary braking and preserve more speed through the element.

Mental Cue

Protect momentum.

Validation Basis

The selected case should distinguish necessary speed reduction from unnecessary braking. A lower minimum speed that enables a clearly stronger exit should not qualify.

Regression Requirement

Minimum speed alone must never be sufficient to diagnose Over-Slowing.

⸻

Case: Discrete Finish-Lift Execution Error

Status: Candidate

Event: To be selected
Analysis Run: To be selected
Reference Run: Faster clean run
Segment: Finish section

Context

The driver lifts or reduces throttle before the timing lights despite having a viable path to complete the run under power.

Observed Differences

Expected evidence includes:

* Abrupt throttle reduction near the finish
* Loss concentrated after the lift
* Lower exit speed
* Driver note or video confirming the event
* Behavior not repeated across normal runs

Expected Diagnosis

Execution Error.

Expected Confidence

High with driver or video confirmation.

Diagnoses That Must Not Win

* Late to Power
* Weak Exit
* Momentum Loss

Expected Coaching

Finish the run under power and correct the isolated mistake without changing the broader approach.

Mental Cue

Finish the run.

Validation Basis

The diagnosis depends on identifying the behavior as a discrete mistake rather than a repeated technique pattern.

Regression Requirement

Execution Error should require strong evidence of a one-time event and should not hide recurring technique problems.

⸻

Case: Low-Confidence Timing Loss

Status: Accepted as a required behavior class

Event: Any event
Analysis Run: Any slower run
Reference Run: Faster comparison run
Segment: Any segment

Context

Some segments are slower even though the available telemetry does not provide a coherent explanation.

Observed Differences

Possible evidence includes:

* Small segment-time loss
* Equal or stronger minimum speed
* Equal or stronger exit speed
* No meaningful throttle delay
* Conflicting brake and speed indicators
* Possible GPS or segment-boundary effects

Expected Diagnosis

No Clear Diagnosis.

Expected Confidence

Low.

Diagnoses That Must Not Win

Any diagnosis that is contradicted by the principal telemetry evidence.

Expected Coaching

Do not make a major technique change. Seek confirmation from another run, GPS trace, video, or driver notes.

Mental Cue

Verify before changing.

Validation Basis

Low-confidence filtering is a core safety mechanism for the coaching engine.

Regression Requirement

Every release must include at least one test confirming that contradictory or insufficient telemetry does not generate confident coaching.

⸻

Case: Whole-Run Reinforcement

Status: Accepted as a required report behavior

Event: Any event with a faster, clean run
Analysis Run: Faster run
Reference Run: Previous clean run
Segment: Whole run or multiple segments

Context

The driver improves through clean execution across several segments without creating a dominant new loss.

Observed Differences

Expected evidence includes:

* Faster total run
* Multiple small segment gains
* No major segment loss
* Stable or improved exit speeds
* No high-confidence corrective diagnosis

Expected Diagnosis

Successful execution or no corrective diagnosis.

Expected Confidence

High that the run should be reinforced rather than corrected.

Diagnoses That Must Not Win

* A low-value diagnosis based on an isolated small metric difference
* A speculative recommendation to search for additional speed

Expected Coaching

Repeat the same rhythm and execution rather than making a major change.

Mental Cue

Repeat the run.

Validation Basis

RaceCoach must reinforce successful habits, not manufacture criticism after every run.

Regression Requirement

A clean faster run should be capable of producing reinforcement-only coaching.

⸻

Diagnosis-Specific Validation Requirements

Late to Power

At least one accepted case should confirm that:

* Throttle commitment is meaningfully later.
* Recovery is weaker.
* Exit speed is lower.
* The loss develops after rotation.
* Late to Power outranks Weak Exit when throttle timing explains the result.

⸻

Over-Driving

At least one accepted case should confirm that:

* Entry speed is higher.
* The higher entry compromises rotation or acceleration.
* Exit speed or recovery is weaker.
* Higher entry speed alone does not trigger the diagnosis.

⸻

Over-Slowing

At least one accepted case should confirm that:

* Minimum speed is meaningfully lower.
* Braking evidence supports unnecessary speed reduction.
* The lower minimum speed does not produce an exit benefit.
* Minimum speed alone does not trigger the diagnosis.

⸻

Momentum Loss

At least one accepted case should confirm that:

* Coast time or repeated lifts are meaningfully higher.
* The loss develops across the segment.
* No more specific diagnosis explains the result.
* Momentum Loss does not become a generic fallback.

⸻

Weak Exit

At least one accepted case should confirm that:

* Exit speed and recovery are weaker.
* The segment is slower.
* No stronger upstream cause, such as Over-Driving or Late to Power, explains the weak exit.

⸻

Execution Error

At least one accepted case should confirm that:

* The behavior is discrete.
* Driver notes or video support the conclusion.
* The engine does not treat a repeated technique problem as an isolated mistake.

⸻

No Clear Diagnosis

At least one accepted case should confirm that:

* Telemetry is contradictory or below meaningful thresholds.
* The engine suppresses corrective coaching.
* The segment may remain visible in detailed tables.

⸻

Inefficient Path

Before this diagnosis becomes production-ready, validation must confirm that RaceCoach can measure or reliably infer:

* Driven distance
* Lateral path difference
* Path curvature
* Line deviation from the reference
* Segment projection consistency

Speed metrics alone are not sufficient to diagnose an inefficient path.

⸻

Validation Workflow

1. Select a Comparison

Choose:

* An analysis run
* A reference run
* A segment
* A specific behavior to evaluate

Use clean runs whenever possible.

⸻

2. Generate Current Reports

Generate:

* Full Markdown report
* Grid Report
* JSON summary
* Any developer diagnostic output available

Record the code revision used for the test.

⸻

3. Inspect the Telemetry

Review the relevant metrics and confirm that:

* Units are correct.
* Signs are correct.
* Segment boundaries are reasonable.
* The selected input channels are valid.
* Missing data or GPS artifacts are not driving the result.

⸻

4. Review External Evidence

When available, compare the report with:

* Video
* GPS trace
* Driver notes
* Course map
* Run result
* Known cone or execution errors

⸻

5. Record the Expected Result

Document:

* Expected diagnosis
* Expected confidence
* Expected coaching
* Diagnoses that must not win
* Any uncertainty

⸻

6. Classify the Outcome

Use one of the following results:

Pass

The diagnosis, confidence, and coaching match the expected result.

Partial Pass

The primary conclusion is acceptable, but confidence, wording, ranking, or supporting evidence needs improvement.

Fail

The diagnosis is materially wrong, contradicted by telemetry, or produces inappropriate coaching.

Inconclusive

The available telemetry or external evidence is insufficient to determine the correct result.

⸻

7. Preserve the Case

Accepted cases should be retained as regression fixtures where practical.

The validation record should identify:

* Event
* Source telemetry files
* Segment configuration
* Expected output
* Date validated
* Code revision
* Notes

⸻

Regression Testing

A diagnosis-engine change should not be accepted solely because it improves one case.

Before merging a significant change:

1. Run all accepted validation cases.
2. Compare winning diagnoses.
3. Compare confidence levels.
4. Review coaching output.
5. Investigate every changed result.
6. Confirm that low-confidence filtering still works.
7. Confirm that successful runs still receive reinforcement coaching.

A changed result is not automatically a regression.

It must be reviewed to determine whether the previous or new behavior is more accurate.

⸻

Suggested Machine-Readable Validation Data

As the validation suite grows, cases should be recorded in a structured format such as YAML or JSON.

Example:

case_id: gglc_2026_06_20_r4_vs_r5_finish
status: accepted
event: gglc_2026-06-20
analysis_run: lap4
reference_run: lap5
segment: Finish section
expected:
  diagnosis: no_clear_diagnosis
  confidence: low
  coaching_contains:
    - review
    - GPS
  forbidden_diagnoses:
    - weak_exit
    - late_to_power
    - over_slowing
observed:
  time_delta_s: 0.32
  min_speed_delta_mph: 2.5
  exit_speed_delta_mph: 4.6
reason:
  Slower segment despite stronger minimum and exit speed.
  Current telemetry does not explain the loss.

The human-readable Markdown document should explain the reasoning.

The machine-readable record should support automated regression testing.

⸻

Validation Backlog

The following work is required to build a complete validation suite:

* Confirm source files for every accepted historical case.
* Record exact analysis and reference lap filenames.
* Standardize segment names across historical events.
* Add at least one accepted case for every production diagnosis.
* Add at least two No Clear Diagnosis cases.
* Add at least one reinforcement-only case.
* Add video-confirmed Execution Error cases.
* Add path-analysis cases before enabling Inefficient Path.
* Create machine-readable expected results.
* Add a command that runs all validation comparisons.
* Store generated validation reports separately from event reports.
* Record code revision and configuration with every validation run.

⸻

Acceptance Criteria for Diagnosis Changes

A diagnosis or scoring change is ready for production when:

* It improves or preserves accepted validation cases.
* It does not create new false-positive coaching.
* It handles conflicting evidence appropriately.
* It preserves low-confidence filtering.
* It produces clear and executable coaching.
* It does not overwhelm the Grid Report with competing recommendations.
* Any changed historical result has been reviewed and documented.

⸻

Related Documentation

* DIAGNOSIS_MODEL.md
* METRICS.md
* COACHING_PHILOSOPHY.md
* REPORT_INTERPRETATION.md
* ARCHITECTURE.md
* OPERATIONS.md
* BACKLOG.md