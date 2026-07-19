"""Drilling operations for shelves and masonry-grid dividers."""

from __future__ import annotations

from querycad.furniture import DrillOperation, DrillPoint
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.upper_bookcase import SHELVES


def shelf_end_operation(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    bay_name: str,
    side: str,
) -> DrillOperation:
    bay = layout.bay(bay_name)
    is_left = side == "left"
    x = 0.0 if is_left else bay.fitted_width
    axis = (-1.0, 0.0, 0.0) if is_left else (1.0, 0.0, 0.0)
    return DrillOperation(
        operation_id=f"DR-UPPER-SHELF-{bay_name.upper()}-{side.upper()}-END",
        part_number=SHELVES[bay_name],
        label=f"Pilot the {side} end of each {bay_name} shelf for its core upright",
        kind="pilot",
        face=f"{side} end",
        view_axes=("y", "z"),
        diameter_mm=spec.pilot_hole_diameter,
        depth_mm=spec.core_shelf_screw_length - spec.core_upright_thickness,
        points=tuple(
            DrillPoint(
                (x, y, spec.shelf_thickness / 2),
                axis,
                f"{side} core fixing {index}",
            )
            for index, y in enumerate(
                (
                    spec.core_anchor_depth_inset,
                    spec.shelf_depth - spec.core_anchor_depth_inset,
                ),
                start=1,
            )
        ),
        fastener_code="CORE-SHELF-5X60-T25",
        counts_fastener=True,
        notes=(
            "Clamp the shelf between the full-height uprights, drill through the upright into "
            "these end pilots, then drive the shelf screws from the concealed outer face."
        ),
    )


def divider_operation(
    spec: BuiltInBookshelfSpec,
    part_number: str,
    height: float,
) -> DrillOperation:
    return DrillOperation(
        operation_id=f"DR-{part_number.removesuffix('-001')}",
        part_number=part_number,
        label="Pilots at both ends of each staggered divider",
        kind="pilot",
        face="divider ends",
        view_axes=("y", "z"),
        diameter_mm=spec.pilot_hole_diameter,
        depth_mm=spec.cabinet_screw_length,
        points=tuple(
            DrillPoint(
                (spec.divider_thickness / 2, y, z),
                axis,
                label,
            )
            for z, axis, label in (
                (10.0, (0.0, 0.0, -1.0), "lower member"),
                (height - 10.0, (0.0, 0.0, 1.0), "upper member"),
            )
            for y in (40.0, spec.shelf_depth - 40.0)
        ),
        fastener_code="CAB-5X50-T20",
        counts_fastener=True,
        notes=(
            "Use the resolved offset for each row; the alternating divider positions create "
            "the masonry-grid rhythm and support the long shelf spans."
        ),
    )
