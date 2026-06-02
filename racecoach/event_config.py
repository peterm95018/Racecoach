from pathlib import Path

import yaml


def load_event_config(event_dir: Path) -> dict:
    config_file = event_dir / "event.yaml"

    if not config_file.exists():
        return {
            "segmentation_mode": "distance",
        }

    data = yaml.safe_load(config_file.read_text()) or {}

    if "segmentation_mode" not in data:
        data["segmentation_mode"] = "distance"

    return data
