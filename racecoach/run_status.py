from __future__ import annotations

from pathlib import Path

import yaml


VALID_RUN_STATUSES = {
    "clean",
    "cone",
    "dnf",
    "off_course",
    "unknown",
}


def normalize_run_status(status: str) -> str:
    normalized = str(status).strip().lower()

    if normalized not in VALID_RUN_STATUSES:
        valid = ", ".join(sorted(VALID_RUN_STATUSES))
        raise ValueError(
            f"Invalid run status {status!r}; expected one of: "
            f"{valid}"
        )

    return normalized


def status_is_clean(status: str) -> bool | None:
    normalized = normalize_run_status(status)

    if normalized == "clean":
        return True

    if normalized in {"cone", "dnf", "off_course"}:
        return False

    return None


def load_run_status(
    event_dir: Path,
    run_name: str,
) -> tuple[str, bool | None]:
    status_file = event_dir / "run_status.yaml"

    if not status_file.exists():
        return "unknown", None

    data = yaml.safe_load(
        status_file.read_text(encoding="utf-8")
    ) or {}

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid run-status document in {status_file}"
        )

    runs = data.get("runs") or {}

    if not isinstance(runs, dict):
        raise ValueError(
            f"Invalid runs mapping in {status_file}"
        )

    run_data = runs.get(run_name) or {}

    if not isinstance(run_data, dict):
        raise ValueError(
            f"Invalid status entry for {run_name} "
            f"in {status_file}"
        )

    status = normalize_run_status(
        run_data.get("status", "unknown")
    )

    return status, status_is_clean(status)


def set_run_status(
    event_dir: Path,
    run_name: str,
    status: str,
) -> Path:
    normalized_name = str(run_name).strip()

    if not normalized_name:
        raise ValueError("Run name is required")

    normalized_status = normalize_run_status(status)
    status_file = event_dir / "run_status.yaml"

    if status_file.exists():
        data = yaml.safe_load(
            status_file.read_text(encoding="utf-8")
        ) or {}
    else:
        data = {}

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid run-status document in {status_file}"
        )

    runs = data.setdefault("runs", {})

    if not isinstance(runs, dict):
        raise ValueError(
            f"Invalid runs mapping in {status_file}"
        )

    existing = runs.get(normalized_name) or {}

    if not isinstance(existing, dict):
        raise ValueError(
            f"Invalid status entry for {normalized_name} "
            f"in {status_file}"
        )

    runs[normalized_name] = {
        **existing,
        "status": normalized_status,
    }

    temporary_path = event_dir / ".run_status.yaml.tmp"
    temporary_path.write_text(
        yaml.safe_dump(
            data,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    temporary_path.replace(status_file)

    return status_file
