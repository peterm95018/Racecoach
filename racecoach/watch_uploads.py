
from __future__ import annotations

import argparse
import shutil
import subprocess
import time
import traceback
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .analyze_run import (
    analyze,
    markdown_to_html,
    write_report,
)
from .data_quality import DataQualityError

def write_data_quality_failure_reports(
    source: Path,
    reports_dir: Path,
    error: DataQualityError,
) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_text = f"""# RaceCoach Data Validation Failed

Run: `{source.name}`

## No coaching generated

RaceCoach rejected this run because the telemetry or course
configuration could not be validated.

**Reason:** {error}

Check the RaceChrono track selection, CSV lap export, reference lap,
and full-course segment coverage before using coaching.
"""

    grid_text = f"""# DATA INVALID

**No coaching generated for `{source.name}`.**

Reason: {error}

Do not use coaching from the previous run. Correct the data or course
configuration and reprocess this run.
"""

    run_path = reports_dir / f"{source.stem}_invalid.md"
    run_path.write_text(report_text)

    run_html_path = reports_dir / f"{source.stem}_invalid.html"
    run_html_path.write_text(markdown_to_html(report_text))

    latest_path = reports_dir / "latest_report.md"
    latest_path.write_text(report_text)

    latest_html_path = reports_dir / "latest_report.html"
    latest_html_path.write_text(markdown_to_html(report_text))

    grid_path = reports_dir / "grid_report.md"
    grid_path.write_text(grid_text)

    grid_html_path = reports_dir / "grid_report.html"
    grid_html_path.write_text(markdown_to_html(grid_text))

    return latest_path, grid_path


def publish_reports_to_drupal(project_dir: Path) -> None:
    publish_script = project_dir / "publish_reports.sh"

    if not publish_script.exists():
        raise FileNotFoundError(
            f"Publishing script not found: {publish_script}"
        )

    subprocess.run(
        [str(publish_script)],
        cwd=project_dir,
        check=True,
    )

class UploadHandler(FileSystemEventHandler):
    def __init__(self, event_dir: Path, reports_dir: Path, processed_dir: Path):
        self.event_dir = event_dir
        self.reports_dir = reports_dir
        self.processed_dir = processed_dir
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.suffix.lower() != ".csv":
            return

        time.sleep(2)

        project_dir = Path(__file__).resolve().parent.parent
        reference_path = self.event_dir / "reference.csv"
        analysis_reference = (
            reference_path if reference_path.exists() else path
        )

        try:
            print(f"Analyzing {path.name}...")

            df, metrics, findings = analyze(
                path,
                self.event_dir,
                analysis_reference,
            )

            if not reference_path.exists():
                shutil.copy2(path, reference_path)
                print(f"Created reference lap: {reference_path.name}")

            analyzed_duration_s = None

            if not df.empty and "time_s" in df.columns:
                analyzed_duration_s = float(df["time_s"].iloc[-1])

            md, js = write_report(
                path,
                reference_path,
                metrics,
                findings,
                self.reports_dir,
                self.event_dir,
                driver_input_source=df.attrs.get(
                    "driver_input_source"
                ),
                analyzed_duration_s=analyzed_duration_s,
                sample_count=len(df),
            )

            publish_reports_to_drupal(project_dir)

            print(f"Report written: {md}")
            print("Reports published to Drupal.")
            print(f"Processed file retained in uploads: {path}")

        except DataQualityError as exc:
            print(f"DATA INVALID for {path.name}: {exc}")

            write_data_quality_failure_reports(
                path,
                self.reports_dir,
                exc,
            )

            try:
                publish_reports_to_drupal(project_dir)
                print("Data-validation warning published to Drupal.")
            except Exception as publish_exc:
                print(
                    "ERROR publishing data-validation warning: "
                    f"{publish_exc}"
                )
                traceback.print_exc()

        except Exception as exc:
            print(f"ERROR analyzing {path.name}: {exc}")
            traceback.print_exc()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--uploads", type=Path, default=Path("uploads"))
    parser.add_argument("--processed", type=Path, default=Path("processed"))
    parser.add_argument("--reports", type=Path, default=Path("reports"))
    parser.add_argument("--event", type=Path, required=True)
    args = parser.parse_args()

    args.uploads.mkdir(parents=True, exist_ok=True)

    handler = UploadHandler(args.event, args.reports, args.processed)
    observer = Observer()
    observer.schedule(handler, str(args.uploads), recursive=False)
    observer.start()

    print(f"Watching {args.uploads} for RaceChrono CSV uploads...")
    print(f"Using event config: {args.event}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
