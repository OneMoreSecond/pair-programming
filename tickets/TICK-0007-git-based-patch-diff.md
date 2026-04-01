# Title

Replace snapshot patch generation with git-based diff

## Status

done

## Priority

high

## Type

feature

## Summary

Improve review quality and patch accuracy by generating `patch.diff` from git state instead of raw workspace snapshots.

## Scope

- Define the git diff baseline for each round
- Replace or augment snapshot-based diff generation
- Handle untracked files and modified files consistently
- Preserve reviewer-readable diff output

## Out of Scope

- Automatic commit creation
- Complex branch management

## Acceptance Criteria

- `patch.diff` is produced from git-aware diff logic
- New files and modified files appear correctly in review context
- The workflow continues to work in normal dirty worktrees

## Notes

- This is one of the most important upgrades for non-dry-run reliability.
- `patch.diff` now uses git-aware diff generation for tracked and untracked files.
