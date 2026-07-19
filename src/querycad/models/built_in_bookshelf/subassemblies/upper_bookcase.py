"""Horizontal shelf courses and staggered masonry-grid divider segments."""

from __future__ import annotations

from querycad.furniture import PartCatalog, stock_box
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.materials import DARK_OAK

DIVIDER_LOWER = "UPPER-DIVIDER-LOWER-001"
DIVIDER_MIDDLE = "UPPER-DIVIDER-MIDDLE-001"
DIVIDER_TOP = "UPPER-DIVIDER-TOP-001"
SHELVES = {
    "left": "UPPER-SHELF-LEFT-001",
    "middle": "UPPER-SHELF-MIDDLE-001",
    "right": "UPPER-SHELF-RIGHT-001",
}


def add_upper_bookcase(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    """Add shelf courses and the offset vertical segments between them."""

    for bay in layout.bays:
        shelves = catalog.define(
            number=SHELVES[bay.name],
            description=f"Full-width shelf for the {bay.name} opening",
            material=spec.finish_material,
            shape=stock_box(bay.fitted_width, spec.shelf_depth, spec.shelf_thickness),
            stock_size_mm=(bay.fitted_width, spec.shelf_depth, spec.shelf_thickness),
            color=DARK_OAK,
        )
        for index, bottom_z in enumerate(layout.shelf_bottoms, start=1):
            shelves.place(
                f"upper_shelf_{bay.name}_{index:02d}",
                (bay.center_x, layout.depths.shelf_center_y, bottom_z),
            )

    divider_types = {
        0: (
            DIVIDER_LOWER,
            "Lower staggered bookshelf divider",
            layout.divider_segments[0].height,
        ),
        1: (
            DIVIDER_MIDDLE,
            "Middle staggered bookshelf divider",
            spec.shelf_pitch - spec.shelf_thickness,
        ),
        spec.shelf_count: (
            DIVIDER_TOP,
            "Top staggered bookshelf divider",
            layout.crown_bottom_z - (layout.shelf_bottoms[-1] + spec.shelf_thickness),
        ),
    }
    divider_handles = {
        key: catalog.define(
            number=number,
            description=description,
            material=spec.finish_material,
            shape=stock_box(spec.divider_thickness, spec.shelf_depth, height),
            stock_size_mm=(spec.divider_thickness, spec.shelf_depth, height),
            color=DARK_OAK,
        )
        for key, (number, description, height) in divider_types.items()
    }
    for divider in layout.divider_segments:
        key = divider.row if divider.row in (0, spec.shelf_count) else 1
        divider_handles[key].place(
            divider.name,
            (divider.center_x, layout.depths.shelf_center_y, divider.bottom_z),
        )
