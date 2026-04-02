import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from opencode_pair.cli import print_history
from opencode_pair.models import MODE_SEMI_AUTO, RoundRecord, TaskConfig, TaskState
from opencode_pair.paths import PairPaths
from opencode_pair.storage import save_config, save_state


class HistoryCommandTests(unittest.TestCase):
    def test_print_history_lists_rounds(self) -> None:
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
                    rounds=[
                        RoundRecord(
                            round=1,
                            status="changes_requested",
                            started_at="2026-04-01T00:00:00Z",
                            review_status="CHANGES_REQUESTED",
                            blocking_count=2,
                            developer_note_path="rounds/001/developer-note.md",
                            patch_path="rounds/001/patch.diff",
                            review_path="rounds/001/review.md",
                        ),
                        RoundRecord(
                            round=2,
                            status="waiting_user",
                            started_at="2026-04-01T00:01:00Z",
                            review_status="CHANGES_REQUESTED",
                            blocking_count=1,
                            developer_note_path="rounds/002/developer-note.md",
                            patch_path="rounds/002/patch.diff",
                            review_path="rounds/002/review.md",
                        ),
                    ],
                ),
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                code = print_history(paths)
            output = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("Rounds:", output)
            self.assertIn("round 1", output)
            self.assertIn("rounds/001/review.md", output)
            self.assertIn("rounds/002/patch.diff", output)
