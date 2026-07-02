# RaceCoach Diagnosis Model

RaceCoach should diagnose driving behavior, not just report telemetry symptoms.

## Diagnosis Template

Each diagnosis should define:

- Evidence
- Conflicting evidence
- Confidence rules
- Prescription
- Mental cue

---

## Late to Power

Evidence:
- Throttle commitment later than reference
- Exit speed lower than reference
- Recovery speed/gain lower after the feature

Conflicting evidence:
- Throttle commitment earlier
- Exit speed equal or better

Prescription:
Commit to throttle as soon as the car is pointed.

Mental cue:
Point, then power.

---

## Over Driving

Evidence:
- Entry speed higher than reference
- Exit speed lower than reference
- Throttle commitment delayed
- Average speed lower through the segment

Conflicting evidence:
- Exit speed equal or better
- Recovery speed equal or better

Prescription:
Give up a little entry speed so the car rotates and exits cleanly.

Mental cue:
Slow hands, fast exit.

---

## Over Slowing

Evidence:
- Minimum speed lower than reference
- Average speed lower
- No clear exit-speed benefit
- Braking earlier or harder than needed

Conflicting evidence:
- Exit speed much better
- Earlier braking produced a faster segment

Prescription:
Trust the grip and preserve momentum.

Mental cue:
Protect momentum.

---

## Momentum Loss

Evidence:
- Long coast time
- Multiple throttle lifts
- Lower average speed
- Loss develops through the segment rather than at one point

Conflicting evidence:
- Strong exit speed
- Clear braking or throttle cause explains the loss

Prescription:
Stay connected to brake or throttle; avoid neutral time.

Mental cue:
Always be doing something.

---

## Execution Error

Evidence:
- Lift before finish
- Abrupt throttle drop near timing lights
- One-off mistake visible in telemetry or driver note

Prescription:
Do not over-analyze it. Fix the mistake next run.

Mental cue:
Flat to the lights.

---

## Low Confidence

Evidence:
- Segment slower but speed metrics are equal or better
- Conflicting telemetry
- Segment boundary or GPS alignment may explain the result

Prescription:
Do not chase setup or technique based on this alone.

Mental cue:
Verify before changing.