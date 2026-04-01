# Title

Ensure `--workdir` defaults to the current directory

## Status

done

## Priority

low

## Type

feature

## Summary

Use the current directory as the default workdir when `--workdir` is not provided.

## Scope

- Confirm CLI default behavior uses the current directory
- Keep command examples consistent with that default

## Out of Scope

- Auto-detecting repository roots above the current directory
- Persisting a last-used working directory

## Acceptance Criteria

- CLI defaults to `.` when `--workdir` is omitted
- Documentation does not contradict the implemented default

## Notes

- This behavior is already present in `src/opencode_pair/cli.py` and does not require further implementation.
