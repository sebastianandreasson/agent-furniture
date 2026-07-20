# ADR 0001: Python source and generated artifact contracts

- Status: accepted
- Date: 2026-07-18

## Context

Furniture geometry must remain editable by coding agents while exact CAD exports and a browser viewer
serve different consumers. Duplicating furniture geometry in JSON or React would create competing
sources of truth and stale previews.

## Decision

Frozen Python design specifications and CadQuery model code are the source of furniture geometry.
Design JSON files select a family, give each independently buildable variant a stable identity, and
optionally override Python defaults. Standard builds generate a manifest and catalog as the artifact
contract. The web studio groups builds by catalog family metadata and switches their complete
artifact sets; it never hard-codes furniture families or assembles variant geometry in React.

## Consequences

- A clean checkout can reproduce every artifact from text sources.
- Generated artifacts remain ignored by Git.
- Manifest/catalog compatibility must be covered by Python and TypeScript tests.
- Browser placement is stored separately and never changes source geometry.
