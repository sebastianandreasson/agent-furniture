# Joinery and drilling contract

QueryCAD treats fabrication guidance as model data, not UI decoration. A `Design` can publish:

- `FastenerSpec` records with a stable code, quantity-driving joints, length, head, drive, thread,
  finish, use, product reference, source, and qualification status.
- `DrillOperation` records tied to stable part numbers. Each operation defines the face, two drawing
  axes, diameter, optional depth/countersink/angle, hole centres, drill axes, and whether geometry is
  cut or only marked.
- `JointSpec` records tying source and target parts to a fastener, drill operations, quantity, and
  assembly step.

`Design.validate_solids()` rejects duplicate identifiers, missing references, out-of-stock drill
points, invalid axes and diameters, and any mismatch between counted drill points and scheduled screw
quantities. The standard BOM export writes `hardware.csv` when hardware is present, and the manifest
contains the complete joinery contract consumed by the Materials page.

## Datum and coordinates

All dimensions are millimetres. Drill centres use the part's unplaced cut-stock coordinates, measured
from its minimum X/Y/Z corner. `view_axes` selects the two axes drawn on a schematic face; the point's
third coordinate and drill-axis vector retain the full 3D instruction. Part placement never changes
the cut pattern.

The printable sheet is a dimensioned reference, not a 1:1 template. Use the written coordinates and
the indicated face. Repeated parts share a part number only when the cut/drill pattern is identical;
orient repeated occurrences during assembly as shown by the placement names and model.

## Entryway bench profile

The current bench is an indoor painted-beech prototype with three hardware lines:

- 36 × `PH-38-FINE`, 38 mm fine-thread zinc pocket-hole screws for rail-to-leg frame joints.
- 12 × `PH-32-FINE`, 32 mm fine-thread zinc pocket-hole screws for attaching the two top boards.
- 36 × `CSK-4X35`, 4.0 × 35 mm countersunk hardwood screws for shelf slats and the shoe stop.

The 9.5 mm, 15° pocket marks are jig-driven and intentionally remain schematic: actual stepped depth
and collar settings depend on measured stock and the jig. Shelf-slat clearance/countersink holes are
cut in the CadQuery solids. Rail pilots and shoe-stop holes are marked for transfer during dry fit.

Fastener selection follows the manufacturer distinction between fine-thread screws for hardwood and
screw length based on actual stock thickness. The generic 4 × 35 mm screw still needs a final product
choice. Its 3.0 mm pilot is a prototype assumption that must be checked against the selected screw's
root diameter, material density, edge distance, and an offcut. Useful primary references:

- Kreg screw selection: <https://learn.kregtool.com/learn/how-to-select-right-pocket-hole-screw/>
- Kreg pocket-hole method and 15° geometry:
  <https://learn.kregtool.com/learn/how-pocket-hole-joints-work/>
- Kreg 9.5 mm Easy-Set stepped bit:
  <https://www.kregtool.com/en/products/pocket-hole-joinery/pocket-hole-jig-accessories/easy-set-pocket-hole-drill-bit/KPHA300.html>
- USDA Forest Products Laboratory, *Wood Handbook*, chapter 8:
  <https://www.fpl.fs.usda.gov/documnts/fplgtr/fplgtr282/chapter_08_fpl_gtr282.pdf>

## Iteration workflow

1. Change the screw and drill defaults in the frozen furniture spec or add an intentional JSON
   variant override.
2. Update drill points and joints in the model; quantities are derived from repeated part placements.
3. Run the normal validation and build gates.
4. Open Materials in the live studio. Hover a part or joint row to inspect it in the assembly, then
   print/save the hardware and drill document.
5. Before fabrication, choose the exact slat screw product and verify all settings on matching
   offcuts. Revisit the schedule if material species, moisture, load, joint method, or stock thickness
   changes.

This contract makes assumptions visible and testable. It does not certify structural capacity,
stability, or workshop safety, and a successful CAD build is not evidence of fabrication readiness.
