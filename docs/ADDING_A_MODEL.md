# Adding a furniture family

Choose the example at the same complexity as the new family:

- `src/querycad/models/apron_table.py` is the minimal single-module example.
- `src/querycad/models/entryway_bench/` is the canonical modular example with a derived layout,
  shared parts across subassemblies, upholstery, drill operations, and a hardware schedule.

Import authoring primitives from `querycad.furniture`, its stable public Interface. Do not reach into
another model family's private modules just to reuse a box or placement helper; promote genuinely
general behavior to that Interface instead.

## Implementation sequence

1. Create a frozen spec dataclass inheriting `FurnitureSpec`. Put user-facing dimensions and early,
   actionable validation there. Keep all units in millimetres.
2. Create an immutable derived layout when several subassemblies need the same calculated positions,
   lengths, signs, or clearances. Layout code calculates design intent but does not create solids.
3. Define local-coordinate solids in a `PartCatalog`. Use `define_stock` for rectangular boards and
   `define` for genuinely machined or composite shapes. Give every unique cut or purchased part a
   stable part number, then add named `Placement` occurrences from each subassembly.
4. When fabrication metadata is in scope, build a `JoineryPlan`. Attach each drill operation to a
   stable source part and let the plan derive screw quantities from drill points × part occurrences.
5. Return one validated `Design` aggregate from a short orchestration function.
6. Add a `ModelDefinition` to `src/querycad/registry.py` and a readable JSON specification under
   `designs/`.
7. Test overall size, quantities, solid validity, joinery totals when present, and at least one
   impossible parameter set. Run the complete quality gate in `AGENTS.md`.

For a modular family, prefer this package shape:

```text
models/my_family/
├── __init__.py   # narrow public exports
├── spec.py       # frozen user-facing inputs and validation
├── layout.py     # geometry-free derived dimensions and positions
├── part_numbers.py # stable output identifiers for a large family
├── parts.py      # concise composition of subassembly builders
├── subassemblies/ # focused local solids and occurrence builders
├── joinery.py    # concise composition of joinery operations
├── joinery_operations/ # focused drilling and connection schedules
└── model.py      # concise orchestration into a Design
```

Not every family needs every file. Split only where it improves Locality and gives a concept a clear
owner. A shallow wrapper around one line of CadQuery is not a useful Module.

## Adding a variant

A variant of an existing family is another design JSON with a unique `name`, the same `model` and
`family`, and its own `variant` and `variant_label`. Put only deliberate parameter overrides in its
`parameters` object. When variants exchange physical modules, keep the selection in the frozen spec
and compose the chosen subassembly in the family's part and joinery builders. Each variant must
remain independently valid and exportable.

```json
{
  "name": "entryway-bench-umbrella",
  "family": "entryway-bench",
  "variant": "umbrella-storage",
  "variant_label": "Umbrella storage",
  "model": "entryway_bench",
  "parameters": { "extension_mode": "umbrella_storage" }
}
```

## Stable output contract

Part numbers and placement names are public output identifiers. Keep them stable after a design has
been shared or fabricated. Repeated parts share one part number only when their geometry and
machining pattern are identical. `stock_size_mm` uses `(X, Y, Z)` and is emitted directly into the
BOM; colors aid assembly review but do not imply a finish specification.

The CLI always writes `manifest.json`. It contains resolved parameters, the overall bounding box,
part quantities, material labels, volumes, placements, joinery, package versions, and artifact paths.
It also contains family and variant identity. The standard build refreshes `build/catalog.json`,
where those fields become `familyId`, `variantId`, and `variantLabel`. Downstream automation and the
web studio must consume these generated contracts rather than scrape console output or hard-code a
furniture family.
