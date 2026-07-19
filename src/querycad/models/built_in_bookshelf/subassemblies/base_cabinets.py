"""Floor-supported cabinet cases, fronts, doors, and post-zone bridges."""

from __future__ import annotations

import cadquery as cq

from querycad.furniture import PartCatalog, stock_box
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.materials import (
    BRASS,
    DARK_OAK,
    OAK_PANEL,
)

BASE_VERTICAL = "BASE-CARCASS-VERTICAL-001"
BASE_DIVIDER = "BASE-CARCASS-DIVIDER-001"
FACE_FRAME_STILE = "FACE-FRAME-STILE-001"
FACE_FRAME_CENTER_STILE = "FACE-FRAME-CENTER-STILE-001"
DOOR_KNOB = "DOOR-KNOB-001"

BASE_BOTTOMS = {
    "left": "BASE-BOTTOM-LEFT-001",
    "middle": "BASE-BOTTOM-MIDDLE-001",
    "right": "BASE-BOTTOM-RIGHT-001",
}
COUNTERS = {
    "left": "COUNTER-LEFT-001",
    "middle": "COUNTER-MIDDLE-001",
    "right": "COUNTER-RIGHT-001",
}
PLINTH_FRONTS = {
    "left": "PLINTH-FRONT-LEFT-001",
    "middle": "PLINTH-FRONT-MIDDLE-001",
    "right": "PLINTH-FRONT-RIGHT-001",
}
FACE_FRAME_RAILS = {
    "left": "FACE-FRAME-RAIL-LEFT-001",
    "middle": "FACE-FRAME-RAIL-MIDDLE-001",
    "right": "FACE-FRAME-RAIL-RIGHT-001",
}
POST_COUNTER_BRIDGES = {
    "left": "POST-CABINET-COUNTER-BRIDGE-LEFT-001",
    "middle": "POST-CABINET-COUNTER-BRIDGE-MIDDLE-001",
}
POST_FIXED_PANELS = {
    "left": "POST-CABINET-FIXED-PANEL-LEFT-001",
    "middle": "POST-CABINET-FIXED-PANEL-MIDDLE-001",
}
POST_PLINTH_BRIDGES = {
    "left": "POST-CABINET-PLINTH-BRIDGE-LEFT-001",
    "middle": "POST-CABINET-PLINTH-BRIDGE-MIDDLE-001",
}
DOORS = {
    "door_left_left": "DOOR-LEFT-LH-001",
    "door_left_right": "DOOR-LEFT-RH-001",
    "door_middle_left": "DOOR-MIDDLE-LH-001",
    "door_middle_right": "DOOR-MIDDLE-RH-001",
    "door_right": "DOOR-RIGHT-001",
}


def _framed_door(
    width: float,
    height: float,
    spec: BuiltInBookshelfSpec,
) -> cq.Workplane:
    """Make a traditional frame-and-recessed-panel door as one shop assembly."""

    outer = stock_box(width, spec.door_thickness, height, corner_radius=2.0)
    opening = stock_box(
        width - 2 * spec.door_frame_width,
        spec.door_thickness + 2.0,
        height - 2 * spec.door_frame_width,
    ).translate((0.0, 0.0, spec.door_frame_width))
    frame = outer.cut(opening)
    panel_overlap = 6.0
    panel = stock_box(
        width - 2 * spec.door_frame_width + 2 * panel_overlap,
        spec.door_thickness - spec.door_panel_recess,
        height - 2 * spec.door_frame_width + 2 * panel_overlap,
    ).translate(
        (
            0.0,
            spec.door_panel_recess / 2,
            spec.door_frame_width - panel_overlap,
        )
    )
    return frame.union(panel)


def _fixed_post_panel(
    width: float,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> cq.Workplane:
    """Make a non-opening framed panel aligned with the operable cabinet doors."""

    panel_width = width - 2 * spec.door_gap
    panel = _framed_door(panel_width, layout.door_height, spec).translate(
        (0.0, 0.0, spec.face_frame_width + spec.door_gap)
    )
    rail_y = -(spec.door_thickness - spec.face_frame_thickness) / 2
    lower_rail = stock_box(
        width,
        spec.face_frame_thickness,
        spec.face_frame_width,
    ).translate((0.0, rail_y, 0.0))
    upper_rail = stock_box(
        width,
        spec.face_frame_thickness,
        spec.face_frame_width,
    ).translate(
        (
            0.0,
            rail_y,
            layout.face_frame_height - spec.face_frame_width,
        )
    )
    return panel.union(lower_rail).union(upper_rail)


def _knob(spec: BuiltInBookshelfSpec) -> cq.Workplane:
    radius = spec.knob_diameter / 2
    stem_length = min(8.0, spec.knob_projection / 2)
    stem = (
        cq.Workplane("XZ")
        .circle(radius / 3)
        .extrude(stem_length)
        .translate((0.0, stem_length, radius))
    )
    head = (
        cq.Workplane("XZ")
        .circle(radius)
        .extrude(spec.knob_projection - stem_length)
        .translate((0.0, spec.knob_projection, radius))
    )
    return stem.union(head).mirror(mirrorPlane="XZ")


def _notched_post_counter_bridge(
    post_width: float,
    bridge_width: float,
    spec: BuiltInBookshelfSpec,
) -> cq.Workplane:
    """Cut fitting pockets around the site post and adjacent core uprights.

    The bridge remains continuous across the room-facing half of the cabinet while
    the wall-facing half clears the fixed timber and the two structural core planks.
    """

    bridge = stock_box(bridge_width, spec.lower_depth, spec.counter_thickness)
    clearance = spec.installation_clearance
    notch_height = spec.counter_thickness + 2.0
    notches = (
        (
            -post_width / 2 - spec.core_upright_thickness / 2,
            spec.core_upright_thickness + 2 * clearance,
            spec.shelf_depth + clearance,
        ),
        (
            0.0,
            post_width + 2 * clearance,
            spec.opening_depth + clearance,
        ),
        (
            post_width / 2 + spec.core_upright_thickness / 2,
            spec.core_upright_thickness + 2 * clearance,
            spec.shelf_depth + clearance,
        ),
    )
    for center_x, width, depth in notches:
        pocket = stock_box(width, depth, notch_height).translate(
            (center_x, (spec.lower_depth - depth) / 2, -1.0)
        )
        bridge = bridge.cut(pocket)
    return bridge


def add_base_cabinets(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    """Add the three cabinet boxes and the decorative run across both site posts."""

    side_panels = catalog.define(
        number=BASE_VERTICAL,
        description="Full-height base cabinet side panel",
        material=spec.panel_material,
        shape=stock_box(
            spec.base_panel_thickness,
            layout.carcass_depth,
            layout.carcass_height,
        ),
        stock_size_mm=(
            spec.base_panel_thickness,
            layout.carcass_depth,
            layout.carcass_height,
        ),
        color=OAK_PANEL,
    )
    for bay in layout.bays:
        side_centers = (
            bay.fitted_left_x + spec.base_panel_thickness / 2,
            bay.fitted_right_x - spec.base_panel_thickness / 2,
        )
        for index, center_x in enumerate(side_centers, start=1):
            side_panels.place(
                f"base_vertical_{bay.name}_{index:02d}",
                (center_x, layout.depths.carcass_center_y, layout.carcass_bottom_z),
            )

    dividers = catalog.define(
        number=BASE_DIVIDER,
        description="Paired-door base cabinet center divider above the cabinet bottom",
        material=spec.panel_material,
        shape=stock_box(
            spec.base_panel_thickness,
            layout.carcass_depth,
            layout.base_divider_height,
        ),
        stock_size_mm=(
            spec.base_panel_thickness,
            layout.carcass_depth,
            layout.base_divider_height,
        ),
        color=OAK_PANEL,
    )
    for bay in layout.bays:
        if bay.door_count == 2:
            dividers.place(
                f"base_divider_{bay.name}",
                (bay.center_x, layout.depths.carcass_center_y, layout.base_divider_bottom_z),
            )

    for bay in layout.bays:
        bottom_width = bay.fitted_width - 2 * spec.base_panel_thickness
        catalog.define(
            number=BASE_BOTTOMS[bay.name],
            description=f"{bay.name.title()} base cabinet bottom",
            material=spec.panel_material,
            shape=stock_box(bottom_width, layout.carcass_depth, spec.base_panel_thickness),
            stock_size_mm=(bottom_width, layout.carcass_depth, spec.base_panel_thickness),
            color=OAK_PANEL,
        ).place(
            f"base_bottom_{bay.name}",
            (bay.center_x, layout.depths.carcass_center_y, layout.carcass_bottom_z),
        )

        catalog.define(
            number=COUNTERS[bay.name],
            description=f"{bay.name.title()} cabinet counter",
            material=spec.finish_material,
            shape=stock_box(bay.fitted_width, spec.lower_depth, spec.counter_thickness),
            stock_size_mm=(bay.fitted_width, spec.lower_depth, spec.counter_thickness),
            color=DARK_OAK,
        ).place(
            f"counter_{bay.name}",
            (
                bay.center_x,
                layout.depths.cabinet_center_y,
                spec.cabinet_top_height - spec.counter_thickness,
            ),
        )

        catalog.define(
            number=PLINTH_FRONTS[bay.name],
            description=f"Recessed {bay.name} cabinet plinth front",
            material=spec.finish_material,
            shape=stock_box(
                bay.fitted_width,
                spec.base_panel_thickness,
                spec.plinth_height,
            ),
            stock_size_mm=(
                bay.fitted_width,
                spec.base_panel_thickness,
                spec.plinth_height,
            ),
            color=DARK_OAK,
        ).place(
            f"plinth_front_{bay.name}",
            (bay.center_x, layout.depths.plinth_center_y, 0.0),
        )

    for post in layout.posts:
        bridge_width = layout.cabinet_bridge_width(post.name)
        catalog.define(
            number=POST_COUNTER_BRIDGES[post.name],
            description=f"Notched counter bridge around the {post.name} existing post",
            material=spec.finish_material,
            shape=_notched_post_counter_bridge(post.width, bridge_width, spec),
            stock_size_mm=(bridge_width, spec.lower_depth, spec.counter_thickness),
            color=DARK_OAK,
        ).place(
            f"post_counter_bridge_{post.name}",
            (
                post.center_x,
                layout.depths.cabinet_center_y,
                spec.cabinet_top_height - spec.counter_thickness,
            ),
        )
        catalog.define(
            number=POST_PLINTH_BRIDGES[post.name],
            description=f"Recessed plinth bridge across the {post.name} existing post",
            material=spec.finish_material,
            shape=stock_box(
                bridge_width,
                spec.base_panel_thickness,
                spec.plinth_height,
            ),
            stock_size_mm=(
                bridge_width,
                spec.base_panel_thickness,
                spec.plinth_height,
            ),
            color=DARK_OAK,
        ).place(
            f"post_plinth_bridge_{post.name}",
            (post.center_x, layout.depths.plinth_center_y, 0.0),
        )
        catalog.define(
            number=POST_FIXED_PANELS[post.name],
            description=(
                f"Non-opening framed inset panel continuing the cabinets across the "
                f"{post.name} post"
            ),
            material=spec.finish_material,
            shape=_fixed_post_panel(bridge_width, spec, layout),
            stock_size_mm=(bridge_width, spec.door_thickness, layout.face_frame_height),
            color=DARK_OAK,
        ).place(
            f"post_fixed_panel_{post.name}",
            (post.center_x, layout.depths.door_center_y, spec.plinth_height),
        )

    full_stiles = catalog.define(
        number=FACE_FRAME_STILE,
        description="Full-height outer base cabinet face-frame stile",
        material=spec.finish_material,
        shape=stock_box(
            spec.face_frame_width,
            spec.face_frame_thickness,
            layout.face_frame_height,
        ),
        stock_size_mm=(
            spec.face_frame_width,
            spec.face_frame_thickness,
            layout.face_frame_height,
        ),
        color=DARK_OAK,
    )
    frame_y = layout.depths.face_frame_center_y
    for bay in layout.bays:
        side_centers = (
            bay.fitted_left_x + spec.face_frame_width / 2,
            bay.fitted_right_x - spec.face_frame_width / 2,
        )
        for index, center_x in enumerate(side_centers, start=1):
            full_stiles.place(
                f"face_frame_stile_{bay.name}_{index:02d}",
                (center_x, frame_y, spec.plinth_height),
            )

        rail_length = bay.fitted_width - 2 * spec.face_frame_width
        rails = catalog.define(
            number=FACE_FRAME_RAILS[bay.name],
            description=f"{bay.name.title()} face-frame top or bottom rail",
            material=spec.finish_material,
            shape=stock_box(
                rail_length,
                spec.face_frame_thickness,
                spec.face_frame_width,
            ),
            stock_size_mm=(
                rail_length,
                spec.face_frame_thickness,
                spec.face_frame_width,
            ),
            color=DARK_OAK,
        )
        rails.place(
            f"face_frame_rail_{bay.name}_bottom",
            (bay.center_x, frame_y, spec.plinth_height),
        )
        rails.place(
            f"face_frame_rail_{bay.name}_top",
            (
                bay.center_x,
                frame_y,
                spec.plinth_height + layout.face_frame_height - spec.face_frame_width,
            ),
        )

    center_stiles = catalog.define(
        number=FACE_FRAME_CENTER_STILE,
        description="Short face-frame center stile fitted between the top and bottom rails",
        material=spec.finish_material,
        shape=stock_box(
            spec.face_frame_width,
            spec.face_frame_thickness,
            layout.center_stile_height,
        ),
        stock_size_mm=(
            spec.face_frame_width,
            spec.face_frame_thickness,
            layout.center_stile_height,
        ),
        color=DARK_OAK,
    )
    for bay in layout.bays:
        if bay.door_count == 2:
            center_stiles.place(
                f"face_frame_center_stile_{bay.name}",
                (bay.center_x, frame_y, layout.center_stile_bottom_z),
            )

    for door in layout.doors:
        door_position = door.name.removeprefix(f"door_{door.bay_name}").strip("_")
        door_label = f"{door_position} door" if door_position else "door"
        catalog.define(
            number=DOORS[door.name],
            description=f"Traditional framed {door.bay_name}-bay {door_label}",
            material=spec.finish_material,
            shape=_framed_door(door.width, layout.door_height, spec),
            stock_size_mm=(door.width, spec.door_thickness, layout.door_height),
            color=DARK_OAK,
        ).place(
            door.name,
            (door.center_x, layout.depths.door_center_y, layout.door_bottom_z),
        )

    knob = catalog.define(
        number=DOOR_KNOB,
        description="Simple round cabinet knob",
        material=spec.metal_material,
        shape=_knob(spec),
        stock_size_mm=(spec.knob_diameter, spec.knob_projection, spec.knob_diameter),
        color=BRASS,
    )
    knob_center_z = layout.door_bottom_z + layout.door_height * spec.knob_height_ratio
    for door in layout.doors:
        knob.place(
            f"knob_{door.name.removeprefix('door_')}",
            (
                door.knob_x,
                layout.depths.cabinet_front_y,
                knob_center_z - spec.knob_diameter / 2,
            ),
        )
