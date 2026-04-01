import unittest

from opencode_pair.review_parser import ReviewProtocolError, parse_review_text


class ReviewParserTests(unittest.TestCase):
    def test_parse_changes_requested_review(self) -> None:
        result = parse_review_text(
            """# Review Result
Status: CHANGES_REQUESTED

## Blocking
- `src/foo.py:1` Broken path
- `src/bar.py:2` Missing test

## Non-blocking
- None.

## Suggested Fix Plan
1. Fix the path

## Summary
Still blocked by correctness issues.
"""
        )
        self.assertEqual(result.status, "CHANGES_REQUESTED")
        self.assertEqual(result.blocking_count, 2)
        self.assertEqual(result.summary, "Still blocked by correctness issues.")

    def test_parse_approved_review(self) -> None:
        result = parse_review_text(
            """# Review Result
Status: APPROVED

## Blocking
- None.

## Non-blocking
- None.

## Summary
Looks good.
"""
        )
        self.assertEqual(result.status, "APPROVED")
        self.assertEqual(result.blocking_count, 0)
        self.assertEqual(result.summary, "Looks good.")

    def test_missing_status_raises(self) -> None:
        with self.assertRaises(ReviewProtocolError):
            parse_review_text("# Review Result\n\n## Blocking\n- None.\n")

    def test_missing_summary_raises(self) -> None:
        with self.assertRaises(ReviewProtocolError):
            parse_review_text(
                """# Review Result
Status: APPROVED

## Blocking
- None.

## Non-blocking
- None.
"""
            )

    def test_empty_blocking_section_raises(self) -> None:
        with self.assertRaises(ReviewProtocolError):
            parse_review_text(
                """# Review Result
Status: APPROVED

## Blocking

## Summary
Looks good.
"""
            )
