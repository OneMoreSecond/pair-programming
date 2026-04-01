import tempfile
import unittest
from pathlib import Path
from unittest import mock

from opencode_pair.models import TaskConfig
from opencode_pair.paths import PairPaths
from opencode_pair.preflight import run_preflight


class PreflightTests(unittest.TestCase):
    def test_missing_prompt_templates_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            config = TaskConfig(goal="Test")
            with mock.patch("shutil.which", return_value="/usr/bin/opencode"):
                report = run_preflight(paths, config)
            self.assertFalse(report.ok)
            self.assertTrue(
                any("missing prompt template" in item for item in report.errors)
            )

    def test_dirty_git_worktree_is_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = PairPaths(root)
            paths.ensure_root()
            paths.developer_template_path().write_text("dev", encoding="utf-8")
            paths.reviewer_template_path().write_text("review", encoding="utf-8")

            with mock.patch("shutil.which", return_value="/usr/bin/opencode"):
                with mock.patch(
                    "opencode_pair.preflight._is_dirty_git_worktree", return_value=True
                ):
                    report = run_preflight(paths, TaskConfig(goal="Test"))

            self.assertTrue(report.ok)
            self.assertTrue(
                any("uncommitted changes" in item for item in report.warnings)
            )

    def test_missing_test_executable_is_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = PairPaths(root)
            paths.ensure_root()
            paths.developer_template_path().write_text("dev", encoding="utf-8")
            paths.reviewer_template_path().write_text("review", encoding="utf-8")

            def fake_which(name: str):
                return "/usr/bin/opencode" if name == "opencode" else None

            with mock.patch("shutil.which", side_effect=fake_which):
                report = run_preflight(
                    paths, TaskConfig(goal="Test", test_command="pytest -q")
                )

            self.assertTrue(report.ok)
            self.assertTrue(any("pytest" in item for item in report.warnings))
