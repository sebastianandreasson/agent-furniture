"""Drilling operations for cabinet cases, face frames, and fixed post panels."""

from __future__ import annotations

from querycad.furniture import DrillOperation, DrillPoint
from querycad.models.built_in_bookshelf.joinery_operations.notes import ASSEMBLY_NOTE
from querycad.models.built_in_bookshelf.layout import BuiltInLayout, PostLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.base_cabinets import (
    BASE_BOTTOMS,
    BASE_DIVIDER,
    BASE_VERTICAL,
    POST_FIXED_PANELS,
)


def base_bottom_operation(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    bay_name: str,
) -> DrillOperation:
    bay = layout.bay(bay_name)
    length = bay.fitted_width - 2 * spec.base_panel_thickness
    y_positions = (55.0, layout.carcass_depth - 55.0)
    points = tuple(
        DrillPoint(
            (x, y, spec.base_panel_thickness / 2),
            axis,
            f"{end} cabinet side",
        )
        for x, axis, end in (
            (12.0, (-1.0, 0.0, 0.0), "left"),
            (length - 12.0, (1.0, 0.0, 0.0), "right"),
        )
        for y in y_positions
    )
    return DrillOperation(
        operation_id=f"DR-BASE-BOTTOM-{bay_name.upper()}",
        part_number=BASE_BOTTOMS[bay_name],
        label=f"Cabinet screws through the {bay_name} bottom into both sides",
        kind="pilot",
        face="bottom-panel ends",
        view_axes=("x", "y"),
        diameter_mm=spec.pilot_hole_diameter,
        depth_mm=spec.cabinet_screw_length,
        points=points,
        fastener_code="CAB-5X50-T20",
        counts_fastener=True,
        notes=ASSEMBLY_NOTE,
    )


def base_side_face_frame_operation(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> DrillOperation:
    return DrillOperation(
        operation_id="DR-BASE-SIDE-FACE-FRAME",
        part_number=BASE_VERTICAL,
        label="Pilots through each cabinet side into its full-height face-frame stile",
        kind="pilot",
        face="front edge",
        view_axes=("z", "x"),
        diameter_mm=spec.pilot_hole_diameter,
        depth_mm=spec.cabinet_screw_length,
        points=tuple(
            DrillPoint(
                (
                    spec.base_panel_thickness / 2,
                    layout.carcass_depth,
                    layout.carcass_height * ratio,
                ),
                (0.0, 1.0, 0.0),
                label,
            )
            for ratio, label in ((0.28, "lower stile fixing"), (0.72, "upper stile fixing"))
        ),
        fastener_code="CAB-5X50-T20",
        counts_fastener=True,
        notes=ASSEMBLY_NOTE,
    )


def base_divider_face_frame_operation(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> DrillOperation:
    return DrillOperation(
        operation_id="DR-BASE-DIVIDER-FACE-FRAME",
        part_number=BASE_DIVIDER,
        label="Pilots through each center divider into its short face-frame stile",
        kind="pilot",
        face="front edge",
        view_axes=("z", "x"),
        diameter_mm=spec.pilot_hole_diameter,
        depth_mm=spec.cabinet_screw_length,
        points=tuple(
            DrillPoint(
                (
                    spec.base_panel_thickness / 2,
                    layout.carcass_depth,
                    layout.base_divider_height * ratio,
                ),
                (0.0, 1.0, 0.0),
                label,
            )
            for ratio, label in ((0.28, "lower stile fixing"), (0.72, "upper stile fixing"))
        ),
        fastener_code="CAB-5X50-T20",
        counts_fastener=True,
        notes=ASSEMBLY_NOTE,
    )


def fixed_post_panel_operation(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    post: PostLayout,
) -> DrillOperation:
    width = layout.cabinet_bridge_width(post.name)
    lower_z = spec.face_frame_width + spec.door_gap + 130.0
    upper_z = layout.face_frame_height - lower_z
    return DrillOperation(
        operation_id=f"DR-POST-CABINET-FIXED-PANEL-{post.name.upper()}",
        part_number=POST_FIXED_PANELS[post.name],
        label=f"Concealed side pilots fixing the {post.name} post panel between cabinet stiles",
        kind="pilot",
        face="concealed side edges",
        view_axes=("x", "z"),
        diameter_mm=spec.pilot_hole_diameter,
        depth_mm=spec.cabinet_screw_length,
        points=tuple(
            DrillPoint(
                (x, spec.door_thickness / 2, z),
                axis,
                f"{side} stile fixing at {z:g} mm",
            )
            for x, axis, side in (
                (0.0, (-1.0, 0.0, 0.0), "left"),
                (width, (1.0, 0.0, 0.0), "right"),
            )
            for z in (lower_z, upper_z)
        ),
        fastener_code="CAB-5X50-T20",
        counts_fastener=True,
        notes=(
            "Fit this as a fixed decorative panel; it has no hinges, knob, or usable cabinet "
            "volume behind it. Drive screws from concealed side edges into the adjacent stiles."
        ),
    )
