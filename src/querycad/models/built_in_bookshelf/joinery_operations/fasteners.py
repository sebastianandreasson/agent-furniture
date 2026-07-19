"""Hardware definitions used by the bookshelf joinery schedule."""

from __future__ import annotations

from querycad.furniture import FastenerSpec
from querycad.models.built_in_bookshelf.joinery_operations.notes import STRUCTURAL_NOTE
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec


def fasteners(spec: BuiltInBookshelfSpec) -> tuple[FastenerSpec, ...]:
    return (
        FastenerSpec(
            code="CAB-5X50-T20",
            description="5 × 50 mm cabinet construction screw",
            length_mm=spec.cabinet_screw_length,
            nominal_size=f"{spec.cabinet_screw_diameter:g} mm",
            head="small washer head",
            drive="T20",
            thread="partial wood thread",
            finish="black oxide",
            application="Base carcass, face frame, fixed post panels, and divider assembly",
            notes="Confirm pilot size and edge distance on matching oak and plywood offcuts.",
        ),
        FastenerSpec(
            code="SHELF-4.5X45-T20",
            description="4.5 × 45 mm countersunk display screw",
            length_mm=spec.shelf_screw_length,
            nominal_size=f"{spec.shelf_screw_diameter:g} mm",
            head="countersunk",
            drive="T20",
            thread="partial wood thread",
            finish="black oxide",
            application="Display ledges and retaining lips",
            notes="Countersink only enough to leave the stained show face clean.",
        ),
        FastenerSpec(
            code="CORE-SHELF-5X60-T25",
            description="5 × 60 mm core-to-shelf construction screw",
            length_mm=spec.core_shelf_screw_length,
            nominal_size=f"{spec.core_shelf_screw_diameter:g} mm",
            head="small washer head",
            drive="T25",
            thread="partial wood thread",
            finish="black oxide",
            application="Full-height core uprights to shelf ends",
            notes=(
                "Use the modeled end pilots and confirm withdrawal resistance in shelf stock "
                "before final assembly."
            ),
        ),
        FastenerSpec(
            code="STRUCT-6X90-T30",
            description="6 × 90 mm structural timber screw",
            length_mm=spec.structural_screw_length,
            nominal_size=f"{spec.structural_screw_diameter:g} mm",
            head="washer head",
            drive="T30",
            thread="structural wood thread",
            finish="black oxide",
            application="Core uprights and trim to verified existing timber",
            status="site_verification_required",
            notes=STRUCTURAL_NOTE,
        ),
        FastenerSpec(
            code="HINGE-3.5X16-PZ2",
            description="3.5 × 16 mm hinge mounting screw",
            length_mm=spec.hinge_screw_length,
            nominal_size=f"{spec.hinge_screw_diameter:g} mm",
            head="countersunk",
            drive="PZ2",
            thread="full wood thread",
            finish="antique brass",
            application="Traditional cabinet door hinges",
            notes="Select hinges after confirming inset geometry and door weight.",
        ),
        FastenerSpec(
            code="KNOB-M4X25",
            description="M4 × 25 mm cabinet knob machine screw",
            length_mm=spec.knob_screw_length,
            nominal_size=f"M{spec.knob_screw_diameter:g}",
            head="pan head",
            drive="cross recess",
            thread="machine thread",
            finish="zinc",
            application="Aged-brass door knobs",
            notes="Confirm screw length against the selected knob and finished door thickness.",
        ),
    )
