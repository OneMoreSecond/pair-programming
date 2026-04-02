# Title

Add explicit stop and cancel controls for running pair tasks

## Status

done

## Priority

medium

## Type

feature

## Summary

Provide a user-facing way to stop an active workflow and persist the task as cancelled without losing artifacts.

## Scope

- Add a stop or cancel command
- Record cancellation state and time in task metadata
- Preserve all existing round artifacts and logs
- Allow future recovery or branching decisions from the cancelled task state

## Out of Scope

- Force-killing external infrastructure beyond the local workflow process
- Deleting task history

## Acceptance Criteria

- Users can stop a task intentionally
- Task state persists as `cancelled`
- Existing artifacts remain available for inspection

## Notes

- This requirement comes from the CLI and workflow design docs.
- The CLI now supports `stop`, and cancelled tasks retain their artifacts and cancellation metadata.
