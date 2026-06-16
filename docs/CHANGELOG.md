2026-06-15 — Upload Watcher Reliability Improvements

Problem

RaceCoach event preparation had evolved to use active_event.txt, but the upload watcher service was still configured using a fixed event path created when the service was originally installed.

As a result:

* The watcher could continue monitoring an old event directory.
* Running prep_event did not automatically reconfigure the watcher.
* Upload processing depended on manual service updates.
* The watcher had drifted from the current write_report() API and could no longer generate reports.

Changes

Upload watcher service now follows active event

Updated install_service.sh to:

* Read active_event.txt
* Resolve the current event directory
* Generate a watcher service that targets:
    * uploads
    * processed
    * reports
    * event configuration

The generated service now points to the currently active event rather than a hardcoded sample event.

Event preparation now reconfigures watcher automatically

Updated prep_event to:

* Create event directories
* Update active_event.txt
* Rebuild and restart the upload watcher service automatically

This removes a manual step from event-day workflow.

Fixed watcher/report API mismatch

watch_uploads.py was updated to match the current write_report() function signature.

The watcher now successfully:

* Detects new CSV uploads
* Runs analysis
* Generates reports
* Moves processed files into the processed directory

Validation

End-to-end workflow successfully tested:

prep_event
→ watcher reconfigured
→ CSV upload detected
→ analysis executed
→ reports generated
→ CSV archived to processed directory

Operational Impact

RaceCoach now supports event switching without manual service edits.

Current workflow:

prep_event
→ FTP upload
→ automatic analysis
→ automatic report generation
→ Drupal report publication

This significantly reduces event-day operational risk.

Tag: event-workflow-ready-v1

Verified:

- prep_event updates active event
- watcher auto-reconfigures
- first upload creates reference.csv
- uploads remain available for later comparisons
- reports generate automatically
- Drupal report updates correctly
- watcher survives service restart

Validated: 2026-06-16