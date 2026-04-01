# Title

Harden review validation, parsing, and retry behavior

## Status

todo

## Priority

high

## Type

feature

## Summary

Strengthen the reviewer output pipeline so malformed or incomplete review files are detected, retried, and surfaced clearly.

## Scope

- Validate required `review.md` sections more robustly
- Retry reviewer execution on invalid output when policy allows
- Distinguish protocol errors from task-level review rejections
- Improve parser behavior and error reporting

## Out of Scope

- Complex AST-based protocol validation
- Replacing markdown with a JSON-only format

## Acceptance Criteria

- Invalid reviewer output is detected reliably
- Retry behavior is predictable and documented
- Users can tell whether a failure is a protocol problem or a real review result

## Notes

- This extends the minimal parser currently implemented in the MVP.
