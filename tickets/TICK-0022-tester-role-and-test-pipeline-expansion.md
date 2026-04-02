# Title

Introduce a tester role and expand test pipeline capabilities

## Status

done

## Priority

medium

## Type

feature

## Summary

Grow the workflow beyond ad hoc test command execution by introducing a clearer tester role and richer test-aware pipeline behavior.

## Scope

- Define a dedicated tester role or phase
- Improve how test results are collected and surfaced
- Support richer test-oriented artifacts beyond a minimal summary

## Out of Scope

- Full CI integration across all platforms
- Performance and load testing infrastructure

## Acceptance Criteria

- Test execution responsibilities are more clearly modeled
- Reviewer and developer receive clearer test context
- The workflow can evolve beyond a single optional test command

## Notes

- This requirement appears in the architecture and advanced rollout phases.
- The workflow now has an explicit tester-phase artifact (`tester-note.md`) and passes tester context into review.
