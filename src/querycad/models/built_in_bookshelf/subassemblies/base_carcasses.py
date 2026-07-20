"""Floor-supported cabinet boxes and post-zone bridges."""

from __future__ import annotations

import cadquery as cq

from querycad.furniture import PartCatalog, stock_box
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.base_parts import (
    BASE_BOTTOMS,
    BASE_DIVIDER,
    BASE_VERTICAL,
    COUNTERS,
    PLINTH_FRONTS,
    POST_COUNTER_BRIDGES,
    POST_PLINTH_BRIDGES,
)
from querycad.models.built_in_bookshelf.subassemblies.materials import DARK_OAK, OAK_PANEL


def _notched_counter_bridge(
    post_width: float,
    bridge_width: float,
    spec: BuiltInBookshelfSpec,
) -> cq.Workplane:
    """Cut fitting pockets for a site post and its adjacent core uprights."""

    bridge = stock_box(bridge_width, spec.lower_depth, spec.counter_thickness)
    clearance = spec.installation_clearance
    notches = (
        (
            -post_width / 2 - spec.core_upright_thickness / 2,
            spec.core_upright_thickness + 2 * clearance,
            spec.shelf_depth + clearance,
        ),
        (0.0, post_width + 2 * clearance, spec.opening_depth + clearance),
        (
            post_width / 2 + spec.core_upright_thickness / 2,
            spec.core_upright_thickness + 2 * clearance,
            spec.shelf_depth + clearance,
        ),
    )
    for center_x, width, depth in notches:
        pocket = stock_box(width, depth, spec.counter_thickness + 2.0).translate(
            (center_x, (spec.lower_depth - depth) / 2, -1.0)
        )
        bridge = bridge.cut(pocket)
    return bridge


def add_base_carcasses(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    side_panels = catalog.define_stock(
        number=BASE_VERTICAL,
        description="Full-height base cabinet side panel",
        material=spec.panel_material,
        size_mm=(spec.base_panel_thickness, layout.carcass_depth, layout.carcass_height),
        color=OAK_PANEL,
    )
    for bay in layout.bays:
        for index, center_x in enumerate(
            (
                bay.fitted_left_x + spec.base_panel_thickness / 2,
                bay.fitted_right_x - spec.base_panel_thickness / 2,
            ),
            start=1,
        ):
            side_panels.place(
                f"base_vertical_{bay.name}_{index:02d}",
                (center_x, layout.depths.carcass_center_y, layout.carcass_bottom_z),
            )

    dividers = catalog.define_stock(
        number=BASE_DIVIDER,
        description="Paired-door base cabinet center divider above the cabinet bottom",
        material=spec.panel_material,
        size_mm=(
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
        catalog.define_stock(
            number=BASE_BOTTOMS[bay.name],
            description=f"{bay.name.title()} base cabinet bottom",
            material=spec.panel_material,
            size_mm=(bottom_width, layout.carcass_depth, spec.base_panel_thickness),
            color=OAK_PANEL,
        ).place(
            f"base_bottom_{bay.name}",
            (bay.center_x, layout.depths.carcass_center_y, layout.carcass_bottom_z),
        )
        catalog.define_stock(
            number=COUNTERS[bay.name],
            description=f"{bay.name.title()} cabinet counter",
            material=spec.finish_material,
            size_mm=(bay.fitted_width, spec.lower_depth, spec.counter_thickness),
            color=DARK_OAK,
        ).place(
            f"counter_{bay.name}",
            (
                bay.center_x,
                layout.depths.cabinet_center_y,
                spec.cabinet_top_height - spec.counter_thickness,
            ),
        )
        catalog.define_stock(
            number=PLINTH_FRONTS[bay.name],
            description=f"Recessed {bay.name} cabinet plinth front",
            material=spec.finish_material,
            size_mm=(bay.fitted_width, spec.base_panel_thickness, spec.plinth_height),
            color=DARK_OAK,
        ).place(
            f"plinth_front_{bay.name}",
            (bay.center_x, layout.depths.plinth_center_y, 0.0),
        )


def add_post_carcass_bridges(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    post_name: str,
) -> None:
    """Continue the counter and plinth around one existing post."""

    post = next(post for post in layout.posts if post.name == post_name)
    bridge_width = layout.cabinet_bridge_width(post.name)
    catalog.define(
        number=POST_COUNTER_BRIDGES[post.name],
        description=f"Notched counter bridge around the {post.name} existing post",
        material=spec.finish_material,
        shape=_notched_counter_bridge(post.width, bridge_width, spec),
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
    catalog.define_stock(
        number=POST_PLINTH_BRIDGES[post.name],
        description=f"Recessed plinth bridge across the {post.name} existing post",
        material=spec.finish_material,
        size_mm=(bridge_width, spec.base_panel_thickness, spec.plinth_height),
        color=DARK_OAK,
    ).place(
        f"post_plinth_bridge_{post.name}",
        (post.center_x, layout.depths.plinth_center_y, 0.0),
    )
