"""Modular base cabinets, masonry shelves, post displays, and crown parts."""

from __future__ import annotations

import cadquery as cq

from querycad.furniture import PartCatalog, stock_box
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec

BASE_VERTICAL = "BASE-CARCASS-VERTICAL-001"
FACE_FRAME_STILE = "FACE-FRAME-STILE-001"
DIVIDER_LOWER = "UPPER-DIVIDER-LOWER-001"
DIVIDER_MIDDLE = "UPPER-DIVIDER-MIDDLE-001"
DIVIDER_TOP = "UPPER-DIVIDER-TOP-001"
DOOR_KNOB = "DOOR-KNOB-001"

CORE_UPRIGHT_LEFT = "BOOKCASE-CORE-UPRIGHT-LH-001"
CORE_UPRIGHT_RIGHT = "BOOKCASE-CORE-UPRIGHT-RH-001"
CORE_UPRIGHT_RIGHT_SCRIBED = "BOOKCASE-CORE-UPRIGHT-RIGHT-SCRIBED-001"

POST_CLADDINGS = {
    "left": "STRUCTURAL-POST-CLADDING-LEFT-001",
    "middle": "STRUCTURAL-POST-CLADDING-MIDDLE-001",
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
POST_DISPLAY_LEDGES = {
    "left": "POST-DISPLAY-LEDGE-LEFT-001",
    "middle": "POST-DISPLAY-LEDGE-MIDDLE-001",
}
POST_DISPLAY_LIPS = {
    "left": "POST-DISPLAY-LIP-LEFT-001",
    "middle": "POST-DISPLAY-LIP-MIDDLE-001",
}

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
SHELVES = {
    "left": "UPPER-SHELF-LEFT-001",
    "middle": "UPPER-SHELF-MIDDLE-001",
    "right": "UPPER-SHELF-RIGHT-001",
}
CROWNS = {
    "left": "CROWN-LEFT-001",
    "middle": "CROWN-MIDDLE-001",
    "right": "CROWN-RIGHT-SLOPED-001",
}
DOORS = {
    "door_left_left": "DOOR-LEFT-LH-001",
    "door_left_right": "DOOR-LEFT-RH-001",
    "door_middle_left": "DOOR-MIDDLE-LH-001",
    "door_middle_right": "DOOR-MIDDLE-RH-001",
    "door_right": "DOOR-RIGHT-001",
}

DARK_OAK = (0.45, 0.24, 0.12, 1.0)
OAK_PANEL = (0.38, 0.20, 0.10, 1.0)
BRASS = (0.58, 0.40, 0.16, 1.0)


def _depth_center(depth: float) -> float:
    """Center a part between the wall plane and its front edge in negative Y."""

    return -depth / 2


def _front_center(overall_depth: float, part_depth: float) -> float:
    """Center a facing part against the front edge of a deeper assembly."""

    return -overall_depth + part_depth / 2


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
                _depth_center(spec.shelf_depth),
                0.0,
            ),
        )
    for bay in layout.bays[:2]:
        right_uprights.place(
            f"core_upright_{bay.name}_right",
            (
                bay.right_x - spec.core_upright_thickness / 2,
                _depth_center(spec.shelf_depth),
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
            _depth_center(spec.shelf_depth),
            0.0,
        ),
    )


def add_base_cabinets(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    """Add three floor-supported cabinet boxes with traditional inset fronts."""

    verticals = catalog.define(
        number=BASE_VERTICAL,
        description="Base cabinet side or paired-door divider",
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
        centers = [
            bay.fitted_left_x + spec.base_panel_thickness / 2,
            bay.fitted_right_x - spec.base_panel_thickness / 2,
        ]
        if bay.door_count == 2:
            centers.insert(1, bay.center_x)
        for index, center_x in enumerate(centers, start=1):
            verticals.place(
                f"base_vertical_{bay.name}_{index:02d}",
                (
                    center_x,
                    _depth_center(layout.carcass_depth),
                    layout.carcass_bottom_z,
                ),
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
            (bay.center_x, _depth_center(layout.carcass_depth), layout.carcass_bottom_z),
        )

        counter_width = bay.fitted_width
        catalog.define(
            number=COUNTERS[bay.name],
            description=f"{bay.name.title()} cabinet counter",
            material=spec.finish_material,
            shape=stock_box(counter_width, spec.lower_depth, spec.counter_thickness),
            stock_size_mm=(counter_width, spec.lower_depth, spec.counter_thickness),
            color=DARK_OAK,
        ).place(
            f"counter_{bay.name}",
            (
                bay.center_x,
                _depth_center(spec.lower_depth),
                spec.cabinet_top_height - spec.counter_thickness,
            ),
        )

        plinth_width = bay.fitted_width
        catalog.define(
            number=PLINTH_FRONTS[bay.name],
            description=f"Recessed {bay.name} cabinet plinth front",
            material=spec.finish_material,
            shape=stock_box(
                plinth_width,
                spec.base_panel_thickness,
                spec.plinth_height,
            ),
            stock_size_mm=(
                plinth_width,
                spec.base_panel_thickness,
                spec.plinth_height,
            ),
            color=DARK_OAK,
        ).place(
            f"plinth_front_{bay.name}",
            (
                bay.center_x,
                (-spec.lower_depth + spec.plinth_recess + spec.base_panel_thickness / 2),
                0.0,
            ),
        )

    for post in layout.posts:
        bridge_width = layout.cabinet_bridge_width(post.name)
        catalog.define(
            number=POST_COUNTER_BRIDGES[post.name],
            description=f"Counter bridge continuing over the {post.name} existing post",
            material=spec.finish_material,
            shape=stock_box(bridge_width, spec.lower_depth, spec.counter_thickness),
            stock_size_mm=(bridge_width, spec.lower_depth, spec.counter_thickness),
            color=DARK_OAK,
        ).place(
            f"post_counter_bridge_{post.name}",
            (
                post.center_x,
                _depth_center(spec.lower_depth),
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
            (
                post.center_x,
                (-spec.lower_depth + spec.plinth_recess + spec.base_panel_thickness / 2),
                0.0,
            ),
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
            (
                post.center_x,
                _front_center(spec.lower_depth, spec.door_thickness),
                spec.plinth_height,
            ),
        )

    stiles = catalog.define(
        number=FACE_FRAME_STILE,
        description="Base cabinet face-frame stile",
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
    frame_y = _front_center(spec.lower_depth, spec.face_frame_thickness)
    for bay in layout.bays:
        centers = [
            bay.fitted_left_x + spec.face_frame_width / 2,
            bay.fitted_right_x - spec.face_frame_width / 2,
        ]
        if bay.door_count == 2:
            centers.insert(1, bay.center_x)
        for index, center_x in enumerate(centers, start=1):
            stiles.place(
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

    door_y = _front_center(spec.lower_depth, spec.door_thickness)
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
            (door.center_x, door_y, layout.door_bottom_z),
        )

    knob = catalog.define(
        number=DOOR_KNOB,
        description="Simple round cabinet knob",
        material=spec.metal_material,
        shape=_knob(spec),
        stock_size_mm=(spec.knob_diameter, spec.knob_projection, spec.knob_diameter),
        color=BRASS,
    )
    knob_center_z = layout.door_bottom_z + layout.door_height * 0.58
    for door in layout.doors:
        knob.place(
            f"knob_{door.name.removeprefix('door_')}",
            (
                door.knob_x,
                -spec.lower_depth,
                knob_center_z - spec.knob_diameter / 2,
            ),
        )


def add_upper_shelving(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    """Add the resolved shelf courses and staggered masonry-grid divider segments."""

    for bay in layout.bays:
        shelf_width = bay.fitted_width
        shelves = catalog.define(
            number=SHELVES[bay.name],
            description=f"Full-width shelf for the {bay.name} opening",
            material=spec.finish_material,
            shape=stock_box(shelf_width, spec.shelf_depth, spec.shelf_thickness),
            stock_size_mm=(shelf_width, spec.shelf_depth, spec.shelf_thickness),
            color=DARK_OAK,
        )
        for index, bottom_z in enumerate(layout.shelf_bottoms, start=1):
            shelves.place(
                f"upper_shelf_{bay.name}_{index:02d}",
                (bay.center_x, _depth_center(spec.shelf_depth), bottom_z),
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
    divider_handles = {}
    for key, (number, description, height) in divider_types.items():
        divider_handles[key] = catalog.define(
            number=number,
            description=description,
            material=spec.finish_material,
            shape=stock_box(spec.divider_thickness, spec.shelf_depth, height),
            stock_size_mm=(spec.divider_thickness, spec.shelf_depth, height),
            color=DARK_OAK,
        )
    for divider in layout.divider_segments:
        key = divider.row if divider.row in (0, spec.shelf_count) else 1
        divider_handles[key].place(
            divider.name,
            (divider.center_x, _depth_center(spec.shelf_depth), divider.bottom_z),
        )


def add_post_trim_and_displays(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    """Clad the existing posts and bridge their shelf lines with tiny display ledges."""

    ledge_back_y = -spec.opening_depth - spec.post_trim_thickness
    for post in layout.posts:
        catalog.define(
            number=POST_CLADDINGS[post.name],
            description=(
                f"Full-height oak face cladding over the {post.name} existing structural post"
            ),
            material=spec.finish_material,
            shape=stock_box(
                post.width,
                spec.post_trim_thickness,
                spec.height_under_beam,
            ),
            stock_size_mm=(
                post.width,
                spec.post_trim_thickness,
                spec.height_under_beam,
            ),
            color=DARK_OAK,
        ).place(
            f"structural_post_cladding_{post.name}",
            (
                post.center_x,
                -spec.opening_depth - spec.post_trim_thickness / 2,
                0.0,
            ),
        )
        ledges = catalog.define(
            number=POST_DISPLAY_LEDGES[post.name],
            description=f"Slim {post.name}-post display ledge for a front-facing book",
            material=spec.finish_material,
            shape=stock_box(
                post.width,
                spec.display_ledge_depth,
                spec.display_ledge_thickness,
            ),
            stock_size_mm=(
                post.width,
                spec.display_ledge_depth,
                spec.display_ledge_thickness,
            ),
            color=DARK_OAK,
        )
        lips = catalog.define(
            number=POST_DISPLAY_LIPS[post.name],
            description=f"Low retaining lip on a {post.name}-post display ledge",
            material=spec.finish_material,
            shape=stock_box(
                post.width,
                spec.display_lip_thickness,
                spec.display_lip_height,
            ),
            stock_size_mm=(
                post.width,
                spec.display_lip_thickness,
                spec.display_lip_height,
            ),
            color=DARK_OAK,
        )
        for shelf_index, shelf_bottom in enumerate(layout.shelf_bottoms, start=1):
            ledges.place(
                f"post_display_ledge_{post.name}_{shelf_index:02d}",
                (
                    post.center_x,
                    ledge_back_y - spec.display_ledge_depth / 2,
                    shelf_bottom + spec.shelf_thickness - spec.display_ledge_thickness,
                ),
            )
            lips.place(
                f"post_display_lip_{post.name}_{shelf_index:02d}",
                (
                    post.center_x,
                    ledge_back_y - spec.display_ledge_depth + spec.display_lip_thickness / 2,
                    shelf_bottom + spec.shelf_thickness,
                ),
            )


def add_crown(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    """Add restrained trim below the exposed beam, including the right slope."""

    crown_y = _front_center(spec.shelf_depth, spec.crown_depth)
    for bay in layout.bays[:2]:
        width = bay.fitted_width
        catalog.define(
            number=CROWNS[bay.name],
            description=f"Simple crown below the top beam in the {bay.name} opening",
            material=spec.finish_material,
            shape=stock_box(width, spec.crown_depth, spec.crown_height),
            stock_size_mm=(width, spec.crown_depth, spec.crown_height),
            color=DARK_OAK,
        ).place(
            f"crown_{bay.name}",
            (bay.center_x, crown_y, layout.crown_bottom_z),
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
        (right_bay.center_x, crown_y, layout.right_crown_base_z),
    )


def build_part_catalog(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> PartCatalog:
    catalog = PartCatalog()
    add_core_uprights(catalog, spec, layout)
    add_base_cabinets(catalog, spec, layout)
    add_upper_shelving(catalog, spec, layout)
    add_post_trim_and_displays(catalog, spec, layout)
    add_crown(catalog, spec, layout)
    return catalog
