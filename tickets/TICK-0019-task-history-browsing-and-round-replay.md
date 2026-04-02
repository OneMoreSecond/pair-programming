# Title

Add task history browsing and round replay support

## Status

done

## Priority

medium

## Type

feature

## Summary

Make past rounds easier to inspect and replay so users can understand how a task evolved and revisit prior artifacts.

## Scope

- Browse round history for a task
- Replay or reconstruct the sequence of round artifacts
- Surface links to prompts, notes, diffs, and reviews across rounds

## Out of Scope

- Full visual timeline UI
- Time-travel mutation of past rounds

## Acceptance Criteria

- Users can inspect more than just the latest round
- The workflow can present a stable round-by-round history
- Replay or review of past task progression is supported in a documented way

## Notes

- This is separate from the narrower `artifacts` command ticket.
- The CLI now includes a `history` command for stable round-by-round inspection of task progression and artifact references.
