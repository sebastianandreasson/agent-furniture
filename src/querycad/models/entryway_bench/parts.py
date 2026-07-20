"""Part-catalog orchestration for the canonical modular bench example."""

from __future__ import annotations

from querycad.furniture import PartCatalog
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.spec import EntrywayBenchSpec
from querycad.models.entryway_bench.subassemblies import (
    add_extension,
    add_main_bench,
    add_upholstery,
)


def build_part_catalog(spec: EntrywayBenchSpec, layout: BenchLayout) -> PartCatalog:
    """Build the main frame, selected extension module, and upholstery."""

    catalog = PartCatalog()
    add_main_bench(catalog, spec, layout)
    add_extension(catalog, spec, layout)
    add_upholstery(catalog, spec, layout)
    return catalog
