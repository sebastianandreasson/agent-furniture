from __future__ import annotations

import pytest

from querycad.models.apron_table import ApronTableSpec, build_apron_table


def test_default_table_geometry_and_bom_quantities() -> None:
    design = build_apron_table("test-table", ApronTableSpec().as_dict())

    design.validate_solids()

    assert design.overall_size_mm() == pytest.approx((1600.0, 800.0, 750.0))
    assert design.total_occurrences() == 9
    assert {part.number: part.quantity for part in design.parts} == {
        "TOP-001": 1,
        "LEG-001": 4,
        "APRON-LONG-001": 2,
        "APRON-END-001": 2,
    }


def test_rejects_unknown_parameter() -> None:
    with pytest.raises(ValueError, match="unknown apron_table parameter"):
        ApronTableSpec.from_mapping({"unsupported": 42})


def test_rejects_impossible_frame_width() -> None:
    values = ApronTableSpec().as_dict()
    values["depth"] = 200.0

    with pytest.raises(ValueError, match="depth is too small"):
        ApronTableSpec.from_mapping(values)


def test_rejects_invalid_material_name() -> None:
    with pytest.raises(ValueError, match="material names must be non-empty strings"):
        ApronTableSpec.from_mapping({"top_material": 42})
