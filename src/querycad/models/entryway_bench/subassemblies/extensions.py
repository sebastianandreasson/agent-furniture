"""Shared extension frame and selectable storage modules."""

from __future__ import annotations

from querycad.furniture import PartCatalog, centered_box, top_countersunk_holes
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.part_numbers import (
    EXTENSION_SHELF_RAIL,
    EXTENSION_SHELF_SLAT,
    EXTENSION_SHELF_STOPPER,
    EXTENSION_STORAGE_BACK,
    EXTENSION_STORAGE_DIVIDER,
    EXTENSION_STORAGE_FLOOR,
    EXTENSION_TOP_RAIL_END,
    EXTENSION_TOP_RAIL_LONG,
    LEG,
    UMBRELLA_HOLDER_FRONT,
)
from querycad.models.entryway_bench.spec import EntrywayBenchSpec

PAINT = (0.43, 0.42, 0.39, 1.0)
PANEL = (0.47, 0.46, 0.43, 1.0)


def _add_frame(catalog: PartCatalog, spec: EntrywayBenchSpec, layout: BenchLayout) -> None:
    legs = catalog.part(LEG)
    legs.place(
        "leg_extension_end_front",
        (layout.extension_far_leg_x, layout.extension_front_leg_y, 0.0),
    ).place(
        "leg_extension_end_back",
        (layout.extension_far_leg_x, layout.extension_back_leg_y, 0.0),
    )

    top_rails = catalog.define_stock(
        number=EXTENSION_TOP_RAIL_LONG,
        description="Long rail below extension deck",
        material=spec.frame_material,
        size_mm=(
            layout.extension_long_member_length,
            spec.top_rail_thickness,
            spec.top_rail_height,
        ),
        color=PAINT,
    )
    for side, y in (
        ("front", layout.extension_front_leg_y),
        ("back", layout.extension_back_leg_y),
    ):
        top_rails.place(
            f"extension_top_rail_{side}",
            (layout.extension_rail_center_x, y, layout.top_rail_z),
        )

    catalog.define_stock(
        number=EXTENSION_TOP_RAIL_END,
        description="End rail below extension deck",
        material=spec.frame_material,
        size_mm=(
            spec.top_rail_thickness,
            layout.extension_end_member_depth,
            spec.top_rail_height,
        ),
        color=PAINT,
    ).place(
        "extension_top_rail_end",
        (layout.extension_far_leg_x, layout.extension_center_y, layout.top_rail_z),
    )


def _add_shoe_shelf(
    catalog: PartCatalog,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
) -> None:
    shelf_rotation = (spec.extension_shelf_angle_deg, 0.0, 0.0)
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
    for side, contact_y, contact_z in (
        ("front", layout.extension_front_rail_contact_y, layout.extension_front_rail_contact_z),
        ("back", layout.extension_back_rail_contact_y, layout.extension_back_rail_contact_z),
    ):
        shelf_rails.place(
            f"extension_shelf_rail_{side}",
            (
                layout.extension_rail_center_x,
                contact_y + layout.extension_shelf_rail_y_offset,
                contact_z - layout.extension_shelf_rail_z_offset,
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
        ((0.0, layout.extension_front_screw_y), (0.0, layout.extension_back_screw_y)),
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


def _add_umbrella_storage(
    catalog: PartCatalog,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
) -> None:
    panel_height = layout.top_rail_z - spec.storage_floor_top_height
    panels = (
        (
            EXTENSION_STORAGE_FLOOR,
            "Flat extension storage floor",
            (layout.storage_run_length, layout.storage_inner_depth, spec.storage_panel_thickness),
            "extension_storage_floor",
            (
                layout.extension_rail_center_x,
                layout.extension_center_y,
                layout.storage_floor_bottom_z,
            ),
        ),
        (
            EXTENSION_STORAGE_BACK,
            "Back retaining panel for extension storage",
            (layout.storage_run_length, spec.storage_panel_thickness, panel_height),
            "extension_storage_back",
            (
                layout.extension_rail_center_x,
                layout.storage_back_center_y,
                spec.storage_floor_top_height,
            ),
        ),
        (
            EXTENSION_STORAGE_DIVIDER,
            "Divider between umbrella and general storage compartments",
            (
                spec.storage_panel_thickness,
                layout.storage_inner_depth - spec.storage_panel_thickness,
                panel_height,
            ),
            "extension_storage_divider",
            (
                layout.storage_divider_center_x,
                layout.storage_divider_center_y,
                spec.storage_floor_top_height,
            ),
        ),
        (
            UMBRELLA_HOLDER_FRONT,
            "Low front retaining panel for umbrella compartment",
            (
                spec.umbrella_compartment_width,
                spec.storage_panel_thickness,
                spec.umbrella_front_height,
            ),
            "umbrella_holder_front",
            (
                layout.umbrella_front_center_x,
                layout.storage_front_center_y,
                spec.storage_floor_top_height,
            ),
        ),
    )
    for number, description, size, name, placement in panels:
        catalog.define_stock(
            number=number,
            description=description,
            material=spec.panel_material,
            size_mm=size,
            color=PANEL,
        ).place(name, placement)


def add_extension(
    catalog: PartCatalog,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
) -> None:
    """Compose the shared extension frame with the selected storage module."""

    if spec.extension_mode == "none":
        return
    _add_frame(catalog, spec, layout)
    if spec.extension_mode == "shoe_shelf":
        _add_shoe_shelf(catalog, spec, layout)
    else:
        _add_umbrella_storage(catalog, spec, layout)
