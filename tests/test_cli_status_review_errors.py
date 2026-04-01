import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from opencode_pair.cli import print_review, print_status
from opencode_pair.paths import PairPaths


class CliErrorOutputTests(unittest.TestCase):
    def test_print_status_without_task_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            buf = io.StringIO()
            with redirect_stderr(buf):
                code = print_status(paths)
            output = buf.getvalue()
            self.assertEqual(code, 1)
            self.assertIn("No active task found.", output)
            self.assertIn("Next action:", output)

    def test_print_review_without_task_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            buf = io.StringIO()
            with redirect_stderr(buf):
                code = print_review(paths, None)
            output = buf.getvalue()
            self.assertEqual(code, 1)
            self.assertIn("No active task found.", output)
            self.assertIn("Next action:", output)
