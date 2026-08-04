# RaceCoach Command-Line Interface

## Purpose

The RaceCoach command-line interface (CLI) provides the primary user interface for operating RaceCoach from the terminal.

Rather than invoking individual Python modules directly, users should use the `racecoach` executable (or the optional `rc` shell alias). The CLI provides a stable interface while allowing the underlying implementation to evolve.

The CLI is the supported interface to RaceCoach. Python modules remain individually executable for development and testing, but users should prefer the CLI for normal operation.

---

# Installation

## Installing the CLI

```bash
pip install -e .
```

## Optional Shell Alias

```bash
alias rc='racecoach'
```

Examples in this document use the shorter `rc` alias.

---

# Command Overview

| Command | Purpose |
|---------|---------|
| `rc status` | Display the current event status |
| `rc reference` | Preview the selected reference lap |
| `rc summary` | Regenerate the session summary |
| `rc finalize` | Promote the reference and rebuild the event |

Future commands:

- `rc publish`
- `rc doctor`
- `rc validate`
- `rc prep`
- `rc event`
- `rc today`

---

# Common Workflows

## Check Event Status

```bash
rc status
```

Displays:

- active event
- analyzed runs
- reference information
- report availability
- upload status

---

## Preview Reference Selection

```bash
rc reference
```

Displays the run that would become the reference without modifying the event.

---

## Finalize an Event

```bash
rc finalize
```

Performs:

1. Select reference
2. Promote `reference.csv`
3. Write `reference_selection.json`
4. Rebuild all reports
5. Regenerate session summary

---

## Regenerate Session Summary

```bash
rc summary
```

Useful after changing run classifications.

---

# Event-Day Workflow

Typical event sequence:

```
Morning
    ↓
Upload Runs
    ↓
Review Grid Reports
    ↓
Lunch
    ↓
rc reference
    ↓
rc finalize
    ↓
Continue Driving
    ↓
End of Event
```

---

# Command Reference

## rc status

Purpose

Options

Output

Examples

---

## rc reference

Purpose

Options

Examples

---

## rc summary

Purpose

Examples

---

## rc finalize

Purpose

Examples

---

# Design Philosophy

The CLI intentionally hides implementation details.

Users should interact with:

```
racecoach
```

rather than:

```
python -m racecoach.select_reference
python -m racecoach.session_summary
python -m racecoach.analyze_run
```

The CLI is considered the stable public interface.

---

# Future Commands

Potential additions include:

- `rc publish`
- `rc doctor`
- `rc validate`
- `rc prep`
- `rc event`
- `rc today`
- `rc review`

---

# Related Documentation

- OPERATIONS.md
- ARCHITECTURE.md
- USER_GUIDE.md