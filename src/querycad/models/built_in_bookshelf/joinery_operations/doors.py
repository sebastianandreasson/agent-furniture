"""Hinge and knob drilling operations for the five operable cabinet doors."""

from __future__ import annotations

from querycad.furniture import DrillOperation, DrillPoint
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.base_cabinets import DOORS


def door_operations(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> tuple[tuple[DrillOperation, DrillOperation], ...]:
    operations = []
    for door in layout.doors:
        number = DOORS[door.name]
        hinge_at_min = door.hinge_side == "left"
        hinge_x = 24.0 if hinge_at_min else door.width - 24.0
        hinge = DrillOperation(
            operation_id=f"DR-{number.removesuffix('-001')}-HINGES",
            part_number=number,
            label="Hinge mounting pilots on the door stile",
            kind="pilot",
            face="inside face",
            view_axes=("x", "z"),
            diameter_mm=2.5,
            depth_mm=spec.hinge_screw_length,
            points=tuple(
                DrillPoint(
                    (hinge_x, spec.door_thickness / 2, z),
                    (0.0, -1.0, 0.0),
                    label,
                )
                for z, label in (
                    (75.0, "lower hinge lower screw"),
                    (100.0, "lower hinge upper screw"),
                    (layout.door_height - 100.0, "upper hinge lower screw"),
                    (layout.door_height - 75.0, "upper hinge upper screw"),
                )
            ),
            fastener_code="HINGE-3.5X16-PZ2",
            counts_fastener=True,
            notes="Confirm the selected inset hinge template before boring the door or stile.",
        )
        knob_at_min = door.hinge_side == "right"
        knob_x = spec.knob_edge_inset if knob_at_min else door.width - spec.knob_edge_inset
        knob = DrillOperation(
            operation_id=f"DR-{number.removesuffix('-001')}-KNOB",
            part_number=number,
            label="Through-hole for the cabinet knob screw",
            kind="clearance",
            face="front face",
            view_axes=("x", "z"),
            diameter_mm=spec.knob_screw_diameter + 0.5,
            depth_mm=spec.door_thickness,
            points=(
                DrillPoint(
                    (
                        knob_x,
                        spec.door_thickness / 2,
                        layout.door_height * spec.knob_height_ratio,
                    ),
                    (0.0, 1.0, 0.0),
                    "knob centre",
                ),
            ),
            fastener_code="KNOB-M4X25",
            counts_fastener=True,
            notes="Drill from the show face with a backer to prevent breakout.",
        )
        operations.append((hinge, knob))
    return tuple(operations)
