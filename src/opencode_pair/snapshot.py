from __future__ import annotations

import difflib
from pathlib import Path
from typing import Dict, Iterable, Tuple

from .utils import ensure_parent


EXCLUDED_TOP_LEVEL = {".git", ".opencode", "__pycache__", ".pytest_cache"}


def iter_workspace_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0] in EXCLUDED_TOP_LEVEL:
            continue
        yield path


def capture_snapshot(root: Path) -> Dict[str, bytes]:
    snapshot: Dict[str, bytes] = {}
    for path in iter_workspace_files(root):
        rel = str(path.relative_to(root))
        snapshot[rel] = path.read_bytes()
    return snapshot


def _decode(data: bytes) -> Tuple[bool, str]:
    try:
        return True, data.decode("utf-8")
    except UnicodeDecodeError:
        return False, ""


def build_patch(before: Dict[str, bytes], after: Dict[str, bytes]) -> str:
    chunks = []
    for rel in sorted(set(before) | set(after)):
        old_bytes = before.get(rel)
        new_bytes = after.get(rel)
        if old_bytes == new_bytes:
            continue
        if old_bytes is None:
            old_ok, old_text = True, ""
            new_ok, new_text = _decode(new_bytes or b"")
        elif new_bytes is None:
            old_ok, old_text = _decode(old_bytes)
            new_ok, new_text = True, ""
        else:
            old_ok, old_text = _decode(old_bytes)
            new_ok, new_text = _decode(new_bytes)
        if old_ok and new_ok:
            diff = difflib.unified_diff(
                old_text.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"a/{rel}",
                tofile=f"b/{rel}",
            )
            chunks.append("".join(diff))
        else:
            chunks.append(f"Binary change detected: {rel}\n")
    return "\n".join(chunk for chunk in chunks if chunk)


def write_patch(path: Path, patch_text: str) -> None:
    ensure_parent(path)
    path.write_text(patch_text, encoding="utf-8")
