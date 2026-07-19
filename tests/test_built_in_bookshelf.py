from __future__ import annotations

import json
from pathlib import Path

import pytest

from querycad.config import load_design
from querycad.export import export_design
from querycad.models.built_in_bookshelf import (
    BuiltInBookshelfSpec,
    BuiltInLayout,
    build_built_in_bookshelf,
)
from querycad.models.built_in_bookshelf.joinery import SITE_TOP_BEAM, SITE_VERTICAL_POSTS


def test_default_spec_preserves_measured_site_envelope() -> None:
    spec = BuiltInBookshelfSpec()

    assert spec.opening_widths == (1100.0, 1450.0, 670.0)
    assert spec.internal_post_widths == (360.0, 140.0)
    assert spec.right_boundary_post_width == 360.0
    assert spec.opening_depth == 145.0
    assert spec.height_under_beam == 2400.0
    assert spec.cabinet_top_height == 700.0
    assert (spec.lower_depth, spec.shelf_depth) == (330.0, 160.0)
    assert spec.core_upright_thickness == 30.0
    assert spec.clear_opening_widths == (1040.0, 1390.0, 610.0)
    assert spec.shelf_count == 4
    assert spec.shelf_pitch == 300.0
    assert spec.knob_edge_inset == spec.door_frame_width / 2
    assert spec.knob_height_ratio == 0.5
    assert spec.right_slope_start_x == 150.0
    assert spec.right_slope_end_height == 2200.0
    assert "do not anchor into the brick wall" in spec.site_anchor_strategy


def test_default_geometry_and_bom_quantities() -> None:
    spec = BuiltInBookshelfSpec()
    design = build_built_in_bookshelf("test-bookshelf", spec.as_dict())

    design.validate()

    assert design.overall_size_mm() == pytest.approx(
        (
            sum(spec.opening_widths) + sum(spec.internal_post_widths),
            spec.lower_depth + spec.knob_projection,
            spec.height_under_beam,
        )
    )
    assert len(design.parts) == 44
    assert design.total_occurrences() == 96
    quantities = {part.number: part.quantity for part in design.parts}
    assert quantities["BASE-CARCASS-VERTICAL-001"] == 8
    assert quantities["FACE-FRAME-STILE-001"] == 8
    assert quantities["DOOR-KNOB-001"] == 5
    assert quantities["UPPER-SHELF-LEFT-001"] == spec.shelf_count
    assert quantities["UPPER-SHELF-MIDDLE-001"] == spec.shelf_count
    assert quantities["UPPER-SHELF-RIGHT-001"] == spec.shelf_count
    assert quantities["BOOKCASE-CORE-UPRIGHT-LH-001"] == 3
    assert quantities["BOOKCASE-CORE-UPRIGHT-RH-001"] == 2
    assert quantities["BOOKCASE-CORE-UPRIGHT-RIGHT-SCRIBED-001"] == 1
    assert quantities["POST-DISPLAY-LEDGE-LEFT-001"] == spec.shelf_count
    assert quantities["POST-DISPLAY-LEDGE-MIDDLE-001"] == spec.shelf_count
    assert quantities["POST-DISPLAY-LIP-LEFT-001"] == spec.shelf_count
    assert quantities["POST-DISPLAY-LIP-MIDDLE-001"] == spec.shelf_count
    assert quantities["STRUCTURAL-POST-CLADDING-LEFT-001"] == 1
    assert quantities["STRUCTURAL-POST-CLADDING-MIDDLE-001"] == 1
    assert quantities["POST-CABINET-FIXED-PANEL-LEFT-001"] == 1
    assert quantities["POST-CABINET-FIXED-PANEL-MIDDLE-001"] == 1
    assert all("POST-BASE-FASCIA" not in part.number for part in design.parts)
    assert "UPPER-SHELF-SIDE-CLEAT-001" not in quantities
    assert all("BACK" not in part.number for part in design.parts)


def test_finished_front_projects_into_room_from_wall_plane() -> None:
    spec = BuiltInBookshelfSpec()
    design = build_built_in_bookshelf("test-bookshelf", spec.as_dict())
    bounds = design.compound().BoundingBox()

    # CAD Y=0 is the wall plane. Negative Y is the room-facing direction, which
    # OpenCascade maps to the browser camera's positive-Z side.
    assert bounds.ymax == pytest.approx(0.0)
    assert bounds.ymin == pytest.approx(-(spec.lower_depth + spec.knob_projection))

    knob = next(part for part in design.parts if part.number == "DOOR-KNOB-001")
    knob_bounds = knob.shape.val().BoundingBox()
    assert knob_bounds.ymin == pytest.approx(-spec.knob_projection)
    assert knob_bounds.ymax == pytest.approx(0.0)


def test_layout_uses_measured_internal_posts_and_stops_at_right_boundary() -> None:
    spec = BuiltInBookshelfSpec()
    layout = BuiltInLayout.from_spec(spec)

    assert layout.furniture_width == pytest.approx(3720.0)
    assert [(post.name, post.width) for post in layout.posts] == [
        ("left", 360.0),
        ("middle", 140.0),
    ]
    assert layout.posts[0].left_x == pytest.approx(layout.bay("left").right_x)
    assert layout.posts[0].right_x == pytest.approx(layout.bay("middle").left_x)
    assert layout.posts[1].left_x == pytest.approx(layout.bay("middle").right_x)
    assert layout.posts[1].right_x == pytest.approx(layout.bay("right").left_x)
    assert layout.bay("right").right_x == pytest.approx(layout.furniture_width / 2)
    assert spec.measured_site_sequence_width == pytest.approx(4080.0)
    assert [bay.fitted_width for bay in layout.bays] == pytest.approx((1034.0, 1384.0, 604.0))


def test_full_height_core_uprights_replace_short_shelf_cleats() -> None:
    spec = BuiltInBookshelfSpec()
    design = build_built_in_bookshelf("test-bookshelf", spec.as_dict())
    parts = {part.number: part for part in design.parts}

    assert parts["BOOKCASE-CORE-UPRIGHT-LH-001"].stock_size_mm == pytest.approx(
        (30.0, 160.0, 2400.0)
    )
    assert parts["BOOKCASE-CORE-UPRIGHT-RH-001"].stock_size_mm == pytest.approx(
        (30.0, 160.0, 2400.0)
    )
    assert parts["BOOKCASE-CORE-UPRIGHT-RIGHT-SCRIBED-001"].stock_size_mm == pytest.approx(
        (30.0, 160.0, 2217.307692)
    )
    assert parts["UPPER-SHELF-LEFT-001"].stock_size_mm[0] == pytest.approx(1034.0)
    assert parts["UPPER-SHELF-MIDDLE-001"].stock_size_mm[0] == pytest.approx(1384.0)
    assert parts["UPPER-SHELF-RIGHT-001"].stock_size_mm[0] == pytest.approx(604.0)
    assert parts["COUNTER-LEFT-001"].stock_size_mm[1] == pytest.approx(330.0)
    assert parts["UPPER-SHELF-LEFT-001"].stock_size_mm[1] == pytest.approx(160.0)


def test_lower_cabinet_run_bridges_both_internal_posts() -> None:
    spec = BuiltInBookshelfSpec()
    layout = BuiltInLayout.from_spec(spec)
    design = build_built_in_bookshelf("test-bookshelf", spec.as_dict())
    parts = {part.number: part for part in design.parts}

    assert [layout.cabinet_bridge_width(post.name) for post in layout.posts] == pytest.approx(
        (426.0, 206.0)
    )
    assert parts["POST-CABINET-COUNTER-BRIDGE-LEFT-001"].stock_size_mm == pytest.approx(
        (426.0, 330.0, 28.0)
    )
    assert parts["POST-CABINET-COUNTER-BRIDGE-MIDDLE-001"].stock_size_mm == pytest.approx(
        (206.0, 330.0, 28.0)
    )
    assert parts["POST-CABINET-FIXED-PANEL-LEFT-001"].stock_size_mm == pytest.approx(
        (426.0, 22.0, layout.face_frame_height)
    )
    assert parts["POST-CABINET-FIXED-PANEL-MIDDLE-001"].stock_size_mm == pytest.approx(
        (206.0, 22.0, layout.face_frame_height)
    )
    assert all(
        parts[number].shape.val().isValid()
        for number in (
            "POST-CABINET-FIXED-PANEL-LEFT-001",
            "POST-CABINET-FIXED-PANEL-MIDDLE-001",
        )
    )
    fixed_panel_operations = [
        operation
        for operation in design.joinery.drill_operations
        if operation.part_number.startswith("POST-CABINET-FIXED-PANEL-")
    ]
    assert len(fixed_panel_operations) == 2
    assert all(len(operation.points) == 4 for operation in fixed_panel_operations)
    assert all(operation.fastener_code == "CAB-5X50-T20" for operation in fixed_panel_operations)


def test_masonry_dividers_stagger_and_support_both_wide_bays() -> None:
    spec = BuiltInBookshelfSpec()
    layout = BuiltInLayout.from_spec(spec)
    left = [item for item in layout.divider_segments if "_left_" in item.name]
    middle = [item for item in layout.divider_segments if "_middle_" in item.name]

    assert len(left) == spec.shelf_count + 1
    assert len(middle) == spec.shelf_count + 1
    assert left[0].center_x != pytest.approx(left[1].center_x)
    assert middle[0].center_x != pytest.approx(middle[1].center_x)
    assert left[0].center_x < layout.bay("left").center_x
    assert middle[0].center_x > layout.bay("middle").center_x
    assert all(segment.height >= 276.0 for segment in layout.divider_segments)


def test_knobs_are_centered_and_single_right_door_has_knob_on_left() -> None:
    spec = BuiltInBookshelfSpec()
    layout = BuiltInLayout.from_spec(spec)
    design = build_built_in_bookshelf("test-bookshelf", spec.as_dict())
    door = layout.doors_for_bay("right")[0]

    assert door.hinge_side == "right"
    assert door.knob_x == pytest.approx(door.center_x - door.width / 2 + spec.knob_edge_inset)

    operations = {
        operation.operation_id: operation for operation in design.joinery.drill_operations
    }
    hinge = operations["DR-DOOR-RIGHT-HINGES"]
    knob = operations["DR-DOOR-RIGHT-KNOB"]
    assert {point.position_mm[0] for point in hinge.points} == {door.width - 24.0}
    assert knob.points[0].position_mm[0] == pytest.approx(spec.knob_edge_inset)

    knob_operations = [
        operation
        for operation in design.joinery.drill_operations
        if operation.operation_id.endswith("-KNOB")
    ]
    assert len(knob_operations) == 5
    assert {
        point.position_mm[2] for operation in knob_operations for point in operation.points
    } == {layout.door_height / 2}

    knob_part = next(part for part in design.parts if part.number == "DOOR-KNOB-001")
    expected_placement_z = layout.door_bottom_z + layout.door_height / 2 - spec.knob_diameter / 2
    assert {placement.translation_mm[2] for placement in knob_part.placements} == {
        expected_placement_z
    }


def test_right_crown_follows_slope_without_clipping_the_shelves() -> None:
    spec = BuiltInBookshelfSpec()
    layout = BuiltInLayout.from_spec(spec)
    design = build_built_in_bookshelf("test-bookshelf", spec.as_dict())
    crown = next(part for part in design.parts if part.number == "CROWN-RIGHT-SLOPED-001")
    bounds = crown.shape.val().BoundingBox()

    assert layout.right_slope_crossing_x == pytest.approx(323.333333)
    assert crown.stock_size_mm == pytest.approx((604.0, 28.0, 216.961538))
    assert bounds.zmin == pytest.approx(0.0)
    assert bounds.zmax == pytest.approx(216.961538)
    assert spec.last_shelf_bottom + spec.shelf_thickness < spec.right_slope_end_height


def test_site_anchors_are_hardware_targets_not_cut_list_parts() -> None:
    spec = BuiltInBookshelfSpec()
    design = build_built_in_bookshelf("test-bookshelf", spec.as_dict())

    assert {target.code for target in design.joinery.external_targets} == {
        SITE_VERTICAL_POSTS,
        SITE_TOP_BEAM,
    }
    assert all(part.number not in {SITE_VERTICAL_POSTS, SITE_TOP_BEAM} for part in design.parts)
    assert design.joinery.hardware_quantities() == {
        "CAB-5X50-T20": 76,
        "SHELF-4.5X45-T20": 40,
        "CORE-SHELF-5X60-T25": 48,
        "STRUCT-6X90-T30": 73,
        "HINGE-3.5X16-PZ2": 20,
        "KNOB-M4X25": 5,
    }
    site_joints = [
        joint
        for joint in design.joinery.joints
        if joint.target_part_number in {SITE_VERTICAL_POSTS, SITE_TOP_BEAM}
    ]
    assert len(site_joints) == 8
    assert sum(joint.quantity for joint in site_joints) == 73


def test_manifest_exports_external_site_targets(tmp_path: Path) -> None:
    design = build_built_in_bookshelf("test-bookshelf", BuiltInBookshelfSpec().as_dict())

    export_design(design, tmp_path, ("bom",))
    manifest = json.loads((tmp_path / "manifest.json").read_text())

    assert {item["code"] for item in manifest["joinery"]["external_targets"]} == {
        SITE_VERTICAL_POSTS,
        SITE_TOP_BEAM,
    }
    bom_text = (tmp_path / "bom.csv").read_text()
    assert SITE_VERTICAL_POSTS not in bom_text
    assert SITE_TOP_BEAM not in bom_text


def test_example_design_resolves_from_python_defaults() -> None:
    design = load_design(Path("designs/beam-wall-bookshelf.json"))

    assert design.parameters == BuiltInBookshelfSpec().as_dict()


def test_rejects_shelves_that_do_not_project_past_the_recess() -> None:
    values = BuiltInBookshelfSpec().as_dict()
    values["shelf_depth"] = values["opening_depth"]

    with pytest.raises(ValueError, match="shelf_depth must project beyond"):
        BuiltInBookshelfSpec.from_mapping(values)


def test_rejects_slope_that_clips_the_highest_shelf() -> None:
    values = BuiltInBookshelfSpec().as_dict()
    values["right_slope_end_below_beam"] = 700.0

    with pytest.raises(ValueError, match="right slope leaves too little clearance"):
        BuiltInBookshelfSpec.from_mapping(values)


def test_rejects_non_integer_shelf_count() -> None:
    values = BuiltInBookshelfSpec().as_dict()
    values["shelf_count"] = 3.5

    with pytest.raises(ValueError, match="shelf_count must be an integer"):
        BuiltInBookshelfSpec.from_mapping(values)


def test_rejects_opening_too_narrow_for_framed_doors() -> None:
    values = BuiltInBookshelfSpec().as_dict()
    values["right_opening_width"] = 150.0

    with pytest.raises(ValueError, match="right opening is too narrow"):
        BuiltInBookshelfSpec.from_mapping(values)


def test_rejects_core_uprights_that_consume_the_door_opening() -> None:
    values = BuiltInBookshelfSpec().as_dict()
    values["core_upright_thickness"] = 250.0

    with pytest.raises(ValueError, match="right opening is too narrow"):
        BuiltInBookshelfSpec.from_mapping(values)
