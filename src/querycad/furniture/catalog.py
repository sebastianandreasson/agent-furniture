"""Modular authoring catalog for stable part definitions and occurrences."""

from __future__ import annotations

from collections.abc import Iterable

import cadquery as cq

from querycad.furniture.design import Color4, Part, Placement, Vector3


class PartHandle:
    """Mutable authoring handle for one part definition before a design is frozen."""

    def __init__(
        self,
        *,
        number: str,
        description: str,
        material: str,
        shape: cq.Workplane,
        stock_size_mm: Vector3,
        color: Color4,
    ) -> None:
        self.number = number
        self.description = description
        self.material = material
        self.shape = shape
        self.stock_size_mm = stock_size_mm
        self.color = color
        self._placements: list[Placement] = []

    @property
    def quantity(self) -> int:
        return len(self._placements)

    def place(
        self,
        name: str,
        translation_mm: Vector3 = (0.0, 0.0, 0.0),
        rotation_deg: Vector3 = (0.0, 0.0, 0.0),
    ) -> PartHandle:
        self._placements.append(Placement(name, translation_mm, rotation_deg))
        return self

    def place_many(self, placements: Iterable[Placement]) -> PartHandle:
        self._placements.extend(placements)
        return self

    def freeze(self) -> Part:
        return Part(
            number=self.number,
            description=self.description,
            material=self.material,
            shape=self.shape,
            stock_size_mm=self.stock_size_mm,
            placements=tuple(self._placements),
            color=self.color,
        )


class PartCatalog:
    """Define each physical part once and let subassemblies add occurrences."""

    def __init__(self) -> None:
        self._handles: dict[str, PartHandle] = {}

    def define(
        self,
        *,
        number: str,
        description: str,
        material: str,
        shape: cq.Workplane,
        stock_size_mm: Vector3,
        color: Color4 = (0.72, 0.52, 0.30, 1.0),
    ) -> PartHandle:
        if number in self._handles:
            raise ValueError(f"part {number} is already defined")
        if not number.strip():
            raise ValueError("part number cannot be empty")
        handle = PartHandle(
            number=number,
            description=description,
            material=material,
            shape=shape,
            stock_size_mm=stock_size_mm,
            color=color,
        )
        self._handles[number] = handle
        return handle

    def part(self, number: str) -> PartHandle:
        try:
            return self._handles[number]
        except KeyError as error:
            raise ValueError(f"part {number} has not been defined") from error

    def quantity(self, number: str) -> int:
        return self.part(number).quantity

    def freeze(self) -> tuple[Part, ...]:
        return tuple(handle.freeze() for handle in self._handles.values())
