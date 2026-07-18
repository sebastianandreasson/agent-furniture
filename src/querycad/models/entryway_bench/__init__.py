"""Canonical detailed furniture family: a modular cushioned entryway bench."""

from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.model import build_entryway_bench
from querycad.models.entryway_bench.spec import EntrywayBenchSpec

__all__ = ["BenchLayout", "EntrywayBenchSpec", "build_entryway_bench"]
