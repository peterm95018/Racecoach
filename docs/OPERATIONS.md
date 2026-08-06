# RaceCoach Operations Guide

Applies to RaceCoach:
reference-path-stable and later

Last major update:
August 2026

## Purpose

This guide describes how RaceCoach is operated and maintained.

It covers:

* creating and managing events
* running the upload pipeline
* managing the active event
* rebuilding reports
* publishing reports
* maintaining the Ubuntu server

It does not explain how to interpret reports or use RaceCoach during competition.

For driver-facing documentation, see USER_GUIDE.md.


---

## RaceCoach Command-Line Interface

RaceCoach provides a unified command-line interface through the `racecoach` executable.

For convenience, many users create the shell alias:

```bash
alias rc='racecoach'

rc status
rc reference
rc summary
rc finalize
```

---


## Event Lifecycle

### Create a New Event

This command creates the event directory skeleton and sets new event as active event.
Run:

./prep_event

This command:

* Creates the event directory.
* Creates the uploads/ directory.
* Creates the reports/ directory.
* Copies the default segments.yaml if needed.
* Sets the new event as the active event.
* Updates the Drupal current report symlinks (Ubuntu server only).
* Refreshes supporting services if install_service.sh is present.


---

### Switch to an Existing Event

Run:

./set_active_event EVENT_NAME

Example:

./set_active_event gglc_2026-06-20

This command:

* Updates active_event.txt.
* Updates the Drupal current report symlinks.
* Verifies that the selected event exists.
* Displays the public report URLs.

---

### Interactive Event Selection

Run:

./set_active_event

RaceCoach displays a numbered list of available events and prompts you to choose one.

---

### Active Event

The currently selected event is stored in:

active_event.txt

Verify the active event:

cat active_event.txt

---

### Event Directory Structure

Each event contains the following directories:

events/
└── gglc_2026-06-20/
    ├── uploads/
    ├── reports/
    └── segments.yaml

* uploads/ — RaceChrono CSV exports.
* reports/ — Generated Grid Reports, Full Reports, HTML, Markdown, and summary files.
* segments.yaml — Event-specific segment definitions.

---

# Event Processing Pipeline

RaceCoach processes an event in two phases.

During the event, each uploaded run is analyzed immediately to provide coaching between runs.

After the event, the session reference can be optimized and the entire event rebuilt using the best available reference lap.

---

## Phase 1 — Immediate Run Analysis

The upload watcher monitors the active event's `uploads/` directory for new RaceChrono CSV files.

When a new CSV is detected, RaceCoach automatically:

1. Imports the telemetry.
2. Analyzes the run using the current `reference.csv`.
3. Generates:
   - Full Report
   - Grid Report
   - Summary JSON
4. Updates the latest published reports.

This provides immediate feedback during the event without modifying the session reference.

The first uploaded run becomes the initial `reference.csv`. That reference remains unchanged until it is explicitly promoted later.

---

## Phase 2 — Reference Optimization

Once the session is complete and run classifications have been reviewed, the session reference can be improved.

RaceCoach evaluates every analyzed run and selects the best reference according to the current selection strategy.

Current selection rules are:

1. Fastest clean run.
2. If no clean runs exist, fastest analyzed run.

Reference selection is deterministic.

Given the same telemetry and run classifications, RaceCoach will always select the same reference lap.

---

## Preview the Selected Reference

To see which run would become the session reference without modifying the event:

```bash
python3 -m racecoach.select_reference \
    --event events/<event-name>
```

This command performs a dry run and reports:

- selected run
- source CSV
- analyzed duration
- selection rule

No files are modified.

---

## Promote the Reference

To replace the session reference:

```bash
python3 -m racecoach.select_reference \
    --event events/<event-name> \
    --promote
```

This command:

- updates `reference.csv`
- records the decision in `reference_selection.json`

Existing reports are not regenerated.

---

## Rebuild the Event

To regenerate the entire event using the promoted reference:

```bash
python3 -m racecoach.select_reference \
    --event events/<event-name> \
    --promote \
    --rebuild
```

This command performs the complete post-session workflow:

1. Promotes the selected reference.
2. Writes `reference_selection.json`.
3. Reanalyzes every uploaded CSV.
4. Regenerates every report and summary JSON.
5. Regenerates `session_summary.md`.

After rebuilding, every report in the event is based on the same reference lap.

---

## Reference Selection Metadata

Each reference promotion records an audit trail in:

```
reference_selection.json
```

Example:

```json
{
  "run": "lap4",
  "source": "session_20260712_103209_lpr-2026-07-12-am_lap4_v3.csv",
  "duration_s": 27.488,
  "selection_rule": "fastest_clean",
  "selected_at": "2026-08-03T18:22:30Z"
}
```

This metadata records:

- which run became the session reference
- the source CSV
- the selection rule
- the analyzed duration
- when the promotion occurred

The metadata provides a reproducible audit trail for validation and future analysis.

---

## Upload Watcher

RaceCoach uses a user-level systemd service to monitor the active event’s upload directory.

The service is installed or refreshed by:

./install_service.sh

When a new event is created using prep_event, the watcher is reconfigured to monitor the new event’s uploads/ directory.

When a new RaceChrono CSV is detected, the watcher automatically:

1. Imports the telemetry.
2. Analyzes the run using the current reference.csv.
3. Generates the Full Report, Grid Report, and summary JSON.
4. Publishes the latest reports to Drupal.

The upload watcher does not automatically change the session reference. The current reference remains in use until a reference promotion is performed.

After a session has been completed and run classifications have been reviewed, the reference can be optimized using:

```
python3 -m racecoach.select_reference \
    --event events/<event-name> \
    --promote \
    --rebuild
```

This workflow:

1. Selects the fastest clean run (or the fastest analyzed run if no clean runs exist).
2. Updates reference.csv.
3. Records the selection in reference_selection.json.
4. Rebuilds every report in the event using the new reference.
5. Regenerates the session summary.


---
## Drupal Report Publishing

The Ubuntu server publishes the active event using symbolic links located at:

/var/www/html/drupal10/web/sites/default/files/racecoach/events/current/

The following files are linked:

* grid_report.html
* grid_report.md
* latest_report.html
* latest_report.md

These links always point to the reports for the currently active event.

---

## Public Report URLs

Grid Report:

https://petermcmillan.com/sites/default/files/racecoach/events/current/grid_report.html

Latest Report:

https://petermcmillan.com/sites/default/files/racecoach/events/current/latest_report.html

---

## Working on Multiple Computers

Development Computer (Mac)

set_active_event updates only:

active_event.txt

Because Drupal is not installed, the script skips the symbolic-link update and reminds you to run the same command on the Ubuntu server after pulling the latest changes.

---

Ubuntu Server

set_active_event updates both:

* active_event.txt
* Drupal current symbolic links

This immediately changes the reports served through Drupal.

---

Upload Processing

RaceCoach watches each event’s uploads/ directory for new RaceChrono CSV files.

When a new CSV is detected, the processing pipeline:

1. Imports the telemetry.
2. Selects or updates the reference lap as needed.
3. Runs the analysis.
4. Generates the Full Report.
5. Generates the Grid Report.
6. Updates the Drupal current links.

---

## Troubleshooting

Empty Report

Usually indicates that no valid reference lap has been established.

Verify:

* A reference lap exists.
* The CSV imported successfully.
* The analysis completed without errors.

---

Drupal Shows an Old Report

Run:

./set_active_event EVENT_NAME

Verify the symbolic links:

ls -l /var/www/html/drupal10/web/sites/default/files/racecoach/events/current

---

Uploads Are Not Processed

Verify:

* The upload watcher is running.
* New CSV files are appearing in the event’s uploads/ directory.
* File permissions allow the watcher to read the uploads.

---

Watcher Does Not Trigger

The watcher responds only to newly created files.

If a CSV existed before the watcher started, re-copy or re-export the file to trigger processing.

--

Report Generation Errors

If report generation fails:

* Verify all scripts are from the same Git branch.
* Confirm prep_event and set_active_event are current.
* Check the console output for Python exceptions or missing telemetry channels.

---

## Typical Workflows

### During an Event

./prep_event

* Create the event.
* Walk the course.
* Update segments.yaml.
* Begin collecting telemetry.

---

Review a Previous Event

./set_active_event gglc_2026-06-20

* Switch the active event.
* Verify the public report URLs.
* Review historical Grid and Full Reports.

---

Related Documentation

* USER_GUIDE.md — Driver workflow and report interpretation.
* ARCHITECTURE.md — Software architecture.
* CLI.md - RaceCoach command-line interface.
* METRICS.md — Telemetry metric definitions.
* REPORT_INTERPRETATION.md — Detailed explanation of report content.
* DEVELOPMENT_LOG.md — Development history and implementation notes.




## Automatic Reference Selection

RaceCoach supports automatic selection and promotion of the session reference lap.

Rather than permanently using the first uploaded run as the reference, RaceCoach can evaluate all analyzed runs and select the best reference automatically.

The reference selection process is deterministic and fully reproducible.

---

### Selection Rules

RaceCoach evaluates every available run summary in the event.

Selection follows these rules:

1. Select the fastest **clean** analyzed run.
2. If no clean runs have been classified, select the fastest analyzed run regardless of status.

The selected run becomes the session reference.

Current selection rules:

- `fastest_clean`
- `fastest_analyzed_fallback`

Future versions may support additional selection strategies.

---

### Dry Run

To preview the selected reference without modifying the event:

```bash
python3 -m racecoach.select_reference \
    --event events/<event-name>
```

Example output:

```
Selected run: lap4
Source CSV: uploads/session_..._lap4.csv
Duration: 27.488s
Selection rule: fastest_clean

Dry run only; reference.csv was not changed.
```

---

### Promote Reference

To update the event reference:

```bash
python3 -m racecoach.select_reference \
    --event events/<event-name> \
    --promote
```

This command:

- copies the selected CSV to `reference.csv`
- overwrites the previous reference
- records the selection in `reference_selection.json`

It does **not** rebuild reports.

---

### Promote and Rebuild

To update the reference and regenerate the entire event:

```bash
python3 -m racecoach.select_reference \
    --event events/<event-name> \
    --promote \
    --rebuild
```

This command performs the complete workflow:

1. Select the reference lap.
2. Update `reference.csv`.
3. Write `reference_selection.json`.
4. Reanalyze every uploaded run against the new reference.
5. Rewrite all run reports and summary JSON files.
6. Regenerate `session_summary.md`.

After completion, every report in the event references the same promoted reference lap.

---

### Reference Selection Metadata

Each promotion records the selection decision in:

```
reference_selection.json
```

Example:

```json
{
  "run": "lap4",
  "source": "session_20260712_103209_lpr-2026-07-12-am_lap4_v3.csv",
  "duration_s": 27.488,
  "selection_rule": "fastest_clean",
  "selected_at": "2026-08-03T18:22:30Z"
}
```

This file provides an audit trail showing:

- which run became the reference
- why it was selected
- when the promotion occurred

---

### Reproducibility

Reference selection is deterministic.

Given the same:

- uploaded CSV files
- summary JSON files
- run classifications

RaceCoach will always select the same reference lap and produce identical rebuilt reports.

This reproducibility is important for validation, regression testing, and future improvements to the diagnosis engine.


## Event Processing Pipeline

RaceCoach processes an event in two distinct phases.

### Phase 1 — Run Analysis

As each RaceChrono CSV is uploaded, the upload watcher automatically:

1. Imports the telemetry.
2. Analyzes the run using the current `reference.csv`.
3. Generates:
   - Full Report
   - Grid Report
   - Summary JSON
4. Publishes the latest reports to Drupal.

This provides immediate feedback between runs while preserving all telemetry and analysis artifacts.

---

### Phase 2 — Reference Optimization

After sufficient runs have been collected, the session reference can be improved.

RaceCoach evaluates every analyzed run and selects the best reference according to the current selection strategy.

Current strategy:

1. Fastest clean run.
2. Otherwise, fastest analyzed run.

Reference selection is deterministic.

Given identical telemetry and run classifications, RaceCoach will always choose the same reference.

---

### Preview the Selected Reference

To see which run would become the reference:

```bash
python3 -m racecoach.select_reference \
    --event events/<event>
```

No files are modified.

---

### Promote the Reference

To replace the current reference:

```bash
python3 -m racecoach.select_reference \
    --event events/<event> \
    --promote
```

This updates:

- `reference.csv`
- `reference_selection.json`

Existing reports are not modified.

---

### Rebuild the Event

After promoting a new reference, regenerate every report:

```bash
python3 -m racecoach.select_reference \
    --event events/<event> \
    --promote \
    --rebuild
```

This command:

1. Promotes the selected reference.
2. Records the selection metadata.
3. Reanalyzes every uploaded run.
4. Regenerates all report Markdown and HTML.
5. Rewrites every summary JSON.
6. Regenerates `session_summary.md`.

After rebuilding, every report within the event is based on the same reference lap.

---

### Reference Selection Metadata

Each promotion records the decision in:

```
reference_selection.json
```

Example:

```json
{
  "run": "lap4",
  "selection_rule": "fastest_clean",
  "duration_s": 27.488
}
```

This provides a reproducible audit trail for the event.

## Typical Administrative Workflow

### During an Event

1. Create the event.

```bash
./prep_event
```

2. Walk the course and update `segments.yaml`.

3. Upload RaceChrono CSV files after each run.

4. Review Grid Reports between runs.

5. Continue collecting telemetry throughout the session.

---

### After the Session

1. Verify run classifications (`run_status.yaml`).

2. Select the optimal reference.

```bash
python3 -m racecoach.select_reference \
    --event events/<event>
```

3. Promote and rebuild.

```bash
python3 -m racecoach.select_reference \
    --event events/<event> \
    --promote \
    --rebuild
```

4. Review the regenerated Session Summary and Full Reports.

5. Archive the completed event.

## See Also

- REPORT_INTERPRETATION.md
- COACHING_PHILOSOPHY.md
- OPERATIONS.md
