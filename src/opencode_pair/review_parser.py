from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


STATUS_RE = re.compile(
    r"^Status:\s*(APPROVED|CHANGES_REQUESTED)\s*$", re.IGNORECASE | re.MULTILINE
)
BLOCKING_SECTION_RE = re.compile(
    r"^## Blocking\s*$\n(?P<body>.*?)(?:^## |\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


@dataclass
class ReviewResult:
    status: str
    blocking_count: int
    summary: str


def parse_review_text(text: str) -> ReviewResult:
    status_match = STATUS_RE.search(text)
    if not status_match:
        raise ValueError("review markdown is missing a valid Status field")

    status = status_match.group(1).upper()
    blocking_count = 0

    blocking_match = BLOCKING_SECTION_RE.search(text)
    if blocking_match:
        body = blocking_match.group("body")
        bullets = [
            line.strip() for line in body.splitlines() if line.strip().startswith("-")
        ]
        meaningful = [
            line for line in bullets if line.lower() not in {"- none.", "- none"}
        ]
        blocking_count = len(meaningful)

    summary = ""
    if "## Summary" in text:
        summary = (
            text.split("## Summary", 1)[1].strip().splitlines()[0]
            if text.split("## Summary", 1)[1].strip()
            else ""
        )

    return ReviewResult(status=status, blocking_count=blocking_count, summary=summary)


def parse_review_file(path: Path) -> ReviewResult:
    return parse_review_text(path.read_text(encoding="utf-8"))
