# Title

Add a CLI command to inspect pair workflow configuration

## Status

done

## Priority

high

## Type

feature

## Summary

Provide a read-only CLI surface for inspecting the effective pair workflow configuration and defaults.

## Scope

- Add a `config` subcommand
- Show current default configuration values
- Support stable terminal output

## Out of Scope

- Editing configuration values
- Project config file loading

## Acceptance Criteria

- Users can inspect workflow defaults from the CLI
- Output is stable and understandable

## Notes

- Child ticket of `TICK-0012-configuration-and-default-policy-management.md`.
- The CLI now includes a read-only `config` command with text and JSON output for built-in defaults.
