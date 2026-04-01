from __future__ import annotations

import subprocess
from pathlib import Path

from .utils import ensure_parent


def _run_git(command: list[str], workdir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=workdir, capture_output=True, text=True)


def is_git_repo(workdir: Path) -> bool:
    result = _run_git(["git", "rev-parse", "--is-inside-work-tree"], workdir)
    return result.returncode == 0 and result.stdout.strip() == "true"


def git_diff_text(workdir: Path) -> str:
    tracked = _run_git(
        ["git", "diff", "--binary", "--", ".", ":(exclude).opencode"], workdir
    )
    if tracked.returncode != 0:
        raise RuntimeError(tracked.stderr.strip() or "git diff failed")

    untracked = _run_git(
        ["git", "ls-files", "--others", "--exclude-standard", ":(exclude).opencode"],
        workdir,
    )
    if untracked.returncode != 0:
        raise RuntimeError(untracked.stderr.strip() or "git ls-files failed")

    chunks = []
    tracked_text = tracked.stdout.strip()
    if tracked_text:
        chunks.append(tracked.stdout)

    for rel in [line.strip() for line in untracked.stdout.splitlines() if line.strip()]:
        file_diff = _run_git(
            ["git", "diff", "--binary", "--no-index", "--", "/dev/null", rel], workdir
        )
        diff_text = file_diff.stdout
        if not diff_text and file_diff.stderr:
            raise RuntimeError(file_diff.stderr.strip() or f"git diff failed for {rel}")
        if diff_text:
            chunks.append(diff_text)

    return "\n".join(chunk.rstrip() for chunk in chunks if chunk.strip()) + (
        "\n" if chunks else ""
    )


def write_patch(path: Path, patch_text: str) -> None:
    ensure_parent(path)
    path.write_text(patch_text, encoding="utf-8")
