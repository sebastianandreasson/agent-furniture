"""A configurable four-leg table with aprons below a solid top."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

from querycad.furniture import Design, FurnitureSpec, PartCatalog


@dataclass(frozen=True)
class ApronTableSpec(FurnitureSpec):
    model_name: ClassVar[str] = "apron_table"
    length: float = 1600.0
    depth: float = 800.0
    height: float = 750.0
    top_thickness: float = 30.0
    top_corner_radius: float = 12.0
    leg_size: float = 70.0
    end_overhang: float = 100.0
    side_overhang: float = 60.0
    apron_height: float = 110.0
    apron_thickness: float = 22.0
    apron_top_gap: float = 15.0
    top_material: str = "oak"
    frame_material: str = "ash"

    def validate(self) -> None:
        self.validate_basics(
            text_fields=("top_material", "frame_material"),
            allow_zero=("top_corner_radius",),
        )
        if self.top_corner_radius >= min(self.length, self.depth) / 2:
            raise ValueError("top_corner_radius must be less than half the shorter top dimension")
        if self.height <= self.top_thickness + self.apron_height + self.apron_top_gap:
            raise ValueError("height leaves no usable leg below the apron")
        clear_length = self.length - 2 * (self.end_overhang + self.leg_size)
        clear_depth = self.depth - 2 * (self.side_overhang + self.leg_size)
        if clear_length <= 0:
            raise ValueError("length is too small for the end overhang and legs")
        if clear_depth <= 0:
            raise ValueError("depth is too small for the side overhang and legs")
        if self.apron_thickness >= self.leg_size:
            raise ValueError("apron_thickness must be smaller than leg_size")


def build_apron_table(name: str, parameters: dict[str, Any]) -> Design:
    spec = ApronTableSpec.from_mapping(parameters)
    leg_height = spec.height - spec.top_thickness

    leg_x = spec.length / 2 - spec.end_overhang - spec.leg_size / 2
    leg_y = spec.depth / 2 - spec.side_overhang - spec.leg_size / 2
    apron_z = leg_height - spec.apron_top_gap - spec.apron_height

    long_apron_length = 2 * leg_x - spec.leg_size
    end_apron_length = 2 * leg_y - spec.leg_size
    long_apron_y = leg_y - spec.leg_size / 2 - spec.apron_thickness / 2
    end_apron_x = leg_x - spec.leg_size / 2 - spec.apron_thickness / 2

    catalog = PartCatalog()
    catalog.define_stock(
        number="TOP-001",
        description="Table top",
        material=spec.top_material,
        size_mm=(spec.length, spec.depth, spec.top_thickness),
        corner_radius=spec.top_corner_radius,
        color=(0.72, 0.45, 0.22, 1.0),
    ).place("table_top", (0.0, 0.0, leg_height))

    legs = catalog.define_stock(
        number="LEG-001",
        description="Square table leg",
        material=spec.frame_material,
        size_mm=(spec.leg_size, spec.leg_size, leg_height),
        color=(0.64, 0.43, 0.24, 1.0),
    )
    for x_name, x in (("left", -leg_x), ("right", leg_x)):
        for y_name, y in (("front", -leg_y), ("back", leg_y)):
            legs.place(f"leg_{x_name}_{y_name}", (x, y, 0.0))

    long_apron = catalog.define_stock(
        number="APRON-LONG-001",
        description="Long apron",
        material=spec.frame_material,
        size_mm=(long_apron_length, spec.apron_thickness, spec.apron_height),
        color=(0.61, 0.40, 0.22, 1.0),
    )
    long_apron.place("apron_long_front", (0.0, -long_apron_y, apron_z))
    long_apron.place("apron_long_back", (0.0, long_apron_y, apron_z))

    end_apron = catalog.define_stock(
        number="APRON-END-001",
        description="End apron",
        material=spec.frame_material,
        size_mm=(spec.apron_thickness, end_apron_length, spec.apron_height),
        color=(0.61, 0.40, 0.22, 1.0),
    )
    end_apron.place("apron_end_left", (-end_apron_x, 0.0, apron_z))
    end_apron.place("apron_end_right", (end_apron_x, 0.0, apron_z))

    return Design(
        name=name,
        model="apron_table",
        parameters=spec.as_dict(),
        parts=catalog.freeze(),
    )
