# Title

Bump project version after completing the P3 roadmap batch

## Status

done

## Priority

high

## Type

release

## Summary

Increase the project version in `pyproject.toml` after completing the current P3 roadmap batch.

## Scope

- Bump `[project].version` in `pyproject.toml`
- Record that the bump corresponds to the completed P3 batch

## Out of Scope

- Publishing a release
- Tagging or changelog automation

## Acceptance Criteria

- `pyproject.toml` version is incremented
- The change is recorded as a standalone ticketed change

## Notes

- Patch version is sufficient for this batch.
