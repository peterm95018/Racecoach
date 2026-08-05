from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


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

    reference_parser = subparsers.add_parser(
        "reference",
        help="Preview or promote the best reference run",
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

    subparsers.add_parser(
        "summary",
        help="Regenerate the session summary",
    )

    subparsers.add_parser(
        "finalize",
        help=(
            "Promote the best reference and rebuild the entire event"
        ),
    )

    return parser


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

    failures = []

    def check(path: Path, label: str) -> None:
        if path.exists():
            print(f"✓ {label}")
        else:
            print(f"✗ {label}")
            failures.append(label)

    check(event_dir, "Event directory")
    check(event_dir / "uploads", "uploads/")
    check(event_dir / "reports", "reports/")
    check(event_dir / "segments.yaml", "segments.yaml")
    check(event_dir / "reference.csv", "reference.csv")
    check(
        event_dir / "reference_selection.json",
        "reference_selection.json",
    )
    check(
        event_dir / "reports/latest_report.md",
        "latest_report.md",
    )
    check(
        event_dir / "reports/grid_report.md",
        "grid_report.md",
    )
    check(
        event_dir / "reports/session_summary.md",
        "session_summary.md",
    )
    check(
        project_root() / "publish_reports.sh",
        "publish_reports.sh",
    )

    print()

    uploads_dir = event_dir / "uploads"
    reports_dir = event_dir / "reports"

    uploads = sorted(uploads_dir.glob("*.csv"))
    summaries = sorted(reports_dir.glob("*_summary.json"))

    print("Consistency")

    if not uploads and not summaries:
        print("○ no uploaded or analyzed runs yet")
    elif len(uploads) == len(summaries):
        print(
            f"✓ uploads and summaries match "
            f"({len(uploads)} run(s))"
        )
    else:
        difference = len(uploads) - len(summaries)
        print(
            f"✗ uploads and summaries differ "
            f"({len(uploads)} uploaded / "
            f"{len(summaries)} analyzed)"
        )
        failures.append(
            f"{difference:+d} upload/summary difference"
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
        print(
            f"✗ unreadable summary JSON "
            f"({len(unreadable_summaries)})"
        )
        failures.append(
            f"{len(unreadable_summaries)} unreadable summary file(s)"
        )
    elif summaries:
        print(
            f"✓ summary JSON readable "
            f"({len(summaries)} file(s))"
        )

    reference_path = event_dir / "reference.csv"
    reference_metadata = event_dir / "reference_selection.json"

    if reference_metadata.exists():
        try:
            metadata = json.loads(
                reference_metadata.read_text(encoding="utf-8")
            )
            source = metadata.get("source")

            if source and (uploads_dir / source).exists():
                print("✓ reference source CSV exists")
            elif source:
                print("✗ reference source CSV missing")
                failures.append("reference source CSV missing")
            else:
                print("✗ reference metadata missing source")
                failures.append("reference metadata missing source")
        except (OSError, json.JSONDecodeError):
            print("✗ reference metadata unreadable")
            failures.append("reference metadata unreadable")

    if summaries and not reference_path.exists():
        print("✗ analyzed runs exist but reference.csv is missing")
        failures.append(
            "analyzed runs exist but reference.csv is missing"
        )

    print()

    if failures:
        print(f"FAILED ({len(failures)} issue(s))")
        raise SystemExit(1)

    print("PASS")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if (
        args.command == "reference"
        and args.rebuild
        and not args.promote
    ):
        parser.error("reference --rebuild requires --promote")

    event_dir = resolve_event(args.event)

    if args.command == "status":
        status_command(event_dir)
    elif args.command == "reference":
        reference_command(
            event_dir,
            promote=args.promote,
            rebuild=args.rebuild,
        )
    elif args.command == "summary":
        summary_command(event_dir)
    elif args.command == "finalize":
        finalize_command(event_dir)
    elif args.command == "publish":
        publish_command(event_dir)
    elif args.command == "doctor":
        doctor_command(event_dir)


if __name__ == "__main__":
    main()