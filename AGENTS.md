# AGENTS.md

## Project Workflow

This repository uses a ticket-driven workflow.

### Core Rules

1. Every requirement must be recorded as a standalone markdown ticket.
2. Only ticketed requirements may be implemented.
3. Verbal, chat-only, or undocumented requests must not be implemented directly.
4. If a new issue is discovered during development and it is not part of the current ticket, create a new ticket for it.
5. If a requirement is too large to implement safely in one pass, it must be split into smaller child tickets before development starts.

## Ticket Rules

### Ticket Location

All tickets live under `tickets/`.

### Ticket Naming

Use this filename format:

```text
TICK-XXXX-short-kebab-name.md
```

Example:

```text
TICK-0001-ticket-driven-project-management.md
```

### Required Ticket Sections

Each ticket must contain at least:

- `Title`
- `Status`
- `Priority`
- `Type`
- `Summary`
- `Scope`
- `Out of Scope`
- `Acceptance Criteria`
- `Notes`

### Ticket Status Values

Use only these statuses:

- `todo`
- `in_progress`
- `blocked`
- `done`

### Ticket Relationships

If a ticket is split, the parent ticket must list its child tickets.

If work reveals unrelated follow-up tasks, add them under `Notes` and create a new standalone ticket.

## Development Rules

Before starting work:

1. Confirm there is a ticket.
2. Confirm the ticket scope is small enough.
3. If not, split it first.

During work:

1. Stay within the current ticket scope.
2. Do not silently include unrelated fixes.
3. Record discovered follow-up issues as new tickets.

After work:

1. Update the ticket status.
2. Update acceptance notes if needed.
3. Link any follow-up tickets created during implementation.

## Roadmap Workflow

When there are unfinished tickets:

1. Scan all incomplete tickets under `tickets/`.
2. Record their priority ordering in `tickets/ROADMAP.md`.
3. Start work from the highest active priority bucket first.
4. Only split a large ticket after it has been selected for implementation.
5. Complete and commit one ticket at a time.

### Roadmap Priority Buckets

Use these buckets in `tickets/ROADMAP.md`:

- `P0`: critical workflow reliability and unblockers
- `P1`: near-term usability and recovery improvements
- `P2`: medium-term workflow management improvements
- `P3`: evaluation, customization, and platform hardening
- `P4`: advanced product capabilities and long-term expansion

### Commit Rules

- Each completed ticket must have its own git commit.
- The commit message must include the ticket ID.
- Do not bundle multiple completed tickets into one commit.

## Current Source Of Truth

- Process rules: `AGENTS.md`
- Active and completed requirements: `tickets/`
- Product and technical design: `docs/design/`
