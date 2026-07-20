"""Main cushioned frame and slatted shoe shelf."""

from __future__ import annotations

import cadquery as cq

from querycad.furniture import PartCatalog, stock_box, top_countersunk_holes
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.part_numbers import (
    LEG,
    SEAT_BASE,
    SHELF_RAIL,
    SHELF_RAIL_END,
    SHELF_SLAT,
    TOP_RAIL_END,
    TOP_RAIL_LONG,
)
from querycad.models.entryway_bench.spec import EntrywayBenchSpec

PAINT = (0.43, 0.42, 0.39, 1.0)
PANEL = (0.47, 0.46, 0.43, 1.0)


def _seat_deck(spec: EntrywayBenchSpec, layout: BenchLayout) -> cq.Workplane:
    main = stock_box(spec.length, spec.depth, spec.seat_base_thickness)
    if spec.extension_mode == "shoe_shelf":
        extension = stock_box(
            spec.extension_length,
            spec.extension_depth,
            spec.seat_base_thickness,
        ).translate((layout.extension_center_x, layout.extension_center_y, 0.0))
        main = main.union(extension)
    if spec.seat_base_corner_radius:
        main = main.edges("|Z").fillet(spec.seat_base_corner_radius)
    return main


def add_main_bench(
    catalog: PartCatalog,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
) -> None:
    """Add the cushioned main frame and its traditional slatted shoe shelf."""

    deck_description = {
        "shoe_shelf": "One-piece L-shaped seat and extension deck",
        "umbrella_storage": "Main seat deck beside open umbrella storage",
        "none": "Main bench seat deck",
    }[spec.extension_mode]
    catalog.define(
        number=SEAT_BASE,
        description=deck_description,
        material=spec.panel_material,
        shape=_seat_deck(spec, layout),
        stock_size_mm=(
            spec.length + (spec.extension_length if spec.extension_mode == "shoe_shelf" else 0.0),
            spec.depth,
            spec.seat_base_thickness,
        ),
        color=PANEL,
    ).place("seat_and_extension_deck", (0.0, 0.0, layout.leg_height))

    legs = catalog.define_stock(
        number=LEG,
        description="Square bench leg",
        material=spec.frame_material,
        size_mm=(spec.leg_size, spec.leg_size, layout.leg_height),
        color=PAINT,
    )
    for x_name, x in (("left", -layout.leg_x), ("right", layout.leg_x)):
        for y_name, y in (("front", -layout.leg_y), ("back", layout.leg_y)):
            legs.place(f"leg_{x_name}_{y_name}", (x, y, 0.0))

    long_rails = catalog.define_stock(
        number=TOP_RAIL_LONG,
        description="Long rail below seat",
        material=spec.frame_material,
        size_mm=(layout.long_member_length, spec.top_rail_thickness, spec.top_rail_height),
        color=PAINT,
    )
    long_rails.place("top_rail_front", (0.0, -layout.leg_y, layout.top_rail_z))
    long_rails.place("top_rail_back", (0.0, layout.leg_y, layout.top_rail_z))

    end_rails = catalog.define_stock(
        number=TOP_RAIL_END,
        description="Flush end rail below seat",
        material=spec.frame_material,
        size_mm=(spec.top_rail_thickness, layout.end_member_depth, spec.top_rail_height),
        color=PAINT,
    )
    end_rails.place("top_rail_left", (-layout.end_rail_x, 0.0, layout.top_rail_z))
    end_rails.place("top_rail_right", (layout.end_rail_x, 0.0, layout.top_rail_z))

    shelf_rails = catalog.define_stock(
        number=SHELF_RAIL,
        description="Long shelf support rail",
        material=spec.frame_material,
        size_mm=(
            layout.long_member_length,
            spec.shelf_rail_thickness,
            spec.shelf_rail_height,
        ),
        color=PAINT,
    )
    shelf_rail_z = spec.lower_shelf_height - spec.shelf_rail_height
    shelf_rails.place("shelf_rail_lower_front", (0.0, -layout.leg_y, shelf_rail_z))
    shelf_rails.place("shelf_rail_lower_back", (0.0, layout.leg_y, shelf_rail_z))

    if spec.extension_mode == "shoe_shelf":
        catalog.define_stock(
            number=SHELF_RAIL_END,
            description="Lower shelf end rail receiving the leg-free extension shelf",
            material=spec.frame_material,
            size_mm=(
                spec.shelf_rail_thickness,
                layout.end_member_depth,
                spec.shelf_rail_height,
            ),
            color=PAINT,
        ).place(
            "shelf_rail_extension_junction",
            (layout.junction_shelf_rail_x, 0.0, layout.junction_shelf_rail_z),
        )

    slat_hole_y = layout.main_slat_depth / 2 - layout.main_slat_hole_inset
    shelf_slat_shape = top_countersunk_holes(
        stock_box(
            spec.shelf_slat_width,
            layout.main_slat_depth,
            spec.shelf_slat_thickness,
            corner_radius=2.0,
        ),
        ((0.0, -slat_hole_y), (0.0, slat_hole_y)),
        diameter=spec.slat_clearance_hole_diameter,
        countersink_diameter=spec.slat_countersink_diameter,
        depth=spec.shelf_slat_thickness,
    )
    shelf_slats = catalog.define(
        number=SHELF_SLAT,
        description="Front-to-back shoe shelf slat",
        material=spec.frame_material,
        shape=shelf_slat_shape,
        stock_size_mm=(
            spec.shelf_slat_width,
            layout.main_slat_depth,
            spec.shelf_slat_thickness,
        ),
        color=PAINT,
    )
    for index, x in enumerate(layout.main_slat_centers, start=1):
        shelf_slats.place(f"shelf_slat_lower_{index:02d}", (x, 0.0, spec.lower_shelf_height))
