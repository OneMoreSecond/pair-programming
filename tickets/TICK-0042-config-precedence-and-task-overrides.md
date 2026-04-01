# Title

Implement config precedence and task-level overrides

## Status

todo

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
