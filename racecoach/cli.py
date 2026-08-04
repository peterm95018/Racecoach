from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path



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

    upload_count = len(list(uploads_dir.glob("*.csv")))
    summary_count = len(list(reports_dir.glob("*_summary.json")))

    print("RaceCoach Status")
    print()
    print(f"Event: {event_dir.name}")
    print(f"Uploads: {upload_count}")
    print(f"Analyzed runs: {summary_count}")

    if reference_metadata.exists():
        data = json.loads(
            reference_metadata.read_text(encoding="utf-8")
        )

        print(
            "Reference: "
            f"{data.get('run', 'unknown')} "
            f"({data.get('duration_s', 0):.3f}s)"
        )
        print(
            "Selection rule: "
            f"{data.get('selection_rule', 'unknown')}"
        )
    elif (event_dir / "reference.csv").exists():
        print("Reference: reference.csv (selection metadata unavailable)")
    else:
        print("Reference: not established")

    latest_report = reports_dir / "latest_report.md"
    grid_report = reports_dir / "grid_report.md"
    session_summary = reports_dir / "session_summary.md"

    print(
        "Latest report: "
        + ("available" if latest_report.exists() else "missing")
    )
    print(
        "Grid report: "
        + ("available" if grid_report.exists() else "missing")
    )
    print(
        "Session summary: "
        + ("available" if session_summary.exists() else "missing")
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

    return parser


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


if __name__ == "__main__":
    main()