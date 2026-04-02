import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from opencode_pair.cli import evaluate_task_files, print_eval
from opencode_pair.paths import PairPaths


class EvalCommandTests(unittest.TestCase):
    def test_evaluate_task_files_defaults_to_example_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            example_dir = root / "examples"
            example_dir.mkdir(parents=True, exist_ok=True)
            (example_dir / "basic-task.md").write_text(
                "# Example\n\nGoal:\n\nDo the thing.\n\nConstraints:\n\n- Keep it small.\n",
                encoding="utf-8",
            )
            paths = PairPaths(root)

            payload = evaluate_task_files(paths, None)

            self.assertEqual(payload["task_count"], 1)
            self.assertEqual(payload["ok_count"], 1)
            self.assertEqual(payload["warning_count"], 0)
            self.assertEqual(payload["tasks"][0]["status"], "ok")

    def test_evaluate_task_files_reports_structural_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_path = root / "missing-sections.md"
            task_path.write_text("# Short\n\nJust text\n", encoding="utf-8")
            paths = PairPaths(root)

            payload = evaluate_task_files(paths, [str(task_path)])

            self.assertEqual(payload["warning_count"], 1)
            self.assertIn("missing_goal_section", payload["tasks"][0]["signals"])
            self.assertIn("missing_constraints_section", payload["tasks"][0]["signals"])
            self.assertIn("task_too_short", payload["tasks"][0]["signals"])

    def test_evaluate_task_files_reports_missing_file_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = PairPaths(root)

            payload = evaluate_task_files(paths, ["does-not-exist.md"])

            self.assertEqual(payload["error_count"], 1)
            self.assertEqual(payload["tasks"][0]["status"], "error")
            self.assertIn("file_not_found", payload["tasks"][0]["signals"])

    def test_print_eval_outputs_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_path = root / "task.md"
            task_path.write_text(
                "# Task\n\nGoal:\n\nShip it.\n\nConstraints:\n\n- Small change.\n",
                encoding="utf-8",
            )
            paths = PairPaths(root)
            buf = io.StringIO()

            with redirect_stdout(buf):
                code = print_eval(paths, [str(task_path)], True)

            self.assertEqual(code, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["task_count"], 1)
            self.assertEqual(payload["tasks"][0]["status"], "ok")

    def test_print_eval_outputs_text_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_path = root / "task.md"
            task_path.write_text("# Task\n\nGoal:\n\nShip it.\n", encoding="utf-8")
            paths = PairPaths(root)
            buf = io.StringIO()

            with redirect_stdout(buf):
                code = print_eval(paths, [str(task_path)], False)

            output = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("Evaluation cases: 1", output)
            self.assertIn("status=warning", output)
            self.assertIn("missing_constraints_section", output)
