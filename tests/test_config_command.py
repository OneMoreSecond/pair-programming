import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from opencode_pair.cli import print_config
from opencode_pair.paths import PairPaths


class ConfigCommandTests(unittest.TestCase):
    def test_print_config_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = print_config(paths, False)
            output = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("Pair workflow defaults:", output)
            self.assertIn("mode:", output)

    def test_print_config_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = PairPaths(Path(tmp))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = print_config(paths, True)
            output = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn('"mode":', output)
            self.assertIn('"reviewer_retry_limit":', output)
