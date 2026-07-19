"""Prototype internal and site-anchor schedule for the built-in bookshelf."""

from __future__ import annotations

from querycad.furniture import (
    DrillOperation,
    DrillPoint,
    ExternalTargetSpec,
    FastenerSpec,
    JoineryPlan,
    JoinerySchedule,
    PartCatalog,
)
from querycad.models.built_in_bookshelf.layout import BuiltInLayout, PostLayout
from querycad.models.built_in_bookshelf.parts import (
    BASE_BOTTOMS,
    BASE_VERTICAL,
    CORE_UPRIGHT_LEFT,
    CORE_UPRIGHT_RIGHT,
    CORE_UPRIGHT_RIGHT_SCRIBED,
    CROWNS,
    DIVIDER_LOWER,
    DIVIDER_MIDDLE,
    DIVIDER_TOP,
    DOOR_KNOB,
    DOORS,
    FACE_FRAME_STILE,
    POST_CLADDINGS,
    POST_DISPLAY_LEDGES,
    POST_DISPLAY_LIPS,
    POST_FIXED_PANELS,
    SHELVES,
)
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec

SITE_VERTICAL_POSTS = "SITE-VERTICAL-POSTS"
SITE_TOP_BEAM = "SITE-TOP-BEAM"

STRUCTURAL_NOTE = (
    "Existing timber dimensions, species, condition, edge distance, and load path must be "
    "verified on site. Do not substitute masonry anchors or infer certified capacity from CAD."
)
ASSEMBLY_NOTE = (
    "Dry-fit and label every bay. Confirm the scribe allowance against the real opening before "
    "drilling or finishing show faces."
)


def _fasteners(spec: BuiltInBookshelfSpec) -> tuple[FastenerSpec, ...]:
    return (
        FastenerSpec(
            code="CAB-5X50-T20",
            description="5 × 50 mm cabinet construction screw",
            length_mm=spec.cabinet_screw_length,
            nominal_size=f"{spec.cabinet_screw_diameter:g} mm",
            head="small washer head",
            drive="T20",
            thread="partial wood thread",
            finish="black oxide",
            application="Base carcass, face frame, fixed post panels, and divider assembly",
            notes="Confirm pilot size and edge distance on matching oak and plywood offcuts.",
        ),
        FastenerSpec(
            code="SHELF-4.5X45-T20",
            description="4.5 × 45 mm countersunk display screw",
            length_mm=spec.shelf_screw_length,
            nominal_size=f"{spec.shelf_screw_diameter:g} mm",
            head="countersunk",
            drive="T20",
            thread="partial wood thread",
            finish="black oxide",
            application="Display ledges and retaining lips",
            notes="Countersink only enough to leave the stained show face clean.",
        ),
        FastenerSpec(
            code="CORE-SHELF-5X60-T25",
            description="5 × 60 mm core-to-shelf construction screw",
            length_mm=spec.core_shelf_screw_length,
            nominal_size=f"{spec.core_shelf_screw_diameter:g} mm",
            head="small washer head",
            drive="T25",
            thread="partial wood thread",
            finish="black oxide",
            application="Full-height core uprights to shelf ends",
            notes=(
                "Use the modeled end pilots and confirm withdrawal resistance in shelf stock "
                "before final assembly."
            ),
        ),
        FastenerSpec(
            code="STRUCT-6X90-T30",
            description="6 × 90 mm structural timber screw",
            length_mm=spec.structural_screw_length,
            nominal_size=f"{spec.structural_screw_diameter:g} mm",
            head="washer head",
            drive="T30",
            thread="structural wood thread",
            finish="black oxide",
            application="Core uprights and trim to verified existing timber",
            status="site_verification_required",
            notes=STRUCTURAL_NOTE,
        ),
        FastenerSpec(
            code="HINGE-3.5X16-PZ2",
            description="3.5 × 16 mm hinge mounting screw",
            length_mm=spec.hinge_screw_length,
            nominal_size=f"{spec.hinge_screw_diameter:g} mm",
            head="countersunk",
            drive="PZ2",
            thread="full wood thread",
            finish="antique brass",
            application="Traditional cabinet door hinges",
            notes="Select hinges after confirming inset geometry and door weight.",
        ),
        FastenerSpec(
            code="KNOB-M4X25",
            description="M4 × 25 mm cabinet knob machine screw",
            length_mm=spec.knob_screw_length,
            nominal_size=f"M{spec.knob_screw_diameter:g}",
            head="pan head",
            drive="cross recess",
            thread="machine thread",
            finish="zinc",
            application="Aged-brass door knobs",
            notes="Confirm screw length against the selected knob and finished door thickness.",
        ),
    )


def _base_bottom_operation(
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


def _face_frame_operation(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> DrillOperation:
    return DrillOperation(
        operation_id="DR-BASE-VERTICAL-FACE-FRAME",
        part_number=BASE_VERTICAL,
        label="Pilots through each base vertical into its face-frame stile",
        kind="pilot",
        face="front edge",
        view_axes=("z", "x"),
        diameter_mm=spec.pilot_hole_diameter,
        depth_mm=spec.cabinet_screw_length,
        points=(
            DrillPoint(
                (
                    spec.base_panel_thickness / 2,
                    layout.carcass_depth,
                    layout.carcass_height * 0.28,
                ),
                (0.0, 1.0, 0.0),
                "lower stile fixing",
            ),
            DrillPoint(
                (
                    spec.base_panel_thickness / 2,
                    layout.carcass_depth,
                    layout.carcass_height * 0.72,
                ),
                (0.0, 1.0, 0.0),
                "upper stile fixing",
            ),
        ),
        fastener_code="CAB-5X50-T20",
        counts_fastener=True,
        notes=ASSEMBLY_NOTE,
    )


def _fixed_post_panel_operation(
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


def _shelf_end_operation(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    bay_name: str,
    side: str,
) -> DrillOperation:
    bay = layout.bay(bay_name)
    is_left = side == "left"
    x = 0.0 if is_left else bay.fitted_width
    axis = (-1.0, 0.0, 0.0) if is_left else (1.0, 0.0, 0.0)
    return DrillOperation(
        operation_id=f"DR-UPPER-SHELF-{bay_name.upper()}-{side.upper()}-END",
        part_number=SHELVES[bay_name],
        label=f"Pilot the {side} end of each {bay_name} shelf for its core upright",
        kind="pilot",
        face=f"{side} end",
        view_axes=("y", "z"),
        diameter_mm=spec.pilot_hole_diameter,
        depth_mm=spec.core_shelf_screw_length - spec.core_upright_thickness,
        points=tuple(
            DrillPoint(
                (x, y, spec.shelf_thickness / 2),
                axis,
                f"{side} core fixing {index}",
            )
            for index, y in enumerate(
                (
                    spec.core_anchor_depth_inset,
                    spec.shelf_depth - spec.core_anchor_depth_inset,
                ),
                start=1,
            )
        ),
        fastener_code="CORE-SHELF-5X60-T25",
        counts_fastener=True,
        notes=(
            "Clamp the shelf between the full-height uprights, drill through the upright into "
            "these end pilots, then drive the shelf screws from the concealed outer face."
        ),
    )


def _divider_operation(
    spec: BuiltInBookshelfSpec,
    part_number: str,
    height: float,
) -> DrillOperation:
    return DrillOperation(
        operation_id=f"DR-{part_number.removesuffix('-001')}",
        part_number=part_number,
        label="Pilots at both ends of each staggered divider",
        kind="pilot",
        face="divider ends",
        view_axes=("y", "z"),
        diameter_mm=spec.pilot_hole_diameter,
        depth_mm=spec.cabinet_screw_length,
        points=tuple(
            DrillPoint(
                (spec.divider_thickness / 2, y, z),
                axis,
                label,
            )
            for z, axis, label in (
                (10.0, (0.0, 0.0, -1.0), "lower member"),
                (height - 10.0, (0.0, 0.0, 1.0), "upper member"),
            )
            for y in (40.0, spec.shelf_depth - 40.0)
        ),
        fastener_code="CAB-5X50-T20",
        counts_fastener=True,
        notes=(
            "Use the resolved offset for each row; the alternating divider positions create "
            "the masonry-grid rhythm and support the long shelf spans."
        ),
    )


def _core_upright_site_operation(
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


def _post_fixing_x_positions(width: float) -> tuple[float, ...]:
    """Return balanced fixing columns appropriate to a measured post width."""

    edge_inset = 30.0
    if width >= 240.0:
        return (edge_inset, width / 2, width - edge_inset)
    return (edge_inset, width - edge_inset)


def _post_cladding_operation(
    spec: BuiltInBookshelfSpec,
    post: PostLayout,
) -> DrillOperation:
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
                f"post anchor at {z:g} mm",
            )
            for z in (850.0, 1550.0, 2250.0)
            for x in _post_fixing_x_positions(post.width)
        ),
        fastener_code="STRUCT-6X90-T30",
        counts_fastener=True,
        notes=STRUCTURAL_NOTE,
    )


def _crown_operation(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    bay_name: str,
) -> DrillOperation:
    bay = layout.bay(bay_name)
    length = bay.fitted_width
    count = 2 if bay_name == "right" else 4
    fitted_start_offset = bay.fitted_left_x - bay.left_x
    usable_length = (
        layout.right_slope_crossing_x - fitted_start_offset if bay_name == "right" else length
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


def _display_operation(
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
            for index, x in enumerate(_post_fixing_x_positions(post.width), start=1)
        )
    else:
        size_y = spec.display_lip_thickness
        size_z = spec.display_lip_height
        axis = (0.0, 0.0, -1.0)
        points = tuple(
            DrillPoint((x, size_y / 2, size_z / 2), axis, f"ledge fixing {index}")
            for index, x in enumerate(_post_fixing_x_positions(post.width), start=1)
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


def _door_operations(
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
                    (knob_x, spec.door_thickness / 2, layout.door_height * 0.58),
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


def build_joinery_schedule(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    catalog: PartCatalog,
) -> JoinerySchedule:
    plan = JoineryPlan(
        catalog.quantity,
        status="prototype_site_verification_required",
        notes=(
            spec.site_anchor_strategy,
            "The furniture is floor-supported. Full-height core uprights carry the cabinets and "
            "shelves, and are restrained only to verified existing timber; the brick wall is "
            "intentionally excluded.",
            "Material, loading, hinge selection, tolerances, scribing, and structural capacity "
            "remain fabrication assumptions requiring on-site verification.",
        ),
    )
    plan.add_external_targets(
        ExternalTargetSpec(
            code=SITE_VERTICAL_POSTS,
            description="Verified existing vertical timber posts",
            notes="Includes the opening boundaries and two internal posts; verify every fixing.",
        ),
        ExternalTargetSpec(
            code=SITE_TOP_BEAM,
            description="Verified existing top horizontal timber beam",
            notes="Used for crown restraint only; preserve the exposed beam face.",
        ),
    ).add_fasteners(*_fasteners(spec))

    for bay in layout.bays:
        plan.add_connection(
            joint_id=f"J-BASE-BOTTOM-{bay.name.upper()}",
            description=f"{bay.name.title()} cabinet bottom to its side panels",
            target_part_number=BASE_VERTICAL,
            operation=_base_bottom_operation(spec, layout, bay.name),
            assembly_step=1,
        )
    plan.add_connection(
        joint_id="J-BASE-FACE-FRAMES",
        description="Base cabinet verticals to matching face-frame stiles",
        target_part_number=FACE_FRAME_STILE,
        operation=_face_frame_operation(spec, layout),
        assembly_step=1,
    )
    for post in layout.posts:
        plan.add_connection(
            joint_id=f"J-POST-CABINET-FIXED-PANEL-{post.name.upper()}",
            description=f"Fixed inset panel across the {post.name} post zone",
            target_part_number=FACE_FRAME_STILE,
            operation=_fixed_post_panel_operation(spec, layout, post),
            assembly_step=1,
        )

    for post in layout.posts:
        plan.add_connection(
            joint_id=f"J-POST-CLADDING-{post.name.upper()}-SITE",
            description=f"{post.name.title()} oak post cladding to existing vertical timber",
            target_part_number=SITE_VERTICAL_POSTS,
            operation=_post_cladding_operation(spec, post),
            assembly_step=2,
            notes=STRUCTURAL_NOTE,
        )

    scribed_height = spec.right_slope_height_at(
        spec.right_opening_width - spec.core_upright_thickness
    )
    for operation in (
        _core_upright_site_operation(
            spec,
            part_number=CORE_UPRIGHT_LEFT,
            side="left",
            height=spec.height_under_beam,
        ),
        _core_upright_site_operation(
            spec,
            part_number=CORE_UPRIGHT_RIGHT,
            side="right",
            height=spec.height_under_beam,
        ),
        _core_upright_site_operation(
            spec,
            part_number=CORE_UPRIGHT_RIGHT_SCRIBED,
            side="right",
            height=scribed_height,
        ),
    ):
        plan.add_connection(
            joint_id=f"J-{operation.part_number.removesuffix('-001')}-SITE",
            description=f"{operation.part_number} to verified opening-boundary timber",
            target_part_number=SITE_VERTICAL_POSTS,
            operation=operation,
            assembly_step=2,
            notes=STRUCTURAL_NOTE,
        )

    for bay in layout.bays:
        for side in ("left", "right"):
            target = CORE_UPRIGHT_LEFT
            if side == "right":
                target = CORE_UPRIGHT_RIGHT_SCRIBED if bay.name == "right" else CORE_UPRIGHT_RIGHT
            operation = _shelf_end_operation(spec, layout, bay.name, side)
            plan.add_connection(
                joint_id=f"J-UPPER-SHELVES-{bay.name.upper()}-{side.upper()}-CORE",
                description=(
                    f"{bay.name.title()} shelf {side} ends to the full-height core upright"
                ),
                target_part_number=target,
                operation=operation,
                assembly_step=3,
            )
    divider_operations = (
        _divider_operation(
            spec,
            DIVIDER_LOWER,
            layout.divider_segments[0].height,
        ),
        _divider_operation(
            spec,
            DIVIDER_MIDDLE,
            spec.shelf_pitch - spec.shelf_thickness,
        ),
        _divider_operation(
            spec,
            DIVIDER_TOP,
            layout.crown_bottom_z - (layout.shelf_bottoms[-1] + spec.shelf_thickness),
        ),
    )
    for operation in divider_operations:
        plan.add_connection(
            joint_id=f"J-{operation.part_number.removesuffix('-001')}",
            description="Staggered divider between adjacent horizontal members",
            target_part_number=SHELVES["middle"],
            operation=operation,
            assembly_step=3,
        )

    for bay in layout.bays:
        plan.add_connection(
            joint_id=f"J-CROWN-{bay.name.upper()}-SITE",
            description=f"{bay.name.title()} crown restraint to the existing top beam",
            target_part_number=SITE_TOP_BEAM,
            operation=_crown_operation(spec, layout, bay.name),
            assembly_step=4,
            notes=STRUCTURAL_NOTE,
        )
    for post in layout.posts:
        for operation, target in (
            _display_operation(
                spec,
                post=post,
                part_number=POST_DISPLAY_LEDGES[post.name],
                label=(
                    f"Concealed screws through each {post.name}-post display ledge "
                    "into its cladding"
                ),
                target=POST_CLADDINGS[post.name],
                is_ledge=True,
            ),
            _display_operation(
                spec,
                post=post,
                part_number=POST_DISPLAY_LIPS[post.name],
                label=f"Pilots through each {post.name}-post retaining lip into its ledge",
                target=POST_DISPLAY_LEDGES[post.name],
                is_ledge=False,
            ),
        ):
            plan.add_connection(
                joint_id=f"J-{operation.part_number.removesuffix('-001')}",
                description=operation.label,
                target_part_number=target,
                operation=operation,
                assembly_step=4,
            )

    for hinge, knob in _door_operations(spec, layout):
        plan.add_connection(
            joint_id=f"J-{hinge.part_number.removesuffix('-001')}-HINGES",
            description=f"Hang {hinge.part_number} on the matching face frame",
            target_part_number=FACE_FRAME_STILE,
            operation=hinge,
            assembly_step=5,
        )
        plan.add_connection(
            joint_id=f"J-{knob.part_number.removesuffix('-001')}-KNOB",
            description=f"Fit the knob to {knob.part_number}",
            target_part_number=DOOR_KNOB,
            operation=knob,
            assembly_step=5,
        )

    return plan.build()
