# Title

Align the command surface with the pair CLI design

## Status

done

## Priority

medium

## Type

feature

## Summary

Bring command names, help text, and user-facing examples in line with the `opencode pair` CLI design while preserving working behavior.

## Scope

- Align command naming and help output with `docs/design/cli.md`
- Update user-facing examples to prefer the native-style invocation path
- Preserve compatibility guidance for the existing CLI during migration

## Out of Scope

- New workflow features unrelated to command naming
- Full UX redesign beyond the command surface

## Acceptance Criteria

- Help text and docs reflect the native command surface
- Users can follow examples from the updated docs without ambiguity
- Migration guidance for the standalone command remains documented

## Notes

- This ticket focuses on command-surface consistency after the wrapper exists.
- Help output now supports the native-style program name, and README examples now prefer `opencode pair` while keeping `opencode-pair` documented as a compatibility path.
