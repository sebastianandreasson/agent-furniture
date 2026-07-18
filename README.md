# queryCAD

A code-first CadQuery workspace for designing parametric furniture under agent control. Design
intent and defaults live in versioned Python, small JSON files select a family and optionally
override values for variants, and one CLI validates and exports fabrication-friendly artifacts.

## Start here

The environment is managed by `uv` and pinned to Python 3.12 and CadQuery 2.8.0.

```bash
uv sync
uv run querycad list
uv run querycad validate designs/dining-table.json
uv run querycad build designs/dining-table.json
uv run querycad build designs/entryway-bench.json
```

The build command writes an assembly STEP file, a browser-viewable GLB, an assembly STL, an SVG
isometric drawing, one STL per unique part, a BOM CSV, an optional hardware CSV, and a
machine-readable manifest beneath `build/dining-table/`. Generated files are intentionally ignored
by Git; source models, design specifications, tests, and the dependency lockfile are committed.

## Web studio

The Vite app in `web/` discovers every complete GLB build through `build/catalog.json`. Its lifecycle
scripts rebuild the example model automatically. For iterative model work, run the Python live
preview from the repository root:

```bash
uv run querycad preview designs/entryway-bench.json
# equivalent convenience script:
uv run python scripts/preview.py designs/entryway-bench.json
```

The preview performs an initial build, starts or reuses the Vite studio at
`http://127.0.0.1:5173`, and watches the selected design JSON, `pyproject.toml`, and every Python file
under `src/querycad/`. After a save settles, it rebuilds in a fresh process. The web UI checks the
catalog revision every second and swaps in the new GLB while preserving furniture placement. A
temporary invalid edit prints a build error but leaves the last successful model visible; fix it and
save again. Stop the watcher with Ctrl-C. Only one watcher can own a design at a time.

For live bench experiments, edit the values on `EntrywayBenchSpec` in
`src/querycad/models/entryway_bench/spec.py`. The example JSON intentionally has an empty `parameters`
object, so Python values drive the build directly. Add a key to that JSON only when you deliberately
want it to override the corresponding Python default for this design variant. The watcher calls out
successful rebuilds that produced the same GLB revision.

The direct frontend workflow remains available when live CAD rebuilding is not needed:

```bash
cd web
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The editor streams an online starter Gaussian splat, loads the exact
CadQuery GLB from `build/`, and provides move/rotate gizmos, numeric millimetre controls, snapping,
camera presets, layer controls, and direct links to STEP, BOM, manifest, and GLB artifacts.

The Materials page turns a model's joinery contract into a printable build document. For the
entryway bench it totals every screw specification, marks drill centres on part-face diagrams, lists
pilot/clearance/pocket-hole operations, sequences the joints, and links hover state back to the 3D
assembly. See `docs/JOINERY_AND_DRILLING.md` for the coordinate contract and the intentionally
conservative fabrication boundary.

The default web lifecycle now builds the photo-derived entryway bench. Its editable defaults live in
`EntrywayBenchSpec`; the design JSON contains optional variant overrides, and the visual assumptions
behind the estimates are documented in `docs/ENTRYWAY_BENCH.md`.

After an agent changes or adds a model, run its normal QueryCAD build. The UI polls the catalog every
second and uses the GLB content hash to replace changed geometry without losing the saved
placement. `npm run build` creates a standalone `web/dist/` bundle containing the current artifacts.

## Agent workflow

Ask an agent in this repository for outcomes such as:

> Make this dining table 1800 mm long, keep a 750 mm overall height, and rebuild the exports.

> Add a parametric wall shelf with three bays, adjustable shelf thickness, and a cut list.

> Add mortise-and-tenon joinery to the table, then test that all solids remain valid.

The repository contract in `AGENTS.md` tells an agent how to make and verify those changes. A new
design variant normally needs only a JSON file. A new furniture family gets a model module,
registry entry, example specification, and tests. The public authoring Interface lives in
`querycad.furniture`; the entryway bench is the canonical modular example and the apron table is the
small single-file example. See `docs/FURNITURE_ARCHITECTURE.md` and `docs/ADDING_A_MODEL.md`.

## Commands

```bash
# Show available furniture families
uv run querycad list

# Live CAD rebuild loop plus web studio
uv run querycad preview designs/entryway-bench.json

# Validate dimensions without creating CAD files
uv run querycad validate designs/dining-table.json

# Build all default formats
uv run querycad build designs/dining-table.json

# Select formats and destination
uv run querycad build designs/dining-table.json \
  --formats step,glb,stl,svg,bom \
  --output build/custom-table

# Run the quality gate
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

All model dimensions are millimetres. Coordinates use X for width/length, Y for depth, and Z for
height inside CadQuery, with the floor at Z=0. The glTF exporter converts that boundary to the web
scene's Y-up convention; browser placements are X left/right, Y vertical, and Z depth. STEP is the
master exchange format; STL is a tessellated convenience format and should not be treated as editable
source.

## Scope and safety

This workspace makes geometry, part lists, and exports reproducible. It does not certify structural
capacity, stability, ergonomics, joinery, tool paths, or building-code compliance. Before fabrication,
verify loads, material properties, joints, clearances, tolerances, and workshop safety with a qualified
person where the consequences warrant it.
