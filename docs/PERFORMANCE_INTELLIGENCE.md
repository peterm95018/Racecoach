# Performance Intelligence

## Purpose

Performance Intelligence is the long-term knowledge layer of RaceCoach.

Telemetry explains what happened during a run.

Diagnosis explains why it happened.

Performance Intelligence captures the persistent knowledge required to help a driver prepare, improve, and perform over many events.

Its purpose is not to replace telemetry analysis.

Its purpose is to provide context for coaching decisions.

---

# Guiding Principle

RaceCoach should learn in the same way an experienced instructor learns.

An experienced instructor remembers:

- the driver
- the venue
- the car
- the conditions
- lessons from previous events

before watching the next run.

Performance Intelligence models that accumulated knowledge.

Its objective is to improve the driver's future performance rather than simply explain previous performance.

---

# Knowledge Domains

Performance Intelligence consists of five complementary knowledge domains.

Each domain answers a different question.

---

## Driver Intelligence

Driver Intelligence captures persistent knowledge about the driver.

It changes slowly over weeks, months, and seasons.

Examples include:

- coaching themes
- strengths
- recurring habits
- weaknesses
- repeatability
- improvement trends
- preparation history
- learning preferences
- performance plateaus

Driver Intelligence answers:

> What kind of driver is this becoming?

---

## Venue Intelligence

Venue Intelligence captures recurring characteristics of a venue and driving discipline.

A venue is defined as:

> A place and driving format with characteristic coaching demands.

Examples

Autocross

- Salinas Airport
- Crows Landing
- Sonoma Fairgrounds
- Laguna Seca Lakebed

HPDE

- Laguna Seca Road Course
- Sonoma Raceway
- Thunderhill Raceway
- Buttonwillow Raceway

Venue Intelligence should describe recurring characteristics rather than specific course layouts.

Example

### Salinas Airport

Typical characteristics

- multiple slaloms are common
- offsets frequently appear
- momentum is important
- large turnarounds are common

### Crows Landing

Typical characteristics

- long acceleration zones
- long slaloms
- higher average speeds
- significant braking opportunities

### Laguna Seca Lakebed

Typical characteristics

- compact paved area
- tight transitions
- turnarounds are common
- efficient rotation is rewarded

Venue Intelligence should never assume an exact course design.

Instead, it should capture the types of driving challenges commonly presented at that venue.

Venue Intelligence answers:

> What skills does this venue usually reward?

---

## Car Intelligence

Car Intelligence captures knowledge specific to the vehicle.

Examples include:

- chassis
- drivetrain
- tires
- suspension
- alignment
- brake configuration
- tire pressure history
- setup changes
- maintenance affecting performance

Different cars require different coaching.

Car Intelligence answers:

> How does this car influence driving technique?

---

## Environment Intelligence

Environment Intelligence captures conditions unique to today's event.

Examples include:

- temperature
- wind
- rain
- surface grip
- dirty pavement
- heat buildup
- run order
- tire temperature

Environment Intelligence changes every event.

Environment Intelligence answers:

> What conditions will influence today's performance?

---

## Session Intelligence

Session Intelligence captures information unique to the current event.

Examples include:

- today's coaching theme
- reference run
- tire pressures
- session consistency
- benchmark competitors
- today's breakthrough
- today's mistakes
- today's strengths

Session Intelligence expires after the event but contributes to Driver Intelligence.

Session Intelligence answers:

> What matters today?

---

# Preparation Intelligence

Preparation Intelligence combines the other knowledge domains into actionable pre-event coaching.

Preparation Brief

=

Driver Intelligence

+

Venue Intelligence

+

Car Intelligence

+

Environment Intelligence

+

Session Intelligence

The objective is not to analyze the previous event.

The objective is to improve the driver's first run.

---

# Evidence Levels

Not every observation should become coaching.

Performance Intelligence distinguishes between three levels of evidence.

## Observation

Something observed once.

Examples

- The shorter drive reduced fatigue.
- Watching another driver helped identify a better line.

Observations are preserved but should not automatically influence future coaching.

---

## Candidate Pattern

A repeated observation that may indicate a trend.

Examples

- Simulator practice appears to improve slalom rhythm.
- Reduced telemetry review appears to improve focus.

Candidate patterns should continue to be monitored before becoming recommendations.

---

## Established Performance Factor

A repeated, reproducible observation supported by multiple events.

Examples

- Earlier throttle commitment consistently reduces time loss.
- Maintaining a single coaching objective improves repeatability.
- Course visualization improves first-run performance.

Only established performance factors should automatically influence future Preparation Briefs.

---

# Knowledge Confidence

Different knowledge domains have different confidence levels.

| Knowledge | Confidence Source |
|-----------|-------------------|
| Telemetry | Direct measurement |
| Metrics | Computed from telemetry |
| Diagnosis | Inference from telemetry |
| Driver Reflection | Self-reported observation |
| Venue Intelligence | Historical experience |
| Preparation Recommendation | Derived from multiple knowledge sources |

Before RaceCoach promotes information into coaching, it should answer:

> How do we know this?

Confidence should increase as observations become repeatable and evidence accumulates.

---

# Design Principles

## Evidence Before Automation

RaceCoach should collect observations before drawing conclusions.

Automation should occur only after repeated evidence supports a recommendation.

---

## Separate Context from Coaching

Historical context is valuable.

Not every historical observation should become coaching.

Example

Appropriate coaching

- Simulator practice improved slalom rhythm.

Historical context

- The drive to the event was shorter.
- The course required less walking.

Context should be preserved without automatically influencing future Preparation Briefs.

---

## Coach Reproducible Behaviors

RaceCoach should prioritize recommendations that the driver can intentionally repeat.

Examples

Good

- Review slalom technique before the event.
- Visualize the course after the course walk.
- Limit unnecessary telemetry review between runs.
- Maintain one coaching objective.

Poor

- Hope for cooler weather.
- Hope for a smaller course.
- Hope for longer breaks between runs.

Preparation recommendations should emphasize controllable behaviors rather than circumstances.

---

## Optimize for Preparation

Performance Intelligence exists to improve the driver's next event rather than simply explain the previous one.

Every recommendation should increase the probability of improved future performance.

---

# Relationship to Other RaceCoach Components

Telemetry measures the run.

Metrics quantify the run.

Diagnosis explains the run.

Coaching recommends the next action.

Performance Intelligence provides the long-term context that makes coaching increasingly personalized over time.

```
Telemetry
        ↓
Metrics
        ↓
Diagnosis
        ↓
Coaching
        ↓
Performance Intelligence
        ↓
Preparation Intelligence
```

---

# Future Components

Performance Intelligence provides the foundation for future RaceCoach capabilities including:

- Driver Profile
- Venue Profiles
- Car Profiles
- Preparation Briefs
- Coaching Themes
- Seasonal Reviews
- Plateau Detection
- Personalized Practice Plans
- Long-term Driver Development
- AI Coaching Assistant

---

# Guiding Principle

RaceCoach should become progressively more knowledgeable about the driver without becoming more speculative.

Every new recommendation should be supported by accumulated evidence rather than isolated observations.

The measure of successful Performance Intelligence is not how much RaceCoach remembers.

The measure is whether the driver consistently arrives at each event better prepared, more focused, and more capable of producing faster runs.