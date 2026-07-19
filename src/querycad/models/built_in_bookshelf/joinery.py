"""Assembly-sequenced internal and site-anchor schedule for the built-in bookshelf."""

from __future__ import annotations

from querycad.furniture import ExternalTargetSpec, JoineryPlan, JoinerySchedule, PartCatalog
from querycad.models.built_in_bookshelf.joinery_operations.base_cabinets import (
    base_bottom_operation,
    base_divider_face_frame_operation,
    base_side_face_frame_operation,
    fixed_post_panel_operation,
)
from querycad.models.built_in_bookshelf.joinery_operations.doors import door_operations
from querycad.models.built_in_bookshelf.joinery_operations.fasteners import fasteners
from querycad.models.built_in_bookshelf.joinery_operations.notes import (
    SITE_TOP_BEAM,
    SITE_VERTICAL_POSTS,
    STRUCTURAL_NOTE,
)
from querycad.models.built_in_bookshelf.joinery_operations.post_displays import (
    display_operation,
)
from querycad.models.built_in_bookshelf.joinery_operations.site_anchors import (
    core_upright_site_operation,
    crown_operation,
    post_cladding_operation,
)
from querycad.models.built_in_bookshelf.joinery_operations.upper_bookcase import (
    divider_operation,
    shelf_end_operation,
)
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.base_cabinets import (
    BASE_VERTICAL,
    DOOR_KNOB,
    FACE_FRAME_CENTER_STILE,
    FACE_FRAME_STILE,
)
from querycad.models.built_in_bookshelf.subassemblies.core_uprights import (
    CORE_UPRIGHT_LEFT,
    CORE_UPRIGHT_RIGHT,
    CORE_UPRIGHT_RIGHT_SCRIBED,
)
from querycad.models.built_in_bookshelf.subassemblies.post_displays import (
    POST_CLADDINGS,
    POST_DISPLAY_LEDGES,
    POST_DISPLAY_LIPS,
)
from querycad.models.built_in_bookshelf.subassemblies.upper_bookcase import (
    DIVIDER_LOWER,
    DIVIDER_MIDDLE,
    DIVIDER_TOP,
    SHELVES,
)

__all__ = ["SITE_TOP_BEAM", "SITE_VERTICAL_POSTS", "build_joinery_schedule"]


def _new_plan(spec: BuiltInBookshelfSpec, catalog: PartCatalog) -> JoineryPlan:
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
    ).add_fasteners(*fasteners(spec))
    return plan


def _add_base_connections(
    plan: JoineryPlan,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    for bay in layout.bays:
        plan.add_connection(
            joint_id=f"J-BASE-BOTTOM-{bay.name.upper()}",
            description=f"{bay.name.title()} cabinet bottom to its side panels",
            target_part_number=BASE_VERTICAL,
            operation=base_bottom_operation(spec, layout, bay.name),
            assembly_step=1,
        )
    plan.add_connection(
        joint_id="J-BASE-SIDE-FACE-FRAMES",
        description="Base cabinet side panels to matching full-height face-frame stiles",
        target_part_number=FACE_FRAME_STILE,
        operation=base_side_face_frame_operation(spec, layout),
        assembly_step=1,
    ).add_connection(
        joint_id="J-BASE-DIVIDER-FACE-FRAMES",
        description="Base cabinet center dividers to short face-frame center stiles",
        target_part_number=FACE_FRAME_CENTER_STILE,
        operation=base_divider_face_frame_operation(spec, layout),
        assembly_step=1,
    )
    for post in layout.posts:
        plan.add_connection(
            joint_id=f"J-POST-CABINET-FIXED-PANEL-{post.name.upper()}",
            description=f"Fixed inset panel across the {post.name} post zone",
            target_part_number=FACE_FRAME_STILE,
            operation=fixed_post_panel_operation(spec, layout, post),
            assembly_step=1,
        )


def _add_site_connections(
    plan: JoineryPlan,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    for post in layout.posts:
        plan.add_connection(
            joint_id=f"J-POST-CLADDING-{post.name.upper()}-SITE",
            description=f"{post.name.title()} oak post cladding to existing vertical timber",
            target_part_number=SITE_VERTICAL_POSTS,
            operation=post_cladding_operation(spec, layout, post),
            assembly_step=2,
            notes=STRUCTURAL_NOTE,
        )

    scribed_height = spec.right_slope_height_at(
        spec.right_opening_width - spec.core_upright_thickness
    )
    for operation in (
        core_upright_site_operation(
            spec,
            part_number=CORE_UPRIGHT_LEFT,
            side="left",
            height=spec.height_under_beam,
        ),
        core_upright_site_operation(
            spec,
            part_number=CORE_UPRIGHT_RIGHT,
            side="right",
            height=spec.height_under_beam,
        ),
        core_upright_site_operation(
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


def _add_upper_connections(
    plan: JoineryPlan,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    for bay in layout.bays:
        for side in ("left", "right"):
            target = CORE_UPRIGHT_LEFT
            if side == "right":
                target = CORE_UPRIGHT_RIGHT_SCRIBED if bay.name == "right" else CORE_UPRIGHT_RIGHT
            operation = shelf_end_operation(spec, layout, bay.name, side)
            plan.add_connection(
                joint_id=f"J-UPPER-SHELVES-{bay.name.upper()}-{side.upper()}-CORE",
                description=f"{bay.name.title()} shelf {side} ends to the full-height core upright",
                target_part_number=target,
                operation=operation,
                assembly_step=3,
            )

    divider_operations = (
        divider_operation(spec, DIVIDER_LOWER, layout.divider_segments[0].height),
        divider_operation(spec, DIVIDER_MIDDLE, spec.shelf_pitch - spec.shelf_thickness),
        divider_operation(
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


def _add_trim_and_display_connections(
    plan: JoineryPlan,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    for bay in layout.bays:
        plan.add_connection(
            joint_id=f"J-CROWN-{bay.name.upper()}-SITE",
            description=f"{bay.name.title()} crown restraint to the existing top beam",
            target_part_number=SITE_TOP_BEAM,
            operation=crown_operation(spec, layout, bay.name),
            assembly_step=4,
            notes=STRUCTURAL_NOTE,
        )
    for post in layout.posts:
        operations = (
            display_operation(
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
            display_operation(
                spec,
                post=post,
                part_number=POST_DISPLAY_LIPS[post.name],
                label=f"Pilots through each {post.name}-post retaining lip into its ledge",
                target=POST_DISPLAY_LEDGES[post.name],
                is_ledge=False,
            ),
        )
        for operation, target in operations:
            plan.add_connection(
                joint_id=f"J-{operation.part_number.removesuffix('-001')}",
                description=operation.label,
                target_part_number=target,
                operation=operation,
                assembly_step=4,
            )


def _add_door_connections(
    plan: JoineryPlan,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    for hinge, knob in door_operations(spec, layout):
        plan.add_connection(
            joint_id=f"J-{hinge.part_number.removesuffix('-001')}-HINGES",
            description=f"Hang {hinge.part_number} on the matching face frame",
            target_part_number=FACE_FRAME_STILE,
            operation=hinge,
            assembly_step=5,
        ).add_connection(
            joint_id=f"J-{knob.part_number.removesuffix('-001')}-KNOB",
            description=f"Fit the knob to {knob.part_number}",
            target_part_number=DOOR_KNOB,
            operation=knob,
            assembly_step=5,
        )


def build_joinery_schedule(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
    catalog: PartCatalog,
) -> JoinerySchedule:
    """Build the joinery plan in the same five stages used during assembly."""

    plan = _new_plan(spec, catalog)
    _add_base_connections(plan, spec, layout)
    _add_site_connections(plan, spec, layout)
    _add_upper_connections(plan, spec, layout)
    _add_trim_and_display_connections(plan, spec, layout)
    _add_door_connections(plan, spec, layout)
    return plan.build()
