from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


TITLE_RE = re.compile(r"^# Review Result\s*$", re.MULTILINE)
STATUS_RE = re.compile(
    r"^Status:\s*(APPROVED|CHANGES_REQUESTED)\s*$", re.IGNORECASE | re.MULTILINE
)
BLOCKING_SECTION_RE = re.compile(
    r"^## Blocking\s*$\n(?P<body>.*?)(?:^## |\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
SUMMARY_SECTION_RE = re.compile(
    r"^## Summary\s*$\n(?P<body>.*?)(?:^## |\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


class ReviewProtocolError(ValueError):
    pass


@dataclass
class ReviewResult:
    status: str
    blocking_count: int
    summary: str


def parse_review_text(text: str) -> ReviewResult:
    if not TITLE_RE.search(text):
        raise ReviewProtocolError(
            "review markdown is missing the '# Review Result' title"
        )

    status_match = STATUS_RE.search(text)
    if not status_match:
        raise ReviewProtocolError("review markdown is missing a valid Status field")

    status = status_match.group(1).upper()
    blocking_match = BLOCKING_SECTION_RE.search(text)
    if not blocking_match:
        raise ReviewProtocolError(
            "review markdown is missing the '## Blocking' section"
        )

    body = blocking_match.group("body")
    bullets = [
        line.strip() for line in body.splitlines() if line.strip().startswith("-")
    ]
    if not bullets:
        raise ReviewProtocolError(
            "review markdown must include at least one bullet in '## Blocking'"
        )
    meaningful = [line for line in bullets if line.lower() not in {"- none.", "- none"}]
    blocking_count = len(meaningful)

    summary_match = SUMMARY_SECTION_RE.search(text)
    if not summary_match:
        raise ReviewProtocolError("review markdown is missing the '## Summary' section")
    summary_body = summary_match.group("body").strip()
    if not summary_body:
        raise ReviewProtocolError(
            "review markdown must include non-empty summary content"
        )
    summary = summary_body.splitlines()[0].strip()

    return ReviewResult(status=status, blocking_count=blocking_count, summary=summary)


def parse_review_file(path: Path) -> ReviewResult:
    return parse_review_text(path.read_text(encoding="utf-8"))
