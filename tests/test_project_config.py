import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from opencode_pair.cli import (
    build_effective_defaults,
    build_task_config_from_args,
    print_config,
)
from opencode_pair.paths import PairPaths


class ProjectConfigTests(unittest.TestCase):
    def test_missing_project_config_keeps_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            payload = build_effective_defaults(paths)
            self.assertEqual(payload["mode"], "semi_auto")
            self.assertEqual(payload["max_rounds"], 3)

    def test_project_config_overrides_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            paths.ensure_root()
            paths.project_config_path().write_text(
                json.dumps({"mode": "auto", "max_rounds": 5}), encoding="utf-8"
            )
            payload = build_effective_defaults(paths)
            self.assertEqual(payload["mode"], "auto")
            self.assertEqual(payload["max_rounds"], 5)

    def test_print_config_reports_project_config_presence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = print_config(paths, False)
            output = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("project_config_present:", output)

    def test_cli_values_override_project_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            paths.ensure_root()
            paths.project_config_path().write_text(
                json.dumps(
                    {"mode": "auto", "max_rounds": 5, "test_command": "pytest -q"}
                ),
                encoding="utf-8",
            )
            args = SimpleNamespace(
                developer_model=None,
                reviewer_model=None,
                max_rounds=2,
                mode="semi_auto",
                test_command=None,
                agent=None,
                dry_run=None,
            )
            config = build_task_config_from_args(paths, args, "Goal")
            self.assertEqual(config.max_rounds, 2)
            self.assertEqual(config.mode, "semi_auto")
            self.assertEqual(config.test_command, "pytest -q")

    def test_omitted_mode_keeps_project_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            paths.ensure_root()
            paths.project_config_path().write_text(
                json.dumps({"mode": "auto"}),
                encoding="utf-8",
            )
            args = SimpleNamespace(
                developer_model=None,
                reviewer_model=None,
                max_rounds=None,
                mode=None,
                test_command=None,
                agent=None,
                dry_run=None,
            )
            config = build_task_config_from_args(paths, args, "Goal")
            self.assertEqual(config.mode, "auto")
