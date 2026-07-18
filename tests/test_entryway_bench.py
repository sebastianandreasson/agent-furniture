from __future__ import annotations

from pathlib import Path

import pytest

from querycad.config import load_design
from querycad.models.entryway_bench import EntrywayBenchSpec, build_entryway_bench


def test_default_bench_geometry_and_bom_quantities() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())

    design.validate_solids()

    assert design.overall_size_mm() == pytest.approx(
        (
            spec.length + spec.extension_length,
            spec.depth,
            spec.frame_height + spec.cushion_thickness,
        )
    )
    assert design.total_occurrences() == (24 + spec.shelf_slat_count + spec.extension_slat_count)
    assert {part.number: part.quantity for part in design.parts} == {
        "SEAT-BASE-001": 1,
        "LEG-001": 7,
        "TOP-RAIL-LONG-001": 2,
        "TOP-RAIL-END-001": 2,
        "SHELF-RAIL-001": 2,
        "SHELF-SLAT-001": spec.shelf_slat_count,
        "EXTENSION-TOP-001": 1,
        "EXTENSION-TOP-RAIL-LONG-001": 2,
        "EXTENSION-TOP-RAIL-END-001": 1,
        "EXTENSION-SHELF-RAIL-001": 2,
        "EXTENSION-SHELF-SLAT-001": spec.extension_slat_count,
        "EXTENSION-SHELF-STOPPER-001": 1,
        "CUSHION-001": 1,
        "CUSHION-PIPING-001": 2,
    }


def test_joinery_schedule_matches_drill_marks_and_hardware_quantities() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())

    design.validate_solids()

    assert design.joinery_status == "prototype_not_structurally_certified"
    assert design.hardware_quantities() == {
        "PH-38-FINE": 36,
        "PH-32-FINE": 12,
        "CSK-4X35": 36,
    }
    assert len(design.joints) == 11
    assert len(design.drill_operations) == 14
    assert (
        sum(
            len(operation.points)
            * next(part.quantity for part in design.parts if part.number == operation.part_number)
            for operation in design.drill_operations
            if operation.counts_fastener
        )
        == 84
    )


def test_shelf_slats_include_documented_clearance_holes() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())
    parts = {part.number: part for part in design.parts}

    solid_slat_volume = (
        spec.shelf_slat_width * (spec.depth - spec.leg_size) * spec.shelf_slat_thickness
    )
    assert parts["SHELF-SLAT-001"].volume_mm3 < solid_slat_volume
    cut_operations = {
        operation.part_number
        for operation in design.drill_operations
        if operation.geometry_mode == "cut"
    }
    assert cut_operations == {"SHELF-SLAT-001", "EXTENSION-SHELF-SLAT-001"}


def test_extension_is_indented_and_has_no_cushion() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())

    parts = {part.number: part for part in design.parts}
    extension_top = parts["EXTENSION-TOP-001"].placements[0]
    cushion = parts["CUSHION-001"]

    extension_sign = 1 if spec.extension_side == "right" else -1
    assert extension_top.translation_mm[0] * extension_sign > spec.length / 2
    assert extension_top.translation_mm[1] == pytest.approx((spec.depth - spec.extension_depth) / 2)
    assert cushion.quantity == 1
    assert cushion.placements[0].translation_mm[0] == 0.0


def test_extension_shoe_shelf_is_longer_than_its_depth_and_sloped() -> None:
    spec = EntrywayBenchSpec()
    design = build_entryway_bench("test-bench", spec.as_dict())
    parts = {part.number: part for part in design.parts}

    extension_rail = parts["EXTENSION-SHELF-RAIL-001"]
    extension_slat = parts["EXTENSION-SHELF-SLAT-001"]
    extension_stopper = parts["EXTENSION-SHELF-STOPPER-001"]

    assert spec.extension_shelf_length > spec.extension_depth
    assert extension_slat.stock_size_mm == pytest.approx(
        (spec.shelf_slat_width, spec.extension_shelf_length, spec.shelf_slat_thickness)
    )
    assert all(
        placement.rotation_deg == pytest.approx((spec.extension_shelf_angle_deg, 0.0, 0.0))
        for placement in (
            *extension_rail.placements,
            *extension_slat.placements,
            *extension_stopper.placements,
        )
    )
    assert extension_stopper.stock_size_mm[1:] == pytest.approx(
        (spec.extension_shelf_stopper_thickness, spec.extension_shelf_stopper_height)
    )
    assert (
        extension_stopper.placements[0].translation_mm[1]
        < extension_slat.placements[0].translation_mm[1]
    )


def test_extension_can_move_to_left_side() -> None:
    values = EntrywayBenchSpec().as_dict()
    values["extension_side"] = "left"
    design = build_entryway_bench("left-extension", values)

    extension_top = next(part for part in design.parts if part.number == "EXTENSION-TOP-001")
    assert extension_top.placements[0].translation_mm[0] < -values["length"] / 2


def test_example_design_resolves_from_python_defaults() -> None:
    design = load_design(Path("designs/entryway-bench.json"))

    assert design.parameters == EntrywayBenchSpec().as_dict()


def test_rejects_unknown_parameter() -> None:
    with pytest.raises(ValueError, match="unknown entryway_bench parameter"):
        EntrywayBenchSpec.from_mapping({"unsupported": 42})


def test_rejects_overlapping_slats() -> None:
    values = EntrywayBenchSpec().as_dict()
    values["shelf_slat_count"] = 40

    with pytest.raises(ValueError, match="shelf slats overlap"):
        EntrywayBenchSpec.from_mapping(values)


def test_rejects_shelf_colliding_with_top_rail() -> None:
    values = EntrywayBenchSpec().as_dict()
    values["lower_shelf_height"] = 360.0

    with pytest.raises(ValueError, match="lower shelf collides"):
        EntrywayBenchSpec.from_mapping(values)


def test_rejects_non_integer_slat_count() -> None:
    values = EntrywayBenchSpec().as_dict()
    values["shelf_slat_count"] = 17.5

    with pytest.raises(ValueError, match="shelf_slat_count must be an integer"):
        EntrywayBenchSpec.from_mapping(values)


def test_rejects_extension_without_an_indent() -> None:
    values = EntrywayBenchSpec().as_dict()
    values["extension_depth"] = values["depth"]

    with pytest.raises(ValueError, match="extension_depth must be smaller"):
        EntrywayBenchSpec.from_mapping(values)


def test_rejects_unknown_extension_side() -> None:
    values = EntrywayBenchSpec().as_dict()
    values["extension_side"] = "middle"

    with pytest.raises(ValueError, match="extension_side must be"):
        EntrywayBenchSpec.from_mapping(values)


def test_rejects_extension_shelf_too_short_for_its_supports() -> None:
    values = EntrywayBenchSpec().as_dict()
    values["extension_shelf_length"] = 100.0

    with pytest.raises(ValueError, match="too short to reach both support rails"):
        EntrywayBenchSpec.from_mapping(values)


def test_rejects_excessive_extension_shelf_angle() -> None:
    values = EntrywayBenchSpec().as_dict()
    values["extension_shelf_angle_deg"] = 60.0

    with pytest.raises(ValueError, match="must be smaller than 60 degrees"):
        EntrywayBenchSpec.from_mapping(values)


def test_rejects_stopper_thicker_than_extension_shelf() -> None:
    values = EntrywayBenchSpec().as_dict()
    values["extension_shelf_stopper_thickness"] = values["extension_shelf_length"]

    with pytest.raises(ValueError, match="stopper_thickness must be smaller"):
        EntrywayBenchSpec.from_mapping(values)
