from __future__ import annotations

import pytest

from querycad.furniture import (
    Design,
    DrillOperation,
    DrillPoint,
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


def test_linear_centers_preserves_equal_spacing_and_clearance() -> None:
    centers = linear_centers(span=300, item_width=30, count=4)

    assert centers == pytest.approx((-135, -45, 45, 135))
    assert [right - left for left, right in zip(centers, centers[1:], strict=False)] == [
        90,
        90,
        90,
    ]
