from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

from .utils import ensure_parent


PLACEHOLDER_RE = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


def render_template(template_text: str, values: Dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return values.get(key, "")

    return PLACEHOLDER_RE.sub(replace, template_text)


def render_prompt_to_file(
    template_path: Path, output_path: Path, values: Dict[str, str]
) -> Path:
    template_text = template_path.read_text(encoding="utf-8")
    rendered = render_template(template_text, values)
    ensure_parent(output_path)
    output_path.write_text(rendered, encoding="utf-8")
    return output_path
