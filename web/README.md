# QueryCAD Studio

React Three Fiber viewer for generated QueryCAD furniture and Gaussian-splat context.

## Run the full flow

For live CadQuery iteration, use the Python preview runner from the repository root:

```bash
uv run querycad preview designs/entryway-bench.json
```

It starts or reuses this Vite app and rebuilds the selected model after JSON or Python changes. The
catalog is polled every second, so a successful build replaces the rendered GLB without losing its
saved scene placement. Vite handles changes under `web/src/` with its own HMR.

To run the UI with only one initial model build:

```bash
npm install
npm run dev
```

`predev` runs the root QueryCAD build first. Vite then serves `../build` as its public directory, so
the UI reads `/catalog.json` and model artifacts without a copy step or hard-coded imports.

Use the **Materials** tab to inspect the active design's generated manifest. It shows material/color
groups, total assembly occurrences, unique part types, stock dimensions, and quantities, with a link
to the CSV cut list. The page follows catalog revisions, so a successful live CAD rebuild refreshes
the inventory along with the geometry. Its proportional part schematic places every unique stock
envelope beside a prominent quantity. Designs with a joinery schedule also show screw quantities and
lengths, drill-face crosshairs, datum coordinates, pilot/clearance/pocket-hole legends, and an
assembly sequence. The complete sheet can be printed or saved as an A4 landscape PDF. An orbitable
model sits beside the on-screen sheet; hovering a part card or joint row highlights its assembly
occurrences using manifest placement names.

Useful commands:

```bash
npm run model:build  # regenerate CAD and build/catalog.json
npm run dev:ui       # Vite only; used by the Python preview runner
npm run check        # lint, strict TypeScript, and UI/unit tests
npm run build        # production UI plus a snapshot of current CAD artifacts
npm run preview      # serve the production bundle
```

## Runtime contract

- `build/catalog.json` lists displayable GLB builds and their content revisions.
- Each build manifest carries BOM rows, exact CAD RGBA colors, and optional validated joinery data.
- Every furniture placement is stored separately in browser local storage.
- Geometry is never browser-scaled as a resizing operation; dimensions change in CadQuery.
- CadQuery files are Z-up. The web scene is Y-up and keeps one world unit equal to one millimetre.
- The included real-photo Mip-NeRF 360 room SPZ is visual context only and has no survey or collision
  authority.
- The room root visually registers reconstruction units with the millimetre workspace; it does not
  assert that the capture itself has metric survey scale.

The scene uses the MIT-licensed Spark renderer for SPZ context and React Three Fiber/Drei for GLB
loading, transform controls, orbit controls, grid, progress UI, and the orientation gizmo. The
included sample is imported as a build asset from `public/splats/`; its attribution and calibrated
root transform live beside the renderer in `src/scene/roomSplatConfig.ts`. Replace both when a real
room capture and measured registration points are available.

The Studio toolbar shows transform gizmos and the selected-object bounding box by default. Use the
**Helpers** toggle to hide or restore all of those overlays together; placement remains unchanged.
