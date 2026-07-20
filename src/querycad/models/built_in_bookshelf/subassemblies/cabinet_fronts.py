"""Face frames, framed doors, knobs, and fixed post-zone panels."""

from __future__ import annotations

import cadquery as cq

from querycad.furniture import PartCatalog, stock_box
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.base_parts import (
    DOOR_KNOB,
    DOORS,
    FACE_FRAME_CENTER_STILE,
    FACE_FRAME_RAILS,
    FACE_FRAME_STILE,
    POST_FIXED_PANELS,
)
from querycad.models.built_in_bookshelf.subassemblies.materials import BRASS, DARK_OAK


def _framed_door(width: float, height: float, spec: BuiltInBookshelfSpec) -> cq.Workplane:
    outer = stock_box(width, spec.door_thickness, height, corner_radius=2.0)
    opening = stock_box(
        width - 2 * spec.door_frame_width,
        spec.door_thickness + 2.0,
        height - 2 * spec.door_frame_width,
    ).translate((0.0, 0.0, spec.door_frame_width))
    panel_overlap = 6.0
    panel = stock_box(
        width - 2 * spec.door_frame_width + 2 * panel_overlap,
        spec.door_thickness - spec.door_panel_recess,
        height - 2 * spec.door_frame_width + 2 * panel_overlap,
    ).translate((0.0, spec.door_panel_recess / 2, spec.door_frame_width - panel_overlap))
    return outer.cut(opening).union(panel)


def _fixed_post_panel(
    width: float,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> cq.Workplane:
    panel = _framed_door(width - 2 * spec.door_gap, layout.door_height, spec).translate(
        (0.0, 0.0, spec.face_frame_width + spec.door_gap)
    )
    rail_y = -(spec.door_thickness - spec.face_frame_thickness) / 2
    rail_size = (width, spec.face_frame_thickness, spec.face_frame_width)
    for z in (0.0, layout.face_frame_height - spec.face_frame_width):
        panel = panel.union(stock_box(*rail_size).translate((0.0, rail_y, z)))
    return panel


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


def add_fixed_post_panel(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    post_name: str,
) -> None:
    """Add the decorative, non-opening front across one post zone."""

    post = next(post for post in layout.posts if post.name == post_name)
    bridge_width = layout.cabinet_bridge_width(post.name)
    catalog.define(
        number=POST_FIXED_PANELS[post.name],
        description=(
            f"Non-opening framed inset panel continuing the cabinets across the {post.name} post"
        ),
        material=spec.finish_material,
        shape=_fixed_post_panel(bridge_width, spec, layout),
        stock_size_mm=(bridge_width, spec.door_thickness, layout.face_frame_height),
        color=DARK_OAK,
    ).place(
        f"post_fixed_panel_{post.name}",
        (post.center_x, layout.depths.door_center_y, spec.plinth_height),
    )


def add_cabinet_fronts(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:

    frame_y = layout.depths.face_frame_center_y
    full_stiles = catalog.define_stock(
        number=FACE_FRAME_STILE,
        description="Full-height outer base cabinet face-frame stile",
        material=spec.finish_material,
        size_mm=(
            spec.face_frame_width,
            spec.face_frame_thickness,
            layout.face_frame_height,
        ),
        color=DARK_OAK,
    )
    for bay in layout.bays:
        for index, center_x in enumerate(
            (
                bay.fitted_left_x + spec.face_frame_width / 2,
                bay.fitted_right_x - spec.face_frame_width / 2,
            ),
            start=1,
        ):
            full_stiles.place(
                f"face_frame_stile_{bay.name}_{index:02d}",
                (center_x, frame_y, spec.plinth_height),
            )

        rails = catalog.define_stock(
            number=FACE_FRAME_RAILS[bay.name],
            description=f"{bay.name.title()} face-frame top or bottom rail",
            material=spec.finish_material,
            size_mm=(
                bay.fitted_width - 2 * spec.face_frame_width,
                spec.face_frame_thickness,
                spec.face_frame_width,
            ),
            color=DARK_OAK,
        )
        for edge, z in (
            ("bottom", spec.plinth_height),
            (
                "top",
                spec.plinth_height + layout.face_frame_height - spec.face_frame_width,
            ),
        ):
            rails.place(f"face_frame_rail_{bay.name}_{edge}", (bay.center_x, frame_y, z))

    center_stiles = catalog.define_stock(
        number=FACE_FRAME_CENTER_STILE,
        description="Short face-frame center stile fitted between the top and bottom rails",
        material=spec.finish_material,
        size_mm=(
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
        position = door.name.removeprefix(f"door_{door.bay_name}").strip("_")
        label = f"{position} door" if position else "door"
        catalog.define(
            number=DOORS[door.name],
            description=f"Traditional framed {door.bay_name}-bay {label}",
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
    knob_z = (
        layout.door_bottom_z + layout.door_height * spec.knob_height_ratio - spec.knob_diameter / 2
    )
    for door in layout.doors:
        knob.place(
            f"knob_{door.name.removeprefix('door_')}",
            (door.knob_x, layout.depths.cabinet_front_y, knob_z),
        )
