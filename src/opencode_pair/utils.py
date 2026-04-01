from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def slugify_task_id(timestamp: datetime | None = None) -> str:
    ts = timestamp or datetime.now(timezone.utc)
    return ts.strftime("pair-%Y%m%d-%H%M%S")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def relative_to(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def format_lines(lines: Iterable[str]) -> str:
    return "\n".join(lines)
