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
- A 400 mm uncovered extension on the selected side, indented to half the main depth
- A 260 mm slatted shoe surface in that extension, rising 25 degrees toward the back
- A small painted retaining lip across the shelf's lower/front edge
- Open ends and the same restrained rectangular proportions as the reference

The loose decorative pillow, shoes, wall, floor, and surrounding hallway are scene dressing and are
not part of the bench model.

## Initial dimensional assumptions

| Dimension | Estimate |
| --- | ---: |
| Overall length | 1600 mm |
| Cushioned main section | 1200 mm |
| Uncovered side extension | 400 × 190 mm |
| Overall depth | 380 mm |
| Painted frame height | 430 mm |
| Cushioned seat height | 500 mm |
| Leg section | 42 × 42 mm |
| Cushion | 1140 × 350 × 70 mm |
| Shelf top | 120 mm |
| Main / extension shelf slats | 12 / 4, each 30 × 16 mm |
| Extension shoe shelf | 260 mm surface, 25° angle, 90 mm front-edge height |
| Shoe-retaining lip | 18 mm high × 12 mm thick |

Every estimate is exposed on `EntrywayBenchSpec` in
`src/querycad/models/entryway_bench/spec.py`. The example JSON leaves `parameters` empty so changes to
those Python defaults rebuild live; JSON keys can still override individual values for a deliberate
variant. The most valuable measurements for a second pass are overall length, overall depth,
floor-to-top-of-wood-frame height, cushion thickness, leg section, and shelf height.

The extension stays aligned to the back edge, producing a 190 mm front indent in plan view;
`extension_side` selects which end it occupies. The cushion remains on the original 1200 mm section
only, and the extension top is exposed painted timber. Its lower slats extend forward into the
indented space and slope upward toward the wall, providing a 260 mm support surface within a shallow
footprint. The 400 mm section is intended to hold one ordinary pair side-by-side, but verify the
actual footwear dimensions before fabrication. A low crosswise lip at the front edge keeps shoes
from sliding off the incline.

## Fabrication boundary

The model publishes a prototype screw schedule, part-local drill centres, and an assembly sequence.
Shelf-slat clearance/countersink holes are cut in their solids; pocket holes and transfer pilots stay
marked-only because their exact result depends on the jig, chosen screw, stock, and dry-fit
orientation. See `JOINERY_AND_DRILLING.md` for those assumptions.

This is still not a fabrication-ready or structurally certified design. Rail intersections are
nominal connection envelopes rather than modeled mortise-and-tenon joints. Upholstery construction,
wood movement, manufacturing clearances, load capacity, stability, and the final hardware products
must be resolved and tested before fabrication.
