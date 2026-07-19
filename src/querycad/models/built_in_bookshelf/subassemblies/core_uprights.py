"""Full-height structural core planks at the boundaries of each opening."""

from __future__ import annotations

import cadquery as cq

from querycad.furniture import PartCatalog, stock_box
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.materials import DARK_OAK

CORE_UPRIGHT_LEFT = "BOOKCASE-CORE-UPRIGHT-LH-001"
CORE_UPRIGHT_RIGHT = "BOOKCASE-CORE-UPRIGHT-RH-001"
CORE_UPRIGHT_RIGHT_SCRIBED = "BOOKCASE-CORE-UPRIGHT-RIGHT-SCRIBED-001"


def _right_scribed_core_upright(spec: BuiltInBookshelfSpec) -> cq.Workplane:
    """Make the right boundary upright with a top scribed to the ceiling slope."""

    half_width = spec.core_upright_thickness / 2
    inner_top = spec.right_slope_height_at(spec.right_opening_width - spec.core_upright_thickness)
    outer_top = spec.right_slope_end_height
    profile = (
        cq.Workplane("XZ")
        .polyline(
            (
                (-half_width, 0.0),
                (half_width, 0.0),
                (half_width, outer_top),
                (-half_width, inner_top),
            )
        )
        .close()
    )
    return profile.extrude(spec.shelf_depth / 2, both=True)


def add_core_uprights(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    """Add the full-height side planks that carry cabinets and upper shelves."""

    left_uprights = catalog.define(
        number=CORE_UPRIGHT_LEFT,
        description="Full-height left-hand bookshelf core upright",
        material=spec.finish_material,
        shape=stock_box(
            spec.core_upright_thickness,
            spec.shelf_depth,
            spec.height_under_beam,
        ),
        stock_size_mm=(
            spec.core_upright_thickness,
            spec.shelf_depth,
            spec.height_under_beam,
        ),
        color=DARK_OAK,
    )
    right_uprights = catalog.define(
        number=CORE_UPRIGHT_RIGHT,
        description="Full-height right-hand bookshelf core upright",
        material=spec.finish_material,
        shape=stock_box(
            spec.core_upright_thickness,
            spec.shelf_depth,
            spec.height_under_beam,
        ),
        stock_size_mm=(
            spec.core_upright_thickness,
            spec.shelf_depth,
            spec.height_under_beam,
        ),
        color=DARK_OAK,
    )
    for bay in layout.bays:
        left_uprights.place(
            f"core_upright_{bay.name}_left",
            (
                bay.left_x + spec.core_upright_thickness / 2,
                layout.depths.shelf_center_y,
                0.0,
            ),
        )
    for bay in layout.bays[:2]:
        right_uprights.place(
            f"core_upright_{bay.name}_right",
            (
                bay.right_x - spec.core_upright_thickness / 2,
                layout.depths.shelf_center_y,
                0.0,
            ),
        )

    right_bay = layout.bay("right")
    scribed_height = spec.right_slope_height_at(
        spec.right_opening_width - spec.core_upright_thickness
    )
    catalog.define(
        number=CORE_UPRIGHT_RIGHT_SCRIBED,
        description="Right-boundary core upright scribed to the ceiling slope",
        material=spec.finish_material,
        shape=_right_scribed_core_upright(spec),
        stock_size_mm=(
            spec.core_upright_thickness,
            spec.shelf_depth,
            scribed_height,
        ),
        color=DARK_OAK,
    ).place(
        "core_upright_right_right_scribed",
        (
            right_bay.right_x - spec.core_upright_thickness / 2,
            layout.depths.shelf_center_y,
            0.0,
        ),
    )
