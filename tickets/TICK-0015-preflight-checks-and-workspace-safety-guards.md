# Title

Add preflight checks and workspace safety guards

## Status

done

## Priority

high

## Type

feature

## Summary

Run lightweight validation before starting a task so the workflow can warn about environment issues, dirty worktrees, missing prompts, or unavailable test commands.

## Scope

- Check repository accessibility and writability
- Detect dirty workspace conditions that may affect review quality
- Validate prompt template availability
- Validate configured test command presence when possible
- Surface warnings and recommended next actions

## Out of Scope

- Perfect environment validation for every ecosystem
- Hard-blocking all non-ideal repositories

## Acceptance Criteria

- Starting a task performs documented preflight checks
- Common environment risks are reported before execution begins
- Users receive actionable warnings instead of opaque failures

## Notes

- This requirement comes primarily from `operations.md` and `ux.md`.
- `start` now runs a lightweight preflight and reports warnings for dirty worktrees and missing test executables.
