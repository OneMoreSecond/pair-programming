# Title

Load pair workflow defaults from a project config file

## Status

done

## Priority

high

## Type

feature

## Summary

Support project-level pair workflow defaults from a config file in the repository.

## Scope

- Define the project config file location and shape
- Load default values such as models, mode, and test command
- Keep missing config files optional

## Out of Scope

- Interactive editing
- Remote config sync

## Acceptance Criteria

- The workflow can read project-level default configuration values
- Missing config files do not break existing behavior

## Notes

- Child ticket of `TICK-0012-configuration-and-default-policy-management.md`.
- The workflow now reads an optional project config file from `.opencode/pair/config.json` for default values.
