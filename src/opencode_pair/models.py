from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


STATUS_INITIALIZED = "initialized"
STATUS_DEVELOPER_RUNNING = "developer_running"
STATUS_DEVELOPER_COMPLETED = "developer_completed"
STATUS_TESTING_RUNNING = "testing_running"
STATUS_REVIEWER_RUNNING = "reviewer_running"
STATUS_CHANGES_REQUESTED = "changes_requested"
STATUS_APPROVED = "approved"
STATUS_WAITING_USER = "waiting_user"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"

RESUME_DEVELOPER = "developer"
RESUME_REVIEWER = "reviewer"
RESUME_TEST = "test"

MODE_AUTO = "auto"
MODE_SEMI_AUTO = "semi_auto"


@dataclass
class RoundRecord:
    round: int
    status: str
    started_at: str
    completed_at: Optional[str] = None
    developer_note_path: Optional[str] = None
    developer_prompt_path: Optional[str] = None
    developer_log_path: Optional[str] = None
    patch_path: Optional[str] = None
    test_summary_path: Optional[str] = None
    test_log_path: Optional[str] = None
    reviewer_prompt_path: Optional[str] = None
    reviewer_log_path: Optional[str] = None
    review_path: Optional[str] = None
    review_status: Optional[str] = None
    blocking_count: int = 0
    reviewer_attempts: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoundRecord":
        return cls(**data)


@dataclass
class TaskConfig:
    goal: str
    developer_model: Optional[str] = None
    reviewer_model: Optional[str] = None
    max_rounds: int = 3
    mode: str = MODE_SEMI_AUTO
    test_command: Optional[str] = None
    opencode_agent: Optional[str] = None
    protocol_version: int = 1
    prompt_version: int = 1
    reviewer_retry_limit: int = 1
    dry_run: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskConfig":
        return cls(**data)


@dataclass
class TaskState:
    version: int
    task_id: str
    goal: str
    status: str
    mode: str
    current_round: int
    max_rounds: int
    developer_model: Optional[str]
    reviewer_model: Optional[str]
    test_command: Optional[str]
    opencode_agent: Optional[str]
    workdir: str
    protocol_version: int
    prompt_version: int
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    last_review_status: Optional[str] = None
    resume_from: str = RESUME_DEVELOPER
    last_error: Optional[str] = None
    rounds: List[RoundRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["rounds"] = [round_record.to_dict() for round_record in self.rounds]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskState":
        rounds = [RoundRecord.from_dict(item) for item in data.get("rounds", [])]
        payload = dict(data)
        payload["rounds"] = rounds
        return cls(**payload)

    def current_round_record(self) -> Optional[RoundRecord]:
        for record in self.rounds:
            if record.round == self.current_round:
                return record
        return None
