# Title

Add observability, metrics, and local reporting for pair tasks

## Status

done

## Priority

medium

## Type

feature

## Summary

Track workflow performance and reliability with task-level metrics and local reporting so the team can evaluate whether the workflow is improving real development outcomes.

## Scope

- Record task and round timings
- Track reviewer outcomes and blocker counts
- Summarize retry, failure, and intervention patterns
- Provide local reporting or inspection views for these metrics

## Out of Scope

- Cloud observability platforms
- Organization-wide analytics dashboards

## Acceptance Criteria

- Key workflow metrics are recorded locally
- Users can inspect task reliability and round behavior over time
- The metrics align with the success criteria described in the operations design

## Notes

- This requirement is rooted in `operations.md` and `state.md`.
- The CLI now includes a local `metrics` command that summarizes rounds, blocker counts, reviewer attempts, and intervention patterns from task state.
