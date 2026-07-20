# Entryway bench: photo-derived assumptions

The `entryway_bench` family reproduces the bench in the user-supplied `bench.PNG` reference. The
single perspective photo establishes the visible design language, but it does not provide a reliable
scale or reveal every joint. The initial model therefore uses furniture-scale estimates rather than
claiming measured dimensions.

## Visible details reproduced

- Warm-grey painted square timber frame and legs
- Shallow perimeter rails immediately below the seat
- Slightly projecting seat support board
- Loose natural-fabric cushion with rounded edges and upper/lower piping
- One low shoe shelf with long support rails and narrow front-to-back slats
- A 600 mm uncovered extension on the selected side, indented to a 150 mm depth
- Interchangeable shoe-shelf, umbrella/general-storage, and no-extension configurations
- Open ends and the same restrained rectangular proportions as the reference

The loose decorative pillow, shoes, wall, floor, and surrounding hallway are scene dressing and are
not part of the bench model.

## Initial dimensional assumptions

| Dimension | Estimate |
| --- | ---: |
| Overall length | 1600 mm |
| Cushioned main section | 1000 mm |
| Uncovered side extension | 600 × 150 mm |
| Overall depth | 250 mm |
| Painted frame height | 520 mm |
| Cushioned seat height | 550 mm |
| Leg section | 42 × 42 mm |
| Cushion | 990 × 240 × 30 mm |
| Shelf top | 120 mm |
| Main / extension shelf slats | 10 / 6, each 30 × 16 mm |
| Extension shoe shelf | 260 mm surface, 40° angle, 90 mm front-edge height |
| Shoe-retaining lip | 18 mm high × 12 mm thick |
| Storage panels | 18 mm |
| Storage floor top | 90 mm |
| Umbrella compartment / front | 180 mm wide / 180 mm high |

Every estimate is exposed on `EntrywayBenchSpec` in
`src/querycad/models/entryway_bench/spec.py`. The shoe-shelf JSON leaves `parameters` empty so changes
to those Python defaults rebuild live; the umbrella JSON selects only
`extension_mode: umbrella_storage`; the compact JSON selects `extension_mode: none`. The most
valuable measurements for a second pass are overall length, overall depth,
floor-to-top-of-wood-frame height, cushion thickness, leg section, and shelf height.

The extension stays aligned to the back edge, producing a 100 mm front indent in plan view;
`extension_side` selects which end it occupies. The cushion remains on the original 1000 mm section
only, and the extension top is exposed painted timber. Its lower slats extend forward into the
indented space and slope upward toward the wall, providing a 260 mm support surface within a shallow
footprint. The 600 mm section is intended to hold one ordinary pair side-by-side, but verify the
actual footwear dimensions before fabrication. A low crosswise lip at the front edge keeps shoes
from sliding off the incline.

## Extension variants

- `designs/entryway-bench.json` is the original **Shoe shelf** variant. It uses two angled support
  rails, six slats, a retaining stop, and a junction shelf rail.
- `designs/entryway-bench-umbrella.json` is **Umbrella storage**. It retains the same main seat, six
  legs, top frame, cushion, and main shoe shelf, removes the solid extension wing, and fills the open
  extension with a flat floor, back, divider, and low umbrella retaining face. The perimeter rails
  form an open top for upright umbrellas; the remaining bay is general storage.
- `designs/entryway-bench-no-extension.json` is **No extension**. It contains only the 1000 mm main
  bench: four legs, the cushioned seat, and its regular lower shoe shelf. No extension parts,
  connector hardware, or extension drilling operations enter its fabrication outputs.

All three JSON files share `family: entryway-bench`, so the web UI presents them as one furniture
family with a dropdown. They export independently, including variant-specific BOM and drilling
metadata.

## Fabrication boundary

The model publishes a prototype screw schedule, part-local drill centres, and an assembly sequence.
Shelf-slat clearance/countersink holes are cut in their solids; pocket holes and transfer pilots stay
marked-only because their exact result depends on the jig, chosen screw, stock, and dry-fit
orientation. See `JOINERY_AND_DRILLING.md` for those assumptions.

This is still not a fabrication-ready or structurally certified design. Rail intersections are
nominal connection envelopes rather than modeled mortise-and-tenon joints. Upholstery construction,
wood movement, manufacturing clearances, load capacity, stability, and the final hardware products
must be resolved and tested before fabrication.
