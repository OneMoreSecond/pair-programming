from __future__ import annotations

import json
from pathlib import Path

from .models import TaskConfig, TaskState
from .utils import ensure_parent


def write_json(path: Path, payload: dict) -> None:
    ensure_parent(path)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(path: Path, config: TaskConfig) -> None:
    write_json(path, config.to_dict())


def load_config(path: Path) -> TaskConfig:
    return TaskConfig.from_dict(read_json(path))


def save_state(path: Path, state: TaskState) -> None:
    write_json(path, state.to_dict())


def load_state(path: Path) -> TaskState:
    return TaskState.from_dict(read_json(path))
