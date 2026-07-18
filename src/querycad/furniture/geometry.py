"""Reusable local-coordinate solids for furniture part definitions."""

from __future__ import annotations

import cadquery as cq


def stock_box(
    x: float,
    y: float,
    z: float,
    *,
    corner_radius: float = 0.0,
) -> cq.Workplane:
    """Make a box centred in X/Y with its bottom at local Z=0."""

    result = cq.Workplane("XY").box(x, y, z, centered=(True, True, False))
    if corner_radius:
        result = result.edges("|Z").fillet(corner_radius)
    return result


def centered_box(
    x: float,
    y: float,
    z: float,
    *,
    corner_radius: float = 0.0,
) -> cq.Workplane:
    """Make a box centred on all axes for placement around a rotation origin."""

    return stock_box(x, y, z, corner_radius=corner_radius).translate((0.0, 0.0, -z / 2))


def soft_box(x: float, y: float, z: float, radius: float) -> cq.Workplane:
    """Make an all-edge rounded box suitable for cushions and soft goods."""

    return cq.Workplane("XY").box(x, y, z, centered=(True, True, False)).edges().fillet(radius)


def rounded_ring(
    x: float,
    y: float,
    z: float,
    width: float,
    radius: float,
) -> cq.Workplane:
    """Make a rounded rectangular ring with its bottom at local Z=0."""

    outer = stock_box(x, y, z, corner_radius=radius)
    inner = stock_box(
        x - 2 * width,
        y - 2 * width,
        z + 2.0,
        corner_radius=radius - width,
    ).translate((0.0, 0.0, -1.0))
    return outer.cut(inner)


def top_countersunk_holes(
    shape: cq.Workplane,
    points_xy: tuple[tuple[float, float], ...],
    *,
    diameter: float,
    countersink_diameter: float,
    depth: float,
) -> cq.Workplane:
    """Cut 90-degree countersunk clearance holes from a part's local top face."""

    return (
        shape.faces(">Z")
        .workplane()
        .pushPoints(points_xy)
        .cskHole(diameter, countersink_diameter, 90.0, depth=depth)
    )
