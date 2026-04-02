import tempfile
import unittest
from pathlib import Path

from opencode_pair.workflow import write_tester_note


class TesterPhaseTests(unittest.TestCase):
    def test_write_tester_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tester-note.md"
            write_tester_note(path, "pytest -q", 0)
            text = path.read_text(encoding="utf-8")
            self.assertIn("# Tester Note", text)
            self.assertIn("pytest -q", text)
            self.assertIn("PASSED", text)
