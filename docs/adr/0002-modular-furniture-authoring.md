# ADR 0002: Modular furniture authoring through catalogs and schedules

- Status: accepted
- Date: 2026-07-18

## Context

Early furniture families constructed every `Part`, placement, fastener, drill operation, and joint in
one model module. That kept prototypes direct but made repeated validation, stable identifiers, and
subassembly reuse difficult as designs became more detailed.

## Decision

Furniture families author through one public `querycad.furniture` interface:

- a design specification maps and validates user values;
- a derived layout centralizes shared spatial calculations;
- a part catalog defines physical parts once and lets subassemblies add occurrences;
- a joinery schedule owns fabrication metadata and cross-validation;
- a design aggregate is the immutable input to assembly and export.

Furniture-family packages may split specification, layout, parts, joinery, and orchestration when
that improves locality. The entryway bench is the canonical detailed example; the apron table remains
the minimal example.

## Consequences

- Model authors learn a small interface with high leverage.
- Shared part definitions can span modular subassemblies without duplicating BOM rows.
- Joinery and hardware counts are validated in one place.
- Simple families are not required to mimic the detailed package layout.
