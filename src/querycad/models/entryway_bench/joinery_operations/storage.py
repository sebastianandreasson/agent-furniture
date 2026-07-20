"""Umbrella-storage panel connections."""

from __future__ import annotations

from querycad.furniture import DrillOperation, DrillPoint, JoineryPlan, rail_end_pocket_holes
from querycad.models.entryway_bench.joinery_operations.shared import (
    END_SETBACK,
    POCKET_NOTE,
    BenchFasteners,
    extension_end_x,
)
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.part_numbers import (
    EXTENSION_STORAGE_BACK,
    EXTENSION_STORAGE_DIVIDER,
    EXTENSION_STORAGE_FLOOR,
    LEG,
    UMBRELLA_HOLDER_FRONT,
)
from querycad.models.entryway_bench.spec import EntrywayBenchSpec


def _panel_clearance(
    *,
    operation_id: str,
    part_number: str,
    label: str,
    face: str,
    view_axes: tuple[str, str],
    points: tuple[DrillPoint, ...],
    notes: str,
    spec: EntrywayBenchSpec,
    fastener_code: str,
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
        depth_mm=spec.storage_panel_thickness,
        countersink_diameter_mm=spec.slat_countersink_diameter,
        angle_deg=90.0,
        fastener_code=fastener_code,
        counts_fastener=True,
        notes=notes,
    )


def add_storage_connections(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    hardware: BenchFasteners,
) -> None:
    """Document the umbrella module's panel joints from its cut-stock datums."""

    if spec.extension_mode != "umbrella_storage":
        return

    panel_height = layout.top_rail_z - spec.storage_floor_top_height
    plan.add_connection(
        joint_id="J19-STORAGE-BACK-LEGS",
        description="Storage back panel to the two back legs",
        target_part_number=LEG,
        operation=rail_end_pocket_holes(
            operation_id="DR-STORAGE-BACK-ENDS",
            part_number=EXTENSION_STORAGE_BACK,
            label="Pocket holes at both storage-back ends",
            run_axis="x",
            length=layout.storage_run_length,
            levels=(panel_height / 4, panel_height * 3 / 4),
            setback=END_SETBACK,
            face="inside face",
            bit_diameter=spec.pocket_hole_bit_diameter,
            angle_deg=spec.pocket_hole_angle_deg,
            fastener_code=hardware.frame.code,
            notes=POCKET_NOTE,
        ),
        assembly_step=5,
    )

    plan.add_connection(
        joint_id="J20-STORAGE-BACK-FLOOR",
        description="Storage back panel to storage floor",
        target_part_number=EXTENSION_STORAGE_FLOOR,
        operation=_panel_clearance(
            operation_id="DR-STORAGE-BACK-FLOOR",
            part_number=EXTENSION_STORAGE_BACK,
            label="Clearance holes along the storage-back bottom edge",
            face="inside face",
            view_axes=("x", "z"),
            points=tuple(
                DrillPoint(
                    (
                        layout.storage_run_length * index / 5,
                        spec.storage_panel_thickness / 2,
                        0.0,
                    ),
                    (0.0, 0.0, -1.0),
                    f"floor fixing {index}",
                )
                for index in range(1, 5)
            ),
            notes="Dry-fit square, then transfer the pilot locations into the storage floor.",
            spec=spec,
            fastener_code=hardware.slat.code,
        ),
        assembly_step=5,
    )

    plan.add_connection(
        joint_id="J21-STORAGE-DIVIDER-FLOOR",
        description="Umbrella compartment divider to storage floor",
        target_part_number=EXTENSION_STORAGE_FLOOR,
        operation=_panel_clearance(
            operation_id="DR-STORAGE-DIVIDER-FLOOR",
            part_number=EXTENSION_STORAGE_DIVIDER,
            label="Clearance holes through the divider bottom edge",
            face="inside face",
            view_axes=("y", "z"),
            points=tuple(
                DrillPoint(
                    (
                        spec.storage_panel_thickness / 2,
                        (layout.storage_inner_depth - spec.storage_panel_thickness) * index / 3,
                        0.0,
                    ),
                    (0.0, 0.0, -1.0),
                    f"floor fixing {index}",
                )
                for index in range(1, 3)
            ),
            notes="Clamp the divider square before transferring pilots into the floor.",
            spec=spec,
            fastener_code=hardware.slat.code,
        ),
        assembly_step=5,
    )

    for inner, joint_id, operation_id, target, description in (
        (
            True,
            "J22-UMBRELLA-FRONT-DIVIDER",
            "DR-UMBRELLA-FRONT-INNER-END",
            EXTENSION_STORAGE_DIVIDER,
            "Umbrella retaining face to compartment divider",
        ),
        (
            False,
            "J23-UMBRELLA-FRONT-LEG",
            "DR-UMBRELLA-FRONT-OUTER-END",
            LEG,
            "Umbrella retaining face to outer front leg",
        ),
    ):
        position, axis, end_label = extension_end_x(
            layout,
            spec.umbrella_compartment_width,
            inner=inner,
            setback=0.0,
        )
        plan.add_connection(
            joint_id=joint_id,
            description=description,
            target_part_number=target,
            operation=_panel_clearance(
                operation_id=operation_id,
                part_number=UMBRELLA_HOLDER_FRONT,
                label=f"Clearance holes at umbrella-front {end_label}",
                face=end_label,
                view_axes=("x", "z"),
                points=tuple(
                    DrillPoint(
                        (
                            position,
                            spec.storage_panel_thickness / 2,
                            spec.umbrella_front_height * index / 3,
                        ),
                        axis,
                        f"{end_label} fixing {index}",
                    )
                    for index in range(1, 3)
                ),
                notes="Transfer pilots after clamping the retaining face flush.",
                spec=spec,
                fastener_code=hardware.slat.code,
            ),
            assembly_step=6,
        )
