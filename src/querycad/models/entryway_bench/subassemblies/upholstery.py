"""Loose cushion and repeated piping detail."""

from __future__ import annotations

from querycad.furniture import PartCatalog, rounded_ring, soft_box
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.part_numbers import CUSHION, CUSHION_PIPING
from querycad.models.entryway_bench.spec import EntrywayBenchSpec

FABRIC = (0.78, 0.74, 0.66, 1.0)
PIPING = (0.68, 0.64, 0.56, 1.0)


def add_upholstery(
    catalog: PartCatalog,
    spec: EntrywayBenchSpec,
    _layout: BenchLayout,
) -> None:
    """Add the loose cushion and its repeated piping detail."""

    catalog.define(
        number=CUSHION,
        description="Loose upholstered seat cushion",
        material=spec.cushion_material,
        shape=soft_box(
            spec.cushion_length,
            spec.cushion_depth,
            spec.cushion_thickness,
            spec.cushion_corner_radius,
        ),
        stock_size_mm=(spec.cushion_length, spec.cushion_depth, spec.cushion_thickness),
        color=FABRIC,
    ).place("seat_cushion", (0.0, 0.0, spec.frame_height))

    piping_size = (
        spec.cushion_length - 4.0,
        spec.cushion_depth - 4.0,
        spec.cushion_piping_height,
    )
    piping = catalog.define(
        number=CUSHION_PIPING,
        description="Cushion perimeter piping",
        material=spec.cushion_material,
        shape=rounded_ring(
            piping_size[0],
            piping_size[1],
            piping_size[2],
            spec.cushion_piping_width,
            spec.cushion_corner_radius - 2.0,
        ),
        stock_size_mm=piping_size,
        color=PIPING,
    )
    piping.place("cushion_piping_lower", (0.0, 0.0, spec.frame_height + 6.0)).place(
        "cushion_piping_upper",
        (
            0.0,
            0.0,
            spec.frame_height + spec.cushion_thickness - spec.cushion_piping_height - 6.0,
        ),
    )
