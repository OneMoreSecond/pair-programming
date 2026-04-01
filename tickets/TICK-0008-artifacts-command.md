# Title

Add a CLI command to list task and round artifacts

## Status

todo

## Priority

medium

## Type

feature

## Summary

Provide a dedicated command for listing round-level artifacts so users can quickly inspect logs, prompts, notes, diffs, and reviews.

## Scope

- Add an `artifacts` subcommand
- Support listing latest round artifacts
- Support selecting a specific round
- Print stable relative paths

## Out of Scope

- Interactive file opening
- TUI artifact browser

## Acceptance Criteria

- `artifacts` lists files for the current task
- Users can target a specific round
- Output is stable and easy to scan

## Notes

- This is useful for debugging and review-heavy workflows.
