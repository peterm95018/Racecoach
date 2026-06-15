# RaceCoach Backlog

## Next Up

### Auto-publish report to Drupal
Priority: High

Current:
- Report generated in event reports directory

Goal:
- Automatically publish latest_report.html to Drupal-served location

Benefit:
- Eliminate manual copy step
- Simplify event workflow

---

### Repository cleanup
Priority: High

- Add .gitignore entries for uploads and generated reports
- Keep segment definitions and course maps under source control

---

## June 20 Validation

### Validate RaceChrono 10.2 accelerator channel

Questions:
- Is accelerator_pos exported?
- Does it replace relative_throttle_pos?

---

### Fix Top Opportunities telemetry formatting
Priority: Medium

Current issue:

The telemetry section in Top Opportunities is difficult to scan on a phone.

Examples:
- Long lines wrap poorly
- Related metrics are separated
- Throttle and braking metrics are not consistently grouped
- Experimental metrics can distract from primary coaching metrics

Goals:
- Improve mobile readability
- Group related metrics together
- Prioritize coaching-relevant metrics
- Reduce visual clutter

Possible approach:

Primary metrics:
- Duration
- Entry speed
- Minimum speed
- Exit speed
- Throttle commitment
- Brake start

Secondary metrics:
- Average speed
- Peak decel
- Coast time

Experimental metrics:
- Recovery gain (+1s)
- Recovery gain (+2s)

Success criteria:

A driver should be able to understand why a segment was flagged within 5 seconds while standing in grid.

### Validate throttle commitment metric

Questions:
- Does throttle commitment produce better coaching than throttle pickup time?
- Does it correctly identify gains and losses?

---

## Analysis Improvements

### Reference-path segmentation
Priority: High

Current:
- Distance-based segments

Future:
- GPS path projection against reference lap

Expected benefit:
- Improved segment accuracy

---

### Line efficiency analysis

Goal:
- Detect driving extra distance versus reference lap

---

### Slalom analysis

Goal:
- Detect delayed transitions
- Detect backside cone losses

---

## Dashboard

### Grid Coach Dashboard

Mobile-friendly summary page:

- Next Run Focus
- Biggest Gain
- Biggest Loss
- Current Reference Lap

---

### Run History

- Trend analysis
- Best segment tracking

---

## Research

### Recovery gain metrics

Status:
- Experimental

Questions:
- Are Rec+1 and Rec+2 providing signal beyond exit speed?
- Keep, move to detail view, or remove?