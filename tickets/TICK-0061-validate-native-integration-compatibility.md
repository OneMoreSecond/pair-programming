# Title

Validate native integration compatibility with existing workflow behavior

## Status

done

## Priority

medium

## Type

feature

## Summary

Verify that the native-style integration preserves the current workflow behavior, outputs, and recovery flows.

## Scope

- Add tests covering the native command path for core actions
- Verify existing status, resume, review, and artifact flows still work
- Document any intentional differences from the standalone CLI

## Out of Scope

- Broad new end-to-end benchmarking
- Multi-reviewer or TUI features

## Acceptance Criteria

- Automated tests cover the native invocation path
- Existing core actions remain available after integration
- Any compatibility caveats are explicitly documented

## Notes

- This ticket closes the loop on the preservation requirement from `TICK-0011`.
- Added wrapper-path tests for status, artifacts, actionable review errors, and native help output.
- Current documented compatibility caveat: `opencode pair` is still provided by this project wrapper rather than an upstream built-in command.
