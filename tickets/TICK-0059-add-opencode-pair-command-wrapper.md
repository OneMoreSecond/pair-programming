# Title

Add an `opencode pair` command wrapper for the existing workflow CLI

## Status

done

## Priority

high

## Type

feature

## Summary

Provide a native-feeling `opencode pair` entry path that forwards to the existing workflow commands without changing orchestrator behavior.

## Scope

- Define a wrapper command shape for `opencode pair`
- Forward native-style subcommands to the current workflow implementation
- Keep existing `opencode-pair` behavior available during the transition

## Out of Scope

- Rewriting the workflow engine
- Removing the standalone CLI entry point

## Acceptance Criteria

- A native-style `opencode pair` command path exists in this project
- Core actions still execute through the existing workflow logic
- The wrapper preserves current task behavior and exit semantics

## Notes

- This is the first implementation step toward `TICK-0011`.
- Implemented with an `opencode` wrapper entry point that requires the `pair` prefix and forwards remaining arguments into the existing CLI.
