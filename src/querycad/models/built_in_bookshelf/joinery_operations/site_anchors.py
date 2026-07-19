"""Verified-timber anchor patterns for core planks, post cladding, and crown."""

from __future__ import annotations

from querycad.furniture import DrillOperation, DrillPoint
from querycad.models.built_in_bookshelf.joinery_operations.notes import STRUCTURAL_NOTE
from querycad.models.built_in_bookshelf.layout import BuiltInLayout, PostLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.crown import CROWNS
from querycad.models.built_in_bookshelf.subassemblies.post_displays import POST_CLADDINGS


def core_upright_site_operation(
    spec: BuiltInBookshelfSpec,
    *,
    part_number: str,
    side: str,
    height: float,
) -> DrillOperation:
    is_left = side == "left"
    x = 0.0 if is_left else spec.core_upright_thickness
    axis = (-1.0, 0.0, 0.0) if is_left else (1.0, 0.0, 0.0)
    bottom = spec.core_anchor_end_inset
    top = height - spec.core_anchor_end_inset
    z_positions = tuple(bottom + (top - bottom) * index / 3 for index in range(4))
    return DrillOperation(
        operation_id=f"DR-{part_number.removesuffix('-001')}-SITE",
        part_number=part_number,
        label="Structural pilots through each full-height core upright into verified timber",
        kind="site_anchor_pilot",
        face="site-facing side",
        view_axes=("y", "z"),
        diameter_mm=spec.structural_pilot_hole_diameter,
        depth_mm=spec.structural_screw_length,
        points=tuple(
            DrillPoint(
                (x, y, z),
                axis,
                f"core anchor row {row}, level {level}",
            )
            for level, z in enumerate(z_positions, start=1)
            for row, y in enumerate(
                (
                    spec.core_anchor_depth_inset,
                    spec.shelf_depth - spec.core_anchor_depth_inset,
                ),
                start=1,
            )
        ),
        fastener_code="STRUCT-6X90-T30",
        counts_fastener=True,
        notes=f"This is the {side}-hand drilling orientation. " + STRUCTURAL_NOTE,
    )


def post_fixing_x_positions(width: float) -> tuple[float, ...]:
    """Return balanced fixing columns appropriate to a measured post width."""

    edge_inset = 30.0
    if width >= 240.0:
        return (edge_inset, width / 2, width - edge_inset)
    return (edge_inset, width - edge_inset)


def post_cladding_operation(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    post: PostLayout,
) -> DrillOperation:
    global_z_positions = (
        layout.post_cladding_bottom_z + 150.0,
        (layout.post_cladding_bottom_z + spec.height_under_beam) / 2,
        spec.height_under_beam - 150.0,
    )
    return DrillOperation(
        operation_id=f"DR-POST-CLADDING-{post.name.upper()}-SITE",
        part_number=POST_CLADDINGS[post.name],
        label=f"Structural pilots through oak cladding into the {post.name} existing post",
        kind="site_anchor_pilot",
        face="front face",
        view_axes=("x", "z"),
        diameter_mm=spec.structural_pilot_hole_diameter,
        depth_mm=spec.structural_screw_length,
        points=tuple(
            DrillPoint(
                (x, spec.post_trim_thickness / 2, z),
                (0.0, -1.0, 0.0),
                f"post anchor at {global_z:g} mm above floor",
            )
            for global_z in global_z_positions
            for z in (global_z - layout.post_cladding_bottom_z,)
            for x in post_fixing_x_positions(post.width)
        ),
        fastener_code="STRUCT-6X90-T30",
        counts_fastener=True,
        notes=STRUCTURAL_NOTE,
    )


def crown_operation(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    bay_name: str,
) -> DrillOperation:
    bay = layout.bay(bay_name)
    count = 2 if bay_name == "right" else 4
    fitted_start_offset = bay.fitted_left_x - bay.left_x
    usable_length = (
        layout.right_slope_crossing_x - fitted_start_offset
        if bay_name == "right"
        else bay.fitted_width
    )
    stock_height = (
        spec.height_under_beam - layout.right_crown_base_z
        if bay_name == "right"
        else spec.crown_height
    )
    return DrillOperation(
        operation_id=f"DR-CROWN-{bay_name.upper()}-SITE",
        part_number=CROWNS[bay_name],
        label=f"Pilots through the {bay_name} crown into the verified top beam",
        kind="site_anchor_pilot",
        face="top edge",
        view_axes=("x", "y"),
        diameter_mm=spec.structural_pilot_hole_diameter,
        depth_mm=spec.structural_screw_length,
        points=tuple(
            DrillPoint(
                (
                    usable_length * index / (count + 1),
                    spec.crown_depth / 2,
                    stock_height,
                ),
                (0.0, 0.0, 1.0),
                f"beam fixing {index}",
            )
            for index in range(1, count + 1)
        ),
        fastener_code="STRUCT-6X90-T30",
        counts_fastener=True,
        notes=STRUCTURAL_NOTE,
    )
