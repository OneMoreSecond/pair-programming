import subprocess
import tempfile
import unittest
from pathlib import Path

from opencode_pair.patches import git_diff_text, is_git_repo


class PatchTests(unittest.TestCase):
    def test_is_git_repo_detects_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            self.assertTrue(is_git_repo(root))

    def test_git_diff_text_includes_modified_and_untracked_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)

            tracked = root / "tracked.txt"
            tracked.write_text("before\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "tracked.txt"], cwd=root, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "init"],
                cwd=root,
                check=True,
                capture_output=True,
            )

            tracked.write_text("after\n", encoding="utf-8")
            new_file = root / "new.txt"
            new_file.write_text("hello\n", encoding="utf-8")

            diff_text = git_diff_text(root)
            self.assertIn("a/tracked.txt", diff_text)
            self.assertIn("b/tracked.txt", diff_text)
            self.assertIn("a/new.txt", diff_text)
            self.assertIn("b/new.txt", diff_text)
