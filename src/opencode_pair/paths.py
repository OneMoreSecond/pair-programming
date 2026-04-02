from __future__ import annotations

from pathlib import Path


class PairPaths:
    def __init__(self, workdir: Path):
        self.workdir = workdir.resolve()
        self.root = self.workdir / ".opencode" / "pair"
        self.prompts_dir = self.root / "prompts"
        self.tasks_dir = self.root / "tasks"
        self.current_task_file = self.root / "current_task"
        self.project_config_file = self.root / "config.json"

    def ensure_root(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

    def task_dir(self, task_id: str) -> Path:
        return self.tasks_dir / task_id

    def rounds_dir(self, task_id: str) -> Path:
        return self.task_dir(task_id) / "rounds"

    def round_dir(self, task_id: str, round_number: int) -> Path:
        return self.rounds_dir(task_id) / f"{round_number:03d}"

    def config_path(self, task_id: str) -> Path:
        return self.task_dir(task_id) / "config.json"

    def state_path(self, task_id: str) -> Path:
        return self.task_dir(task_id) / "state.json"

    def goal_path(self, task_id: str) -> Path:
        return self.task_dir(task_id) / "goal.md"

    def developer_template_path(self) -> Path:
        return self.prompts_dir / "developer.md"

    def reviewer_template_path(self) -> Path:
        return self.prompts_dir / "reviewer.md"

    def prompt_profile_dir(self, profile: str) -> Path:
        return self.prompts_dir / profile

    def resolved_developer_template_path(self, profile: str) -> Path:
        if profile != "default":
            candidate = self.prompt_profile_dir(profile) / "developer.md"
            if candidate.exists():
                return candidate
        return self.developer_template_path()

    def resolved_reviewer_template_path(self, profile: str) -> Path:
        if profile != "default":
            candidate = self.prompt_profile_dir(profile) / "reviewer.md"
            if candidate.exists():
                return candidate
        return self.reviewer_template_path()

    def project_config_path(self) -> Path:
        return self.project_config_file
