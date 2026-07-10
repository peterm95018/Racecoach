# RaceCoach Operations Guide

Applies to RaceCoach:
reference-path-stable and later

Last major update:
July 2026

## Purpose

This document describes how RaceCoach is deployed, configured, and maintained.

It is intended for system administration rather than driver coaching. For using RaceCoach during an event, see USER_GUIDE.md.

⸻

Managing Events

Create a New Event

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

⸻

Switch to an Existing Event

Run:

./set_active_event EVENT_NAME

Example:

./set_active_event gglc_2026-06-20

This command:

* Updates active_event.txt.
* Updates the Drupal current report symlinks.
* Verifies that the selected event exists.
* Displays the public report URLs.

⸻

Interactive Event Selection

Run:

./set_active_event

RaceCoach displays a numbered list of available events and prompts you to choose one.

⸻

Active Event

The currently selected event is stored in:

active_event.txt

Verify the active event:

cat active_event.txt

⸻

Event Directory Structure

Each event contains the following directories:

events/
└── gglc_2026-06-20/
    ├── uploads/
    ├── reports/
    └── segments.yaml

* uploads/ — RaceChrono CSV exports.
* reports/ — Generated Grid Reports, Full Reports, HTML, Markdown, and summary files.
* segments.yaml — Event-specific segment definitions.

⸻

Drupal Report Publishing

The Ubuntu server publishes the active event using symbolic links located at:

/var/www/html/drupal10/web/sites/default/files/racecoach/events/current/

The following files are linked:

* grid_report.html
* grid_report.md
* latest_report.html
* latest_report.md

These links always point to the reports for the currently active event.

⸻

Public Report URLs

Grid Report:

https://petermcmillan.com/sites/default/files/racecoach/events/current/grid_report.html

Latest Report:

https://petermcmillan.com/sites/default/files/racecoach/events/current/latest_report.html

⸻

Working on Multiple Computers

Development Computer (Mac)

set_active_event updates only:

active_event.txt

Because Drupal is not installed, the script skips the symbolic-link update and reminds you to run the same command on the Ubuntu server after pulling the latest changes.

⸻

Ubuntu Server

set_active_event updates both:

* active_event.txt
* Drupal current symbolic links

This immediately changes the reports served through Drupal.

⸻

Upload Processing

RaceCoach watches each event’s uploads/ directory for new RaceChrono CSV files.

When a new CSV is detected, the processing pipeline:

1. Imports the telemetry.
2. Selects or updates the reference lap as needed.
3. Runs the analysis.
4. Generates the Full Report.
5. Generates the Grid Report.
6. Updates the Drupal current links.

⸻

Troubleshooting

Empty Report

Usually indicates that no valid reference lap has been established.

Verify:

* A reference lap exists.
* The CSV imported successfully.
* The analysis completed without errors.

⸻

Drupal Shows an Old Report

Run:

./set_active_event EVENT_NAME

Verify the symbolic links:

ls -l /var/www/html/drupal10/web/sites/default/files/racecoach/events/current

⸻

Uploads Are Not Processed

Verify:

* The upload watcher is running.
* New CSV files are appearing in the event’s uploads/ directory.
* File permissions allow the watcher to read the uploads.

⸻

Watcher Does Not Trigger

The watcher responds only to newly created files.

If a CSV existed before the watcher started, re-copy or re-export the file to trigger processing.

⸻

Report Generation Errors

If report generation fails:

* Verify all scripts are from the same Git branch.
* Confirm prep_event and set_active_event are current.
* Check the console output for Python exceptions or missing telemetry channels.

⸻

Typical Administrative Workflow

New Event

./prep_event

* Create the event.
* Walk the course.
* Update segments.yaml.
* Begin collecting telemetry.

⸻

Review a Previous Event

./set_active_event gglc_2026-06-20

* Switch the active event.
* Verify the public report URLs.
* Review historical Grid and Full Reports.

⸻

Related Documentation

* USER_GUIDE.md — Driver workflow and report interpretation.
* ARCHITECTURE.md — Software architecture.
* METRICS.md — Telemetry metric definitions.
* REPORT_INTERPRETATION.md — Detailed explanation of report content.
* DEVELOPMENT_LOG.md — Development history and implementation notes.


Upload Watcher

RaceCoach uses a user-level systemd service to monitor the active event’s upload directory.

The service is installed or refreshed by:

./install_service.sh

When a new event is created using prep_event, the watcher is reconfigured to monitor the new event’s uploads/ directory.

When a new RaceChrono CSV is detected, the watcher:

1. Imports the telemetry.
2. Creates the reference lap if necessary.
3. Runs the analysis.
4. Generates the Grid Report and Full Report.
5. Archives the processed CSV.
6. Updates the public Drupal reports.

## See Also

- REPORT_INTERPRETATION.md
- COACHING_PHILOSOPHY.md
- OPERATIONS.md