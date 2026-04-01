import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from opencode_pair.cli import build_effective_defaults, print_config
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
