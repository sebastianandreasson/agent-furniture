"""Frame, extension-junction, and seat-deck connections."""

from __future__ import annotations

from querycad.furniture import DrillOperation, JoineryPlan, rail_end_pocket_holes
from querycad.models.entryway_bench.joinery_operations.shared import (
    END_SETBACK,
    JUNCTION_NOTE,
    POCKET_NOTE,
    BenchFasteners,
    inner_end_holes,
    one_end_pocket_holes,
    upward_pocket_holes,
)
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.part_numbers import (
    EXTENSION_SHELF_RAIL,
    EXTENSION_TOP_RAIL_END,
    EXTENSION_TOP_RAIL_LONG,
    LEG,
    SEAT_BASE,
    SHELF_RAIL,
    SHELF_RAIL_END,
    TOP_RAIL_END,
    TOP_RAIL_LONG,
)
from querycad.models.entryway_bench.spec import EntrywayBenchSpec


def _add_junction_pair(
    plan: JoineryPlan,
    *,
    operation: DrillOperation,
    joint_ids: tuple[str, str],
    descriptions: tuple[str, str],
    targets: tuple[str, str],
    fastener_code: str,
    quantity: int,
) -> None:
    plan.add_operation(operation)
    for joint_id, description, target in zip(joint_ids, descriptions, targets, strict=True):
        plan.add_joint(
            joint_id=joint_id,
            description=description,
            source_part_number=operation.part_number,
            target_part_number=target,
            fastener_code=fastener_code,
            quantity=quantity,
            drill_operation_ids=(operation.operation_id,),
            assembly_step=3,
            notes=JUNCTION_NOTE,
        )


def add_frame_connections(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    hardware: BenchFasteners,
) -> None:
    top_levels = (END_SETBACK, spec.top_rail_height - END_SETBACK)
    standard_connections = (
        (
            "J01-MAIN-LONG-RAILS",
            "Main long top rails to four legs",
            "DR-TOP-RAIL-LONG-ENDS",
            TOP_RAIL_LONG,
            "Pocket holes at both rail ends",
            "x",
            layout.long_member_length,
            top_levels,
            1,
        ),
        (
            "J02-MAIN-END-RAILS",
            "Flush main end rails to four legs",
            "DR-TOP-RAIL-END-ENDS",
            TOP_RAIL_END,
            "Pocket holes at both end-rail ends",
            "y",
            layout.end_member_depth,
            top_levels,
            1,
        ),
        (
            "J03-EXT-END-RAIL",
            "Extension end rail to its two outer legs",
            "DR-EXT-TOP-RAIL-END-ENDS",
            EXTENSION_TOP_RAIL_END,
            "Pocket holes at both extension end-rail ends",
            "y",
            layout.extension_end_member_depth,
            top_levels,
            1,
        ),
        (
            "J04-MAIN-SHELF-RAILS",
            "Main shelf support rails to four legs",
            "DR-SHELF-RAIL-ENDS",
            SHELF_RAIL,
            "Single pocket hole at each shelf-rail end",
            "x",
            layout.long_member_length,
            (spec.shelf_rail_height / 2,),
            2,
        ),
    )
    for (
        joint_id,
        description,
        operation_id,
        source,
        label,
        axis,
        length,
        levels,
        step,
    ) in standard_connections:
        if spec.extension_mode == "none" and source == EXTENSION_TOP_RAIL_END:
            continue
        plan.add_connection(
            joint_id=joint_id,
            description=description,
            target_part_number=LEG,
            operation=rail_end_pocket_holes(
                operation_id=operation_id,
                part_number=source,
                label=label,
                run_axis=axis,
                length=length,
                levels=levels,
                setback=END_SETBACK,
                face="inside face",
                bit_diameter=spec.pocket_hole_bit_diameter,
                angle_deg=spec.pocket_hole_angle_deg,
                fastener_code=hardware.frame.code,
                notes=POCKET_NOTE,
            ),
            assembly_step=step,
        )

    if spec.extension_mode == "none":
        return

    plan.add_connection(
        joint_id="J05-EXT-TOP-OUTER-ENDS",
        description="Outer ends of extension top rails to the two outer legs",
        target_part_number=LEG,
        operation=one_end_pocket_holes(
            operation_id="DR-EXT-TOP-RAIL-OUTER-ENDS",
            part_number=EXTENSION_TOP_RAIL_LONG,
            label="Pocket holes at outer ends of extension top rails",
            length=layout.extension_long_member_length,
            levels=top_levels,
            layout=layout,
            bit_diameter=spec.pocket_hole_bit_diameter,
            angle_deg=spec.pocket_hole_angle_deg,
            fastener_code=hardware.frame.code,
        ),
        assembly_step=1,
    )
    top_connectors = inner_end_holes(
        operation_id="DR-EXT-TOP-RAIL-INNER-CONNECTOR",
        part_number=EXTENSION_TOP_RAIL_LONG,
        label="Concealed connector clearance at each upper inner rail end",
        length=layout.extension_long_member_length,
        rail_thickness=spec.top_rail_thickness,
        levels=(spec.top_rail_height / 2,),
        layout=layout,
        diameter=spec.connector_clearance_hole_diameter,
        fastener_code=hardware.connector.code,
        kind="connector_clearance",
    )
    _add_junction_pair(
        plan,
        operation=top_connectors,
        joint_ids=("J06-EXT-TOP-FRONT-JUNCTION", "J07-EXT-TOP-BACK-JUNCTION"),
        descriptions=(
            "Front extension apron to flush main end apron",
            "Back extension apron to existing main back leg",
        ),
        targets=(TOP_RAIL_END, LEG),
        fastener_code=hardware.connector.code,
        quantity=1,
    )

    top_dowels = inner_end_holes(
        operation_id="DR-EXT-TOP-RAIL-INNER-DOWELS",
        part_number=EXTENSION_TOP_RAIL_LONG,
        label="Alignment dowels at each upper inner rail end",
        length=layout.extension_long_member_length,
        rail_thickness=spec.top_rail_thickness,
        levels=(14.0, spec.top_rail_height - 14.0),
        layout=layout,
        diameter=spec.alignment_dowel_diameter,
        fastener_code=hardware.dowel.code,
        kind="alignment_dowel",
    )
    _add_junction_pair(
        plan,
        operation=top_dowels,
        joint_ids=("J08-EXT-TOP-FRONT-DOWELS", "J09-EXT-TOP-BACK-DOWELS"),
        descriptions=(
            "Align front extension apron with main end apron",
            "Align back extension apron with main back leg",
        ),
        targets=(TOP_RAIL_END, LEG),
        fastener_code=hardware.dowel.code,
        quantity=2,
    )

    if spec.extension_mode != "shoe_shelf":
        return

    plan.add_connection(
        joint_id="J10-EXT-SHELF-OUTER-ENDS",
        description="Outer ends of angled shelf rails to the two outer legs",
        target_part_number=LEG,
        operation=one_end_pocket_holes(
            operation_id="DR-EXT-SHELF-RAIL-OUTER-ENDS",
            part_number=EXTENSION_SHELF_RAIL,
            label="Pocket hole at outer end of each angled shelf rail",
            length=layout.extension_long_member_length,
            levels=(spec.shelf_rail_height / 2,),
            layout=layout,
            bit_diameter=spec.pocket_hole_bit_diameter,
            angle_deg=spec.pocket_hole_angle_deg,
            fastener_code=hardware.frame.code,
        ),
        assembly_step=2,
    )
    shelf_connectors = inner_end_holes(
        operation_id="DR-EXT-SHELF-RAIL-INNER-CONNECTOR",
        part_number=EXTENSION_SHELF_RAIL,
        label="Concealed connector clearance at each angled inner rail end",
        length=layout.extension_long_member_length,
        rail_thickness=spec.shelf_rail_thickness,
        levels=(spec.shelf_rail_height / 2,),
        layout=layout,
        diameter=spec.connector_clearance_hole_diameter,
        fastener_code=hardware.connector.code,
        kind="connector_clearance",
    )
    _add_junction_pair(
        plan,
        operation=shelf_connectors,
        joint_ids=("J11-EXT-SHELF-FRONT-JUNCTION", "J12-EXT-SHELF-BACK-JUNCTION"),
        descriptions=(
            "Front angled shelf rail to the main lower-shelf end rail",
            "Back angled shelf rail to existing main back leg",
        ),
        targets=(SHELF_RAIL_END, LEG),
        fastener_code=hardware.connector.code,
        quantity=1,
    )

    plan.add_connection(
        joint_id="J13-LOWER-SHELF-END-RAIL",
        description="Lower shelf end rail to the two main legs at the extension side",
        target_part_number=LEG,
        operation=rail_end_pocket_holes(
            operation_id="DR-SHELF-RAIL-END-ENDS",
            part_number=SHELF_RAIL_END,
            label="Pocket holes at both lower shelf end-rail ends",
            run_axis="y",
            length=layout.end_member_depth,
            levels=(spec.shelf_rail_height / 2,),
            setback=END_SETBACK,
            face="inside face",
            bit_diameter=spec.pocket_hole_bit_diameter,
            angle_deg=spec.pocket_hole_angle_deg,
            fastener_code=hardware.frame.code,
            notes=POCKET_NOTE,
        ),
        assembly_step=2,
    )


def add_top_connections(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    hardware: BenchFasteners,
) -> None:
    connections = [
        (
            "J14-MAIN-DECK",
            "Seat deck to main long rails",
            "DR-TOP-RAIL-LONG-DECK",
            TOP_RAIL_LONG,
            "Upward pocket holes for the L-shaped deck",
            layout.long_member_length,
            4,
        )
    ]
    if spec.extension_mode == "shoe_shelf":
        connections.append(
            (
                "J15-EXTENSION-DECK",
                "Extension wing of L-shaped deck to extension rails",
                "DR-EXT-TOP-RAIL-DECK",
                EXTENSION_TOP_RAIL_LONG,
                "Upward pocket holes for the extension wing",
                layout.extension_long_member_length,
                2,
            )
        )
    for joint_id, description, operation_id, part_number, label, length, count in connections:
        plan.add_connection(
            joint_id=joint_id,
            description=description,
            target_part_number=SEAT_BASE,
            operation=upward_pocket_holes(
                operation_id=operation_id,
                part_number=part_number,
                label=label,
                length=length,
                count=count,
                rail_height=spec.top_rail_height,
                bit_diameter=spec.pocket_hole_bit_diameter,
                angle_deg=spec.pocket_hole_angle_deg,
                fastener_code=hardware.top.code,
            ),
            assembly_step=4,
        )
