# Title

Improve CLI output and error handling for real usage

## Status

done

## Priority

medium

## Type

feature

## Summary

Improve command-line usability with clearer errors, better summaries, and more forgiving argument handling where appropriate.

## Scope

- Improve user-facing error messages
- Continue smoothing argument parsing behavior
- Make status and resume outputs more actionable
- Document common failure modes and next steps

## Out of Scope

- Full TUI redesign
- Localization

## Acceptance Criteria

- Common CLI errors produce actionable output
- Real users can recover from common mistakes more easily
- README reflects the improved command behavior

## Notes

- A related argument parsing bug around `--workdir` was already fixed, but broader usability improvements remain.
- Common no-task and no-artifact CLI failures now return clearer, actionable next steps.
