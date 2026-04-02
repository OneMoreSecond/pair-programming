# Title

Distinguish CLI defaults from explicit user arguments

## Status

done

## Priority

high

## Type

feature

## Summary

Separate argparse defaults from explicit user input so config precedence can reliably tell whether a CLI value should override project defaults.

## Scope

- Adjust parser or argument handling to preserve whether a value was provided explicitly
- Cover flags like `mode`, `max_rounds`, and other optional parameters
- Keep existing CLI behavior stable for users

## Out of Scope

- Reworking the entire CLI framework
- Interactive prompting

## Acceptance Criteria

- The workflow can distinguish omitted CLI values from explicit values equal to the default
- Config precedence behaves correctly for project defaults versus explicit CLI overrides

## Notes

- This was discovered while implementing `TICK-0042-config-precedence-and-task-overrides.md`.
- The `start` command now preserves omitted values as `None`, allowing config precedence to distinguish project defaults from explicit CLI overrides.
