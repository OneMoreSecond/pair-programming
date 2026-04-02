import tempfile
import unittest
from pathlib import Path

from opencode_pair.models import MODE_SEMI_AUTO, TaskConfig, TaskState
from opencode_pair.paths import PairPaths
from opencode_pair.storage import save_config, save_state
from opencode_pair.workflow import cancel_task


class CancelTaskTests(unittest.TestCase):
    def test_cancel_task_marks_state_cancelled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = PairPaths(root)
            paths.ensure_root()
            task_id = "pair-1"
            paths.task_dir(task_id).mkdir(parents=True, exist_ok=True)
            paths.current_task_file.write_text(task_id + "\n", encoding="utf-8")
            save_config(paths.config_path(task_id), TaskConfig(goal="Goal"))
            save_state(
                paths.state_path(task_id),
                TaskState(
                    version=1,
                    task_id=task_id,
                    goal="Goal",
                    status="waiting_user",
                    mode=MODE_SEMI_AUTO,
                    current_round=1,
                    max_rounds=3,
                    developer_model=None,
                    reviewer_model=None,
                    test_command=None,
                    opencode_agent=None,
                    workdir=str(root),
                    protocol_version=1,
                    prompt_version=1,
                    created_at="2026-04-01T00:00:00Z",
                    updated_at="2026-04-01T00:00:00Z",
                ),
            )
            state = cancel_task(paths, "user requested stop")
            self.assertEqual(state.status, "cancelled")
            self.assertEqual(state.cancellation_reason, "user requested stop")
            self.assertIsNotNone(state.cancelled_at)
