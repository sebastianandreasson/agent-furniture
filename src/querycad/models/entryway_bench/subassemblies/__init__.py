"""Modular entryway-bench subassemblies."""

from querycad.models.entryway_bench.subassemblies.extensions import add_extension
from querycad.models.entryway_bench.subassemblies.main_bench import add_main_bench
from querycad.models.entryway_bench.subassemblies.upholstery import add_upholstery

__all__ = ["add_extension", "add_main_bench", "add_upholstery"]
