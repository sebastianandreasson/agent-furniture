# QueryCAD Studio

React Three Fiber viewer for generated QueryCAD furniture and Gaussian-splat context.

## Run the full flow

```bash
npm install
npm run dev
```

`predev` runs the root QueryCAD build first. Vite then serves `../build` as its public directory, so
the UI reads `/catalog.json` and model artifacts without a copy step or hard-coded imports.

Useful commands:

```bash
npm run model:build  # regenerate CAD and build/catalog.json
npm run check        # lint, strict TypeScript, and UI/unit tests
npm run build        # production UI plus a snapshot of current CAD artifacts
npm run preview      # serve the production bundle
```

## Runtime contract

- `build/catalog.json` lists displayable GLB builds and their content revisions.
- Every furniture placement is stored separately in browser local storage.
- Geometry is never browser-scaled as a resizing operation; dimensions change in CadQuery.
- CadQuery files are Z-up. The web scene is Y-up and keeps one world unit equal to one millimetre.
- The remote starter splat is visual context only and has no dimensional or collision authority.

The scene uses Drei for the streamed splat, GLB loading/cloning, transform controls, orbit controls,
grid, progress UI, and orientation gizmo. Replace the starter URL in `src/scene/StarterSplat.tsx`
when an apartment capture is ready.
