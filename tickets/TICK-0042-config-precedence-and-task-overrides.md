# Title

Implement config precedence and task-level overrides

## Status

done

## Priority

high

## Type

feature

## Summary

Apply a clear precedence model across CLI flags, task config, project config, and built-in defaults.

## Scope

- Define the precedence order in code
- Apply task-level override handling consistently
- Keep behavior compatible with existing task state

## Out of Scope

- Interactive editing surfaces
- Secret management

## Acceptance Criteria

- The workflow consistently applies documented precedence rules
- Task-level overrides work without breaking project defaults

## Notes

- Child ticket of `TICK-0012-configuration-and-default-policy-management.md`.
- `start` now builds task config using a documented precedence model where CLI flags override project defaults and built-in defaults.
- Follow-up ticket: `TICK-0045-distinguish-cli-defaults-from-explicit-args.md` for remaining parser-default ambiguity.
