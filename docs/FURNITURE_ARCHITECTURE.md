# Furniture authoring architecture

QueryCAD keeps editable design intent in text and concentrates CadQuery-specific mechanics behind a
small public authoring Interface. The architecture is deliberately asymmetric: furniture families
can express detailed domain intent while exports and the web studio consume one stable aggregate.

## Authoring flow

```text
design JSON identity + overrides
        ↓
frozen specification ── validates user-facing dimensions
        ↓
derived layout ──────── shares calculated intent across subassemblies
        ↓
part catalog ────────── one local solid + many named placements per part number
        ├────────────── joinery plan derives drilling and hardware quantities
        ↓
validated Design aggregate
        ↓
STEP · GLB · STL · SVG · BOM · hardware CSV · manifest · catalog
```

The `querycad.furniture` package is the public authoring Interface. Its main concepts are:

- `FurnitureSpec`: common mapping, serialization, and baseline validation for frozen specifications.
- `PartCatalog` and `PartHandle`: an authoring Implementation that lets separate subassemblies add
  occurrences to one stable part definition before it is frozen. `define_stock` is the concise path
  for rectangular cut stock; `define` remains the explicit path for machined or composite solids.
- `Placement`, `Part`, and `Design`: immutable output records. A `Design` is the aggregate root
  validated and consumed by every exporter; its family and variant identity travel with every
  artifact.
- `JoineryPlan` and `JoinerySchedule`: the authoring and immutable forms of fabrication metadata. The
  plan removes duplicated quantity arithmetic; the schedule owns cross-reference validation.
- Geometry and layout helpers such as `stock_box`, `soft_box`, `linear_centers`, and
  `rail_end_pocket_holes`: reused only when they encode a recurring furniture operation.

This Interface is intentionally deeper than the old general-purpose core module: callers specify
part and connection intent, while placement collection, quantity derivation, cross-validation, and
serialization stay hidden in the Implementation.

## Family boundaries

The entryway bench package is the detailed baseline:

- `spec.py` owns editable values and impossible-combination checks.
- `layout.py` owns every derived position and clearance shared by other Modules.
- `part_numbers.py` is the stable output vocabulary; `parts.py` only composes the focused builders in
  `subassemblies/`. The shoe-shelf and umbrella-storage variants select an extension builder while
  reusing the main `LEG-001` definition through the catalog.
- `joinery.py` composes the focused frame, shelf, and storage operations in
  `joinery_operations/`. Shared fastener and drilling factories live beside those operations rather
  than being repeated across the schedule.
- `model.py` is a short composition root with no geometry literals.

The built-in bookshelf applies the same shape at a larger scale. In particular, its cabinet run
separates the structural carcasses, post-zone bridges, decorative fronts, and stable part numbers.
The orchestrator preserves artifact order while each Module keeps one construction concern local.

The apron table remains intentionally small. It demonstrates that a family should not be split into
files until the additional Seams improve Locality.

## Dependency direction

Furniture families depend on `querycad.furniture`; the public authoring package never depends on a
specific family. The registry depends only on each family's narrow `__init__.py`. Configuration,
validation, CLI, and export code consume `Design` and do not know bench-specific part numbers.

The browser has the same boundary. Python produces `manifest.json` and `build/catalog.json`; the web
studio parses those contracts into generic types. Materials UI modules project the manifest into
inventory summaries, schematics, schedules, and the highlighted assembly without importing model
source or recognizing individual furniture builds. Catalog `familyId`, `variantId`, and
`variantLabel` fields group independently generated builds; selecting a variant replaces the whole
artifact set rather than patching browser geometry.

Within the browser, `lib/contract.ts` is the decoding Interface for generated JSON and
`scene/furnitureAsset.ts` owns GLB loading plus axis normalization. The materials workspace hook owns
navigation and selection state; render Modules receive that state and stay presentation-focused.
Large style sheets are split by the UI surface they describe, preserving cascade order without one
global file becoming the owner of unrelated screens.

## When to deepen the Interface

Promote code into `querycad.furniture` when at least two families need the same operation or when the
operation hides meaningful CadQuery or validation complexity. Keep family-specific layout rules,
part numbers, material assumptions, and joinery policy within the family. This preserves Leverage
without turning the shared package into a collection of shallow forwarding helpers.

Architectural decisions and the source/artifact boundary are recorded in `docs/adr/`. Domain terms
and invariants are defined in the repository `CONTEXT.md`.
