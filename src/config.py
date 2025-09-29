import yaml
from pathlib import Path
from typing import Any


def load_config(config_path: str = "config.yaml") -> dict[str, Any]:
    if not Path(config_path).exists():
        raise FileNotFoundError(
            f"Config file {config_path} not found. Copy config.yaml.example to config.yaml."
        )
    with open(config_path) as f:
        return yaml.safe_load(f)
