
from __future__ import annotations

import argparse
import shutil
import time
import traceback
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .analyze_run import analyze, write_report


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

        try:
            print(f"Analyzing {path.name}...")
            _, metrics, findings = analyze(path, self.event_dir)
            md, js = write_report(path, metrics, findings, self.reports_dir)
            dest = self.processed_dir / path.name
            shutil.move(str(path), str(dest))
            print(f"Report written: {md}")
            print(f"Processed file moved to: {dest}")
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
