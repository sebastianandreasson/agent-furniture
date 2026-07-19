"""Drilling operations for the front-facing-book display ledges and lips."""

from __future__ import annotations

from querycad.furniture import DrillOperation, DrillPoint
from querycad.models.built_in_bookshelf.joinery_operations.site_anchors import (
    post_fixing_x_positions,
)
from querycad.models.built_in_bookshelf.layout import PostLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec


def display_operation(
    spec: BuiltInBookshelfSpec,
    *,
    post: PostLayout,
    part_number: str,
    label: str,
    target: str,
    is_ledge: bool,
) -> tuple[DrillOperation, str]:
    if is_ledge:
        size_y = spec.display_ledge_depth
        size_z = spec.display_ledge_thickness
        axis = (0.0, -1.0, 0.0)
        points = tuple(
            DrillPoint((x, 10.0, size_z / 2), axis, f"post fixing {index}")
            for index, x in enumerate(post_fixing_x_positions(post.width), start=1)
        )
    else:
        size_y = spec.display_lip_thickness
        size_z = spec.display_lip_height
        axis = (0.0, 0.0, -1.0)
        points = tuple(
            DrillPoint((x, size_y / 2, size_z / 2), axis, f"ledge fixing {index}")
            for index, x in enumerate(post_fixing_x_positions(post.width), start=1)
        )
    return (
        DrillOperation(
            operation_id=f"DR-{part_number.removesuffix('-001')}",
            part_number=part_number,
            label=label,
            kind="pilot",
            face="concealed fixing face",
            view_axes=("x", "z"),
            diameter_mm=spec.pilot_hole_diameter,
            depth_mm=spec.shelf_screw_length,
            points=points,
            fastener_code="SHELF-4.5X45-T20",
            counts_fastener=True,
            notes="Keep all fixings behind the front-facing book and below the retaining lip.",
        ),
        target,
    )
