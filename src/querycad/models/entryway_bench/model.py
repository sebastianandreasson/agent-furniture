"""Concise orchestration for the canonical modular furniture example."""

from __future__ import annotations

from typing import Any

from querycad.furniture import Design
from querycad.models.entryway_bench.joinery import build_joinery_schedule
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.parts import build_part_catalog
from querycad.models.entryway_bench.spec import EntrywayBenchSpec


def build_entryway_bench(name: str, parameters: dict[str, Any]) -> Design:
    """Resolve specification, layout, subassemblies, and joinery into one design."""

    spec = EntrywayBenchSpec.from_mapping(parameters)
    layout = BenchLayout.from_spec(spec)
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
