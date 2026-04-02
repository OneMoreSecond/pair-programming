import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from opencode_pair.cli import print_metrics
from opencode_pair.models import MODE_SEMI_AUTO, RoundRecord, TaskConfig, TaskState
from opencode_pair.paths import PairPaths
from opencode_pair.storage import save_config, save_state


class MetricsCommandTests(unittest.TestCase):
    def test_print_metrics_outputs_summary(self) -> None:
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
                    current_round=2,
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
                    intervention_count=1,
                    rounds=[
                        RoundRecord(
                            round=1,
                            status="changes_requested",
                            started_at="2026-04-01T00:00:00Z",
                            review_status="CHANGES_REQUESTED",
                            blocking_count=2,
                            reviewer_attempts=1,
                        ),
                        RoundRecord(
                            round=2,
                            status="waiting_user",
                            started_at="2026-04-01T00:01:00Z",
                            review_status="CHANGES_REQUESTED",
                            blocking_count=1,
                            reviewer_attempts=2,
                        ),
                    ],
                ),
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                code = print_metrics(paths)
            output = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("Round count: 2", output)
            self.assertIn("Reviewer attempts total: 3", output)
            self.assertIn("Intervention count: 1", output)
