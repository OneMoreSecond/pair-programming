import tempfile
import unittest
from pathlib import Path

from opencode_pair.models import TaskConfig
from opencode_pair.paths import PairPaths
from opencode_pair.workflow import ensure_prompt_templates


class PromptProfileTests(unittest.TestCase):
    def test_profile_specific_templates_are_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            paths.ensure_root()
            profile_dir = paths.prompt_profile_dir("frontend")
            profile_dir.mkdir(parents=True, exist_ok=True)
            (profile_dir / "developer.md").write_text("dev", encoding="utf-8")
            (profile_dir / "reviewer.md").write_text("review", encoding="utf-8")
            self.assertEqual(
                paths.resolved_developer_template_path("frontend"),
                profile_dir / "developer.md",
            )
            self.assertEqual(
                paths.resolved_reviewer_template_path("frontend"),
                profile_dir / "reviewer.md",
            )

    def test_default_templates_fallback_when_profile_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            paths.ensure_root()
            paths.developer_template_path().write_text("dev", encoding="utf-8")
            paths.reviewer_template_path().write_text("review", encoding="utf-8")
            ensure_prompt_templates(
                paths, TaskConfig(goal="Goal", prompt_profile="backend")
            )
