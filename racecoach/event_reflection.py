from __future__ import annotations

from pathlib import Path

import yaml


DEFAULT_REFLECTION = {
    "schema_version": 1,
    "preparation": {},
    "performance": {},
    "observations": [],
    "breakthrough": None,
}


def load_event_reflection(event_dir: Path) -> dict | None:
    """
    Load optional driver reflection data for an event.

    Events without event_reflection.yaml return None. Reflection data is
    observational input for future Driver Intelligence features and does
    not affect telemetry analysis or diagnosis.
    """
    path = event_dir / "event_reflection.yaml"

    if not path.exists():
        return None

    data = yaml.safe_load(
        path.read_text(encoding="utf-8")
    )

    if data is None:
        data = {}

    if not isinstance(data, dict):
        raise ValueError(
            f"event_reflection.yaml must contain a mapping: {path}"
        )

    reflection = {
        **DEFAULT_REFLECTION,
        **data,
    }

    for field in ("preparation", "performance"):
        value = reflection[field]

        if not isinstance(value, dict):
            raise ValueError(
                f"{field} must be a mapping in {path}"
            )

    observations = reflection["observations"]

    if not isinstance(observations, list):
        raise ValueError(
            f"observations must be a list in {path}"
        )

    if not all(
        isinstance(observation, str)
        for observation in observations
    ):
        raise ValueError(
            f"observations must contain only strings in {path}"
        )

    breakthrough = reflection["breakthrough"]

    if breakthrough is not None and not isinstance(
        breakthrough,
        str,
    ):
        raise ValueError(
            f"breakthrough must be text or null in {path}"
        )

    return reflection
