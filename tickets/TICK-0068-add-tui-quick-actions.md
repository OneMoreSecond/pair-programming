# Title

Add TUI workflow quick actions

## Status

todo

## Priority

medium

## Type

feature

## Summary

Add shortcut actions to the TUI so common next steps are easier than typing repeated raw commands.

## Scope

- Add quick actions such as continue, inspect review, approve-and-stop, or blocking-only focus
- Wire quick actions to existing workflow commands or state transitions
- Keep action behavior consistent with existing CLI semantics

## Out of Scope

- Complex keyboard remapping
- New workflow policies unrelated to existing commands

## Acceptance Criteria

- Common next actions are easier than typing raw commands repeatedly
- TUI actions preserve the same underlying task behavior as the CLI
- Action labels clearly communicate what will happen

## Notes

- This milestone should build on the earlier TUI read-only views.
