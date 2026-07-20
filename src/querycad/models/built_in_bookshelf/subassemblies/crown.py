"""Simple top trim below the exposed beam and right-hand ceiling slope."""

from __future__ import annotations

import cadquery as cq

from querycad.furniture import PartCatalog
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.materials import DARK_OAK

CROWNS = {
    "left": "CROWN-LEFT-001",
    "middle": "CROWN-MIDDLE-001",
    "right": "CROWN-RIGHT-SLOPED-001",
}


def _right_crown(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> cq.Workplane:
    bay = layout.bay("right")
    width = bay.fitted_width
    fitted_start_offset = bay.fitted_left_x - bay.left_x
    crossing_from_clear_left = layout.right_slope_crossing_x - fitted_start_offset
    crossing_x = -width / 2 + crossing_from_clear_left
    beam_top = spec.height_under_beam - layout.right_crown_base_z
    level_bottom = layout.crown_bottom_z - layout.right_crown_base_z
    fitted_end_offset = bay.fitted_right_x - bay.left_x
    end_top = spec.right_slope_height_at(fitted_end_offset) - layout.right_crown_base_z
    profile = (
        cq.Workplane("XZ")
        .polyline(
            (
                (-width / 2, level_bottom),
                (crossing_x, level_bottom),
                (width / 2, 0.0),
                (width / 2, end_top),
                (crossing_x, beam_top),
                (-width / 2, beam_top),
            )
        )
        .close()
    )
    return profile.extrude(spec.crown_depth / 2, both=True)


def add_crown(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    """Add restrained trim below the exposed beam, including the right slope."""

    for bay in layout.bays[:2]:
        catalog.define_stock(
            number=CROWNS[bay.name],
            description=f"Simple crown below the top beam in the {bay.name} opening",
            material=spec.finish_material,
            size_mm=(bay.fitted_width, spec.crown_depth, spec.crown_height),
            color=DARK_OAK,
        ).place(
            f"crown_{bay.name}",
            (bay.center_x, layout.depths.crown_center_y, layout.crown_bottom_z),
        )

    right_bay = layout.bay("right")
    right_crown_height = spec.height_under_beam - layout.right_crown_base_z
    catalog.define(
        number=CROWNS["right"],
        description="Scribed crown following the right-hand ceiling slope",
        material=spec.finish_material,
        shape=_right_crown(spec, layout),
        stock_size_mm=(
            right_bay.fitted_width,
            spec.crown_depth,
            right_crown_height,
        ),
        color=DARK_OAK,
    ).place(
        "crown_right_sloped",
        (right_bay.center_x, layout.depths.crown_center_y, layout.right_crown_base_z),
    )
