# Title

Expand status, review, and resume controls for better recovery and inspection

## Status

done

## Priority

high

## Type

feature

## Summary

Improve the query and recovery surface so users can inspect tasks more deeply and resume from explicit tasks, rounds, or phases.

## Scope

- Support richer `status` output such as `--json` and `--verbose`
- Support selecting a task by ID
- Support resuming from an explicit phase or round when safe
- Improve review inspection across rounds

## Out of Scope

- Full interactive TUI browsing
- Remote task management

## Acceptance Criteria

- Users can inspect a chosen task in more detail
- Users can resume from more than just the implicit current state when supported
- Recovery guidance is clearer for interrupted tasks

## Notes

- This consolidates advanced status and recovery capabilities from `cli.md` and `workflow.md`.
- The CLI now supports `status --json/--verbose`, task-targeted inspection, and `resume --from` for safe phase selection.
