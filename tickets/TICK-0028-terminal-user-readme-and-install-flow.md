# Title

Rewrite README for terminal users and add install instructions

## Status

done

## Priority

high

## Type

docs

## Summary

Update `README.md` so it is written for terminal users, includes installation instructions, and avoids requiring explicit `PYTHONPATH` setup in the normal usage path.

## Scope

- Rewrite `README.md` from the perspective of end users running commands in a terminal
- Add installation instructions for the package or CLI entrypoint
- Update examples so normal usage does not require explicit `PYTHONPATH`
- Keep development-only workflow details separate from basic user-facing instructions

## Out of Scope

- Packaging to external package registries
- Full cross-platform installer automation

## Acceptance Criteria

- `README.md` clearly explains how a terminal user installs and runs the tool
- Normal usage examples do not require setting `PYTHONPATH`
- Development-only instructions remain available but are clearly distinguished

## Notes

- This requirement improves first-run usability for terminal users.
- `README.md` now leads with terminal-user install and usage flow based on `python3 -m pip install -e .` and `opencode-pair`.
