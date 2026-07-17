"""Domain objects shared by all furniture models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cadquery as cq
from OCP.BRepTools import BRepTools

Vector3 = tuple[float, float, float]
Color4 = tuple[float, float, float, float]


@dataclass(frozen=True)
class Placement:
    """A named occurrence of a local-coordinate part."""

    name: str
    translation_mm: Vector3 = (0.0, 0.0, 0.0)
    rotation_deg: Vector3 = (0.0, 0.0, 0.0)

    def location(self) -> cq.Location:
        return cq.Location(self.translation_mm, self.rotation_deg)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "translation_mm": list(self.translation_mm),
            "rotation_deg": list(self.rotation_deg),
        }


@dataclass(frozen=True)
class Part:
    """One unique part definition and all of its assembly occurrences."""

    number: str
    description: str
    material: str
    shape: cq.Workplane
    stock_size_mm: Vector3
    placements: tuple[Placement, ...]
    color: Color4 = (0.72, 0.52, 0.30, 1.0)

    @property
    def quantity(self) -> int:
        return len(self.placements)

    @property
    def volume_mm3(self) -> float:
        return float(self.shape.val().Volume())


@dataclass(frozen=True)
class Design:
    """A resolved furniture design ready for validation and export."""

    name: str
    model: str
    parameters: dict[str, Any]
    parts: tuple[Part, ...]

    def assembly(self) -> cq.Assembly:
        assembly = cq.Assembly(name=self.name)
        for part in self.parts:
            color = cq.Color(*part.color)
            for placement in part.placements:
                assembly.add(
                    part.shape,
                    name=placement.name,
                    color=color,
                    loc=placement.location(),
                )
        return assembly

    def compound(self) -> cq.Compound:
        return self.assembly().toCompound()

    def overall_size_mm(self) -> Vector3:
        compound = self.compound()
        # STL/glTF meshing caches a triangulation whose deflection can inflate later bounds.
        # Remove that cache before asking OpenCascade for the exact B-rep bounds.
        BRepTools.Clean_s(compound.wrapped)
        bounds = compound.BoundingBox()
        return (float(bounds.xlen), float(bounds.ylen), float(bounds.zlen))

    def total_occurrences(self) -> int:
        return sum(part.quantity for part in self.parts)

    def validate_solids(self) -> None:
        if not self.parts:
            raise ValueError("a design must contain at least one part")
        names: set[str] = set()
        numbers: set[str] = set()
        for part in self.parts:
            if part.number in numbers:
                raise ValueError(f"duplicate part number: {part.number}")
            numbers.add(part.number)
            if part.quantity < 1:
                raise ValueError(f"part {part.number} has no placements")
            shape = part.shape.val()
            if shape.isNull() or not shape.isValid() or shape.Volume() <= 0:
                raise ValueError(f"part {part.number} is not a valid solid")
            for placement in part.placements:
                if placement.name in names:
                    raise ValueError(f"duplicate placement name: {placement.name}")
                names.add(placement.name)
