# Title

Implement CLI, state handling, and MVP workflow skeleton

## Status

done

## Priority

high

## Type

feature

## Summary

Build the first runnable orchestrator skeleton with task initialization, state persistence, round directories, prompt rendering, and developer/reviewer execution flow.

## Scope

- Add Python package under `src/opencode_pair/`
- Implement `start`, `status`, `resume`, and `review`
- Persist `config.json` and `state.json`
- Generate round-level artifacts and logs

## Out of Scope

- Native `opencode pair` integration
- Advanced recovery and strategy policies

## Acceptance Criteria

- CLI can initialize a task and write state
- Dry-run mode can complete one round
- Round artifacts are written under `.opencode/pair/tasks/<task-id>/`

## Notes

- Implemented as a Python MVP CLI with dry-run and non-dry-run support.
