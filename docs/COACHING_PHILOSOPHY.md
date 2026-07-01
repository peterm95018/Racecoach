RaceCoach Vision Session

Date: June 30, 2026

Purpose

This discussion marked a transition in the RaceCoach project from being a telemetry analysis tool to becoming a driver development and coaching system.

The objective is no longer to produce more metrics. The objective is to produce better coaching.

⸻

Mission Statement

RaceCoach exists to help the driver find the fastest next run.

Telemetry is only the evidence. The output should be coaching that a driver can understand and immediately apply while sitting on grid.

RaceCoach should answer three questions:

1. What was my biggest opportunity?
2. Why did it happen?
3. What is the one thing I should change on the next run?

⸻

Design Philosophy

RaceCoach should coach driving behaviors, not telemetry metrics.

Examples:

Instead of:

* Minimum speed
* Exit speed delta
* Throttle pickup delay

Use:

* Get back to power sooner.
* Protect exit speed.
* You coasted too long.
* You over-drove the entry.
* You slowed the car more than necessary.

Internal telemetry should support the coaching but should rarely appear in the final recommendation.

Example:

Instead of:

Throttle delayed 0.38 s after minimum speed.

Use:

You waited 0.38 s too long to get back to power, costing approximately 0.42 s before the finish.

⸻

Driver Behavior Categories

RaceCoach should classify opportunities into recognizable driving behaviors.

Late to Power

Symptoms:

* Delayed throttle commitment
* Reduced exit speed
* Reduced recovery speed

Coaching:

Commit to throttle as soon as the car is pointed.

⸻

Over Driving

Symptoms:

* Excessive entry speed
* Delayed rotation
* Poor exit speed
* Late throttle

Coaching:

Slow the car earlier, rotate it, then commit to power.

⸻

Over Slowing

Symptoms:

* Excessive braking
* Lower than necessary corner speed
* Conservative approach

Coaching:

Trust the grip and preserve momentum.

⸻

Momentum Loss

Symptoms:

* Long coasting periods
* Multiple unnecessary lifts
* Hesitation between brake and throttle

Coaching:

Keep the car connected to either brake or throttle.

⸻

Braking Opportunity

Symptoms:

* Early braking
* Long brake release
* Excessive brake duration

Coaching:

Brake later and finish braking sooner.

⸻

Poor Line (Future)

Potential inputs:

* GPS path length
* Apex position
* Steering corrections
* Line consistency

⸻

Excellent Execution

RaceCoach should positively reinforce successful driving.

Example:

Excellent exit.

Earlier throttle commitment gained 0.32 s.
Repeat this next run.

⸻

Execution Errors

Separate one-time mistakes from recurring habits.

Examples:

* Lift before finish
* Cone contact
* Missed gate
* Incorrect line through one element

These should not be confused with recurring driving limitations.

⸻

Habits vs. Mistakes

RaceCoach should distinguish between:

Recurring Habits

Examples:

* Late to power
* Over driving
* Over slowing
* Momentum loss

These create long-term performance plateaus.

Execution Mistakes

Examples:

* Lift before finish
* One missed apex
* One braking mistake

These affect an individual run but are not necessarily recurring limitations.

⸻

Confidence

Every diagnosis should include an internal confidence score.

High confidence requires multiple pieces of supporting evidence.

Example:

Late to Power

Confidence: High

Reason:

* Delayed throttle
* Lower exit speed
* Reduced recovery speed

⸻

One Thing

Every Grid Report should end with one coaching instruction.

Example:

NEXT RUN

Commit to throttle immediately after the turnaround.

One instruction is easier to remember than several competing recommendations.

⸻

Event Coaching Workflow

Between Runs

Review the Grid Report.

Answer:

* What happened?
* What should I change?

Target review time:

30 seconds.

⸻

Lunch

Review trends:

* Recurring behaviors
* Tire strategy
* Course evolution
* Driver observations

This is the time for deeper discussion.

⸻

After the Event

Review:

* What recurring habit limited performance?
* What improved?
* What becomes the next development priority?

⸻

July 11–12 Salinas Objectives

The July Porsche Club weekend will serve as the first field validation of RaceCoach’s coaching philosophy.

Objectives:

* Improve coaching language.
* Introduce behavior classification.
* Add confidence to diagnoses.
* Produce a concise Grid Report.
* Compare RaceCoach’s conclusions against driver perception after each run.

Each diagnosis should be evaluated as:

* Correct
* Partially Correct
* Incorrect

The goal is to refine coaching heuristics using real-world feedback.

⸻

Long-Term Vision

RaceCoach should evolve through three levels.

Grid Report

Immediate coaching for the next run.

Event Report

Patterns across the current event.

Driver Development Report

Long-term improvement across months and seasons.

Rather than only comparing lap times, RaceCoach should identify recurring habits and document driver progression over time.

Examples:

* Reduced over slowing.
* Earlier throttle commitment.
* Improved momentum preservation.
* Increased consistency.

⸻

Core Principle

RaceCoach does not exist to analyze telemetry.

RaceCoach exists to identify the one driving behavior that, if improved, will make the driver faster on the next run.

Everything else is supporting evidence.
