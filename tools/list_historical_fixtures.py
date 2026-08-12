#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


FIXTURE_DIR = Path("tests/fixtures/historical")


def main() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.json"))

    if not paths:
        print("No historical fixtures found.")
        return

    print(
        f"{'Event':24} "
        f"{'Run':10} "
        f"{'Segment':28} "
        f"{'Diagnosis':18} "
        f"{'Confidence':10}"
    )

    print("-" * 96)

    for path in paths:
        data = json.loads(path.read_text())
        source = data["source"]
        expected = data["expected"]

        print(
            f"{source.get('event', ''):24} "
            f"{source.get('run', ''):10} "
            f"{source.get('segment', ''):28} "
            f"{expected.get('diagnosis', ''):18} "
            f"{expected.get('confidence', ''):10}"
        )


if __name__ == "__main__":
    main()
