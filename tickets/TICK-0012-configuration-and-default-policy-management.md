# Title

Add configuration and default policy management for the pair workflow

## Status

done

## Priority

medium

## Type

feature

## Summary

Support project-level and task-level configuration for models, modes, test commands, policy defaults, and precedence rules.

## Scope

- Add a config viewing and editing surface
- Support project defaults and task overrides
- Define parameter precedence between CLI, task config, project config, and system defaults
- Cover mode and policy defaults such as max rounds and blocking issue limits

## Out of Scope

- Remote configuration sync
- Secret management for external providers

## Acceptance Criteria

- Users can inspect pair workflow defaults
- The workflow consistently applies documented config precedence rules
- Common defaults can be set without editing source code

## Notes

- This includes the configuration responsibilities described across `cli.md`, `architecture.md`, and `operations.md`.
- Child tickets:
  - `TICK-0040-config-inspect-command.md`
  - `TICK-0041-project-config-file-loading.md`
  - `TICK-0042-config-precedence-and-task-overrides.md`
- Current implementation now supports config inspection, project defaults, and precedence handling. Remaining parser-default ambiguity is tracked separately in `TICK-0045-distinguish-cli-defaults-from-explicit-args.md`.
