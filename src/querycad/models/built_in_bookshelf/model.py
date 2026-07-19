"""Orchestration for the three-bay built-in bookshelf family."""

from __future__ import annotations

from typing import Any

from querycad.furniture import Design
from querycad.models.built_in_bookshelf.joinery import build_joinery_schedule
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.parts import build_part_catalog
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec


def build_built_in_bookshelf(name: str, parameters: dict[str, Any]) -> Design:
    """Resolve the measured envelope, modular parts, and site-aware joinery."""

    spec = BuiltInBookshelfSpec.from_mapping(parameters)
    layout = BuiltInLayout.from_spec(spec)
    catalog = build_part_catalog(spec, layout)
    design = Design(
        name=name,
        model=spec.model_name,
        parameters=spec.as_dict(),
        parts=catalog.freeze(),
        joinery=build_joinery_schedule(spec, layout, catalog),
    )
    design.validate()
    return design
