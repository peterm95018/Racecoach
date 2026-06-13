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