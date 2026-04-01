import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from opencode_pair.cli import print_status
from opencode_pair.models import MODE_SEMI_AUTO, TaskConfig, TaskState
from opencode_pair.paths import PairPaths
from opencode_pair.storage import save_config, save_state


class StatusQueryModeTests(unittest.TestCase):
    def test_print_status_json_for_specific_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = PairPaths(root)
            paths.ensure_root()
            task_id = "pair-1"
            paths.task_dir(task_id).mkdir(parents=True, exist_ok=True)
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

            buf = io.StringIO()
            with redirect_stdout(buf):
                code = print_status(paths, task_id, True, False)
            output = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn('"task_id": "pair-1"', output)
