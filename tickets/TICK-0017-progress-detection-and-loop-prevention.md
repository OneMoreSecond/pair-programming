# Title

Add progress detection and loop prevention policies

## Status

todo

## Priority

high

## Type

feature

## Summary

Detect when the workflow is failing to make progress and stop infinite or low-value iteration loops automatically.

## Scope

- Track whether diffs are changing between rounds
- Compare blocking issue counts across rounds
- Detect repeated unresolved blocking issues
- Escalate to `waiting_user` when progress stalls

## Out of Scope

- Sophisticated semantic scoring or LLM-based quality prediction
- Cross-task historical learning

## Acceptance Criteria

- The workflow can detect repeated low-progress rounds
- Repeated blocker patterns can trigger manual intervention
- Users receive a clear explanation for why automatic progress stopped

## Notes

- This requirement comes from the state machine and operations design.
