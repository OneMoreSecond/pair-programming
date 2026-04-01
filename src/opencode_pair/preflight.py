from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .models import TaskConfig
from .paths import PairPaths


@dataclass
class PreflightReport:
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _run_git(command: list[str], workdir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=workdir, capture_output=True, text=True)


def _is_dirty_git_worktree(workdir: Path) -> Optional[bool]:
    probe = _run_git(["git", "rev-parse", "--is-inside-work-tree"], workdir)
    if probe.returncode != 0:
        return None
    status = _run_git(["git", "status", "--porcelain"], workdir)
    if status.returncode != 0:
        return None
    return bool(status.stdout.strip())


def run_preflight(paths: PairPaths, config: TaskConfig) -> PreflightReport:
    report = PreflightReport()
    workdir = paths.workdir

    if not workdir.exists():
        report.errors.append(f"workdir does not exist: {workdir}")
        return report
    if not workdir.is_dir():
        report.errors.append(f"workdir is not a directory: {workdir}")
        return report
    if not workdir.exists() or not workdir.is_dir():
        return report

    if not (workdir.stat().st_mode & 0o200):
        report.errors.append(f"workdir is not writable: {workdir}")

    for prompt_path in [
        paths.developer_template_path(),
        paths.reviewer_template_path(),
    ]:
        if not prompt_path.exists():
            report.errors.append(f"missing prompt template: {prompt_path}")

    dirty = _is_dirty_git_worktree(workdir)
    if dirty is True:
        report.warnings.append(
            "git worktree has uncommitted changes; patch and review context may include existing edits"
        )

    if shutil.which("opencode") is None:
        report.errors.append("opencode CLI is not available on PATH")

    if config.test_command:
        shell_name = (
            config.test_command.strip().split()[0]
            if config.test_command.strip()
            else ""
        )
        if shell_name and shutil.which(shell_name) is None:
            report.warnings.append(
                f"test command executable may be unavailable on PATH: {shell_name}"
            )

    return report
