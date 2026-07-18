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
    EXTENSION_TOP,
    EXTENSION_TOP_RAIL_END,
    EXTENSION_TOP_RAIL_LONG,
    LEG,
    SEAT_BASE,
    SHELF_RAIL,
    SHELF_SLAT,
    TOP_RAIL_END,
    TOP_RAIL_LONG,
)
from querycad.models.entryway_bench.spec import EntrywayBenchSpec

END_SETBACK = 18.0
POCKET_NOTE = (
    "Use a 9.5 mm stepped pocket-hole bit and 15° jig. Datum all dimensions from "
    "the cut-stock minimum corner; verify the jig setting on an offcut."
)


def _hardware(spec: EntrywayBenchSpec) -> tuple[FastenerSpec, ...]:
    frame_length = f"{spec.frame_pocket_screw_length:g}"
    top_length = f"{spec.top_pocket_screw_length:g}"
    slat_diameter = f"{spec.slat_screw_diameter:g}"
    slat_length = f"{spec.slat_screw_length:g}"
    return (
        FastenerSpec(
            code=f"PH-{frame_length}-FINE",
            description=f"{frame_length} mm fine-thread zinc pocket-hole screw",
            length_mm=spec.frame_pocket_screw_length,
            nominal_size="Kreg fine-thread",
            head="Maxi-Loc washer head",
            drive="#2 square",
            thread="fine, self-tapping",
            finish="indoor zinc",
            application="Rail-to-leg frame joints in painted beech",
            manufacturer="Kreg",
            product_code=(
                "SML-F150" if spec.frame_pocket_screw_length == 38.0 else "verify-selection"
            ),
            source_url=("https://learn.kregtool.com/learn/how-to-select-right-pocket-hole-screw/"),
            notes=(
                "Prototype selection for 24 mm hardwood rails. Confirm jig collar and screw "
                "breakthrough on an offcut before drilling finished parts."
            ),
        ),
        FastenerSpec(
            code=f"PH-{top_length}-FINE",
            description=f"{top_length} mm fine-thread zinc pocket-hole screw",
            length_mm=spec.top_pocket_screw_length,
            nominal_size="Kreg fine-thread",
            head="Maxi-Loc washer head",
            drive="#2 square",
            thread="fine, self-tapping",
            finish="indoor zinc",
            application="Rail-to-seat-board attachment in painted beech",
            manufacturer="Kreg",
            product_code=(
                "SML-F125" if spec.top_pocket_screw_length == 32.0 else "verify-selection"
            ),
            source_url=(
                "https://www.kregtool.com/en/products/pocket-hole-joinery/"
                "pocket-hole-screws-plugs/pocket-hole-screws-zinc-coated/"
                "SML-F125-100.html"
            ),
            notes=(
                "Prototype selection for the 22 mm seat boards. Check point location from the "
                "show face and verify no breakthrough on scrap."
            ),
        ),
        FastenerSpec(
            code=f"CSK-{slat_diameter}X{slat_length}",
            description=(
                f"{spec.slat_screw_diameter:.1f} × {slat_length} mm countersunk hardwood screw"
            ),
            length_mm=spec.slat_screw_length,
            nominal_size=f"{spec.slat_screw_diameter:.1f} mm",
            head="90° countersunk",
            drive="T20 or Pozidriv #2; keep one drive type throughout",
            thread="partial-thread wood screw",
            finish="indoor zinc",
            application="Shelf slats and angled-shelf retaining stop",
            notes=(
                "Product remains to be selected. The 3.0 mm pilot is a hardwood prototype "
                "assumption; confirm against the selected screw root diameter and an offcut."
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
                f"top attachment {index}",
            )
            for index in range(1, count + 1)
        ),
        angle_deg=angle_deg,
        fastener_code=fastener_code,
        counts_fastener=True,
        notes=POCKET_NOTE,
    )


def _add_frame_connections(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    frame_fastener: FastenerSpec,
) -> None:
    top_levels = (END_SETBACK, spec.top_rail_height - END_SETBACK)
    connections = (
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
            "Main end top rails to four legs",
            "DR-TOP-RAIL-END-ENDS",
            TOP_RAIL_END,
            "Pocket holes at both end-rail ends",
            "y",
            layout.end_member_depth,
            top_levels,
            1,
        ),
        (
            "J03-EXT-LONG-RAILS",
            "Extension long top rails to transition and end legs",
            "DR-EXT-TOP-RAIL-LONG-ENDS",
            EXTENSION_TOP_RAIL_LONG,
            "Pocket holes at both extension-rail ends",
            "x",
            layout.extension_long_member_length,
            top_levels,
            2,
        ),
        (
            "J04-EXT-END-RAIL",
            "Extension end top rail to its two legs",
            "DR-EXT-TOP-RAIL-END-ENDS",
            EXTENSION_TOP_RAIL_END,
            "Pocket holes at both extension end-rail ends",
            "y",
            layout.extension_end_member_depth,
            top_levels,
            2,
        ),
        (
            "J05-MAIN-SHELF-RAILS",
            "Main shelf support rails to four legs",
            "DR-SHELF-RAIL-ENDS",
            SHELF_RAIL,
            "Single pocket hole at each shelf-rail end",
            "x",
            layout.long_member_length,
            (spec.shelf_rail_height / 2,),
            3,
        ),
        (
            "J06-EXT-SHELF-RAILS",
            "Angled shelf support rails to extension legs",
            "DR-EXT-SHELF-RAIL-ENDS",
            EXTENSION_SHELF_RAIL,
            "Single pocket hole at each angled shelf-rail end",
            "x",
            layout.extension_long_member_length,
            (spec.shelf_rail_height / 2,),
            3,
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
    ) in connections:
        operation = rail_end_pocket_holes(
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
        )
        plan.add_connection(
            joint_id=joint_id,
            description=description,
            target_part_number=LEG,
            operation=operation,
            assembly_step=step,
        )


def _add_top_connections(
    plan: JoineryPlan,
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    top_fastener: FastenerSpec,
) -> None:
    plan.add_connection(
        joint_id="J07-MAIN-SEAT",
        description="Main seat support board to long top rails",
        target_part_number=SEAT_BASE,
        operation=_upward_pocket_holes(
            operation_id="DR-TOP-RAIL-LONG-SEAT",
            part_number=TOP_RAIL_LONG,
            label="Upward pocket holes for the main seat board",
            length=layout.long_member_length,
            count=4,
            rail_height=spec.top_rail_height,
            bit_diameter=spec.pocket_hole_bit_diameter,
            angle_deg=spec.pocket_hole_angle_deg,
            fastener_code=top_fastener.code,
        ),
        assembly_step=4,
    )
    plan.add_connection(
        joint_id="J08-EXTENSION-TOP",
        description="Uncovered extension top to its long rails",
        target_part_number=EXTENSION_TOP,
        operation=_upward_pocket_holes(
            operation_id="DR-EXT-TOP-RAIL-SEAT",
            part_number=EXTENSION_TOP_RAIL_LONG,
            label="Upward pocket holes for the extension top",
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
        joint_id="J09-MAIN-SHELF-SLATS",
        description="Main shelf slats to front and back support rails",
        target_part_number=SHELF_RAIL,
        operation=main_clearance,
        assembly_step=5,
    )

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
        joint_id="J10-EXT-SHELF-SLATS",
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
        joint_id="J11-SHOE-STOP",
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
            label="Hardwood pilot holes receiving main shelf-slat screws",
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
    plan.add_operation(
        DrillOperation(
            operation_id="DR-EXT-SHELF-RAIL-PILOTS",
            part_number=EXTENSION_SHELF_RAIL,
            label="Hardwood pilot holes receiving angled shelf-slat screws",
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


def build_joinery_schedule(
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    catalog: PartCatalog,
) -> JoinerySchedule:
    """Build a count-safe schedule from the same part catalog used for geometry."""

    frame_fastener, top_fastener, slat_fastener = _hardware(spec)
    plan = JoineryPlan(
        catalog.quantity,
        status="prototype_not_structurally_certified",
        notes=(
            "Indoor painted-beech prototype based on nominal stock sizes; no design loads "
            "have been certified.",
            "Confirm material species, moisture, screw product, edge distances, and jig "
            "settings on offcuts before fabrication.",
            "Pocket locations are jig marks, while shelf-slat clearance holes are cut into "
            "the CAD.",
        ),
    ).add_fasteners(frame_fastener, top_fastener, slat_fastener)
    _add_frame_connections(plan, spec, layout, frame_fastener)
    _add_top_connections(plan, spec, layout, top_fastener)
    _add_shelf_connections(plan, spec, layout, slat_fastener)
    _add_transfer_pilots(plan, spec, layout, slat_fastener)
    return plan.build()
