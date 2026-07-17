# Agent operating contract

This repository is intended to be changed and operated by coding agents. Work autonomously inside
the repository, keep the source of truth in text files, and leave every requested design buildable by
another agent from a clean checkout.

## Required workflow

1. Read the target JSON in `designs/`, the corresponding module in `src/querycad/models/`, and its
   tests before changing geometry.
2. Keep units in millimetres. X is width/length, Y is depth, Z is height, and the floor is Z=0.
3. Put user-facing dimensions in a frozen spec dataclass. Validate impossible combinations early and
   use named parameters instead of unexplained geometry literals.
4. Keep part geometry in local coordinates and place occurrences through `Placement`. Use stable,
   descriptive part numbers because they become STEP names, STL filenames, and BOM identifiers.
5. Run `uv run querycad validate <design.json>`, `uv run ruff check .`,
   `uv run ruff format --check .`, and `uv run pytest` after a change. For geometry changes, also run
   `uv run querycad build <design.json>` and inspect the reported bounding box and artifact list.
   For viewer changes, run `cd web && npm run check && npm run build`.
   During iterative geometry work, `uv run querycad preview <design.json>` keeps the selected build
   and web studio live; it does not replace the final quality gate.
6. Never commit `.venv/`, `build/`, exports, caches, or editor state. Do commit `uv.lock` whenever
   dependencies change.

## Definition of done for a furniture family

- The model is registered in `src/querycad/registry.py`.
- A readable example exists in `designs/`.
- Invalid proportions fail with an actionable message.
- Repeated parts share one part number and use multiple placements so BOM quantities stay correct.
- Tests cover overall size, part quantities, solid validity, and at least one invalid parameter set.
- The standard build produces STEP, GLB, STL, SVG, per-part STL, BOM, and manifest outputs.
- A default build refreshes `build/catalog.json`; the web UI discovers GLB builds only through that
  generated contract. Do not hard-code individual furniture builds in React.

## Coordinate boundary

CadQuery source uses its conventional Z-up construction space: X length, Y depth, Z height. Browser
world space is Y-up: X left/right, Y vertical, Z depth. OpenCascade's glTF writer performs the axis
conversion, and `FurnitureModel` verifies/normalizes the GLB bounds against manifest dimensions at a
single scene boundary. Placement values in the UI are always browser-world millimetres. Do not add
arbitrary mesh scale to saved placement state.

## Fabrication boundary

Do not claim that generated furniture is structurally certified or fabrication-ready solely because
the CAD kernel accepts it. Clearly surface assumptions about material, loading, joinery, tolerances,
hardware, and manufacturing method. Preserve exact user requirements in the design specification or
adjacent documentation.
