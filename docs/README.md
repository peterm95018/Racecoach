RaceCoach Documentation

This directory contains the user, operational, architectural, coaching, and development documentation for RaceCoach.

If you are using RaceCoach at an event, begin with USER_GUIDE.md.

If you are maintaining, extending, or developing RaceCoach, use this page as the documentation index.

⸻

Applies to: reference-path-stable and later

Last major update: July 2026

⸻

Where Should I Start?

I want to…	Read
Use RaceCoach at an event	USER_GUIDE.md
Administer the server or manage events	OPERATIONS.md
Understand telemetry metrics	METRICS.md
Learn why RaceCoach made a recommendation	DIAGNOSIS_MODEL.md
Understand the software architecture	ARCHITECTURE.md
Continue development	TODO.md

⸻

User Documentation

USER_GUIDE.md

How to use RaceCoach during an autocross or track event.

OPERATIONS.md

System administration, event management, deployment, server configuration, and Drupal report publishing.

⸻

Event Resources

JUNE20_CHECKLIST.md

Event-day checklist and lessons learned.

course_maps/

Archived course maps, segment definitions, and planning notes.

⸻

Driver Coaching

COACHING_PHILOSOPHY.md

The driving principles and coaching philosophy used throughout RaceCoach.

DIAGNOSIS_MODEL.md

How telemetry is interpreted and converted into coaching recommendations.

REPORT_INTERPRETATION.md

How to read and understand Grid Reports, Full Reports, and coaching recommendations.

SEGMENT_TYPES.md

Recommended segmentation strategies for common autocross course elements.

⸻

Software Design

ARCHITECTURE.md

High-level software architecture and major components.

ARCHITECTURE_COMPLETE.md

Detailed implementation notes, module interactions, and internal design decisions.

METRICS.md

Definitions and explanations of telemetry metrics and calculations.

⸻

Development

BACKLOG.md

Long-term feature ideas and future enhancements.

TODO.md

Current development priorities and active tasks.

CHANGELOG.md

History of significant project changes.

DEVELOPMENT_LOG.md

Chronological development notes and implementation history.

CHECKPOINT.md

Stable milestones, recovery points, and notable project states.

KNOWN_ISSUES.md

Current bugs, limitations, and documented workarounds.

⸻

Reports

RaceCoach currently generates three primary reports:

* Grid Report — A concise, between-run coaching report designed to be read in under 30 seconds while waiting on grid.
* Full Report — A detailed run comparison including telemetry analysis, opportunities, and coaching recommendations.
* Session Summary (under development) — An end-of-session report that identifies recurring strengths, weaknesses, and overall driver trends across multiple runs.