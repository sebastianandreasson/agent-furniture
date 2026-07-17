# Adding a furniture family

Use `src/querycad/models/apron_table.py` as the reference implementation.

1. Create a frozen spec dataclass with defaults, `from_mapping()`, `as_dict()`, and `validate()`.
2. Build local-coordinate solids and group identical stock parts into `Part` records.
3. Locate each occurrence with a named `Placement` and return a `Design`.
4. Add a `ModelDefinition` to `src/querycad/registry.py`.
5. Add a concise JSON specification under `designs/`.
6. Add geometry and validation tests, then run the quality gate in `AGENTS.md`.

Part numbers are public output identifiers. Keep them stable after a design has been fabricated.
`stock_size_mm` uses `(X, Y, Z)` and is emitted directly into the BOM. Colors aid assembly review but
do not imply a finish specification.

The CLI always writes `manifest.json`. It contains the resolved parameters, overall bounding box,
part quantities, material labels, volumes, placements, package versions, and requested artifact
paths. Downstream automation should consume the manifest rather than scrape console output.
