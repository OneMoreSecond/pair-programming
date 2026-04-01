import unittest

from opencode_pair.models import RoundRecord, TaskState
from opencode_pair.workflow import detect_progress_issues


class WorkflowProgressTests(unittest.TestCase):
    def test_empty_patch_is_flagged(self) -> None:
        state = TaskState(
            version=1,
            task_id="pair-1",
            goal="Goal",
            status="reviewer_running",
            mode="auto",
            current_round=1,
            max_rounds=3,
            developer_model=None,
            reviewer_model=None,
            test_command=None,
            opencode_agent=None,
            workdir="/tmp/repo",
            protocol_version=1,
            prompt_version=1,
            created_at="2026-04-01T00:00:00Z",
            updated_at="2026-04-01T00:00:00Z",
        )
        record = RoundRecord(
            round=1,
            status="changes_requested",
            started_at="2026-04-01T00:00:00Z",
            blocking_count=1,
        )
        issues = detect_progress_issues(state, record, "")
        self.assertTrue(any("empty patch" in item for item in issues))

    def test_blocking_count_non_decrease_is_flagged(self) -> None:
        previous = RoundRecord(
            round=1,
            status="changes_requested",
            started_at="2026-04-01T00:00:00Z",
            review_status="CHANGES_REQUESTED",
            blocking_count=2,
        )
        state = TaskState(
            version=1,
            task_id="pair-1",
            goal="Goal",
            status="reviewer_running",
            mode="auto",
            current_round=2,
            max_rounds=3,
            developer_model=None,
            reviewer_model=None,
            test_command=None,
            opencode_agent=None,
            workdir="/tmp/repo",
            protocol_version=1,
            prompt_version=1,
            created_at="2026-04-01T00:00:00Z",
            updated_at="2026-04-01T00:00:00Z",
            rounds=[previous],
        )
        record = RoundRecord(
            round=2,
            status="changes_requested",
            started_at="2026-04-01T00:01:00Z",
            blocking_count=2,
        )
        issues = detect_progress_issues(state, record, "diff")
        self.assertTrue(any("did not decrease" in item for item in issues))
