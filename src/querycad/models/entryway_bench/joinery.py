"""Fasteners, drilling operations, and connection sequence for the bench."""

from __future__ import annotations

from querycad.furniture import (
    DrillOperation,
    DrillPoint,
    FastenerSpec,
    JoineryPlan,
    JoinerySchedule,
    PartCatalog,
    rail_end_pocket_holes,
)
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.parts import (
    EXTENSION_SHELF_RAIL,
    EXTENSION_SHELF_SLAT,
    EXTENSION_SHELF_STOPPER,
    EXTENSION_STORAGE_BACK,
    EXTENSION_STORAGE_DIVIDER,
    EXTENSION_STORAGE_FLOOR,
    EXTENSION_TOP_RAIL_END,
    EXTENSION_TOP_RAIL_LONG,
    LEG,
    SEAT_BASE,
    SHELF_RAIL,
    SHELF_RAIL_END,
    SHELF_SLAT,
    TOP_RAIL_END,
    TOP_RAIL_LONG,
    UMBRELLA_HOLDER_FRONT,
)
from querycad.models.entryway_bench.spec import EntrywayBenchSpec

END_SETBACK = 18.0
POCKET_NOTE = (
    "Use a 9.5 mm stepped pocket-hole bit and 15° jig. Datum all dimensions from "
    "the cut-stock minimum corner; verify the jig setting on an offcut."
)
JUNCTION_NOTE = (
    "Dry-fit the extension against the flush main end rail. Use the dowels for alignment, "
    "then tighten the concealed connector bolt from the extension side. Transfer receiver "
    "holes in assembly; do not infer certified capacity from the CAD joint."
)


def _hardware(
    spec: EntrywayBenchSpec,
) -> tuple[FastenerSpec, FastenerSpec, FastenerSpec, FastenerSpec, FastenerSpec]:
    frame_length = f"{spec.frame_pocket_screw_length:g}"
    top_length = f"{spec.top_pocket_screw_length:g}"
    slat_diameter = f"{spec.slat_screw_diameter:g}"
    slat_length = f"{spec.slat_screw_length:g}"
    connector_diameter = f"{spec.connector_bolt_diameter:g}"
    connector_length = f"{spec.connector_bolt_length:g}"
    dowel_diameter = f"{spec.alignment_dowel_diameter:g}"
    dowel_length = f"{spec.alignment_dowel_length:g}"
    return (
        FastenerSpec(
            code=f"PH-{frame_length}-T20",
            description=f"{frame_length} mm fine-thread pocket-hole screw",
            length_mm=spec.frame_pocket_screw_length,
            nominal_size="hardwood pocket screw",
            head="washer head",
            drive="T20",
            thread="fine, self-tapping",
            finish="indoor zinc",
            application="Rail-to-leg frame joints",
            notes=(
                "Prototype selection for 24 mm hardwood rails. Confirm collar setting, "
                "withdrawal resistance, and breakthrough on an offcut."
            ),
        ),
        FastenerSpec(
            code=f"PH-{top_length}-T20",
            description=f"{top_length} mm fine-thread pocket-hole screw",
            length_mm=spec.top_pocket_screw_length,
            nominal_size="hardwood pocket screw",
            head="washer head",
            drive="T20",
            thread="fine, self-tapping",
            finish="indoor zinc",
            application="Rail-to-L-shaped seat deck attachment",
            notes=(
                "Prototype selection for the 22 mm plywood deck. Verify point location and "
                "no show-face breakthrough on scrap."
            ),
        ),
        FastenerSpec(
            code=f"CSK-{slat_diameter}X{slat_length}-T20",
            description=(f"{spec.slat_screw_diameter:.1f} × {slat_length} mm slat screw"),
            length_mm=spec.slat_screw_length,
            nominal_size=f"{spec.slat_screw_diameter:.1f} mm",
            head="90° countersunk",
            drive="T20",
            thread="partial-thread wood screw",
            finish="indoor zinc",
            application="Shelf slats, shoe stop, and extension storage panels",
            notes=(
                "The 3.0 mm pilot is a hardwood prototype assumption; confirm "
                "against the selected screw root diameter and an offcut."
            ),
        ),
        FastenerSpec(
            code=f"CB-M{connector_diameter}X{connector_length}",
            description=(f"M{connector_diameter} × {connector_length} mm concealed connector bolt"),
            length_mm=spec.connector_bolt_length,
            nominal_size=f"M{connector_diameter}",
            head="low-profile furniture connector",
            drive="hex or Torx to suit selected system",
            thread="machine thread into matched receiver",
            finish="indoor zinc",
            application="Demountable inner ends of extension rails",
            notes=(
                "Select a matched bolt and cross-dowel or threaded receiver system, then "
                "verify edge distances and tightening access in a full-scale joint sample."
            ),
        ),
        FastenerSpec(
            code=f"DOWEL-{dowel_diameter}X{dowel_length}",
            description=(f"{dowel_diameter} × {dowel_length} mm fluted hardwood alignment dowel"),
            length_mm=spec.alignment_dowel_length,
            nominal_size=f"{dowel_diameter} mm",
            head="none",
            drive="none",
            thread="none",
            finish="unfinished hardwood",
            application="Alignment of upper extension rails at the clean junction",
            notes=(
                "Use dry at the demountable interface unless the final assembly is intended "
                "to be permanent. Confirm fit and moisture movement on offcuts."
            ),
        ),
    )


def _upward_pocket_holes(
    *,
    operation_id: str,
    part_number: str,
    label: str,
    length: float,
    count: int,
    rail_height: float,
    bit_diameter: float,
    angle_deg: float,
    fastener_code: str,
) -> DrillOperation:
    return DrillOperation(
        operation_id=operation_id,
        part_number=part_number,
        label=label,
        kind="pocket_hole",
        face="inside face",
        view_axes=("x", "z"),
        diameter_mm=bit_diameter,
        points=tuple(
            DrillPoint(
                (length * index / (count + 1), 0.0, rail_height - END_SETBACK),
                (0.0, 0.0, 1.0),
                f"deck attachment {index}",
            )
            for index in range(1, count + 1)
        ),
        angle_deg=angle_deg,
        fastener_code=fastener_code,
        counts_fastener=True,
        notes=POCKET_NOTE,
    )


def _extension_end_x(
    layout: BenchLayout,
    length: float,
    *,
    inner: bool,
    setback: float,
) -> tuple[float, tuple[float, float, float], str]:
    inner_is_minimum = layout.extension_sign > 0
    use_minimum = inner_is_minimum if inner else not inner_is_minimum
    if use_minimum:
        return setback, (-1.0, 0.0, 0.0), "inner end" if inner else "outer end"
    return (
        length - setback,
        (1.0, 0.0, 0.0),
        "inner end" if inner else "outer end",
    )


def _one_end_pocket_holes(
    *,
    operation_id: str,
    part_number: str,
    label: str,
    length: float,
    levels: tuple[float, ...],
    layout: BenchLayout,
    bit_diameter: float,
    angle_deg: float,
    fastener_code: str,
) -> DrillOperation:
    position, axis, end_label = _extension_end_x(layout, length, inner=False, setback=END_SETBACK)
    return DrillOperation(
        operation_id=operation_id,
        part_number=part_number,
        label=label,
        kind="pocket_hole",
        face="inside face",
        view_axes=("x", "z"),
        diameter_mm=bit_diameter,
        points=tuple(DrillPoint((position, 0.0, level), axis, end_label) for level in levels),
        angle_deg=angle_deg,
        fastener_code=fastener_code,
        counts_fastener=True,
        notes=POCKET_NOTE,
    )


def _inner_end_holes(
    *,
    operation_id: str,
    part_number: str,
    label: str,
    length: float,
    rail_thickness: float,
    levels: tuple[float, ...],
    layout: BenchLayout,
    diameter: float,
    fastener_code: str,
    kind: str,
) -> DrillOperation:
    position, axis, end_label = _extension_end_x(layout, length, inner=True, setback=0.0)
    return DrillOperation(
        operation_id=operation_id,
        part_number=part_number,
        label=label,
        kind=kind,
        face="inner end",
        view_axes=("y", "z"),
        diameter_mm=diameter,
        points=tuple(
            DrillPoint(
                (position, rail_thickness / 2, level),
                axis,
                f"{end_label} level {index}",
            )
            for index, level in enumerate(levels, start=1)
        ),
        depth_mm=None,
        fastener_code=fastener_code,
        counts_fastener=True,
        notes=JUNCTION_NOTE,
    )


def _add_frame_connections(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    frame_fastener: FastenerSpec,
    connector: FastenerSpec,
    dowel: FastenerSpec,
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
        source_part,
        label,
        run_axis,
        length,
        levels,
        step,
    ) in standard_connections:
        if spec.extension_mode == "none" and source_part == EXTENSION_TOP_RAIL_END:
            continue
        plan.add_connection(
            joint_id=joint_id,
            description=description,
            target_part_number=LEG,
            operation=rail_end_pocket_holes(
                operation_id=operation_id,
                part_number=source_part,
                label=label,
                run_axis=run_axis,
                length=length,
                levels=levels,
                setback=END_SETBACK,
                face="inside face",
                bit_diameter=spec.pocket_hole_bit_diameter,
                angle_deg=spec.pocket_hole_angle_deg,
                fastener_code=frame_fastener.code,
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
        operation=_one_end_pocket_holes(
            operation_id="DR-EXT-TOP-RAIL-OUTER-ENDS",
            part_number=EXTENSION_TOP_RAIL_LONG,
            label="Pocket holes at outer ends of extension top rails",
            length=layout.extension_long_member_length,
            levels=top_levels,
            layout=layout,
            bit_diameter=spec.pocket_hole_bit_diameter,
            angle_deg=spec.pocket_hole_angle_deg,
            fastener_code=frame_fastener.code,
        ),
        assembly_step=1,
    )
    top_connectors = _inner_end_holes(
        operation_id="DR-EXT-TOP-RAIL-INNER-CONNECTOR",
        part_number=EXTENSION_TOP_RAIL_LONG,
        label="Concealed connector clearance at each upper inner rail end",
        length=layout.extension_long_member_length,
        rail_thickness=spec.top_rail_thickness,
        levels=(spec.top_rail_height / 2,),
        layout=layout,
        diameter=spec.connector_clearance_hole_diameter,
        fastener_code=connector.code,
        kind="connector_clearance",
    )
    plan.add_operation(top_connectors)
    plan.add_joint(
        joint_id="J06-EXT-TOP-FRONT-JUNCTION",
        description="Front extension apron to flush main end apron",
        source_part_number=EXTENSION_TOP_RAIL_LONG,
        target_part_number=TOP_RAIL_END,
        fastener_code=connector.code,
        quantity=1,
        drill_operation_ids=(top_connectors.operation_id,),
        assembly_step=3,
        notes=JUNCTION_NOTE,
    )
    plan.add_joint(
        joint_id="J07-EXT-TOP-BACK-JUNCTION",
        description="Back extension apron to existing main back leg",
        source_part_number=EXTENSION_TOP_RAIL_LONG,
        target_part_number=LEG,
        fastener_code=connector.code,
        quantity=1,
        drill_operation_ids=(top_connectors.operation_id,),
        assembly_step=3,
        notes=JUNCTION_NOTE,
    )

    top_dowels = _inner_end_holes(
        operation_id="DR-EXT-TOP-RAIL-INNER-DOWELS",
        part_number=EXTENSION_TOP_RAIL_LONG,
        label="Alignment dowels at each upper inner rail end",
        length=layout.extension_long_member_length,
        rail_thickness=spec.top_rail_thickness,
        levels=(14.0, spec.top_rail_height - 14.0),
        layout=layout,
        diameter=spec.alignment_dowel_diameter,
        fastener_code=dowel.code,
        kind="alignment_dowel",
    )
    plan.add_operation(top_dowels)
    plan.add_joint(
        joint_id="J08-EXT-TOP-FRONT-DOWELS",
        description="Align front extension apron with main end apron",
        source_part_number=EXTENSION_TOP_RAIL_LONG,
        target_part_number=TOP_RAIL_END,
        fastener_code=dowel.code,
        quantity=2,
        drill_operation_ids=(top_dowels.operation_id,),
        assembly_step=3,
        notes=JUNCTION_NOTE,
    )
    plan.add_joint(
        joint_id="J09-EXT-TOP-BACK-DOWELS",
        description="Align back extension apron with main back leg",
        source_part_number=EXTENSION_TOP_RAIL_LONG,
        target_part_number=LEG,
        fastener_code=dowel.code,
        quantity=2,
        drill_operation_ids=(top_dowels.operation_id,),
        assembly_step=3,
        notes=JUNCTION_NOTE,
    )

    if spec.extension_mode != "shoe_shelf":
        return

    plan.add_connection(
        joint_id="J10-EXT-SHELF-OUTER-ENDS",
        description="Outer ends of angled shelf rails to the two outer legs",
        target_part_number=LEG,
        operation=_one_end_pocket_holes(
            operation_id="DR-EXT-SHELF-RAIL-OUTER-ENDS",
            part_number=EXTENSION_SHELF_RAIL,
            label="Pocket hole at outer end of each angled shelf rail",
            length=layout.extension_long_member_length,
            levels=(spec.shelf_rail_height / 2,),
            layout=layout,
            bit_diameter=spec.pocket_hole_bit_diameter,
            angle_deg=spec.pocket_hole_angle_deg,
            fastener_code=frame_fastener.code,
        ),
        assembly_step=2,
    )
    shelf_connectors = _inner_end_holes(
        operation_id="DR-EXT-SHELF-RAIL-INNER-CONNECTOR",
        part_number=EXTENSION_SHELF_RAIL,
        label="Concealed connector clearance at each angled inner rail end",
        length=layout.extension_long_member_length,
        rail_thickness=spec.shelf_rail_thickness,
        levels=(spec.shelf_rail_height / 2,),
        layout=layout,
        diameter=spec.connector_clearance_hole_diameter,
        fastener_code=connector.code,
        kind="connector_clearance",
    )
    plan.add_operation(shelf_connectors)
    plan.add_joint(
        joint_id="J11-EXT-SHELF-FRONT-JUNCTION",
        description="Front angled shelf rail to the main lower-shelf end rail",
        source_part_number=EXTENSION_SHELF_RAIL,
        target_part_number=SHELF_RAIL_END,
        fastener_code=connector.code,
        quantity=1,
        drill_operation_ids=(shelf_connectors.operation_id,),
        assembly_step=3,
        notes=JUNCTION_NOTE,
    )
    plan.add_joint(
        joint_id="J12-EXT-SHELF-BACK-JUNCTION",
        description="Back angled shelf rail to existing main back leg",
        source_part_number=EXTENSION_SHELF_RAIL,
        target_part_number=LEG,
        fastener_code=connector.code,
        quantity=1,
        drill_operation_ids=(shelf_connectors.operation_id,),
        assembly_step=3,
        notes=JUNCTION_NOTE,
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
            fastener_code=frame_fastener.code,
            notes=POCKET_NOTE,
        ),
        assembly_step=2,
    )


def _add_top_connections(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    top_fastener: FastenerSpec,
) -> None:
    plan.add_connection(
        joint_id="J14-MAIN-DECK",
        description="Seat deck to main long rails",
        target_part_number=SEAT_BASE,
        operation=_upward_pocket_holes(
            operation_id="DR-TOP-RAIL-LONG-DECK",
            part_number=TOP_RAIL_LONG,
            label="Upward pocket holes for the L-shaped deck",
            length=layout.long_member_length,
            count=4,
            rail_height=spec.top_rail_height,
            bit_diameter=spec.pocket_hole_bit_diameter,
            angle_deg=spec.pocket_hole_angle_deg,
            fastener_code=top_fastener.code,
        ),
        assembly_step=4,
    )
    if spec.extension_mode != "shoe_shelf":
        return

    plan.add_connection(
        joint_id="J15-EXTENSION-DECK",
        description="Extension wing of L-shaped deck to extension rails",
        target_part_number=SEAT_BASE,
        operation=_upward_pocket_holes(
            operation_id="DR-EXT-TOP-RAIL-DECK",
            part_number=EXTENSION_TOP_RAIL_LONG,
            label="Upward pocket holes for the extension wing",
            length=layout.extension_long_member_length,
            count=2,
            rail_height=spec.top_rail_height,
            bit_diameter=spec.pocket_hole_bit_diameter,
            angle_deg=spec.pocket_hole_angle_deg,
            fastener_code=top_fastener.code,
        ),
        assembly_step=4,
    )


def _add_shelf_connections(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    slat_fastener: FastenerSpec,
) -> None:
    main_clearance = DrillOperation(
        operation_id="DR-SHELF-SLAT-CLEARANCE",
        part_number=SHELF_SLAT,
        label="Countersunk clearance holes through each main shelf slat",
        kind="countersunk_clearance",
        face="top face",
        view_axes=("y", "x"),
        diameter_mm=spec.slat_clearance_hole_diameter,
        points=(
            DrillPoint(
                (
                    spec.shelf_slat_width / 2,
                    layout.main_slat_hole_inset,
                    spec.shelf_slat_thickness,
                ),
                (0.0, 0.0, -1.0),
                "front rail",
            ),
            DrillPoint(
                (
                    spec.shelf_slat_width / 2,
                    layout.main_slat_depth - layout.main_slat_hole_inset,
                    spec.shelf_slat_thickness,
                ),
                (0.0, 0.0, -1.0),
                "back rail",
            ),
        ),
        depth_mm=spec.shelf_slat_thickness,
        countersink_diameter_mm=spec.slat_countersink_diameter,
        angle_deg=90.0,
        fastener_code=slat_fastener.code,
        counts_fastener=True,
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

    extension_clearance = DrillOperation(
        operation_id="DR-EXT-SHELF-SLAT-CLEARANCE",
        part_number=EXTENSION_SHELF_SLAT,
        label="Countersunk clearance holes through each angled shelf slat",
        kind="countersunk_clearance",
        face="top face",
        view_axes=("y", "x"),
        diameter_mm=spec.slat_clearance_hole_diameter,
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
        depth_mm=spec.shelf_slat_thickness,
        countersink_diameter_mm=spec.slat_countersink_diameter,
        angle_deg=90.0,
        fastener_code=slat_fastener.code,
        counts_fastener=True,
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

    stopper_clearance = DrillOperation(
        operation_id="DR-STOPPER-CLEARANCE",
        part_number=EXTENSION_SHELF_STOPPER,
        label="Clearance holes through the shoe-stop face",
        kind="countersunk_clearance",
        face="front face",
        view_axes=("x", "z"),
        diameter_mm=spec.slat_clearance_hole_diameter,
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
        depth_mm=spec.extension_shelf_stopper_thickness,
        countersink_diameter_mm=spec.slat_countersink_diameter,
        angle_deg=90.0,
        fastener_code=slat_fastener.code,
        counts_fastener=True,
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


def _add_transfer_pilots(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    slat_fastener: FastenerSpec,
) -> None:
    plan.add_operation(
        DrillOperation(
            operation_id="DR-SHELF-RAIL-PILOTS",
            part_number=SHELF_RAIL,
            label="Hardwood pilots receiving main shelf-slat screws",
            kind="pilot",
            face="top face",
            view_axes=("x", "y"),
            diameter_mm=spec.slat_pilot_hole_diameter,
            points=tuple(
                DrillPoint(
                    (
                        center + layout.long_member_length / 2,
                        spec.shelf_rail_thickness / 2,
                        spec.shelf_rail_height,
                    ),
                    (0.0, 0.0, -1.0),
                    f"slat {index}",
                )
                for index, center in enumerate(layout.main_slat_centers, start=1)
            ),
            depth_mm=min(20.0, spec.shelf_rail_height - 2.0),
            fastener_code=slat_fastener.code,
            notes="Transfer from the clearance-drilled slats during a dry fit.",
        )
    )
    if spec.extension_mode != "shoe_shelf":
        return

    plan.add_operation(
        DrillOperation(
            operation_id="DR-EXT-SHELF-RAIL-PILOTS",
            part_number=EXTENSION_SHELF_RAIL,
            label="Hardwood pilots receiving angled shelf-slat screws",
            kind="pilot",
            face="top face",
            view_axes=("x", "y"),
            diameter_mm=spec.slat_pilot_hole_diameter,
            points=tuple(
                DrillPoint(
                    (
                        center
                        - layout.extension_rail_center_x
                        + layout.extension_long_member_length / 2,
                        spec.shelf_rail_thickness / 2,
                        spec.shelf_rail_height,
                    ),
                    (0.0, 0.0, -1.0),
                    f"slat {index}",
                )
                for index, center in enumerate(layout.extension_slat_centers, start=1)
            ),
            depth_mm=min(20.0, spec.shelf_rail_height - 2.0),
            fastener_code=slat_fastener.code,
            notes="Transfer from the clearance-drilled slats during a dry fit.",
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
            fastener_code=slat_fastener.code,
            notes="Transfer the centre from the stop after clamping the dry assembly.",
        )
    )


def _add_storage_connections(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    frame_fastener: FastenerSpec,
    panel_fastener: FastenerSpec,
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
            fastener_code=frame_fastener.code,
            notes=POCKET_NOTE,
        ),
        assembly_step=5,
    )

    back_floor = DrillOperation(
        operation_id="DR-STORAGE-BACK-FLOOR",
        part_number=EXTENSION_STORAGE_BACK,
        label="Clearance holes along the storage-back bottom edge",
        kind="countersunk_clearance",
        face="inside face",
        view_axes=("x", "z"),
        diameter_mm=spec.slat_clearance_hole_diameter,
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
        depth_mm=spec.storage_panel_thickness,
        countersink_diameter_mm=spec.slat_countersink_diameter,
        angle_deg=90.0,
        fastener_code=panel_fastener.code,
        counts_fastener=True,
        notes="Dry-fit square, then transfer the pilot locations into the storage floor.",
    )
    plan.add_connection(
        joint_id="J20-STORAGE-BACK-FLOOR",
        description="Storage back panel to storage floor",
        target_part_number=EXTENSION_STORAGE_FLOOR,
        operation=back_floor,
        assembly_step=5,
    )

    divider_floor = DrillOperation(
        operation_id="DR-STORAGE-DIVIDER-FLOOR",
        part_number=EXTENSION_STORAGE_DIVIDER,
        label="Clearance holes through the divider bottom edge",
        kind="countersunk_clearance",
        face="inside face",
        view_axes=("y", "z"),
        diameter_mm=spec.slat_clearance_hole_diameter,
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
        depth_mm=spec.storage_panel_thickness,
        countersink_diameter_mm=spec.slat_countersink_diameter,
        angle_deg=90.0,
        fastener_code=panel_fastener.code,
        counts_fastener=True,
        notes="Clamp the divider square before transferring pilots into the floor.",
    )
    plan.add_connection(
        joint_id="J21-STORAGE-DIVIDER-FLOOR",
        description="Umbrella compartment divider to storage floor",
        target_part_number=EXTENSION_STORAGE_FLOOR,
        operation=divider_floor,
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
        position, axis, end_label = _extension_end_x(
            layout,
            spec.umbrella_compartment_width,
            inner=inner,
            setback=0.0,
        )
        plan.add_connection(
            joint_id=joint_id,
            description=description,
            target_part_number=target,
            operation=DrillOperation(
                operation_id=operation_id,
                part_number=UMBRELLA_HOLDER_FRONT,
                label=f"Clearance holes at umbrella-front {end_label}",
                kind="countersunk_clearance",
                face=end_label,
                view_axes=("x", "z"),
                diameter_mm=spec.slat_clearance_hole_diameter,
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
                depth_mm=spec.storage_panel_thickness,
                countersink_diameter_mm=spec.slat_countersink_diameter,
                angle_deg=90.0,
                fastener_code=panel_fastener.code,
                counts_fastener=True,
                notes="Transfer pilots after clamping the retaining face flush.",
            ),
            assembly_step=6,
        )


def build_joinery_schedule(
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    catalog: PartCatalog,
) -> JoinerySchedule:
    """Build a count-safe schedule from the same part catalog used for geometry."""

    frame_fastener, top_fastener, slat_fastener, connector, dowel = _hardware(spec)
    notes = (
        "Indoor four-leg prototype without an extension; no design loads have been certified.",
        "Confirm material grades, moisture, edge distances, pilots, and jig settings on "
        "full-scale offcuts before fabrication.",
        "Pocket-hole locations are jig marks; slat clearance holes are cut CAD.",
    )
    if spec.extension_mode != "none":
        notes = (
            "Indoor six-leg prototype with a plywood seat deck; no design loads have been "
            "certified.",
            "The extension module transfers seat load through the flush apron joint. "
            "Load-test the selected storage module and its junction before use.",
            "Confirm material grades, connector system, moisture, edge distances, pilots, "
            "and jig settings on full-scale offcuts before fabrication.",
            "Pocket and connector locations are jig marks; slat clearance holes are cut CAD.",
        )

    plan = JoineryPlan(
        catalog.quantity,
        status="prototype_not_structurally_certified",
        notes=notes,
    ).add_fasteners(frame_fastener, top_fastener, slat_fastener)
    if spec.extension_mode != "none":
        plan.add_fasteners(connector, dowel)
    _add_frame_connections(plan, spec, layout, frame_fastener, connector, dowel)
    _add_top_connections(plan, spec, layout, top_fastener)
    _add_shelf_connections(plan, spec, layout, slat_fastener)
    _add_transfer_pilots(plan, spec, layout, slat_fastener)
    _add_storage_connections(plan, spec, layout, frame_fastener, slat_fastener)
    return plan.build()
