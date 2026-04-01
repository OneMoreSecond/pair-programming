# Title

Add prompt customization, project profiles, and version management

## Status

todo

## Priority

medium

## Type

feature

## Summary

Allow the workflow to evolve prompts safely across projects by supporting versioning, project-level overrides, and domain-specific prompt profiles.

## Scope

- Version prompt templates explicitly
- Support project-level prompt overrides cleanly
- Support different prompt profiles for frontend, backend, or infrastructure contexts
- Keep prompt changes compatible with task state and protocol expectations

## Out of Scope

- Automatic prompt optimization services
- Provider-specific secret management

## Acceptance Criteria

- Prompt versions are tracked explicitly
- Projects can customize prompts without patching source code directly
- Prompt profile selection is documented and repeatable

## Notes

- This requirement grows out of `prompts.md` and `protocol.md`.
