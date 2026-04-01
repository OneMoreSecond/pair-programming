from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .utils import ensure_parent


@dataclass
class CommandResult:
    command: List[str]
    returncode: int
    stdout: str
    stderr: str


def run_command(
    command: List[str], workdir: Path, log_path: Path, dry_run: bool = False
) -> CommandResult:
    ensure_parent(log_path)
    if dry_run:
        stdout = "DRY RUN\n" + shlex.join(command) + "\n"
        log_path.write_text(stdout, encoding="utf-8")
        return CommandResult(command=command, returncode=0, stdout=stdout, stderr="")

    completed = subprocess.run(command, cwd=workdir, capture_output=True, text=True)
    log_path.write_text(
        completed.stdout
        + ("\n[stderr]\n" + completed.stderr if completed.stderr else ""),
        encoding="utf-8",
    )
    return CommandResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def run_opencode(
    *,
    prompt_file: Path,
    workdir: Path,
    log_path: Path,
    model: Optional[str] = None,
    agent: Optional[str] = None,
    title: Optional[str] = None,
    dry_run: bool = False,
) -> CommandResult:
    command = [
        "opencode",
        "run",
        "Read the attached task file and follow it exactly.",
        "--dir",
        str(workdir),
        "--file",
        str(prompt_file),
    ]
    if model:
        command.extend(["--model", model])
    if agent:
        command.extend(["--agent", agent])
    if title:
        command.extend(["--title", title])
    return run_command(command, workdir=workdir, log_path=log_path, dry_run=dry_run)


def run_test_command(
    command_text: str, workdir: Path, log_path: Path, dry_run: bool = False
) -> CommandResult:
    command = ["bash", "-lc", command_text]
    return run_command(command, workdir=workdir, log_path=log_path, dry_run=dry_run)
