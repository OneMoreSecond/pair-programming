# Title

Build a real-task regression and prompt evaluation harness

## Status

done

## Priority

medium

## Type

feature

## Summary

Create a repeatable way to run representative real tasks against the workflow so changes to prompts, policies, or orchestration can be evaluated with evidence.

## Scope

- Define a set of representative pair workflow tasks
- Record expected qualitative or structural outcomes
- Compare prompt and workflow revisions against those tasks

## Out of Scope

- Full benchmark lab for all repositories
- Automated provider cost optimization

## Acceptance Criteria

- The project has a repeatable set of real-task validation cases
- Prompt and workflow changes can be evaluated against those cases
- Regression signals are visible when behavior degrades

## Notes

- This follows directly from the design guidance to validate each phase with real tasks.
- Implemented via an `eval` CLI command that checks representative task files for baseline structural signals.
- Default evaluation target is `examples/basic-task.md`, with support for repeated `--task-file` inputs and JSON output.
