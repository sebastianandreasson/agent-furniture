from __future__ import annotations

import pytest

from querycad.furniture import (
    Design,
    DrillOperation,
    DrillPoint,
    ExternalTargetSpec,
    FastenerSpec,
    JoineryPlan,
    PartCatalog,
    linear_centers,
    stock_box,
)


def test_part_catalog_collects_occurrences_from_multiple_subassemblies() -> None:
    catalog = PartCatalog()
    legs = catalog.define(
        number="LEG-001",
        description="Shared leg",
        material="beech",
        shape=stock_box(42, 42, 400),
        stock_size_mm=(42, 42, 400),
    )
    legs.place("main_leg", (0, 0, 0))

    catalog.part("LEG-001").place("extension_leg", (500, 0, 0))
    parts = catalog.freeze()

    assert len(parts) == 1
    assert parts[0].quantity == 2
    assert [placement.name for placement in parts[0].placements] == [
        "main_leg",
        "extension_leg",
    ]


def test_part_catalog_rejects_duplicate_definitions() -> None:
    catalog = PartCatalog()
    definition = {
        "number": "RAIL-001",
        "description": "Rail",
        "material": "beech",
        "shape": stock_box(400, 24, 60),
        "stock_size_mm": (400, 24, 60),
    }
    catalog.define(**definition)

    with pytest.raises(ValueError, match="already defined"):
        catalog.define(**definition)


def test_part_catalog_defines_rectangular_stock_with_matching_envelope() -> None:
    part = (
        PartCatalog()
        .define_stock(
            number="SHELF-001",
            description="Rounded shelf",
            material="oak",
            size_mm=(600, 200, 18),
            corner_radius=4,
        )
        .place("shelf", (0, 0, 400))
        .freeze()
    )

    bounds = part.shape.val().BoundingBox()
    assert part.stock_size_mm == (600, 200, 18)
    assert (bounds.xlen, bounds.ylen, bounds.zlen) == pytest.approx(part.stock_size_mm)


def test_joinery_plan_derives_hardware_from_drill_points_and_occurrences() -> None:
    catalog = PartCatalog()
    source = catalog.define(
        number="RAIL-001",
        description="Rail",
        material="beech",
        shape=stock_box(400, 24, 60),
        stock_size_mm=(400, 24, 60),
    )
    source.place("rail_front").place("rail_back")
    catalog.define(
        number="LEG-001",
        description="Leg",
        material="beech",
        shape=stock_box(42, 42, 400),
        stock_size_mm=(42, 42, 400),
    ).place("leg")

    fastener = FastenerSpec(
        code="PH-38",
        description="38 mm pocket screw",
        length_mm=38,
        nominal_size="fine",
        head="washer",
        drive="square",
        thread="fine",
        finish="zinc",
        application="rail to leg",
    )
    operation = DrillOperation(
        operation_id="DR-RAIL-ENDS",
        part_number="RAIL-001",
        label="End pockets",
        kind="pocket_hole",
        face="inside",
        view_axes=("x", "z"),
        diameter_mm=9.5,
        points=(
            DrillPoint((18, 0, 30), (-1, 0, 0)),
            DrillPoint((382, 0, 30), (1, 0, 0)),
        ),
        fastener_code=fastener.code,
        counts_fastener=True,
    )
    joinery = (
        JoineryPlan(catalog.quantity, status="prototype")
        .add_fasteners(fastener)
        .add_connection(
            joint_id="J01",
            description="Rails to legs",
            target_part_number="LEG-001",
            operation=operation,
            assembly_step=1,
        )
        .build()
    )
    design = Design(
        name="catalog-test",
        model="test",
        parameters={},
        parts=catalog.freeze(),
        joinery=joinery,
    )

    design.validate()

    assert design.joinery.hardware_quantities() == {"PH-38": 4}
    assert design.joinery.joints[0].quantity == 4


def test_joinery_plan_accepts_declared_site_targets_without_bom_parts() -> None:
    catalog = PartCatalog()
    rail = catalog.define(
        number="MOUNTING-RAIL-001",
        description="Wall mounting rail",
        material="oak",
        shape=stock_box(400, 18, 50),
        stock_size_mm=(400, 18, 50),
    )
    rail.place("mounting_rail")
    fastener = FastenerSpec(
        code="STRUCT-90",
        description="Structural timber screw",
        length_mm=90,
        nominal_size="6 mm",
        head="washer",
        drive="T30",
        thread="wood",
        finish="black",
        application="Existing timber post",
    )
    operation = DrillOperation(
        operation_id="DR-MOUNTING-RAIL",
        part_number="MOUNTING-RAIL-001",
        label="Site anchors",
        kind="pilot",
        face="front",
        view_axes=("x", "z"),
        diameter_mm=4,
        points=(DrillPoint((200, 9, 25), (0, -1, 0)),),
        fastener_code=fastener.code,
        counts_fastener=True,
    )
    schedule = (
        JoineryPlan(catalog.quantity, status="site_verification_required")
        .add_external_targets(ExternalTargetSpec("SITE-POST", "Verified existing timber post"))
        .add_fasteners(fastener)
        .add_connection(
            joint_id="J-SITE",
            description="Rail to existing post",
            target_part_number="SITE-POST",
            operation=operation,
            assembly_step=1,
        )
        .build()
    )
    design = Design(
        name="site-target-test",
        model="test",
        parameters={},
        parts=catalog.freeze(),
        joinery=schedule,
    )

    design.validate()

    assert design.joinery.hardware_quantities() == {"STRUCT-90": 1}
    assert all(part.number != "SITE-POST" for part in design.parts)


def test_linear_centers_preserves_equal_spacing_and_clearance() -> None:
    centers = linear_centers(span=300, item_width=30, count=4)

    assert centers == pytest.approx((-135, -45, 45, 135))
    assert [right - left for left, right in zip(centers, centers[1:], strict=False)] == [
        90,
        90,
        90,
    ]
