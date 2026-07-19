from __future__ import annotations

import pytest

from querycad.furniture import Design, Part, Placement, find_interferences, stock_box


def _design_with_second_box_at(x: float) -> Design:
    return Design(
        name="interference-sample",
        model="test",
        parameters={},
        parts=(
            Part(
                number="BOX-A-001",
                description="First box",
                material="test",
                shape=stock_box(100.0, 100.0, 100.0),
                stock_size_mm=(100.0, 100.0, 100.0),
                placements=(Placement("box_a"),),
            ),
            Part(
                number="BOX-B-001",
                description="Second box",
                material="test",
                shape=stock_box(100.0, 100.0, 100.0),
                stock_size_mm=(100.0, 100.0, 100.0),
                placements=(Placement("box_b", (x, 0.0, 0.0)),),
            ),
        ),
    )


def test_interference_audit_reports_exact_shared_volume() -> None:
    interference = find_interferences(_design_with_second_box_at(75.0))

    assert len(interference) == 1
    assert interference[0].first_placement_name == "box_a"
    assert interference[0].second_placement_name == "box_b"
    assert interference[0].volume_mm3 == pytest.approx(250_000.0)


def test_interference_audit_allows_face_to_face_contacts() -> None:
    assert find_interferences(_design_with_second_box_at(100.0)) == ()


def test_interference_audit_rejects_non_positive_threshold() -> None:
    with pytest.raises(ValueError, match="min_volume_mm3 must be greater than zero"):
        find_interferences(_design_with_second_box_at(75.0), min_volume_mm3=0.0)
