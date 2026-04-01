# Title

Integrate the workflow as a native `opencode pair` command surface

## Status

todo

## Priority

high

## Type

feature

## Summary

Move the MVP from a standalone Python CLI shape toward the intended `opencode pair` command experience described in the design documents.

## Scope

- Define how the workflow plugs into the `opencode` command surface
- Align command naming and invocation with the design docs
- Preserve the current orchestrator behavior during integration

## Out of Scope

- Full redesign of the workflow engine
- Web or remote interfaces

## Acceptance Criteria

- The workflow can be invoked through a native `opencode pair` command surface
- Existing core actions remain available after integration
- Documentation reflects the new invocation path

## Notes

- The current MVP still runs as `python -m opencode_pair` / `opencode-pair`.
