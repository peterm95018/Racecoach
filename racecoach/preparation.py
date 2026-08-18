from __future__ import annotations

from pathlib import Path

from racecoach.coaching_themes import load_coaching_themes
from racecoach.event_reflection import load_event_reflection


def find_latest_reflection(project_dir: Path) -> tuple[Path, dict] | None:
    events_dir = project_dir / "events"

    if not events_dir.is_dir():
        return None

    candidates = []

    for event_dir in events_dir.iterdir():
        if not event_dir.is_dir():
            continue

        path = event_dir / "event_reflection.yaml"

        if path.exists():
            candidates.append(
                (
                    path.stat().st_mtime,
                    event_dir,
                )
            )

    if not candidates:
        return None

    _, event_dir = max(
        candidates,
        key=lambda item: item[0],
    )

    reflection = load_event_reflection(event_dir)

    if reflection is None:
        return None

    return event_dir, reflection


def build_preparation_brief(project_dir: Path) -> dict:
    themes = load_coaching_themes(project_dir)
    latest_reflection = find_latest_reflection(project_dir)

    brief = {
        "primary_theme": None,
        "secondary_theme": None,
        "reflection_event": None,
        "preparation": {},
        "performance": {},
        "observations": [],
        "breakthrough": None,
    }

    if themes:
        brief["primary_theme"] = themes.get("primary")
        brief["secondary_theme"] = themes.get("secondary")

    if latest_reflection:
        event_dir, reflection = latest_reflection

        brief["reflection_event"] = event_dir.name
        brief["preparation"] = (
            reflection.get("preparation") or {}
        )
        brief["performance"] = (
            reflection.get("performance") or {}
        )
        brief["observations"] = (
            reflection.get("observations") or []
        )
        brief["breakthrough"] = reflection.get(
            "breakthrough"
        )

    return brief
