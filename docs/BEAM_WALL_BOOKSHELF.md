# Beam-wall built-in bookshelf

This design translates the two July 2026 reference photographs and the measured site notes into a
parametric three-bay built-in. The source of truth is `BuiltInBookshelfSpec`; the example JSON keeps
an empty `parameters` object so edits to Python defaults appear immediately in the live preview.

## Confirmed requirements

- Clear openings are 1100, 1450, and 670 mm wide.
- The two internal posts included in the furniture span are 360 and 140 mm wide. The 360 mm post at
  the far-right boundary is recorded in the specification, but the furniture stops at its near edge.
- The recess is 145 mm deep, the underside of the top beam is 2400 mm above the floor, and the base
  cabinet counter is 700 mm high.
- Base cabinets are 330 mm deep from the wall plane to their finished front edge. Open shelves and
  structural core uprights remain 160 mm deep, intentionally projecting 15 mm beyond the recess.
- The wall plane is CAD Y=0 and every furniture layer projects into the room along negative Y. This
  keeps the finished front facing the default browser perspective without mirroring the bay layout.
- Six continuous oak core uprights sit at the two ends of each opening. They are 160 mm deep, run
  from floor to the available top envelope, and fasten sideways into verified timber. The far-right
  upright is scribed under the ceiling slope.
- Cabinets, face frames, counters, shelves, dividers, and crown pieces fit between these structural
  uprights. The shelves fasten into them directly; the previous short shelf-cleat concept is removed.
- Each opening has four shelf courses at a 300 mm pitch. The two wide openings use alternating divider
  positions to make a masonry-grid rhythm and reduce unsupported spans.
- The lower cabinets have two, two, and one traditional framed doors from left to right. The lone
  right-bay door is left-hinged with its knob on the right.
- The lower cabinet counter, recessed plinth, and finished front continue across both internal post
  zones. Each post zone receives a matching framed inset panel that is fixed shut, has no knob or
  hinges, and does not imply usable storage behind the existing timber.
- Existing vertical posts receive matching oak cladding. At every shelf course, each internal post
  receives a shallow ledge and lip for one front-facing book.
- There are no back panels. The finish is dark stained oak, with oak-veneered plywood for carcass
  panels and aged-brass knobs.
- Furniture restraint is limited to verified existing vertical timber and the top horizontal beam.
  The brick wall is not an anchor target.
- The visible beams remain fixed site anchors with matching decorative face cladding. They are not
  counted as furniture structure or cut-list parts.

## Editable assumptions

The measured opening and post widths produce a 3720 mm furniture span: 1100 + 360 + 1450 + 140 +
670 mm. The separate right-boundary post width makes the full site sequence 4080 mm but is not added
to the modeled furniture. The current structural concept assumes 30 mm thick solid or laminated oak
core uprights, 3 mm fitting clearance between those uprights and removable horizontal parts, 24 mm
shelf boards, and 300 mm shelf pitch. With those defaults, fitted widths become 1034, 1384, and 604
mm. Preliminary shelf attachment uses 5 × 60 mm screws through the core uprights into piloted shelf
ends. Measure the real posts at multiple heights before fabrication.

The right slope uses a screen-style offset convention from the supplied notes: it begins 150 mm into
the right opening at a point 100 mm above the beam underside, then reaches 200 mm below the beam
underside at the outer edge. The crown is level while the top beam controls the opening and becomes
sloped only after those envelopes cross. All four shelf boards remain level below the lowest slope.

## Fabrication boundary

The model documents nominal parts, assembly order, pilot locations, and preliminary hardware
counts. It does not certify the existing structure, shelf loading, timber condition, fastener
capacity, hinge selection, fire clearances, ventilation around the visible duct, or the fit of an old
wall. Confirm every opening at the bottom, counter, shelf, and beam levels; scribe fillers in the
workshop only after a site dry fit. A qualified person should verify the structural posts and beam
before any attachment holes are drilled. In particular, confirm that every modeled upright location
has sound timber beside it; if the far-left boundary is not timber, it needs a floor-and-top-supported
detail rather than an anchor into brick.
