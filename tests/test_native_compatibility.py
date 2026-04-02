import io
import tempfile
import unittest
from contextlib import redirect_stderr
from contextlib import redirect_stdout
from pathlib import Path

from opencode_pair.models import MODE_SEMI_AUTO, RoundRecord, TaskConfig, TaskState
from opencode_pair.opencode_wrapper import main as wrapper_main
from opencode_pair.paths import PairPaths
from opencode_pair.storage import save_config, save_state


class NativeCompatibilityTests(unittest.TestCase):
    def test_wrapper_status_json_matches_existing_query_flow(self) -> None:
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
                code = wrapper_main(
                    [
                        "pair",
                        "status",
                        "--workdir",
                        str(root),
                        "--task-id",
                        task_id,
                        "--json",
                    ]
                )

            self.assertEqual(code, 0)
            self.assertIn('"task_id": "pair-1"', buf.getvalue())

    def test_wrapper_artifacts_matches_existing_query_flow(self) -> None:
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
                code = wrapper_main(["pair", "artifacts", "--workdir", str(root)])

            self.assertEqual(code, 0)
            output = buf.getvalue()
            self.assertIn("Round: 1", output)
            self.assertIn("rounds/001/review.md", output)

    def test_wrapper_review_without_task_keeps_actionable_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            buf = io.StringIO()
            with redirect_stderr(buf):
                code = wrapper_main(["pair", "review", "--workdir", tmp])

            self.assertEqual(code, 1)
            output = buf.getvalue()
            self.assertIn("No active task found.", output)
            self.assertIn("Next action:", output)

    def test_wrapper_help_uses_native_prog_name(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            with self.assertRaises(SystemExit) as exc:
                wrapper_main(["pair", "--help"])

        self.assertEqual(exc.exception.code, 0)
        self.assertIn("usage: opencode pair", buf.getvalue())
