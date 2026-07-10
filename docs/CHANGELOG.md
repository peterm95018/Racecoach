# RaceCoach Changelog

This document records major milestones and stable recovery points for the RaceCoach project.

---

# 2026-06-16 — Event Workflow Ready

**Tag:** `event-workflow-ready-v1`

## Problem

RaceCoach event preparation had evolved to use `active_event.txt`, but the upload watcher service was still configured using a fixed event path created when the service was originally installed.

As a result:

- The watcher could continue monitoring an old event directory.
- Running `prep_event` did not automatically reconfigure the watcher.
- Upload processing depended on manual service updates.
- The watcher had drifted from the current `write_report()` API.

## Changes

### Upload watcher follows active event

- `install_service.sh` now reads `active_event.txt`.
- The generated service targets the active event automatically.
- Hard-coded event paths were removed.

### Event preparation reconfigures the watcher

`prep_event` now:

- Creates event directories.
- Updates `active_event.txt`.
- Rebuilds the upload watcher.
- Restarts the watcher automatically.

### Upload processing fixed

`watch_uploads.py` was updated to match the current reporting API.

The watcher now:

- Detects uploads.
- Runs analysis.
- Generates reports.
- Archives processed CSV files.

## Validation

Successfully verified:

- `prep_event`
- watcher restart
- upload detection
- automatic analysis
- report generation
- Drupal publication
- processed archive creation

## Outcome

RaceCoach now supports event switching without manual service edits.

---

# 2026-06-17 — Previous Run Comparison

**Tag:** `previous-run-comparison-v1`

## Added

- Compare against previous run.
- Compare against any selected run.
- Existing reference-lap workflow preserved.

---

# 2026-06-24 — Stable Reference Path Segmentation

**Tag:** `reference-path-stable`

## Added

- Five named course segments.
- Reference-path segmentation mode.
- Stable named segment reporting.
- Environment-controlled segment debug logging.

## Changed

- Production reference positioning now uses normalized/scaled lap distance.
- Grid reports suppress low-confidence coaching recommendations.

## Fixed

- Eliminated false multi-second segment losses caused by GPS projection jumps.
- Prevented empty or collapsed segments on overlapping autocross layouts.
- Restored stable coaching output for production use.

## Deferred

Future GPS projection work remains planned:

- Heading-aware nearest-point matching.
- Forward-only search window.
- Robust handling of overlapping course sections.
- Turnaround validation.
- Replacement of normalized distance with true GPS projection after validation.

---

# Recovery Tags

| Tag | Purpose |
|------|---------|
| `event-workflow-ready-v1` | Stable event preparation and upload automation |
| `previous-run-comparison-v1` | Previous-run comparison workflow |
| `reference-path-stable` | Stable named-segment reference path baseline |

## See Also

- REPORT_INTERPRETATION.md
- COACHING_PHILOSOPHY.md
- OPERATIONS.md