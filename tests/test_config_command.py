import io
import unittest
from contextlib import redirect_stdout

from opencode_pair.cli import print_config


class ConfigCommandTests(unittest.TestCase):
    def test_print_config_text(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = print_config(False)
        output = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Pair workflow defaults:", output)
        self.assertIn("mode:", output)

    def test_print_config_json(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = print_config(True)
        output = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn('"mode":', output)
        self.assertIn('"reviewer_retry_limit":', output)
