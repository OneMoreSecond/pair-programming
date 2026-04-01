import tempfile
import unittest
from pathlib import Path

from opencode_pair.cli import load_goal


class GoalFileTests(unittest.TestCase):
    def test_load_goal_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "goal.md"
            path.write_text("Ship the feature\n", encoding="utf-8")
            self.assertEqual(load_goal(None, str(path)), "Ship the feature")

    def test_missing_goal_file_raises(self) -> None:
        with self.assertRaises(ValueError):
            load_goal(None, "missing-goal.md")
