# Title

Create concrete developer and reviewer prompt template files

## Status

done

## Priority

high

## Type

feature

## Summary

Turn the prompt design into concrete template files that the orchestrator can render and pass into developer and reviewer sessions.

## Scope

- Add `.opencode/pair/prompts/developer.md`
- Add `.opencode/pair/prompts/reviewer.md`
- Support placeholder-driven rendering from orchestrator code

## Out of Scope

- Prompt optimization for all project types
- Few-shot tuning for difficult tasks

## Acceptance Criteria

- Both default prompt templates exist
- Templates include required workflow placeholders
- Templates can be rendered by the MVP code

## Notes

- Implemented in `.opencode/pair/prompts/` and `src/opencode_pair/prompts.py`.
