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
envelope beside a prominent quantity and can be printed or saved as a clean A4 landscape PDF. An
orbitable model sits beside the on-screen sheet; hovering a part card highlights all of its assembly
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
- Each build manifest carries the BOM rows and exact CAD RGBA color used by the Materials page.
- Every furniture placement is stored separately in browser local storage.
- Geometry is never browser-scaled as a resizing operation; dimensions change in CadQuery.
- CadQuery files are Z-up. The web scene is Y-up and keeps one world unit equal to one millimetre.
- The remote starter splat is visual context only and has no dimensional or collision authority.

The scene uses Drei for the streamed splat, GLB loading/cloning, transform controls, orbit controls,
grid, progress UI, and orientation gizmo. Replace the starter URL in `src/scene/StarterSplat.tsx`
when an apartment capture is ready.

The Studio toolbar shows transform gizmos and the selected-object bounding box by default. Use the
**Helpers** toggle to hide or restore all of those overlays together; placement remains unchanged.
