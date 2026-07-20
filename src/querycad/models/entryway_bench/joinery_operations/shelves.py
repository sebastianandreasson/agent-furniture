"""Shelf-slat clearances and transferred support-rail pilots."""

from __future__ import annotations

from querycad.furniture import DrillOperation, DrillPoint, JoineryPlan
from querycad.models.entryway_bench.joinery_operations.shared import BenchFasteners
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.part_numbers import (
    EXTENSION_SHELF_RAIL,
    EXTENSION_SHELF_SLAT,
    EXTENSION_SHELF_STOPPER,
    SHELF_RAIL,
    SHELF_SLAT,
)
from querycad.models.entryway_bench.spec import EntrywayBenchSpec


def _clearance_operation(
    *,
    operation_id: str,
    part_number: str,
    label: str,
    points: tuple[DrillPoint, ...],
    depth: float,
    spec: EntrywayBenchSpec,
    fastener_code: str,
    notes: str,
    face: str = "top face",
    view_axes: tuple[str, str] = ("y", "x"),
    geometry_mode: str = "marked_only",
) -> DrillOperation:
    return DrillOperation(
        operation_id=operation_id,
        part_number=part_number,
        label=label,
        kind="countersunk_clearance",
        face=face,
        view_axes=view_axes,
        diameter_mm=spec.slat_clearance_hole_diameter,
        points=points,
        depth_mm=depth,
        countersink_diameter_mm=spec.slat_countersink_diameter,
        angle_deg=90.0,
        fastener_code=fastener_code,
        counts_fastener=True,
        geometry_mode=geometry_mode,
        notes=notes,
    )


def add_shelf_connections(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    hardware: BenchFasteners,
) -> None:
    main_clearance = _clearance_operation(
        operation_id="DR-SHELF-SLAT-CLEARANCE",
        part_number=SHELF_SLAT,
        label="Countersunk clearance holes through each main shelf slat",
        points=tuple(
            DrillPoint(
                (
                    spec.shelf_slat_width / 2,
                    y,
                    spec.shelf_slat_thickness,
                ),
                (0.0, 0.0, -1.0),
                rail,
            )
            for y, rail in (
                (layout.main_slat_hole_inset, "front rail"),
                (layout.main_slat_depth - layout.main_slat_hole_inset, "back rail"),
            )
        ),
        depth=spec.shelf_slat_thickness,
        spec=spec,
        fastener_code=hardware.slat.code,
        geometry_mode="cut",
        notes="Drill clearance and countersink from the show face.",
    )
    plan.add_connection(
        joint_id="J16-MAIN-SHELF-SLATS",
        description="Main shelf slats to front and back support rails",
        target_part_number=SHELF_RAIL,
        operation=main_clearance,
        assembly_step=5,
    )

    if spec.extension_mode != "shoe_shelf":
        return

    extension_clearance = _clearance_operation(
        operation_id="DR-EXT-SHELF-SLAT-CLEARANCE",
        part_number=EXTENSION_SHELF_SLAT,
        label="Countersunk clearance holes through each angled shelf slat",
        points=tuple(
            DrillPoint(
                (
                    spec.shelf_slat_width / 2,
                    local_y + spec.extension_shelf_length / 2,
                    spec.shelf_slat_thickness,
                ),
                (0.0, 0.0, -1.0),
                label,
            )
            for local_y, label in (
                (layout.extension_front_screw_y, "front support rail"),
                (layout.extension_back_screw_y, "back support rail"),
            )
        ),
        depth=spec.shelf_slat_thickness,
        spec=spec,
        fastener_code=hardware.slat.code,
        geometry_mode="cut",
        notes="Drill clearance and countersink from the show face.",
    )
    plan.add_connection(
        joint_id="J17-EXT-SHELF-SLATS",
        description="Angled shelf slats to both support rails",
        target_part_number=EXTENSION_SHELF_RAIL,
        operation=extension_clearance,
        assembly_step=5,
    )

    stopper_clearance = _clearance_operation(
        operation_id="DR-STOPPER-CLEARANCE",
        part_number=EXTENSION_SHELF_STOPPER,
        label="Clearance holes through the shoe-stop face",
        points=tuple(
            DrillPoint(
                (
                    center - layout.extension_rail_center_x + layout.extension_slat_span / 2,
                    0.0,
                    spec.extension_shelf_stopper_height / 2,
                ),
                (0.0, 1.0, 0.0),
                f"slat {index}",
            )
            for index, center in enumerate(layout.extension_slat_centers, start=1)
        ),
        depth=spec.extension_shelf_stopper_thickness,
        spec=spec,
        fastener_code=hardware.slat.code,
        face="front face",
        view_axes=("x", "z"),
        notes=(
            "Mark from the slat centres after a dry fit. These holes are documented but "
            "not cut in the model because the stop is drilled in assembly."
        ),
    )
    plan.add_connection(
        joint_id="J18-SHOE-STOP",
        description="Angled shelf shoe stop to the front of each slat",
        target_part_number=EXTENSION_SHELF_SLAT,
        operation=stopper_clearance,
        assembly_step=6,
    )


def _rail_pilot_operation(
    *,
    operation_id: str,
    part_number: str,
    label: str,
    centers: tuple[float, ...],
    center_offset: float,
    spec: EntrywayBenchSpec,
    fastener_code: str,
) -> DrillOperation:
    return DrillOperation(
        operation_id=operation_id,
        part_number=part_number,
        label=label,
        kind="pilot",
        face="top face",
        view_axes=("x", "y"),
        diameter_mm=spec.slat_pilot_hole_diameter,
        points=tuple(
            DrillPoint(
                (
                    center + center_offset,
                    spec.shelf_rail_thickness / 2,
                    spec.shelf_rail_height,
                ),
                (0.0, 0.0, -1.0),
                f"slat {index}",
            )
            for index, center in enumerate(centers, start=1)
        ),
        depth_mm=min(20.0, spec.shelf_rail_height - 2.0),
        fastener_code=fastener_code,
        notes="Transfer from the clearance-drilled slats during a dry fit.",
    )


def add_transfer_pilots(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    hardware: BenchFasteners,
) -> None:
    plan.add_operation(
        _rail_pilot_operation(
            operation_id="DR-SHELF-RAIL-PILOTS",
            part_number=SHELF_RAIL,
            label="Hardwood pilots receiving main shelf-slat screws",
            centers=layout.main_slat_centers,
            center_offset=layout.long_member_length / 2,
            spec=spec,
            fastener_code=hardware.slat.code,
        )
    )
    if spec.extension_mode != "shoe_shelf":
        return

    plan.add_operation(
        _rail_pilot_operation(
            operation_id="DR-EXT-SHELF-RAIL-PILOTS",
            part_number=EXTENSION_SHELF_RAIL,
            label="Hardwood pilots receiving angled shelf-slat screws",
            centers=layout.extension_slat_centers,
            center_offset=(
                -layout.extension_rail_center_x + layout.extension_long_member_length / 2
            ),
            spec=spec,
            fastener_code=hardware.slat.code,
        )
    )
    plan.add_operation(
        DrillOperation(
            operation_id="DR-EXT-SLAT-STOPPER-PILOT",
            part_number=EXTENSION_SHELF_SLAT,
            label="Pilot at the front end of each slat for the shoe stop",
            kind="pilot",
            face="front end",
            view_axes=("x", "z"),
            diameter_mm=spec.slat_pilot_hole_diameter,
            points=(
                DrillPoint(
                    (
                        spec.shelf_slat_width / 2,
                        0.0,
                        spec.shelf_slat_thickness / 2,
                    ),
                    (0.0, 1.0, 0.0),
                    "shoe-stop screw",
                ),
            ),
            depth_mm=min(20.0, spec.extension_shelf_length - 2.0),
            fastener_code=hardware.slat.code,
            notes="Transfer the centre from the stop after clamping the dry assembly.",
        )
    )
