# Title

Add pyproject versioning workflow to AGENTS.md

## Status

done

## Priority

medium

## Type

process

## Summary

Define a version management workflow in `AGENTS.md` so `pyproject.toml` versioning is updated in a consistent way after completing a batch of tickets.

## Scope

- Document version management rules in `AGENTS.md`
- Define what counts as a completed batch of tickets
- Define when and how `pyproject.toml` version should be incremented
- Clarify how version bumps relate to ticket completion and commits

## Out of Scope

- Automated release publishing
- Semantic release tooling integration

## Acceptance Criteria

- `AGENTS.md` documents the project versioning workflow
- The workflow specifies when to bump the version after ticket batches
- The workflow references `pyproject.toml` as the version source

## Notes

- This is a process rule and should be documented before being enforced in implementation work.
- `AGENTS.md` now defines `pyproject.toml` as the package version source and requires a version bump after each completed roadmap batch.
