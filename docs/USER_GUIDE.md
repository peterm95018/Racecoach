RaceCoach User Guide

Purpose

RaceCoach compares a run against a reference lap and identifies the biggest opportunities to reduce time.

The report is designed to answer one question:

What should I do differently on the next run?

⸻

Event Workflow

1. Complete a run

Record telemetry using:

* RaceChrono Pro
* RaceBox GPS
* OBDLink (optional)
* GoPro (optional)

2. Export CSV

From RaceChrono:

* Open the run
* Export CSV
* Share to FTP Manager

3. Upload

Upload the CSV to the RaceCoach Ubuntu server.

RaceCoach automatically:

* Detects the upload
* Runs analysis
* Updates the latest report

4. View Report

Open:

https://petermcmillan.com/sites/default/files/racecoach/events/current/latest_report.html

⸻

Understanding the Report

Run Summary

Highlights:

* Biggest gain
* Biggest loss
* Key speed differences

Next Run Focus

The most important section.

Read this before your next run.

Example:

1. Middle course: pick up throttle earlier
2. Protect exit speed
3. Repeat what worked in Finish section

Segment Time vs Reference Lap

Shows where time was gained or lost compared to the reference lap.

Example:

* Middle course: +0.73s
* Finish section: -1.45s

Positive values are slower.

Negative values are faster.

Top Opportunities

Explains why time was lost.

Typical causes:

* Over-driving entry
* Late throttle commitment
* Weak exit speed
* Overslowing
* Excess coasting

Segment Table

Quick comparison of all segments.

Columns:

* Δ Time = time difference vs reference
* Min Δ = minimum speed difference
* Exit Δ = exit speed difference
* Rec+1 = recovery gain 1 second after minimum speed (experimental)
* Rec+2 = recovery gain 2 seconds after minimum speed (experimental)
* Notes = key observations

⸻

Key Metrics

Exit Speed

Most important metric in autocross.

Higher exit speed usually produces lower segment times.

Throttle Commitment

Measures how long after minimum speed the throttle is reapplied.

Smaller values are generally better.

Minimum Speed

Useful diagnostic.

Higher minimum speed is not always faster.

A higher minimum speed combined with a lower exit speed usually indicates over-driving the entry.

⸻

Driver Guidelines

When Exit Speed Is Down

Focus on:

* Earlier vision
* Earlier rotation
* Earlier throttle commitment

When Minimum Speed Is Too Low

Focus on:

* Less braking
* Earlier brake release
* Smoother rotation

When Throttle Commitment Is Late

Focus on:

* Finishing rotation sooner
* Committing to throttle earlier

When A Segment Shows A Gain

Repeat the technique.

Protect gains before searching for new speed.

⸻

Current Limitations

* Recovery metrics are experimental.
* Segment boundaries are event-specific.
* Reference-path segmentation is not yet active.
* Coaching quality depends on telemetry quality.

⸻

Support Documents

* ARCHITECTURE.md — engineering details
* Event segment definitions
* RaceChrono setup documentation
