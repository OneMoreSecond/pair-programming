# Title

Adopt roadmap-driven ticket execution workflow

## Status

done

## Priority

high

## Type

process

## Summary

Extend the repository process so incomplete tickets are scanned into a shared roadmap, prioritized explicitly, and executed in priority order with one commit per completed ticket.

## Scope

- Update `AGENTS.md` with the roadmap-driven execution rules
- Add `tickets/ROADMAP.md` with priorities for incomplete tickets
- Begin executing P0 tickets in order
- Record the completed ticket ID in each commit message

## Out of Scope

- Reprioritizing completed tickets
- Splitting large backlog tickets before they are selected for implementation

## Acceptance Criteria

- `AGENTS.md` documents the roadmap-driven execution workflow
- `tickets/ROADMAP.md` lists all incomplete tickets by priority bucket
- P0 ticket execution begins in priority order
- Each completed ticket is committed separately with the ticket ID in the commit message

## Notes

- This ticket formalizes the current execution loop for backlog work.
- `AGENTS.md` and `tickets/ROADMAP.md` now record the roadmap-driven execution process.
