"""Exact volumetric interference checks for placed furniture parts."""

from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq

from querycad.furniture.design import Design


@dataclass(frozen=True)
class Interference:
    """One pair of part occurrences sharing unintended solid volume."""

    first_part_number: str
    first_placement_name: str
    second_part_number: str
    second_placement_name: str
    volume_mm3: float


@dataclass(frozen=True)
class _PlacedSolid:
    part_number: str
    placement_name: str
    shape: cq.Shape


def _placed_solids(design: Design) -> tuple[_PlacedSolid, ...]:
    return tuple(
        _PlacedSolid(
            part_number=part.number,
            placement_name=placement.name,
            shape=part.shape.val().moved(placement.location()),
        )
        for part in design.parts
        for placement in part.placements
    )


def _bounds_overlap(first: cq.Shape, second: cq.Shape, tolerance_mm: float) -> bool:
    a = first.BoundingBox()
    b = second.BoundingBox()
    return all(
        overlap > tolerance_mm
        for overlap in (
            min(a.xmax, b.xmax) - max(a.xmin, b.xmin),
            min(a.ymax, b.ymax) - max(a.ymin, b.ymin),
            min(a.zmax, b.zmax) - max(a.zmin, b.zmin),
        )
    )


def find_interferences(
    design: Design,
    *,
    min_volume_mm3: float = 0.1,
    bounds_tolerance_mm: float = 1e-6,
) -> tuple[Interference, ...]:
    """Return exact positive-volume intersections between placed part occurrences.

    Axis-aligned bounds provide a cheap broad phase. CadQuery boolean intersections
    are only evaluated for candidates whose bounds overlap in all three axes, so
    face-to-face construction contacts are not reported as interferences.
    """

    if min_volume_mm3 <= 0:
        raise ValueError("min_volume_mm3 must be greater than zero")
    if bounds_tolerance_mm < 0:
        raise ValueError("bounds_tolerance_mm cannot be negative")

    solids = _placed_solids(design)
    result: list[Interference] = []
    for index, first in enumerate(solids):
        for second in solids[index + 1 :]:
            if not _bounds_overlap(first.shape, second.shape, bounds_tolerance_mm):
                continue
            volume = float(first.shape.intersect(second.shape).Volume())
            if volume <= min_volume_mm3:
                continue
            result.append(
                Interference(
                    first_part_number=first.part_number,
                    first_placement_name=first.placement_name,
                    second_part_number=second.part_number,
                    second_placement_name=second.placement_name,
                    volume_mm3=volume,
                )
            )
    return tuple(result)
