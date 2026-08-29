from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from racecoach.event_reflection import load_event_reflection

from racecoach.coaching_themes import load_coaching_themes

from racecoach.preparation import build_preparation_brief

from racecoach.run_status import (
    VALID_RUN_STATUSES,
    set_run_status,
)

from racecoach.select_reference import (
    load_candidates,
    rebuild_event,
    reconcile_live_reference,
)

from racecoach.timing_config import load_event_timing

from racecoach.clokkr import fetch_driver_result


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_event(event_arg: Path | None) -> Path:
    if event_arg is not None:
        event_dir = event_arg
    else:
        active_event_file = Path("active_event.txt")

        if not active_event_file.exists():
            raise SystemExit(
                "No event specified and active_event.txt was not found. "
                "Use --event events/<event-name>."
            )

        active_event = active_event_file.read_text(
            encoding="utf-8"
        ).strip()

        if not active_event:
            raise SystemExit("active_event.txt is empty")

        event_dir = Path("events") / active_event

    if not event_dir.exists():
        raise SystemExit(f"Event directory not found: {event_dir}")

    return event_dir


def status_command(event_dir: Path) -> None:
    reports_dir = event_dir / "reports"
    uploads_dir = event_dir / "uploads"
    reference_metadata = event_dir / "reference_selection.json"

    uploads = sorted(
        uploads_dir.glob("*.csv"),
        key=lambda path: path.stat().st_mtime,
    )
    summaries = sorted(reports_dir.glob("*_summary.json"))

    status_counts = {
        "clean": 0,
        "cone": 0,
        "dnf": 0,
        "off_course": 0,
        "unknown": 0,
    }

    for summary_path in summaries:
        try:
            data = json.loads(
                summary_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            status_counts["unknown"] += 1
            continue

        run = data.get("run") or {}
        status = str(run.get("status", "unknown")).lower()

        if status not in status_counts:
            status = "unknown"

        status_counts[status] += 1

    latest_upload = uploads[-1].name if uploads else None

    print("RaceCoach Status")
    print()
    print(f"Event: {event_dir.name}")
    print(
        f"Runs: {len(uploads)} uploaded / "
        f"{len(summaries)} analyzed"
    )

    classified_parts = []

    for status in ("clean", "cone", "dnf", "off_course", "unknown"):
        count = status_counts[status]

        if count:
            label = status.replace("_", " ")
            classified_parts.append(f"{count} {label}")

    print(
        "Status: "
        + (", ".join(classified_parts) if classified_parts else "none")
    )

    if reference_metadata.exists():
        try:
            data = json.loads(
                reference_metadata.read_text(encoding="utf-8")
            )
            run_name = data.get("run", "unknown")
            duration = data.get("duration_s")
            rule = data.get("selection_rule", "unknown")

            if isinstance(duration, (int, float)):
                print(
                    f"Reference: {run_name} — "
                    f"{duration:.3f}s ({rule})"
                )
            else:
                print(f"Reference: {run_name} ({rule})")
        except (OSError, json.JSONDecodeError):
            print("Reference: metadata unreadable")
    elif (event_dir / "reference.csv").exists():
        print("Reference: reference.csv (metadata unavailable)")
    else:
        print("Reference: not established")

    print(
        "Latest upload: "
        + (latest_upload if latest_upload else "none")
    )

    latest_report = reports_dir / "latest_report.md"
    grid_report = reports_dir / "grid_report.md"
    session_summary = reports_dir / "session_summary.md"

    print()
    print("Reports:")
    print(
        "  Latest: "
        + ("OK" if latest_report.exists() else "MISSING")
    )
    print(
        "  Grid: "
        + ("OK" if grid_report.exists() else "MISSING")
    )
    print(
        "  Session summary: "
        + ("OK" if session_summary.exists() else "MISSING")
    )

    problems = []

    if len(uploads) != len(summaries):
        problems.append(
            f"{len(uploads) - len(summaries):+d} upload/summary difference"
        )

    if not (event_dir / "reference.csv").exists():
        problems.append("reference.csv missing")

    if not latest_report.exists():
        problems.append("latest report missing")

    if not grid_report.exists():
        problems.append("grid report missing")

    print()
    print(
        "Health: "
        + ("OK" if not problems else "; ".join(problems))
    )


def finalize_command(event_dir: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "racecoach.select_reference",
            "--event",
            str(event_dir),
            "--promote",
            "--rebuild",
        ],
        check=True,
    )


def reference_command(
    event_dir: Path,
    promote: bool,
    rebuild: bool,
) -> None:
    command = [
        sys.executable,
        "-m",
        "racecoach.select_reference",
        "--event",
        str(event_dir),
    ]

    if promote:
        command.append("--promote")

    if rebuild:
        command.append("--rebuild")

    subprocess.run(command, check=True)

def read_optional_file(path: Path) -> bytes | None:
    if not path.exists():
        return None

    return path.read_bytes()


def restore_optional_file(
    path: Path,
    previous_contents: bytes | None,
) -> None:
    if previous_contents is None:
        path.unlink(missing_ok=True)
        return

    path.write_bytes(previous_contents)

def classify_command(
    event_dir: Path,
    run_name: str,
    status: str,
    *,
    reprocess: bool = True,
) -> None:
    normalized_run_name = str(run_name).strip()

    if not reprocess:
        status_path = set_run_status(
            event_dir,
            normalized_run_name,
            status,
        )
        print(
            f"Classified {normalized_run_name} as "
            f"{status.strip().lower()}."
        )
        print(f"Updated: {status_path}")
        print("Reprocessing skipped.")
        return

    existing_candidates = load_candidates(event_dir)

    if not any(
        candidate.run_name == normalized_run_name
        for candidate in existing_candidates
    ):
        raise ValueError(
            f"{normalized_run_name}: no analyzed run was found; "
            "use --no-reprocess to classify it before upload"
        )

    status_path = event_dir / "run_status.yaml"
    reference_path = event_dir / "reference.csv"
    metadata_path = event_dir / "reference_selection.json"

    previous_files = {
        status_path: read_optional_file(status_path),
        reference_path: read_optional_file(reference_path),
        metadata_path: read_optional_file(metadata_path),
    }

    try:
        set_run_status(
            event_dir,
            normalized_run_name,
            status,
        )

        candidates = load_candidates(event_dir)
        selected, reference_changed = (
            reconcile_live_reference(
                event_dir,
                candidates,
            )
        )

        rebuild_reference = (
            reference_path if reference_path.exists() else None
        )

        rebuild_event(
            event_dir,
            rebuild_reference,
        )

    except Exception:
        for path, previous_contents in previous_files.items():
            restore_optional_file(
                path,
                previous_contents,
            )

        print(
            "Classification and reference update rolled back "
            "after rebuild failure."
        )
        raise

    print(
        f"Classified {normalized_run_name} as "
        f"{status.strip().lower()}."
    )
    print(f"Updated: {status_path}")

    if selected is None:
        print("No eligible live reference is available.")
    else:
        print(
            f"Live reference: {selected.run_name} "
            f"({selected.duration_s:.3f}s)"
        )

    if reference_changed:
        print("Reference selection changed.")

    publish_command(event_dir)
    print("Event reports rebuilt and published.")


def summary_command(event_dir: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "racecoach.session_summary",
            "--event",
            str(event_dir),
        ],
        check=True,
    )


def publish_command(event_dir: Path) -> None:
    project_dir = Path(__file__).resolve().parent.parent
    publish_script = project_dir / "publish_reports.sh"

    if not publish_script.exists():
        raise SystemExit(
            f"Publishing script not found: {publish_script}"
        )

    subprocess.run(
    [
        "bash",
        str(publish_script),
        str(event_dir),
    ],
    cwd=project_dir,
    check=True,
)

def reflection_command(event_dir: Path) -> None:
    reflection = load_event_reflection(event_dir)

    print("RaceCoach Event Reflection")
    print()
    print("Event")
    print("-----")
    print(event_dir.name)

    if reflection is None:
        print()
        print("No event_reflection.yaml found.")
        return

    print()
    print("Preparation")
    print("-----------")

    preparation = reflection.get("preparation") or {}

    if preparation:
        for key, value in preparation.items():
            label = key.replace("_", " ")

            if isinstance(value, bool):
                display = "yes" if value else "no"
            else:
                display = str(value)

            print(f"{label}: {display}")
    else:
        print("No preparation observations recorded.")

    print()
    print("Performance")
    print("-----------")

    performance = reflection.get("performance") or {}

    if performance:
        for key, value in performance.items():
            label = key.replace("_", " ")
            print(f"{label}: {value}")
    else:
        print("No performance observations recorded.")

    print()
    print("Observations")
    print("------------")

    observations = reflection.get("observations") or []

    if observations:
        for observation in observations:
            print(f"- {observation}")
    else:
        print("No observations recorded.")

    print()
    print("Breakthrough")
    print("------------")

    breakthrough = reflection.get("breakthrough")

    if breakthrough:
        print(breakthrough)
    else:
        print("No breakthrough recorded.")

def prepare_command() -> None:
    brief = build_preparation_brief(project_root())

    print("RaceCoach Preparation Brief")
    print()

    primary = brief.get("primary_theme")
    secondary = brief.get("secondary_theme")

    print("Primary Focus")
    print("-------------")

    if primary:
        print(primary.get("name", "Unnamed theme"))

        practice = primary.get("practice_objective")
        if practice:
            print(f"Practice: {practice}")

        cue = primary.get("reinforcement_cue")
        if cue:
            print(f"Cue: {cue}")
    else:
        print("No primary coaching theme established.")

    print()
    print("Secondary Focus")
    print("---------------")

    if secondary:
        print(secondary.get("name", "Unnamed theme"))

        cue = secondary.get("reinforcement_cue")
        if cue:
            print(f"Cue: {cue}")
    else:
        print("None")

    reflection_event = brief.get("reflection_event")

    print()
    print("What Helped Previously")
    print("----------------------")

    if reflection_event:
        print(f"From: {reflection_event}")

        observations = brief.get("observations") or []

        if observations:
            for observation in observations:
                print(f"- {observation}")

        breakthrough = brief.get("breakthrough")

        if breakthrough:
            print()
            print(f"Breakthrough: {breakthrough}")
    else:
        print("No prior event reflection available.")

    preparation = brief.get("preparation") or {}

    print()
    print("Preparation Reminders")
    print("---------------------")

    enabled = [
        key.replace("_", " ")
        for key, value in preparation.items()
        if value is True
    ]

    if enabled:
        for reminder in enabled:
            print(f"- {reminder}")
    else:
        print("No preparation observations available.")

    print()
    print("One Thing")
    print("---------")

    if primary and primary.get("reinforcement_cue"):
        print(primary["reinforcement_cue"])
    elif primary:
        print(primary.get("name", "Primary coaching theme"))
    else:
        print("Arrive focused and establish one coaching objective.")


def themes_command() -> None:
    project_dir = project_root()
    themes = load_coaching_themes(project_dir)

    print("RaceCoach Coaching Themes")
    print()

    if themes is None:
        print("No driver/coaching_themes.yaml found.")
        return

    def show_theme(label: str, theme: dict | None) -> None:
        print(label)
        print("-" * len(label))

        if not theme:
            print("None")
            print()
            return

        print(theme.get("name", "Unnamed theme"))

        status = theme.get("status")
        if status:
            print(f"Status: {status}")

        priority = theme.get("priority")
        if priority is not None:
            print(f"Priority: {priority}")

        started = theme.get("started")
        if started:
            print(f"Started: {started}")

        practice = theme.get("practice_objective")
        if practice:
            print(f"Practice: {practice}")

        cue = theme.get("reinforcement_cue")
        if cue:
            print(f"Cue: {cue}")

        notes = theme.get("notes")
        if notes:
            print(f"Notes: {notes}")

        print()

    show_theme("Primary", themes.get("primary"))
    show_theme("Secondary", themes.get("secondary"))

    print("Completed")
    print("---------")

    completed = themes.get("completed") or []

    if completed:
        for theme in completed:
            if isinstance(theme, dict):
                name = theme.get("name", "Unnamed theme")
                completed_date = theme.get("completed")

                if completed_date:
                    print(f"- {name} ({completed_date})")
                else:
                    print(f"- {name}")
            else:
                print(f"- {theme}")
    else:
        print("None")

    print()
    print("Future Candidates")
    print("-----------------")

    candidates = themes.get("future_candidates") or []

    if candidates:
        for candidate in candidates:
            print(f"- {candidate}")
    else:
        print("None")


def timing_command(
    event_dir: Path,
    *,
    show_runs: bool = False,
) -> None:
    timing = load_event_timing(event_dir)

    print("RaceCoach Live Timing")
    print()

    if timing is None:
        print("No live-timing configuration is available.")
        return

    print(f"Organizer: {timing.organizer or 'unspecified'}")
    print(f"Profile: {timing.profile or 'event-specific'}")
    print(f"Provider: {timing.provider}")
    print(f"Driver number: {timing.driver_number}")
    print(f"Results: {timing.results_url}")

    if not show_runs:
        return

    if timing.provider != "clokkr":
        raise ValueError(
            f"Live results are not supported for "
            f"provider {timing.provider!r}"
        )

    result = fetch_driver_result(
        timing.results_url,
        timing.driver_number,
    )

    print()
    print(f"Car: {result.car_number}")
    print(f"Class: {result.car_class}")
    print(f"Vehicle: {result.car_name}")
    print()
    print("Run  Raw      Adjusted  Status")

    for run in result.runs:
        raw = (
            f"{run.time_s:.3f}"
            if run.time_s is not None
            else "-"
        )
        adjusted = (
            f"{run.adjusted_time_s:.3f}"
            if run.adjusted_time_s is not None
            else "-"
        )

        print(
            f"{run.index:<4} "
            f"{raw:<8} "
            f"{adjusted:<9} "
            f"{run.status}"
        )

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="racecoach",
        description="RaceCoach command-line interface",
    )

    parser.add_argument(
        "--event",
        type=Path,
        help=(
            "Event directory. If omitted, use the event named "
            "in active_event.txt."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "status",
        help="Show event and report status",
    )

    subparsers.add_parser(
        "publish",
        help="Publish the selected event's latest reports",
    )

    subparsers.add_parser(
        "doctor",
        help="Validate the RaceCoach installation and event",
    )

    subparsers.add_parser(
        "validate",
        help="Run RaceCoach regression validation",
    )

    reference_parser = subparsers.add_parser(
        "reference",
        help="Preview or promote the best reference run",
    )

    subparsers.add_parser(
        "today",
        help="Show the active event dashboard",
    )

    subparsers.add_parser(
        "reflection",
        help="Show the selected event's driver reflection",
    )

    reference_parser.add_argument(
        "--promote",
        action="store_true",
        help="Promote the selected run to reference.csv",
    )

    reference_parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the event after promotion",
    )

    classify_parser = subparsers.add_parser(
        "classify",
        help="Classify a run as clean, cone, DNF, or off-course",
    )

    classify_parser.add_argument(
        "run",
        help="Run name, for example lap2",
    )

    classify_parser.add_argument(
        "status",
        choices=sorted(VALID_RUN_STATUSES),
        help="Official run classification",
    )
    classify_parser.add_argument(
        "--no-reprocess",
        dest="reprocess",
        action="store_false",
        help=(
            "Only record the classification; do not rebuild or publish"
        ),
    )
    classify_parser.set_defaults(reprocess=True)

    subparsers.add_parser(
        "summary",
        help="Regenerate the session summary",
    )

    timing_parser = subparsers.add_parser(
        "timing",
        help="Show live-timing configuration and results",
    )

    timing_parser.add_argument(
        "--runs",
        dest="show_runs",
        action="store_true",
        help="Fetch and show runs for the configured driver",
    )

    subparsers.add_parser(
        "finalize",
        help=(
            "Promote the best reference and rebuild the entire event"
        ),
    )

    subparsers.add_parser(
        "themes",
        help="Show current driver coaching themes",
    )

    subparsers.add_parser(
        "prepare",
        help="Show a pre-event preparation brief",
    )


    return parser

def today_command(event_dir: Path) -> None:
    uploads_dir = event_dir / "uploads"
    reports_dir = event_dir / "reports"
    reference_metadata = event_dir / "reference_selection.json"
    session_summary = reports_dir / "session_summary.md"

    uploads = sorted(
        uploads_dir.glob("*.csv"),
        key=lambda path: path.stat().st_mtime,
    )
    summaries = sorted(reports_dir.glob("*_summary.json"))

    status_counts = {
        "clean": 0,
        "cone": 0,
        "dnf": 0,
        "off_course": 0,
        "unknown": 0,
    }

    for summary_path in summaries:
        try:
            data = json.loads(
                summary_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            status_counts["unknown"] += 1
            continue

        run = data.get("run") or {}
        status = str(run.get("status", "unknown")).lower()

        if status not in status_counts:
            status = "unknown"

        status_counts[status] += 1

    scorecard = {}

    if session_summary.exists():
        lines = session_summary.read_text(
            encoding="utf-8"
        ).splitlines()

        for line in lines:
            if line.startswith("- Best repeat:"):
                scorecard["best_repeat"] = line.removeprefix(
                    "- Best repeat:"
                ).strip().replace("**", "")
            elif line.startswith("- Clean-run percentage:"):
                scorecard["clean_percentage"] = line.removeprefix(
                    "- Clean-run percentage:"
                ).strip().replace("**", "")
            elif line.startswith("- Consistency interpretation:"):
                scorecard["focus"] = line.removeprefix(
                    "- Consistency interpretation:"
                ).strip().replace("**", "")

    print("RaceCoach Today")
    print()

    print("Event")
    print("-----")
    print(event_dir.name)
    print()

    print("Runs")
    print("----")
    print(
        f"{len(uploads)} uploaded / "
        f"{len(summaries)} analyzed"
    )

    classified_parts = []

    for status in ("clean", "cone", "dnf", "off_course", "unknown"):
        count = status_counts[status]

        if count:
            classified_parts.append(
                f"{count} {status.replace('_', ' ')}"
            )

    print(
        ", ".join(classified_parts)
        if classified_parts
        else "No classified runs"
    )
    print()

    print("Reference")
    print("---------")

    if reference_metadata.exists():
        try:
            metadata = json.loads(
                reference_metadata.read_text(encoding="utf-8")
            )
            run_name = metadata.get("run", "unknown")
            duration = metadata.get("duration_s")
            rule = metadata.get("selection_rule", "unknown")

            if isinstance(duration, (int, float)):
                print(f"{run_name} — {duration:.3f}s")
            else:
                print(run_name)

            print(rule)
        except (OSError, json.JSONDecodeError):
            print("Metadata unreadable")
    elif (event_dir / "reference.csv").exists():
        print("reference.csv")
        print("Selection metadata unavailable")
    else:
        print("Not established")

    print()
    print("Consistency")
    print("-----------")
    print(
        "Best repeat: "
        + scorecard.get("best_repeat", "Not available")
    )
    print(
        "Clean runs: "
        + scorecard.get("clean_percentage", "Not available")
    )

    print()
    print("Current Focus")
    print("-------------")
    print(
        scorecard.get(
            "focus",
            "No session-level coaching focus available.",
        )
    )

    latest_report = reports_dir / "latest_report.md"
    grid_report = reports_dir / "grid_report.md"

    print()
    print("Reports")
    print("-------")
    print(
        "Latest: "
        + ("OK" if latest_report.exists() else "MISSING")
    )
    print(
        "Grid: "
        + ("OK" if grid_report.exists() else "MISSING")
    )
    print(
        "Session summary: "
        + ("OK" if session_summary.exists() else "MISSING")
    )

    problems = []

    if len(uploads) != len(summaries):
        problems.append("upload/summary mismatch")

    if not (event_dir / "reference.csv").exists():
        problems.append("reference missing")

    if not latest_report.exists():
        problems.append("latest report missing")

    if not grid_report.exists():
        problems.append("grid report missing")

    print()
    print("Health")
    print("------")
    print("OK" if not problems else "; ".join(problems))


def run_module(*args: str) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            *args,
        ],
        check=True,
    )


def doctor_command(event_dir: Path) -> None:
    print("RaceCoach Doctor")
    print()

    failures: list[str] = []
    warnings: list[str] = []

    def pass_check(label: str) -> None:
        print(f"✓ {label}")

    def fail_check(label: str) -> None:
        print(f"✗ {label}")
        failures.append(label)

    def warn_check(label: str) -> None:
        print(f"⚠ {label}")
        warnings.append(label)

    def skip_check(label: str) -> None:
        print(f"○ {label}")

    project_dir = project_root()
    uploads_dir = event_dir / "uploads"
    reports_dir = event_dir / "reports"
    reference_path = event_dir / "reference.csv"
    reference_metadata = event_dir / "reference_selection.json"

    print("Environment")
    print("-----------")

    pass_check(
        f"Python "
        f"{sys.version_info.major}."
        f"{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )

    if sys.prefix != sys.base_prefix:
        pass_check("Virtual environment active")
    else:
        warn_check("Virtual environment not active")

    if project_dir.exists():
        pass_check(f"Project root: {project_dir}")
    else:
        fail_check(f"Project root missing: {project_dir}")

    publish_script = project_dir / "publish_reports.sh"

    if publish_script.exists():
        pass_check("publish_reports.sh")
    else:
        fail_check("publish_reports.sh missing")

    print()
    print("Event")
    print("-----")

    if event_dir.exists():
        pass_check(f"Event directory: {event_dir.name}")
    else:
        fail_check(f"Event directory missing: {event_dir}")

    if uploads_dir.is_dir():
        pass_check("uploads/")
    else:
        fail_check("uploads/ missing")

    if reports_dir.is_dir():
        pass_check("reports/")
    else:
        fail_check("reports/ missing")

    segments_path = event_dir / "segments.yaml"

    if segments_path.exists():
        pass_check("segments.yaml")
    else:
        fail_check("segments.yaml missing")

    uploads = (
        sorted(uploads_dir.glob("*.csv"))
        if uploads_dir.is_dir()
        else []
    )
    summaries = (
        sorted(reports_dir.glob("*_summary.json"))
        if reports_dir.is_dir()
        else []
    )

    print()
    print("Reference")
    print("---------")

    if reference_path.exists():
        pass_check("reference.csv")
    elif uploads or summaries:
        fail_check("reference.csv missing")
    else:
        warn_check("reference.csv not established yet")

    if reference_metadata.exists():
        try:
            metadata = json.loads(
                reference_metadata.read_text(encoding="utf-8")
            )
            source = metadata.get("source")

            pass_check("reference_selection.json readable")

            if source and (uploads_dir / source).exists():
                pass_check("Reference source CSV exists")
            elif source:
                fail_check("Reference source CSV missing")
            else:
                fail_check("Reference metadata missing source")
        except (OSError, json.JSONDecodeError):
            fail_check("reference_selection.json unreadable")
    elif uploads or summaries:
        warn_check("reference_selection.json missing")
    else:
        skip_check("reference selection metadata not expected yet")

    print()
    print("Reports")
    print("-------")

    latest_report = reports_dir / "latest_report.md"
    grid_report = reports_dir / "grid_report.md"
    session_summary = reports_dir / "session_summary.md"

    if latest_report.exists():
        pass_check("latest_report.md")
    elif summaries:
        warn_check("latest_report.md missing")
    else:
        skip_check("latest report not expected yet")

    if grid_report.exists():
        pass_check("grid_report.md")
    elif summaries:
        warn_check("grid_report.md missing")
    else:
        skip_check("grid report not expected yet")

    if session_summary.exists():
        pass_check("session_summary.md")
    elif summaries:
        warn_check("session_summary.md missing")
    else:
        skip_check("session summary not expected yet")

    print()
    print("Consistency")
    print("-----------")

    if not uploads and not summaries:
        skip_check("No uploaded or analyzed runs yet")
    elif len(uploads) == len(summaries):
        pass_check(
            f"Uploads and summaries match "
            f"({len(uploads)} run(s))"
        )
    else:
        difference = len(uploads) - len(summaries)
        fail_check(
            f"Uploads and summaries differ "
            f"({len(uploads)} uploaded / "
            f"{len(summaries)} analyzed; "
            f"{difference:+d} difference)"
        )

    unreadable_summaries = []

    for summary_path in summaries:
        try:
            json.loads(
                summary_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            unreadable_summaries.append(summary_path.name)

    if unreadable_summaries:
        fail_check(
            f"Unreadable summary JSON "
            f"({len(unreadable_summaries)} file(s))"
        )
    elif summaries:
        pass_check(
            f"Summary JSON readable "
            f"({len(summaries)} file(s))"
        )

    print()
    print("Services")
    print("--------")

    if sys.platform.startswith("linux"):
        service_result = subprocess.run(
            [
                "systemctl",
                "--user",
                "is-active",
                "racecoach-watch.service",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        service_status = service_result.stdout.strip()

        if service_result.returncode == 0:
            pass_check(
                f"Watcher service active "
                f"({service_status or 'active'})"
            )
        else:
            fail_check(
                f"RaceCoach upload watcher inactive  "
                f"({service_status or 'unknown'})"
            )

        drupal_parent = Path(
            "/var/www/html/drupal10/web/sites/default/files/"
            "racecoach/events"
        )

        if drupal_parent.is_dir():
            pass_check("Drupal publishing destination available")
        else:
            warn_check("Drupal publishing destination unavailable")
    else:
        skip_check("Watcher service check skipped on macOS")
        skip_check("Drupal publishing check skipped on macOS")

    print()
    print("Result")
    print("------")

    if failures:
        print(
            f"FAIL — {len(failures)} failure(s), "
            f"{len(warnings)} warning(s)"
        )
        raise SystemExit(1)

    if warnings:
        print(f"WARN — {len(warnings)} warning(s)")
        return

    print("PASS — no problems found")


def validate_command() -> None:
    project_dir = project_root()

    print("RaceCoach Validation")
    print()

    failures: list[str] = []

    def pass_check(label: str) -> None:
        print(f"✓ {label}")

    def fail_check(label: str) -> None:
        print(f"✗ {label}")
        failures.append(label)

    print("Static Checks")
    print("-------------")

    compile_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "py_compile",
            str(project_dir / "racecoach" / "analyze_run.py"),
        ],
        cwd=project_dir,
        check=False,
    )

    if compile_result.returncode == 0:
        pass_check("analyze_run.py compiles")
    else:
        fail_check("analyze_run.py compile failed")

    print()
    print("Automated Regression")
    print("--------------------")

    test_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-v",
        ],
        cwd=project_dir,
        check=False,
    )

    if test_result.returncode == 0:
        pass_check("Regression test suite")
    else:
        fail_check("Regression test suite")

    print()
    print("Historical Corpus")
    print("-----------------")

    historical_dir = (
        project_dir / "tests" / "fixtures" / "historical"
    )

    historical_fixtures = sorted(
        historical_dir.glob("*.json")
    )

    if historical_fixtures:
        pass_check(
            f"{len(historical_fixtures)} historical fixture(s)"
        )
    else:
        fail_check("No historical fixtures found")

    print()
    print("Result")
    print("------")

    if failures:
        print(
            f"FAIL — {len(failures)} validation failure(s)"
        )
        raise SystemExit(1)

    print("PASS — validation complete")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if (
        args.command == "reference"
        and args.rebuild
        and not args.promote
    ):
        parser.error("reference --rebuild requires --promote")

    if args.command == "validate":
        validate_command()
        return

    if args.command == "themes":
        themes_command()
        return

    if args.command == "prepare":
        prepare_command()
        return

    event_dir = resolve_event(args.event)

    if args.command == "status":
        status_command(event_dir)
    elif args.command == "reference":
        reference_command(
            event_dir,
            promote=args.promote,
            rebuild=args.rebuild,
        )
    elif args.command == "classify":
        classify_command(
            event_dir,
            args.run,
            args.status,
            reprocess=args.reprocess,
        )
    elif args.command == "summary":
        summary_command(event_dir)
    elif args.command == "finalize":
        finalize_command(event_dir)
    elif args.command == "publish":
        publish_command(event_dir)
    elif args.command == "doctor":
        doctor_command(event_dir)
    elif args.command == "today":
        today_command(event_dir)
    elif args.command == "reflection":
        reflection_command(event_dir)
    elif args.command == "timing":
        timing_command(
            event_dir,
            show_runs=args.show_runs,
        )

if __name__ == "__main__":
    main()
