from __future__ import annotations

from pathlib import Path

import yaml


VALID_STATUSES = {
    "emerging",
    "active",
    "improving",
    "reinforced",
    "retired",
}


def load_coaching_themes(project_dir: Path) -> dict | None:
    path = project_dir / "driver" / "coaching_themes.yaml"

    if not path.exists():
        return None

    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    if data is None:
        data = {}

    if not isinstance(data, dict):
        raise ValueError(
            f"coaching_themes.yaml must contain a mapping: {path}"
        )

    for key in ("primary", "secondary"):
        theme = data.get(key)

        if theme is None:
            continue

        if not isinstance(theme, dict):
            raise ValueError(
                f"{key} must be a mapping in {path}"
            )

        status = theme.get("status")

        if status is not None and status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status for {key}: {status}"
            )

    completed = data.get("completed", [])

    if not isinstance(completed, list):
        raise ValueError(
            f"completed must be a list in {path}"
        )

    return data
