import tempfile
import unittest
from pathlib import Path

from opencode_pair.prompts import render_prompt_to_file, render_template


class PromptTests(unittest.TestCase):
    def test_render_template_replaces_placeholders(self) -> None:
        rendered = render_template(
            "Hello {{ name }} from {{place}}", {"name": "dev", "place": "repo"}
        )
        self.assertEqual(rendered, "Hello dev from repo")

    def test_render_prompt_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template = root / "template.md"
            output = root / "nested" / "output.md"
            template.write_text("Task: {{ goal }}\n", encoding="utf-8")
            render_prompt_to_file(template, output, {"goal": "Ship MVP"})
            self.assertEqual(output.read_text(encoding="utf-8"), "Task: Ship MVP\n")
