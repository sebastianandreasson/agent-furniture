# Furniture CAD in a Metric Gaussian-Splat Apartment

## 1. Purpose

Build a local-first, open-source application for designing parametric furniture in Python with CadQuery and placing the generated furniture inside a photorealistic Gaussian-splat reconstruction of an apartment.

The application must support two different kinds of truth:

- **Visual truth:** the Gaussian splat gives a realistic impression of the apartment.
- **Dimensional truth:** measured anchors, room proxy geometry, and CadQuery models provide reliable dimensions for construction.

The browser experience will use **React Three Fiber** as the Three.js frontend layer. Gaussian splats and conventional meshes must coexist in one scene, share one metric coordinate system, and remain synchronized when furniture parameters or placements change.

## 2. Core design principles

1. **CadQuery source files are the furniture source of truth.**
2. **One world unit equals one millimetre throughout the application.**
3. **The Gaussian splat is never treated as manufacturing geometry.**
4. **Measured room anchors override inferred scan dimensions.**
5. **Furniture placement is stored separately from furniture geometry.**
6. **Every generated physical board is a named semantic part.**
7. **The system should remain useful without cloud services.**
8. **An AI coding agent edits structured Python models, tests, and project specifications rather than driving a CAD GUI.**

## 3. Product scope

### 3.1 Initial product

The first useful version should let a user:

- Open a Gaussian-splat apartment scene.
- Calibrate it against several real measurements.
- Display a simplified metric room proxy.
- Generate furniture from CadQuery templates.
- Adjust furniture parameters numerically.
- Place, rotate, duplicate, and snap furniture in the room.
- Inspect clearances and collisions.
- Save multiple furniture-layout alternatives.
- Export STEP, GLB, DXF, metadata JSON, and a cut-list CSV.

### 3.2 Explicit non-goals for the first version

- Training Gaussian splats directly in the application.
- Full architectural BIM functionality.
- Photorealistic relighting of inserted furniture.
- Automatic extraction of perfect wall geometry from a splat.
- Browser-side execution of arbitrary CadQuery Python.
- CNC toolpath generation.
- Multi-user collaborative editing.

## 4. Proposed technology stack

### 4.1 Frontend

- React
- TypeScript
- Vite
- React Three Fiber
- Drei for camera controls, loaders, gizmos, bounds, helpers, and HTML overlays
- Zustand for editor state
- TanStack Query for API state and rebuild status
- Zod for client-side schema validation
- Optional component library such as Radix UI or shadcn/ui

React Three Fiber is a React renderer for Three.js and supports reusable, interactive scene components that participate in normal React state and lifecycle patterns. This makes it the preferred scene-management layer rather than using raw Three.js throughout the UI.

### 4.2 Gaussian-splat rendering

Use an adapter abstraction so the renderer can be replaced without changing the rest of the application.

Preferred initial implementation:

- **Spark**, through `@sparkjsdev/spark`, wrapped in a React Three Fiber component.

Reasons:

- It is designed to place Gaussian splats in a normal Three.js scene alongside meshes.
- It supports common formats including PLY, SOGS, SPZ, SPLAT, and KSPLAT.
- It is actively maintained and designed for web rendering.
- It gives more control than a hosted iframe or viewer embed.

Alternative or fallback implementations:

- A small React Three Fiber wrapper around an existing Three.js Gaussian-splat renderer.
- A dedicated R3F splat component for a simpler proof of concept.
- Drei's splat support, if its supported formats and interaction model satisfy the project requirements at implementation time.

The application must not couple apartment project files to one renderer-specific format. Store the original splat asset and allow generated optimized derivatives such as `.spz` or `.splat`.

### 4.3 Backend

- Python 3.12+
- FastAPI
- Pydantic
- CadQuery
- NumPy
- SciPy for calibration optimization where useful
- Trimesh for mesh-side inspection and collision helpers
- Pytest
- Uvicorn for local development

CadQuery can export assemblies to GLB/glTF for browser visualization while separately exporting precise STEP geometry. CadQuery Python remains the only parametric source representation.

### 4.4 Persistence

Start with filesystem-based projects and SQLite metadata.

- SQLite stores project records, versions, placements, calibration runs, and build status.
- Project assets remain ordinary files in a documented directory structure.
- Large splat and model assets are not stored as SQLite blobs.

This keeps the project portable, inspectable, and friendly to Git where appropriate.

## 5. System architecture

```text
                            Browser
┌────────────────────────────────────────────────────────────┐
│ React UI                                                   │
│                                                            │
│  ┌──────────────── React Three Fiber ────────────────────┐ │
│  │ Gaussian splat                                         │ │
│  │ Room proxy mesh                                        │ │
│  │ CadQuery furniture GLBs                                │ │
│  │ Measurements, anchors, clearances, gizmos              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                            │
│ Parameter editor | Cut list | Layouts | Calibration        │
└──────────────────────────────┬─────────────────────────────┘
                               │ HTTP/WebSocket
                               ▼
┌────────────────────────────────────────────────────────────┐
│ FastAPI application                                        │
│                                                            │
│ Project service     Calibration service    Build service    │
│ Placement service   Export service         Validation       │
└──────────────┬──────────────────┬──────────────────────────┘
               │                  │
               ▼                  ▼
       CadQuery model code   Apartment assets
       model specifications  splat + proxy + anchors
               │                  │
               └─────────┬────────┘
                         ▼
                  Generated artifacts
             GLB | STEP | DXF | JSON | CSV
```

## 6. Shared coordinate system

### 6.1 Canonical convention

Use the following convention everywhere:

- Unit: millimetres
- X axis: left/right
- Y axis: vertical
- Z axis: forward/back
- Floor plane: `Y = 0`
- Default room origin: a selected floor corner
- Rotation order: quaternion internally; Euler angles only for display

### 6.2 Splat calibration transform

A splat reconstructed from monocular imagery may have arbitrary scale and orientation. Store a similarity transform that maps raw splat coordinates into metric apartment coordinates:

```text
p_metric = scale * rotation * p_splat + translation
```

Persist it as:

```json
{
  "scale": 1024.1834,
  "rotationQuaternion": [0.0, 0.7071, 0.0, 0.7071],
  "translationMm": [-1840.0, 0.0, 3260.0],
  "rmsErrorMm": 3.8,
  "maxErrorMm": 8.1
}
```

### 6.3 Calibration workflow

1. Load the raw splat.
2. Ask the user to identify corresponding points or marker centres.
3. Record direct real-world coordinates or known distances.
4. Solve a best-fit similarity transform.
5. Display residual error for every anchor.
6. Require a minimum of three non-collinear anchors.
7. Recommend six or more anchors distributed throughout the room.
8. Allow critical dimensions to be locked as authoritative constraints.
9. Save calibration as a versioned object rather than overwriting it silently.

### 6.4 Accuracy policy

The UI must distinguish:

- **Measured:** taken directly with a tape or laser measure.
- **Calibrated:** transformed from scan coordinates.
- **Inferred:** estimated from reconstruction or geometry extraction.

Never present inferred dimensions with the same confidence styling as measured values.

## 7. Apartment representation

Each apartment project contains three layers.

### 7.1 Visual layer

- Gaussian splat asset
- Renderer-optimized derivative
- Splat calibration transform
- Optional visibility masks or crop regions

### 7.2 Metric room proxy

A lightweight mesh or semantic plane model containing:

- Floor
- Ceiling
- Walls
- Doors
- Windows
- Skirting boards
- Radiators
- Pipes
- Fixed cabinets
- Power outlets
- Other construction-relevant obstacles

The room proxy is used for selection, snapping, collision tests, section views, dimensions, and occlusion helpers.

### 7.3 Measurement layer

- Point anchors
- Line measurements
- Plane anchors
- Named openings
- Critical clearances
- Confidence/source metadata

Example:

```json
{
  "id": "living-room-north-wall-width",
  "type": "distance",
  "from": [0, 0, 0],
  "to": [4182, 0, 0],
  "valueMm": 4182,
  "source": "laser",
  "locked": true
}
```

## 8. Furniture representation

### 8.1 Source model

Furniture is authored in Python using reusable CadQuery components.

```text
backend/furniture_cad/
├── components/
│   ├── panel.py
│   ├── shelf.py
│   ├── door.py
│   ├── drawer.py
│   ├── plinth.py
│   └── joinery.py
├── models/
│   ├── cabinet.py
│   ├── bookshelf.py
│   ├── desk.py
│   └── wardrobe.py
├── exporters/
├── validation/
└── schemas/
```

### 8.2 Model contract

Every furniture model must provide:

- Typed parameters
- A CadQuery assembly
- Named physical parts
- Overall dimensions
- Placement origin and axes
- Snap surfaces
- Clearance volumes
- Manufacturing metadata
- Validation results

Conceptual interface:

```python
class FurnitureModel(Protocol):
    model_type: str

    def build(self, parameters: dict) -> BuildResult:
        ...
```

### 8.3 Part semantics

Every physical board should retain:

- Stable ID
- Human-readable name
- Material
- Finished dimensions
- Blank dimensions
- Grain direction
- Quantity
- Edge banding
- Joinery operations
- Local transform
- Optional supplier or stock reference

### 8.4 Generated artifacts

Each successful build produces:

```text
generated/<build-id>/
├── preview.glb
├── model.step
├── metadata.json
├── cut-list.csv
├── validation.json
├── drawings/
│   └── *.dxf
└── thumbnails/
    └── preview.webp
```

The GLB is for visualization. STEP and the CadQuery source are authoritative for exact geometry.

## 9. Furniture placement model

Placement is separate from generated geometry.

```json
{
  "id": "placement-01",
  "furnitureBuildId": "build-bookshelf-a17",
  "positionMm": [1840, 0, 320],
  "rotationQuaternion": [0, 0.7071, 0, 0.7071],
  "scale": [1, 1, 1],
  "locked": false,
  "snapConstraint": {
    "type": "face-to-plane",
    "sourceFace": "rear",
    "targetPlane": "north-wall",
    "offsetMm": 10
  }
}
```

Furniture scale must remain `[1, 1, 1]`. Resizing furniture always changes CadQuery parameters and triggers a rebuild. Arbitrary mesh scaling would break manufacturing dimensions.

## 10. Frontend scene design

### 10.1 React Three Fiber scene tree

```tsx
<Canvas>
  <SceneCamera />
  <ApartmentRoot transform={calibrationTransform}>
    <GaussianSplatLayer />
    <RoomProxyLayer />
    <MeasurementLayer />
  </ApartmentRoot>
  <FurnitureLayer />
  <ClearanceLayer />
  <SelectionLayer />
  <TransformControls />
</Canvas>
```

The raw splat and any raw scan-space derivatives live beneath `ApartmentRoot`. Metric furniture is placed directly in world coordinates.

### 10.2 Gaussian-splat adapter

Define a renderer-neutral component contract:

```ts
interface GaussianSplatProps {
  src: string;
  visible?: boolean;
  opacity?: number;
  quality?: "low" | "medium" | "high";
  cropBox?: Box3Data;
  onLoad?: (metadata: SplatMetadata) => void;
}
```

Initial implementation:

```tsx
function SparkGaussianSplat(props: GaussianSplatProps) {
  // Create and manage a Spark SplatMesh inside the R3F scene.
}
```

Do not allow renderer-specific objects to leak into project state.

### 10.3 Viewer modes

- Perspective
- Orthographic
- Top/floor plan
- Front
- Side
- Isometric
- Section plane
- Furniture-only
- Room-proxy-only
- Splat-only
- Combined

### 10.4 Interaction tools

- Orbit, pan, and zoom
- Click selection
- Box selection for room-proxy editing
- Transform gizmo for furniture placement
- Numeric position and rotation inputs
- Snap to wall/floor/anchor
- Point-to-point measurement
- Hide/isolate selected objects
- Exploded furniture view
- Clearance-volume toggle
- Collision highlighting

## 11. Drop-in Gaussian-splat integration strategy

The first proof of concept should compare two routes:

### Route A: Spark wrapper

Use `@sparkjsdev/spark` directly inside a React Three Fiber component.

Advantages:

- Designed for mixing splats with ordinary Three.js meshes.
- Broad format support.
- Active ecosystem and performance-oriented implementation.
- Better long-term control over scene integration.

Risks:

- Requires a small custom lifecycle wrapper.
- Renderer updates may require adapter maintenance.

### Route B: existing R3F splat component

Use a ready-made React Three Fiber component where supported.

Advantages:

- Very fast proof of concept.
- Minimal wrapper code.

Risks:

- Potentially narrower format support.
- May be less actively maintained.
- May expose fewer sorting, clipping, LOD, and performance controls.

### Decision gate

Adopt the simplest component only if it passes all of these tests:

- Renders together with multiple GLB meshes.
- Obeys parent transforms correctly.
- Supports object disposal and scene switching.
- Maintains acceptable performance on an M1 Mac.
- Supports crop or clipping requirements.
- Does not take over the entire WebGL render loop.
- Allows correct mesh/splat depth behavior for the planned interaction modes.

Default expectation: use the Spark adapter for the real application and a drop-in component only for the earliest prototype.

## 12. Backend API

### 12.1 Projects

```text
POST   /api/projects
GET    /api/projects
GET    /api/projects/{projectId}
PATCH  /api/projects/{projectId}
DELETE /api/projects/{projectId}
```

### 12.2 Apartment assets

```text
POST /api/projects/{projectId}/splat
POST /api/projects/{projectId}/room-proxy
GET  /api/projects/{projectId}/scene
```

### 12.3 Calibration

```text
POST /api/projects/{projectId}/calibrations/solve
GET  /api/projects/{projectId}/calibrations
POST /api/projects/{projectId}/calibrations/{id}/activate
```

### 12.4 Furniture builds

```text
GET  /api/furniture/models
GET  /api/furniture/models/{modelType}/schema
POST /api/furniture/builds
GET  /api/furniture/builds/{buildId}
GET  /api/furniture/builds/{buildId}/artifacts/{artifactName}
```

Example build request:

```json
{
  "modelType": "bookshelf",
  "parameters": {
    "widthMm": 1700,
    "heightMm": 2200,
    "depthMm": 340,
    "panelThicknessMm": 18,
    "shelfCount": 5
  }
}
```

### 12.5 Placements and layouts

```text
POST   /api/projects/{projectId}/layouts
GET    /api/projects/{projectId}/layouts
PATCH  /api/layouts/{layoutId}
POST   /api/layouts/{layoutId}/placements
PATCH  /api/placements/{placementId}
DELETE /api/placements/{placementId}
```

### 12.6 Build execution

For the local MVP, builds can run in a subprocess managed by the FastAPI application. Return a build ID immediately and expose status through polling or a WebSocket.

For later multi-user deployment, move builds to a dedicated worker queue. Do not execute arbitrary user-submitted Python; only registered model types and validated parameters may run.

## 13. Rebuild lifecycle

1. User changes a furniture parameter.
2. Client validates the parameter schema.
3. Client sends a build request.
4. Backend creates a versioned build record.
5. Worker executes the registered CadQuery model.
6. Validation runs before artifact publication.
7. Backend exports GLB, STEP, DXF, metadata, and cut list.
8. Client receives build-complete notification.
9. Existing placement switches to the new build while preserving its transform.
10. Old builds remain available for rollback and layout comparison.

Use debouncing for slider input, but provide an explicit **Rebuild** button for expensive models.

## 14. Validation

### 14.1 Furniture geometry checks

- Positive dimensions
- Minimum practical panel sizes
- Valid panel thickness
- No unintended self-intersections
- Stable part IDs
- Overall bounding dimensions equal requested dimensions within tolerance
- Shelves and dividers remain inside the carcass
- Doors and drawers have valid gaps
- Joinery does not break through unintended faces
- Every physical part appears in the cut list

### 14.2 Placement checks

- Furniture rests on or intentionally offsets from a support plane
- No collision with room proxy unless explicitly permitted
- Door and drawer clearance volumes remain unobstructed
- Required wall and radiator gaps are respected
- Placement does not rely on arbitrary mesh scaling

### 14.3 Calibration checks

- Minimum anchor count
- Non-degenerate anchor distribution
- RMS and maximum residuals
- Warnings for extrapolation far outside measured anchors
- Warnings when critical furniture boundaries depend only on inferred geometry

## 15. Collision and clearance strategy

Do not perform collision tests against the Gaussian splat.

Use:

- Room proxy meshes for static collision.
- Simplified furniture collision meshes or exact bounding solids.
- Semantic clearance volumes for doors, drawers, chairs, and walkways.

Clearance definitions are part of the furniture model:

```json
{
  "id": "drawer-bank-front-clearance",
  "type": "box",
  "dimensionsMm": [800, 700, 500],
  "transform": {
    "positionMm": [0, 350, 250]
  },
  "severity": "warning"
}
```

## 16. Room-proxy creation

### 16.1 MVP approach

Create room geometry manually in the viewer using measured dimensions:

- Place floor polygon.
- Extrude wall planes.
- Add openings numerically.
- Add obstacles as boxes or cylinders.
- Align the proxy visually against the calibrated splat.

This is slower than automatic extraction but much more trustworthy for furniture fitting.

### 16.2 Later assistance

Add assisted extraction tools:

- Fit a plane through selected splat points or imported point-cloud samples.
- Detect dominant horizontal and vertical planes.
- Suggest wall intersections.
- Let the user accept and then constrain results using measured dimensions.

Automatic results remain suggestions until confirmed.

## 17. Project directory layout

```text
furniture-apartment-cad/
├── plan.md
├── README.md
├── pyproject.toml
├── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── calibration/
│   │   ├── database/
│   │   ├── furniture_cad/
│   │   ├── projects/
│   │   ├── services/
│   │   └── workers/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── editor/
│   │   ├── scene/
│   │   │   ├── splats/
│   │   │   ├── furniture/
│   │   │   ├── room-proxy/
│   │   │   └── measurements/
│   │   ├── state/
│   │   └── types/
│   └── tests/
├── projects/
│   └── example-apartment/
│       ├── project.json
│       ├── apartment/
│       │   ├── original.ply
│       │   ├── preview.spz
│       │   ├── room-proxy.glb
│       │   ├── room-proxy.json
│       │   ├── anchors.json
│       │   └── calibration.json
│       ├── layouts/
│       └── generated/
└── scripts/
    ├── convert-splat.*
    ├── build-model.py
    └── validate-project.py
```

## 18. State model

Separate persistent domain state from temporary editor state.

### Persistent state

- Project
- Apartment assets
- Calibration versions
- Measurement anchors
- Room proxy
- Furniture build versions
- Layouts
- Placements
- Snap constraints

### Temporary editor state

- Current selection
- Camera position
- Active tool
- Hover target
- Gizmo mode
- Layer visibility
- Draft parameter edits
- Unsaved room-proxy edits

Do not serialize raw Three.js objects into application state.

## 19. Milestones

### Milestone 0: technical spikes

Deliverables:

- R3F scene containing one splat and one GLB mesh.
- Spark adapter prototype.
- Alternative drop-in splat component prototype.
- M1 performance notes.
- Parent-transform and cleanup tests.
- CadQuery assembly exported to GLB and STEP.

Exit criteria:

- A furniture mesh can be positioned inside the splat scene.
- Both layers use a consistent transform.
- The application can switch apartment scenes without leaking GPU resources.

### Milestone 1: local vertical slice

Deliverables:

- Vite React frontend.
- FastAPI backend.
- One bookshelf CadQuery model.
- Parameter form.
- Build endpoint.
- GLB preview replacement.
- STEP and CSV export.
- Basic orbit camera and selection.

Exit criteria:

- Changing bookshelf width produces a new exact CadQuery build and updates the browser preview without changing its placement.

### Milestone 2: metric apartment calibration

Deliverables:

- Calibration-point placement tool.
- Similarity-transform solver.
- Residual visualization.
- Saved calibration versions.
- Millimetre grid and measurement tool.

Exit criteria:

- Known room distances display within the defined tolerance after calibration.

### Milestone 3: room proxy and snapping

Deliverables:

- Manual floor and wall editor.
- Openings and obstacle primitives.
- Snap furniture to floor and wall.
- Numeric offsets.
- Collision checks.

Exit criteria:

- A cabinet can be snapped to a measured wall with a specified rear clearance.

### Milestone 4: useful furniture library

Deliverables:

- Cabinet
- Bookshelf
- Wardrobe
- Desk
- Shelf system
- Reusable doors and drawers
- Cut-list metadata
- Clearance volumes

Exit criteria:

- Models share component conventions and pass common geometry tests.

### Milestone 5: layout comparison

Deliverables:

- Named layouts.
- Duplicate layout.
- Side-by-side parameter comparison.
- Saved camera viewpoints.
- Screenshot export.

Exit criteria:

- The user can compare two furniture widths and placements in the same apartment.

### Milestone 6: AI-agent workflow

Deliverables:

- Repository instructions for the coding agent.
- Model-template generator.
- Required test suite for new furniture.
- Structured project specification files.
- Safe commands for build, validation, and artifact generation.

Exit criteria:

- An agent can add a new furniture model by following repository conventions without modifying the viewer architecture.

## 20. Testing strategy

### Backend

- Unit tests for furniture parameters and part generation.
- Golden metadata tests.
- Bounding-box tolerance tests.
- Calibration solver tests with synthetic transforms and noise.
- API schema tests.
- Export smoke tests for GLB, STEP, and DXF.

### Frontend

- Component tests for parameter forms.
- State tests for build replacement and placement preservation.
- Playwright tests for selection, snapping, layout save, and downloads.
- Scene smoke tests with fixed screenshots where practical.

### Performance

Test on an M1 Mac with representative splat sizes.

Track:

- Initial asset load time
- GPU memory use
- Frame time while orbiting
- Frame time with splat plus multiple furniture GLBs
- Rebuild latency
- Asset disposal after scene changes

## 21. Security and execution boundaries

- Never execute arbitrary Python sent from the browser.
- Register allowed furniture models on the backend.
- Validate every parameter with Pydantic.
- Run CadQuery builds in isolated subprocesses.
- Apply CPU-time and memory limits where feasible.
- Write outputs only inside a build-specific directory.
- Treat uploaded GLB, PLY, SPLAT, SPZ, and ZIP files as untrusted.
- Sanitize filenames and reject path traversal.

## 22. Open questions and decision points

1. Which splat formats will be accepted as original project assets?
2. Should the application ship a conversion command for SPZ as the default web format?
3. Does Spark provide the required clipping and depth behavior for furniture occlusion in the chosen version?
4. Should furniture GLBs use millimetres directly or be converted to metres at export with a root transform in the viewer?
5. How should room-proxy edits be represented: semantic planes, constructive primitives, or an editable mesh?
6. Which direct-measurement workflow will be used: manual tape values, laser-measure entry, AprilTags, or a combination?
7. What tolerance is acceptable for visual planning versus cutting approval?
8. Should layouts pin furniture build versions or automatically track the newest build?

Recommended initial answers:

- Preserve original splat files and generate SPZ or another optimized derivative.
- Keep the application domain in millimetres, but evaluate rendering in metres if large-coordinate precision becomes an issue. If converted, perform that conversion only at a single scene root.
- Use semantic planes and primitives for the room proxy.
- Combine manual laser measurements with visual anchor placement.
- Pin layout placements to explicit build versions.

## 23. Definition of done for the first practical release

The release is useful when the user can:

1. Load an apartment splat.
2. Calibrate it using real measurements.
3. Build a reliable room proxy around the intended furniture area.
4. Generate a parametric furniture model with CadQuery.
5. Resize it through numeric controls.
6. Place and snap it in the photorealistic apartment scene.
7. Inspect collisions and operating clearances.
8. Save alternative layouts.
9. Export exact STEP geometry and a verified cut list.
10. See calibration and validation warnings before treating dimensions as construction-ready.

## 24. Recommended first implementation sequence

1. Create the monorepo and shared TypeScript/Pydantic schemas.
2. Prove Spark plus React Three Fiber plus GLB coexistence.
3. Create the CadQuery bookshelf model and exporters.
4. Implement versioned build requests and artifact serving.
5. Add furniture placement with transform controls.
6. Add calibration anchors and the similarity-transform solver.
7. Add the semantic room proxy.
8. Add snapping, collision, and clearance volumes.
9. Add layouts and build-version pinning.
10. Expand the furniture component library and agent instructions.

## 25. References

- React Three Fiber documentation: https://r3f.docs.pmnd.rs/
- Spark Gaussian-splat renderer: https://sparkjs.dev/
- Spark source repository: https://github.com/sparkjsdev/spark
- CadQuery documentation: https://cadquery.readthedocs.io/
- CadQuery import/export documentation: https://cadquery.readthedocs.io/en/latest/importexport.html
- FastAPI documentation: https://fastapi.tiangolo.com/
