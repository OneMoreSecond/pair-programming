# Title

Support manual intervention controls between workflow rounds

## Status

todo

## Priority

medium

## Type

feature

## Summary

Allow users to pause between rounds and intentionally influence the next step, such as editing review output, skipping non-blocking issues, changing models, or adjusting limits.

## Scope

- Support safe pause points between rounds
- Allow user edits to review artifacts before resuming
- Allow users to skip non-blocking issues or focus only on blockers
- Allow users to change models or round settings before continuing

## Out of Scope

- Fully interactive conversational control loop inside the orchestrator
- Multi-user concurrent intervention

## Acceptance Criteria

- Users can intervene safely between rounds
- The next round reflects the selected intervention policy
- Intervention actions are visible in task state or artifacts

## Notes

- This groups together the user intervention needs called out in `ux.md` and `workflow.md`.
