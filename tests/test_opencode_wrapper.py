import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from opencode_pair.opencode_wrapper import main


class OpencodeWrapperTests(unittest.TestCase):
    def test_wrapper_requires_pair_prefix(self) -> None:
        buf = io.StringIO()
        with redirect_stderr(buf):
            code = main(["status"])
        self.assertEqual(code, 2)
        self.assertIn("opencode pair", buf.getvalue())

    def test_wrapper_forwards_pair_subcommands(self) -> None:
        with patch(
            "opencode_pair.opencode_wrapper.pair_main", return_value=7
        ) as mock_main:
            code = main(["pair", "status", "--json"])
        self.assertEqual(code, 7)
        mock_main.assert_called_once_with(
            ["status", "--json"], prog_name="opencode pair"
        )
