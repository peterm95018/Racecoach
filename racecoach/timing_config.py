from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from racecoach.event_config import load_event_config


DEFAULT_PROFILES_PATH = Path(__file__).with_name(
    "timing_profiles.yaml"
)


@dataclass(frozen=True)
class TimingConfig:
    organizer: str | None
    profile: str | None
    provider: str
    results_url: str
    driver_number: str


def load_timing_profiles(
    profiles_path: Path | None = None,
) -> dict[str, dict]:
    path = profiles_path or DEFAULT_PROFILES_PATH

    if not path.exists():
        raise FileNotFoundError(
            f"Timing profiles file not found: {path}"
        )

    data = yaml.safe_load(
        path.read_text(encoding="utf-8")
    ) or {}

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid timing profiles document: {path}"
        )

    profiles = data.get("profiles")

    if not isinstance(profiles, dict):
        raise ValueError(
            f"Missing timing profiles mapping: {path}"
        )

    normalized = {}

    for name, profile in profiles.items():
        profile_name = str(name).strip().lower()

        if not profile_name:
            raise ValueError(
                f"Empty timing profile name in {path}"
            )

        if not isinstance(profile, dict):
            raise ValueError(
                f"Invalid timing profile {profile_name!r} "
                f"in {path}"
            )

        normalized[profile_name] = dict(profile)

    return normalized


def load_event_timing(
    event_dir: Path,
    profiles_path: Path | None = None,
) -> TimingConfig | None:
    event_config = load_event_config(event_dir)
    profiles = load_timing_profiles(profiles_path)

    organizer_value = event_config.get("organizer")
    organizer = (
        str(organizer_value).strip().lower()
        if organizer_value is not None
        else None
    )

    timing_data = event_config.get("timing")

    if timing_data is None:
        timing = {}
    elif isinstance(timing_data, dict):
        timing = dict(timing_data)
    else:
        raise ValueError(
            f"{event_dir}: timing configuration must be a mapping"
        )

    profile_value = timing.pop("profile", None)

    if profile_value is not None:
        profile_name = str(profile_value).strip().lower()
    elif organizer in profiles:
        profile_name = organizer
    else:
        profile_name = None

    resolved = {}

    if profile_name is not None:
        if profile_name not in profiles:
            raise ValueError(
                f"{event_dir}: unknown timing profile "
                f"{profile_name!r}"
            )

        resolved.update(profiles[profile_name])

    resolved.update(timing)

    if not resolved:
        return None

    provider = str(resolved.get("provider", "")).strip().lower()
    results_url = str(
        resolved.get("results_url", "")
    ).strip()
    driver_number = str(
        resolved.get("driver_number", "")
    ).strip()

    if not provider:
        raise ValueError(
            f"{event_dir}: timing provider is required"
        )

    if not results_url.startswith("https://"):
        raise ValueError(
            f"{event_dir}: timing results_url must use HTTPS"
        )

    if not driver_number:
        raise ValueError(
            f"{event_dir}: timing driver_number is required"
        )

    return TimingConfig(
        organizer=organizer,
        profile=profile_name,
        provider=provider,
        results_url=results_url,
        driver_number=driver_number,
    )