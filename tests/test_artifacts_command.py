import io
import tempfile
import unittest
from contextlib import redirect_stdout
from contextlib import redirect_stderr
from pathlib import Path

from opencode_pair.cli import print_artifacts
from opencode_pair.models import MODE_SEMI_AUTO, RoundRecord, TaskConfig, TaskState
from opencode_pair.paths import PairPaths
from opencode_pair.storage import save_config, save_state


class ArtifactsCommandTests(unittest.TestCase):
    def test_print_artifacts_for_latest_round(self) -> None:
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
                    rounds=[
                        RoundRecord(
                            round=1,
                            status="waiting_user",
                            started_at="2026-04-01T00:00:00Z",
                            developer_note_path="rounds/001/developer-note.md",
                            patch_path="rounds/001/patch.diff",
                            review_path="rounds/001/review.md",
                        )
                    ],
                ),
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                code = print_artifacts(paths, None)
            output = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("Round: 1", output)
            self.assertIn("rounds/001/developer-note.md", output)
            self.assertIn("rounds/001/patch.diff", output)
            self.assertIn("rounds/001/review.md", output)

    def test_print_artifacts_without_task_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            buf = io.StringIO()
            with redirect_stderr(buf):
                code = print_artifacts(paths, None)
            output = buf.getvalue()
            self.assertEqual(code, 1)
            self.assertIn("No active task found.", output)
            self.assertIn("Next action:", output)
