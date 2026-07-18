"""Modular part definitions and occurrences for the entryway bench."""

from __future__ import annotations

import cadquery as cq

from querycad.furniture import (
    PartCatalog,
    centered_box,
    rounded_ring,
    soft_box,
    stock_box,
    top_countersunk_holes,
)
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.spec import EntrywayBenchSpec

SEAT_BASE = "SEAT-BASE-001"
LEG = "LEG-001"
TOP_RAIL_LONG = "TOP-RAIL-LONG-001"
TOP_RAIL_END = "TOP-RAIL-END-001"
SHELF_RAIL = "SHELF-RAIL-001"
SHELF_RAIL_END = "SHELF-RAIL-END-001"
SHELF_SLAT = "SHELF-SLAT-001"
EXTENSION_TOP_RAIL_LONG = "EXTENSION-TOP-RAIL-LONG-001"
EXTENSION_TOP_RAIL_END = "EXTENSION-TOP-RAIL-END-001"
EXTENSION_SHELF_RAIL = "EXTENSION-SHELF-RAIL-001"
EXTENSION_SHELF_SLAT = "EXTENSION-SHELF-SLAT-001"
EXTENSION_SHELF_STOPPER = "EXTENSION-SHELF-STOPPER-001"
CUSHION = "CUSHION-001"
CUSHION_PIPING = "CUSHION-PIPING-001"

PAINT = (0.43, 0.42, 0.39, 1.0)
PANEL = (0.47, 0.46, 0.43, 1.0)
FABRIC = (0.78, 0.74, 0.66, 1.0)
PIPING = (0.68, 0.64, 0.56, 1.0)


def _l_shaped_seat_deck(
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
) -> cq.Workplane:
    """Make the main seat and indented extension as one stable sheet part."""

    main = stock_box(spec.length, spec.depth, spec.seat_base_thickness)
    extension = stock_box(
        spec.extension_length,
        spec.extension_depth,
        spec.seat_base_thickness,
    ).translate((layout.extension_center_x, layout.extension_center_y, 0.0))
    deck = main.union(extension)
    if spec.seat_base_corner_radius:
        deck = deck.edges("|Z").fillet(spec.seat_base_corner_radius)
    return deck


def add_main_bench(
    catalog: PartCatalog,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
) -> None:
    """Add the cushioned main frame and its traditional slatted shoe shelf."""

    catalog.define(
        number=SEAT_BASE,
        description="One-piece L-shaped seat and extension deck",
        material=spec.panel_material,
        shape=_l_shaped_seat_deck(spec, layout),
        stock_size_mm=(
            spec.length + spec.extension_length,
            spec.depth,
            spec.seat_base_thickness,
        ),
        color=PANEL,
    ).place("seat_and_extension_deck", (0.0, 0.0, layout.leg_height))

    legs = catalog.define(
        number=LEG,
        description="Square bench leg",
        material=spec.frame_material,
        shape=stock_box(spec.leg_size, spec.leg_size, layout.leg_height),
        stock_size_mm=(spec.leg_size, spec.leg_size, layout.leg_height),
        color=PAINT,
    )
    for x_name, x in (("left", -layout.leg_x), ("right", layout.leg_x)):
        for y_name, y in (("front", -layout.leg_y), ("back", layout.leg_y)):
            legs.place(f"leg_{x_name}_{y_name}", (x, y, 0.0))

    long_rails = catalog.define(
        number=TOP_RAIL_LONG,
        description="Long rail below seat",
        material=spec.frame_material,
        shape=stock_box(
            layout.long_member_length,
            spec.top_rail_thickness,
            spec.top_rail_height,
        ),
        stock_size_mm=(
            layout.long_member_length,
            spec.top_rail_thickness,
            spec.top_rail_height,
        ),
        color=PAINT,
    )
    long_rails.place("top_rail_front", (0.0, -layout.leg_y, layout.top_rail_z))
    long_rails.place("top_rail_back", (0.0, layout.leg_y, layout.top_rail_z))

    end_rails = catalog.define(
        number=TOP_RAIL_END,
        description="Flush end rail below seat",
        material=spec.frame_material,
        shape=stock_box(
            spec.top_rail_thickness,
            layout.end_member_depth,
            spec.top_rail_height,
        ),
        stock_size_mm=(
            spec.top_rail_thickness,
            layout.end_member_depth,
            spec.top_rail_height,
        ),
        color=PAINT,
    )
    end_rails.place("top_rail_left", (-layout.end_rail_x, 0.0, layout.top_rail_z))
    end_rails.place("top_rail_right", (layout.end_rail_x, 0.0, layout.top_rail_z))

    shelf_rails = catalog.define(
        number=SHELF_RAIL,
        description="Long shelf support rail",
        material=spec.frame_material,
        shape=stock_box(
            layout.long_member_length,
            spec.shelf_rail_thickness,
            spec.shelf_rail_height,
        ),
        stock_size_mm=(
            layout.long_member_length,
            spec.shelf_rail_thickness,
            spec.shelf_rail_height,
        ),
        color=PAINT,
    )
    shelf_rail_z = spec.lower_shelf_height - spec.shelf_rail_height
    shelf_rails.place("shelf_rail_lower_front", (0.0, -layout.leg_y, shelf_rail_z))
    shelf_rails.place("shelf_rail_lower_back", (0.0, layout.leg_y, shelf_rail_z))

    catalog.define(
        number=SHELF_RAIL_END,
        description="Lower shelf end rail receiving the leg-free extension shelf",
        material=spec.frame_material,
        shape=stock_box(
            spec.shelf_rail_thickness,
            layout.end_member_depth,
            spec.shelf_rail_height,
        ),
        stock_size_mm=(
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
        shelf_slats.place(
            f"shelf_slat_lower_{index:02d}",
            (x, 0.0, spec.lower_shelf_height),
        )


def add_extension(
    catalog: PartCatalog,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
) -> None:
    """Add the clean six-leg extension and its angled slatted shelf."""

    legs = catalog.part(LEG)
    legs.place(
        "leg_extension_end_front",
        (layout.extension_far_leg_x, layout.extension_front_leg_y, 0.0),
    )
    legs.place(
        "leg_extension_end_back",
        (layout.extension_far_leg_x, layout.extension_back_leg_y, 0.0),
    )

    top_rails = catalog.define(
        number=EXTENSION_TOP_RAIL_LONG,
        description="Long rail below extension deck",
        material=spec.frame_material,
        shape=stock_box(
            layout.extension_long_member_length,
            spec.top_rail_thickness,
            spec.top_rail_height,
        ),
        stock_size_mm=(
            layout.extension_long_member_length,
            spec.top_rail_thickness,
            spec.top_rail_height,
        ),
        color=PAINT,
    )
    top_rails.place(
        "extension_top_rail_front",
        (
            layout.extension_rail_center_x,
            layout.extension_front_leg_y,
            layout.top_rail_z,
        ),
    )
    top_rails.place(
        "extension_top_rail_back",
        (
            layout.extension_rail_center_x,
            layout.extension_back_leg_y,
            layout.top_rail_z,
        ),
    )

    catalog.define(
        number=EXTENSION_TOP_RAIL_END,
        description="End rail below extension deck",
        material=spec.frame_material,
        shape=stock_box(
            spec.top_rail_thickness,
            layout.extension_end_member_depth,
            spec.top_rail_height,
        ),
        stock_size_mm=(
            spec.top_rail_thickness,
            layout.extension_end_member_depth,
            spec.top_rail_height,
        ),
        color=PAINT,
    ).place(
        "extension_top_rail_end",
        (layout.extension_far_leg_x, layout.extension_center_y, layout.top_rail_z),
    )

    shelf_rails = catalog.define(
        number=EXTENSION_SHELF_RAIL,
        description="Angled rail below extension shelf slats",
        material=spec.frame_material,
        shape=centered_box(
            layout.extension_long_member_length,
            spec.shelf_rail_thickness,
            spec.shelf_rail_height,
        ),
        stock_size_mm=(
            layout.extension_long_member_length,
            spec.shelf_rail_thickness,
            spec.shelf_rail_height,
        ),
        color=PAINT,
    )
    shelf_rotation = (spec.extension_shelf_angle_deg, 0.0, 0.0)
    shelf_rails.place(
        "extension_shelf_rail_front",
        (
            layout.extension_rail_center_x,
            layout.extension_front_rail_contact_y + layout.extension_shelf_rail_y_offset,
            layout.extension_front_rail_contact_z - layout.extension_shelf_rail_z_offset,
        ),
        shelf_rotation,
    )
    shelf_rails.place(
        "extension_shelf_rail_back",
        (
            layout.extension_rail_center_x,
            layout.extension_back_rail_contact_y + layout.extension_shelf_rail_y_offset,
            layout.extension_back_rail_contact_z - layout.extension_shelf_rail_z_offset,
        ),
        shelf_rotation,
    )

    extension_slat_shape = top_countersunk_holes(
        centered_box(
            spec.shelf_slat_width,
            spec.extension_shelf_length,
            spec.shelf_slat_thickness,
            corner_radius=2.0,
        ),
        (
            (0.0, layout.extension_front_screw_y),
            (0.0, layout.extension_back_screw_y),
        ),
        diameter=spec.slat_clearance_hole_diameter,
        countersink_diameter=spec.slat_countersink_diameter,
        depth=spec.shelf_slat_thickness,
    )
    extension_slats = catalog.define(
        number=EXTENSION_SHELF_SLAT,
        description="Angled front-to-back extension shoe shelf slat",
        material=spec.frame_material,
        shape=extension_slat_shape,
        stock_size_mm=(
            spec.shelf_slat_width,
            spec.extension_shelf_length,
            spec.shelf_slat_thickness,
        ),
        color=PAINT,
    )
    for index, x in enumerate(layout.extension_slat_centers, start=1):
        extension_slats.place(
            f"extension_shelf_slat_{index:02d}",
            (x, layout.extension_shelf_center_y, layout.extension_shelf_center_z),
            shelf_rotation,
        )

    catalog.define(
        number=EXTENSION_SHELF_STOPPER,
        description="Low retaining lip at front of angled shoe shelf",
        material=spec.frame_material,
        shape=centered_box(
            layout.extension_slat_span,
            spec.extension_shelf_stopper_thickness,
            spec.extension_shelf_stopper_height,
            corner_radius=2.0,
        ),
        stock_size_mm=(
            layout.extension_slat_span,
            spec.extension_shelf_stopper_thickness,
            spec.extension_shelf_stopper_height,
        ),
        color=PAINT,
    ).place(
        "extension_shelf_front_stopper",
        (
            layout.extension_rail_center_x,
            layout.extension_stopper_center_y,
            layout.extension_stopper_center_z,
        ),
        shelf_rotation,
    )


def add_upholstery(
    catalog: PartCatalog,
    spec: EntrywayBenchSpec,
    _layout: BenchLayout,
) -> None:
    """Add the loose cushion and its repeated piping detail."""

    catalog.define(
        number=CUSHION,
        description="Loose upholstered seat cushion",
        material=spec.cushion_material,
        shape=soft_box(
            spec.cushion_length,
            spec.cushion_depth,
            spec.cushion_thickness,
            spec.cushion_corner_radius,
        ),
        stock_size_mm=(
            spec.cushion_length,
            spec.cushion_depth,
            spec.cushion_thickness,
        ),
        color=FABRIC,
    ).place("seat_cushion", (0.0, 0.0, spec.frame_height))

    piping_shape = rounded_ring(
        spec.cushion_length - 4.0,
        spec.cushion_depth - 4.0,
        spec.cushion_piping_height,
        spec.cushion_piping_width,
        spec.cushion_corner_radius - 2.0,
    )
    piping = catalog.define(
        number=CUSHION_PIPING,
        description="Cushion perimeter piping",
        material=spec.cushion_material,
        shape=piping_shape,
        stock_size_mm=(
            spec.cushion_length - 4.0,
            spec.cushion_depth - 4.0,
            spec.cushion_piping_height,
        ),
        color=PIPING,
    )
    piping.place("cushion_piping_lower", (0.0, 0.0, spec.frame_height + 6.0))
    piping.place(
        "cushion_piping_upper",
        (
            0.0,
            0.0,
            spec.frame_height + spec.cushion_thickness - spec.cushion_piping_height - 6.0,
        ),
    )


def build_part_catalog(spec: EntrywayBenchSpec, layout: BenchLayout) -> PartCatalog:
    catalog = PartCatalog()
    add_main_bench(catalog, spec, layout)
    add_extension(catalog, spec, layout)
    add_upholstery(catalog, spec, layout)
    return catalog
