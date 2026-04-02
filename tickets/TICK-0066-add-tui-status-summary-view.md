# Title

Add a TUI status summary view

## Status

todo

## Priority

high

## Type

feature

## Summary

Provide a terminal-friendly status screen that surfaces the current task, round, and next-step context more clearly than raw text output.

## Scope

- Render current role, task status, and round information in a TUI-oriented layout
- Reuse existing task state rather than introducing a new state source
- Keep the first TUI view read-only

## Out of Scope

- Artifact browsing interactions
- Quick action execution

## Acceptance Criteria

- Users can inspect task progress through a TUI-oriented status view
- The view reflects the same underlying task state as existing CLI commands
- The first TUI screen remains stable on desktop and narrow terminal widths

## Notes

- This is the first milestone extracted from `TICK-0020`.
