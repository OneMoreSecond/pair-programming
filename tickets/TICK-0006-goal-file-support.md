# Title

Support reading task goals from a markdown file

## Status

todo

## Priority

medium

## Type

feature

## Summary

Allow the CLI to accept a goal from a file so larger task descriptions can be stored, reviewed, and reused more easily.

## Scope

- Add `--goal-file` support to `start`
- Validate that the file exists and is readable
- Make `--goal` and `--goal-file` mutually exclusive or clearly prioritized
- Document usage in `README.md`

## Out of Scope

- Multi-file goal composition
- External ticket parser integration

## Acceptance Criteria

- `start` accepts `--goal-file <path>`
- The loaded file content is stored as the task goal
- CLI output clearly reports file read errors

## Notes

- This was identified as a natural next usability improvement for real usage.
