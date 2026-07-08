# RaceCoach Roadmap


## Projection Development Notes

### Work Completed

We began implementing reference-path segmentation so RaceCoach could report on named course elements instead of generic Start / Middle / Finish sections.

Initial goal:

- Use the reference lap GPS path as the segmentation backbone.
- Project each analysis lap sample onto the nearest point of the reference path.
- Use the projected reference position as the segment distance.

### Files Involved

Primary implementation files:

- `racecoach/reference_path.py`
  - GPS path distance calculation
  - Reference-path projection helpers
  - Experimental nearest-point projection logic

- `racecoach/analyze_run.py`
  - Event segmentation mode selection
  - Reference-path branch inside `analyze()`
  - Segment range generation from `segments.yaml`
  - Segment debug output
  - Grid report filtering for low-confidence losses

Event configuration file:

- `events/gglc_2026-06-20/event.yaml`
  - Enables `segmentation_mode: reference_path`

Segment definition file:

- `events/gglc_2026-06-20/segments.yaml`
  - Defines the five named course segments

### Logic Changes Tried

#### 1. Direct GPS Nearest-Point Projection

We first projected each analysis-lap sample to the nearest GPS point on the reference path.

Result:

- Fast after NumPy optimization.
- Worked in simple areas.
- Failed on overlapping autocross sections.
- Projection jumped forward across course sections.

Observed failure:

- `Offsets to turnaround` received zero samples.
- `Turnaround to left sweep` absorbed too much time.
- Reports produced impossible +8 to +11 second segment losses.

Conclusion:

Nearest GPS point alone is not reliable for autocross courses with overlapping paths, turnarounds, or nearby parallel elements.

#### 2. Monotonic Projection

We forced projected reference position to never move backward.

Result:

- Prevented backward jumps.
- Did not prevent large forward jumps.
- Still skipped or compressed course sections.

Conclusion:

Monotonic projection is necessary but not sufficient.

#### 3. Fixed Forward-Step Clamp

We limited how far the projected reference position could advance per sample.

Values tested:

- `3.0m`
- `0.15m`
- `0.05m`

Result:

- Large values still allowed jumps.
- Small values distorted the whole lap by spreading reference distance too evenly over time.
- Segment timing became artificial.

Conclusion:

A fixed clamp is not robust because allowed progression should depend on actual vehicle movement and sample spacing.

#### 4. Dynamic Clamp Based on Raw Distance

We tried limiting projected reference advancement based on the car’s actual raw distance delta.

Result:

- Improved behavior slightly.
- Still compressed `Offsets to turnaround` and inflated `Turnaround to left sweep`.
- Did not fully solve overlapping path ambiguity.

Conclusion:

Dynamic clamping is better than fixed clamping but still not sufficient without a more robust path-tracking model.

#### 5. Stable Distance-Normalized Reference Position

We replaced GPS projection for production reference-path mode with normalized lap distance:

```python
max_ref_d = float(ref_df["gps_path_m"].max())
max_lap_d = float(df["distance"].max())

df["ref_pos_m"] = df["distance"] / max_lap_d * max_ref_d
df["ref_error_m"] = 0.0
```

Result:

- All five named segments received valid samples.
- Segment durations became plausible.
- Large false gains/losses disappeared.
- Grid report returned to sensible coaching.
- This became the current stable baseline.

Conclusion:

Distance-normalized reference position is not the final GPS projection solution, but it is stable enough for production use and gives RaceCoach named segment reporting now.

### Current Production Choice

RaceCoach currently uses distance-normalized reference positioning in `analyze_run.py` for reference-path mode.

This is intentional.

It provides reliable named course segmentation while preserving future work on true GPS projection.

### Future GPS Projection Requirements

A future true GPS projection implementation should include:

- Heading-aware nearest-point matching.
- Forward-only local search window.
- Maximum jump rejection.
- Awareness of previous matched reference index.
- Handling for overlapping course sections.
- Turnaround/crossover validation.
- Comparison against the current distance-normalized baseline.

### Success Criteria

A future GPS projection replacement must:

- Assign samples to all expected segments.
- Avoid impossible segment gains/losses.
- Keep segment durations plausible.
- Preserve or improve coaching output compared with the current stable baseline.
- Pass validation on GGLC 2026-06-20 lap 1 → lap 2.

### Key Validation Case

GGLC 2026-06-20, Lap 1 → Lap 2.

Stable result using normalized reference distance:

- All five segments present.
- No major losses detected.
- Grid report recommends repeating clean sections.
- No fake +8s to +11s segment losses.


## Current Stable Baseline

**Git Tag:** `reference-path-stable`

### Status

This tag represents the current production baseline for RaceCoach after stabilizing the reference-path segmentation workflow.

It is the recommended version to return to before beginning work on experimental GPS projection algorithms or major analysis changes.

### Included

- Five named course segments generated from the event configuration.
- Stable reference-path segmentation using normalized course distance.
- Consistent segment boundaries across reference and analysis laps.
- Grid report filters out low-confidence coaching.
- Debug segment logging controlled by the `RACECOACH_DEBUG_SEGMENTS` environment variable.
- Production-quality Markdown, HTML, and Grid reports.

### Known Limitations

- Reference position is currently derived from normalized lap distance rather than true GPS projection.
- Segment boundaries remain accurate as long as laps follow a similar driving line.
- Courses with large shortcuts, alternate lines, or repeated crossovers may require a more sophisticated GPS projection algorithm.

### Next Major Development

Replace the temporary distance-normalized reference positioning with a robust GPS reference projection that includes:

- Heading-aware nearest-point matching
- Forward-only progression along the reference path
- Local search window to prevent jumps
- Reliable handling of overlapping course sections and turnarounds
- Validation against the current stable baseline

### Validation Criteria

Any future GPS projection implementation should produce segment timing that is at least as stable as this baseline before replacing it as the production default.



## Current Status

Current stable tag:
reference-path-stable

Current segmentation:
- Five named course segments
- Distance-normalized reference segmentation
- Stable grid reports
- Production ready for June 2026 event analysis

---

## High Priority

### GPS Reference Projection

Status: Prototype

Goal:
Replace distance-normalized projection with true GPS path projection.

Remaining work:
- Heading-aware nearest-point search
- Forward-only projection
- Local search window
- Handle overlapping paths
- Validate turnaround behavior
- Compare against distance-normalized baseline

Success criteria:
Reference projection agrees with segment boundaries within ±2 m.

---

### Driver Coaching

- Better diagnosis ranking
- Detect line errors
- Detect early throttle lifts
- Better braking advice
- Improve confidence scoring

---

### Reports

- HTML improvements
- Interactive plots
- Overlay reference vs analysis
- Better momentum visualizations

---

### Event Workflow

- Automatic segment validation
- Event setup wizard
- Reference lap selection
- Session summaries

---

### Future

- Multi-run trend analysis
- Driver improvement over season
- AI coaching summaries
- Video synchronization
- Racing line comparison
