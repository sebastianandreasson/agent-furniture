from __future__ import annotations

from pathlib import Path

import pytest

from querycad.config import load_design
from querycad.models.entryway_bench import EntrywayBenchSpec, build_entryway_bench

OVERLAP_VOLUME_TOLERANCE_MM3 = 1e-3
INTENTIONAL_SOFT_OVERLAPS = {
    frozenset(("CUSHION-001", "CUSHION-PIPING-001")),
}


def test_default_spec_matches_measured_dimensions() -> None:
    spec = EntrywayBenchSpec()

    assert (spec.length, spec.depth) == (1000.0, 250.0)
    assert (spec.extension_length, spec.extension_depth) == (600.0, 150.0)
    assert (spec.cushion_length, spec.cushion_depth, spec.cushion_thickness) == (
        990.0,
        240.0,
        30.0,
    )
    assert (spec.length - spec.cushion_length) / 2 == 5.0
    assert (spec.depth - spec.cushion_depth) / 2 == 5.0
    assert spec.frame_height + spec.cushion_thickness == 550.0
    assert spec.extension_shelf_angle_deg == 40.0


def test_default_bench_geometry_and_bom_quantities() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())

    design.validate()

    assert design.overall_size_mm() == pytest.approx(
        (
            spec.length + spec.extension_length,
            spec.depth,
            spec.frame_height + spec.cushion_thickness,
        )
    )
    assert design.total_occurrences() == 39
    assert {part.number: part.quantity for part in design.parts} == {
        "SEAT-BASE-001": 1,
        "LEG-001": 6,
        "TOP-RAIL-LONG-001": 2,
        "TOP-RAIL-END-001": 2,
        "SHELF-RAIL-001": 2,
        "SHELF-RAIL-END-001": 1,
        "SHELF-SLAT-001": spec.shelf_slat_count,
        "EXTENSION-TOP-RAIL-LONG-001": 2,
        "EXTENSION-TOP-RAIL-END-001": 1,
        "EXTENSION-SHELF-RAIL-001": 2,
        "EXTENSION-SHELF-SLAT-001": spec.extension_slat_count,
        "EXTENSION-SHELF-STOPPER-001": 1,
        "CUSHION-001": 1,
        "CUSHION-PIPING-001": 2,
    }


@pytest.mark.parametrize(
    ("extension_mode", "extension_side"),
    (
        ("shoe_shelf", "left"),
        ("shoe_shelf", "right"),
        ("umbrella_storage", "left"),
        ("umbrella_storage", "right"),
        ("none", "left"),
    ),
)
def test_rigid_part_occurrences_do_not_interpenetrate(
    extension_side: str,
    extension_mode: str,
) -> None:
    values = EntrywayBenchSpec().as_dict()
    values["extension_side"] = extension_side
    values["extension_mode"] = extension_mode
    design = build_entryway_bench("interference-check", values)
    occurrences = [
        (
            placement.name,
            part.number,
            part.shape.val().located(placement.location()),
        )
        for part in design.parts
        for placement in part.placements
    ]
    overlaps = []
    for index, (name_a, number_a, shape_a) in enumerate(occurrences):
        for name_b, number_b, shape_b in occurrences[index + 1 :]:
            if frozenset((number_a, number_b)) in INTENTIONAL_SOFT_OVERLAPS:
                continue
            volume = float(shape_a.intersect(shape_b).Volume())
            if volume > OVERLAP_VOLUME_TOLERANCE_MM3:
                overlaps.append((name_a, name_b, volume))

    assert overlaps == []


def test_joinery_schedule_matches_drill_marks_and_hardware_quantities() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())

    design.validate()

    assert design.joinery.status == "prototype_not_structurally_certified"
    assert design.joinery.hardware_quantities() == {
        "PH-38-T20": 32,
        "PH-32-T20": 12,
        "CSK-4X35-T20": 38,
        "CB-M6X50": 4,
        "DOWEL-8X40": 4,
    }
    assert len(design.joinery.joints) == 18
    assert len(design.joinery.drill_operations) == 18
    assert (
        sum(
            len(operation.points)
            * next(part.quantity for part in design.parts if part.number == operation.part_number)
            for operation in design.joinery.drill_operations
            if operation.counts_fastener
        )
        == 90
    )


def test_shelf_slats_include_documented_clearance_holes() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())
    parts = {part.number: part for part in design.parts}

    solid_main_slat_volume = (
        spec.shelf_slat_width * (spec.depth - spec.leg_size) * spec.shelf_slat_thickness
    )
    assert parts["SHELF-SLAT-001"].volume_mm3 < solid_main_slat_volume
    cut_operations = {
        operation.part_number
        for operation in design.joinery.drill_operations
        if operation.geometry_mode == "cut"
    }
    assert cut_operations == {"SHELF-SLAT-001", "EXTENSION-SHELF-SLAT-001"}


def test_one_piece_deck_retains_indent_and_main_only_cushion() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())

    parts = {part.number: part for part in design.parts}
    deck = parts["SEAT-BASE-001"]
    cushion = parts["CUSHION-001"]
    bounds = deck.shape.val().BoundingBox()

    assert "EXTENSION-TOP-001" not in parts
    assert deck.material == spec.panel_material
    assert bounds.xlen == pytest.approx(spec.length + spec.extension_length)
    assert bounds.ylen == pytest.approx(spec.depth)
    assert deck.volume_mm3 > spec.length * spec.depth * spec.seat_base_thickness
    assert deck.volume_mm3 < (
        (spec.length + spec.extension_length) * spec.depth * spec.seat_base_thickness
    )
    assert cushion.quantity == 1
    assert cushion.placements[0].translation_mm[0] == 0.0


def test_extension_has_six_leg_clean_junction_and_supported_shelf() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())
    parts = {part.number: part for part in design.parts}

    legs = parts["LEG-001"]
    end_rails = parts["TOP-RAIL-END-001"]
    extension_rails = parts["EXTENSION-TOP-RAIL-LONG-001"]
    shelf_end_rail = parts["SHELF-RAIL-END-001"]
    extension_shelf_rails = parts["EXTENSION-SHELF-RAIL-001"]
    extension_sign = 1 if spec.extension_side == "right" else -1
    side_name = "top_rail_right" if extension_sign > 0 else "top_rail_left"
    side_end_rail = next(
        placement for placement in end_rails.placements if placement.name == side_name
    )
    front_extension_rail = next(
        placement
        for placement in extension_rails.placements
        if placement.name == "extension_top_rail_front"
    )
    main_outer_face = side_end_rail.translation_mm[0] + (
        extension_sign * spec.top_rail_thickness / 2
    )
    extension_inner_end = front_extension_rail.translation_mm[0] - (
        extension_sign * extension_rails.stock_size_mm[0] / 2
    )
    shelf_end_placement = shelf_end_rail.placements[0]
    shelf_end_outer_face = shelf_end_placement.translation_mm[0] + (
        extension_sign * spec.shelf_rail_thickness / 2
    )
    front_extension_shelf_rail = next(
        placement
        for placement in extension_shelf_rails.placements
        if placement.name == "extension_shelf_rail_front"
    )
    extension_shelf_inner_end = front_extension_shelf_rail.translation_mm[0] - (
        extension_sign * extension_shelf_rails.stock_size_mm[0] / 2
    )

    assert legs.quantity == 6
    assert all("transition" not in placement.name for placement in legs.placements)
    assert "EXTENSION-JUNCTION-CLEAT-001" not in parts
    assert main_outer_face == pytest.approx(extension_sign * spec.length / 2)
    assert extension_inner_end == pytest.approx(main_outer_face)
    assert shelf_end_outer_face == pytest.approx(extension_sign * spec.length / 2)
    assert extension_shelf_inner_end == pytest.approx(shelf_end_outer_face)
    assert shelf_end_placement.translation_mm[2] + shelf_end_rail.stock_size_mm[2] / 2 == (
        pytest.approx(front_extension_shelf_rail.translation_mm[2])
    )


def test_extension_shoe_shelf_is_longer_than_its_depth_and_sloped() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())
    parts = {part.number: part for part in design.parts}

    extension_rail = parts["EXTENSION-SHELF-RAIL-001"]
    extension_slats = parts["EXTENSION-SHELF-SLAT-001"]
    extension_stopper = parts["EXTENSION-SHELF-STOPPER-001"]

    assert spec.extension_shelf_length > spec.extension_depth
    assert extension_slats.stock_size_mm == pytest.approx(
        (
            spec.shelf_slat_width,
            spec.extension_shelf_length,
            spec.shelf_slat_thickness,
        )
    )
    assert all(
        placement.rotation_deg == pytest.approx((spec.extension_shelf_angle_deg, 0.0, 0.0))
        for placement in (
            *extension_rail.placements,
            *extension_slats.placements,
            *extension_stopper.placements,
        )
    )
    assert extension_stopper.stock_size_mm[1:] == pytest.approx(
        (spec.extension_shelf_stopper_thickness, spec.extension_shelf_stopper_height)
    )
    assert (
        extension_stopper.placements[0].translation_mm[1]
        < extension_slats.placements[0].translation_mm[1]
    )


def test_umbrella_variant_swaps_only_the_extension_storage_module() -> None:
    spec = EntrywayBenchSpec(extension_mode="umbrella_storage")
    design = build_entryway_bench("umbrella-bench", spec.as_dict())
    parts = {part.number: part for part in design.parts}

    assert design.total_occurrences() == 33
    assert {part.number: part.quantity for part in design.parts} == {
        "SEAT-BASE-001": 1,
        "LEG-001": 6,
        "TOP-RAIL-LONG-001": 2,
        "TOP-RAIL-END-001": 2,
        "SHELF-RAIL-001": 2,
        "SHELF-SLAT-001": spec.shelf_slat_count,
        "EXTENSION-TOP-RAIL-LONG-001": 2,
        "EXTENSION-TOP-RAIL-END-001": 1,
        "EXTENSION-STORAGE-FLOOR-001": 1,
        "EXTENSION-STORAGE-BACK-001": 1,
        "EXTENSION-STORAGE-DIVIDER-001": 1,
        "UMBRELLA-HOLDER-FRONT-001": 1,
        "CUSHION-001": 1,
        "CUSHION-PIPING-001": 2,
    }
    assert {
        "SHELF-RAIL-END-001",
        "EXTENSION-SHELF-RAIL-001",
        "EXTENSION-SHELF-SLAT-001",
        "EXTENSION-SHELF-STOPPER-001",
    }.isdisjoint(parts)

    floor = parts["EXTENSION-STORAGE-FLOOR-001"]
    back = parts["EXTENSION-STORAGE-BACK-001"]
    divider = parts["EXTENSION-STORAGE-DIVIDER-001"]
    front = parts["UMBRELLA-HOLDER-FRONT-001"]
    deck = parts["SEAT-BASE-001"]
    deck_bounds = deck.shape.val().BoundingBox()
    assert deck_bounds.xlen == pytest.approx(spec.length)
    assert deck.stock_size_mm[0] == pytest.approx(spec.length)
    assert floor.stock_size_mm == pytest.approx(
        (
            spec.extension_length - spec.leg_size,
            spec.extension_depth - 2 * spec.leg_size,
            spec.storage_panel_thickness,
        )
    )
    assert back.stock_size_mm[2] == pytest.approx(
        spec.frame_height
        - spec.seat_base_thickness
        - spec.top_rail_height
        - spec.storage_floor_top_height
    )
    assert divider.stock_size_mm[1] == pytest.approx(
        floor.stock_size_mm[1] - spec.storage_panel_thickness
    )
    assert front.stock_size_mm == pytest.approx(
        (
            spec.umbrella_compartment_width,
            spec.storage_panel_thickness,
            spec.umbrella_front_height,
        )
    )


def test_umbrella_variant_joinery_matches_its_panel_module() -> None:
    spec = EntrywayBenchSpec(extension_mode="umbrella_storage")
    design = build_entryway_bench("umbrella-bench", spec.as_dict())

    assert design.joinery.hardware_quantities() == {
        "PH-38-T20": 32,
        "PH-32-T20": 8,
        "CSK-4X35-T20": 30,
        "CB-M6X50": 2,
        "DOWEL-8X40": 4,
    }
    operation_parts = {operation.part_number for operation in design.joinery.drill_operations}
    assert "EXTENSION-STORAGE-BACK-001" in operation_parts
    assert "EXTENSION-STORAGE-DIVIDER-001" in operation_parts
    assert "UMBRELLA-HOLDER-FRONT-001" in operation_parts
    assert "EXTENSION-SHELF-SLAT-001" not in operation_parts


def test_umbrella_variant_ignores_unused_shoe_shelf_geometry() -> None:
    spec = EntrywayBenchSpec(
        extension_mode="umbrella_storage",
        extension_slat_count=1,
        extension_shelf_length=1.0,
        extension_shelf_angle_deg=90.0,
    )

    design = build_entryway_bench("umbrella-with-unused-shoe-values", spec.as_dict())

    assert design.total_occurrences() == 33


def test_no_extension_variant_is_only_the_four_leg_main_bench() -> None:
    spec = EntrywayBenchSpec(extension_mode="none")
    design = build_entryway_bench("bench-without-extension", spec.as_dict())
    parts = {part.number: part for part in design.parts}

    assert design.overall_size_mm() == pytest.approx(
        (spec.length, spec.depth, spec.frame_height + spec.cushion_thickness)
    )
    assert design.total_occurrences() == 24
    assert {part.number: part.quantity for part in design.parts} == {
        "SEAT-BASE-001": 1,
        "LEG-001": 4,
        "TOP-RAIL-LONG-001": 2,
        "TOP-RAIL-END-001": 2,
        "SHELF-RAIL-001": 2,
        "SHELF-SLAT-001": spec.shelf_slat_count,
        "CUSHION-001": 1,
        "CUSHION-PIPING-001": 2,
    }
    assert not any(part_number.startswith("EXTENSION-") for part_number in parts)
    assert "SHELF-RAIL-END-001" not in parts
    assert parts["SEAT-BASE-001"].shape.val().BoundingBox().xlen == pytest.approx(spec.length)


def test_no_extension_joinery_contains_only_main_bench_hardware() -> None:
    spec = EntrywayBenchSpec(extension_mode="none")
    design = build_entryway_bench("bench-without-extension", spec.as_dict())

    assert design.joinery.hardware_quantities() == {
        "PH-38-T20": 20,
        "PH-32-T20": 8,
        "CSK-4X35-T20": 20,
    }
    assert len(design.joinery.joints) == 5
    assert all(
        "EXTENSION" not in operation.operation_id for operation in design.joinery.drill_operations
    )


def test_extension_can_move_to_right_side() -> None:
    values = EntrywayBenchSpec().as_dict()
    values["extension_side"] = "right"
    design = build_entryway_bench("right-extension", values)

    deck = next(part for part in design.parts if part.number == "SEAT-BASE-001")
    bounds = deck.shape.val().BoundingBox()
    assert bounds.xmin == pytest.approx(-values["length"] / 2)
    assert bounds.xmax == pytest.approx(values["length"] / 2 + values["extension_length"])


def test_example_design_resolves_from_python_defaults() -> None:
    design = load_design(Path("designs/entryway-bench.json"))

    assert design.parameters == EntrywayBenchSpec().as_dict()
    assert (design.family_id, design.variant, design.variant_label) == (
        "entryway-bench",
        "shoe-shelf",
        "Shoe shelf",
    )


def test_umbrella_example_is_a_second_variant_of_the_bench_family() -> None:
    design = load_design(Path("designs/entryway-bench-umbrella.json"))

    assert design.parameters["extension_mode"] == "umbrella_storage"
    assert (design.family_id, design.variant, design.variant_label) == (
        "entryway-bench",
        "umbrella-storage",
        "Umbrella storage",
    )


def test_no_extension_example_is_a_third_variant_of_the_bench_family() -> None:
    design = load_design(Path("designs/entryway-bench-no-extension.json"))

    assert design.parameters["extension_mode"] == "none"
    assert (design.family_id, design.variant, design.variant_label) == (
        "entryway-bench",
        "no-extension",
        "No extension",
    )


@pytest.mark.parametrize(
    ("overrides", "message"),
    (
        ({"unsupported": 42}, "unknown entryway_bench parameter"),
        ({"shelf_slat_count": 40}, "shelf slats overlap"),
        ({"lower_shelf_height": 450.0}, "lower shelf collides"),
        ({"shelf_slat_count": 7.5}, "shelf_slat_count must be an integer"),
        ({"extension_depth": 250.0}, "extension_depth must be smaller"),
        ({"extension_side": "middle"}, "extension_side must be"),
        ({"extension_mode": "laundry"}, "extension_mode must be"),
        (
            {"extension_mode": "umbrella_storage", "umbrella_compartment_width": 600.0},
            "leaves no general storage area",
        ),
        ({"extension_shelf_length": 100.0}, "too short to reach both support rails"),
        ({"extension_shelf_angle_deg": 60.0}, "must be smaller than 60 degrees"),
        ({"extension_shelf_stopper_thickness": 260.0}, "stopper_thickness must be smaller"),
    ),
)
def test_rejects_invalid_spec(overrides: dict[str, object], message: str) -> None:
    values = EntrywayBenchSpec().as_dict() | overrides
    with pytest.raises(ValueError, match=message):
        EntrywayBenchSpec.from_mapping(values)
