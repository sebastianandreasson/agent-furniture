"""Photo-inspired cushioned bench with an indented, uncovered side extension."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from math import cos, radians, sin
from typing import Any

import cadquery as cq

from querycad.core import Design, Part, Placement


@dataclass(frozen=True)
class EntrywayBenchSpec:
    """User-facing dimensions for the painted timber and upholstered bench."""

    length: float = 1200.0
    depth: float = 380.0
    extension_length: float = 400.0
    extension_depth: float = 190.0
    extension_side: str = "left"
    frame_height: float = 430.0
    seat_base_thickness: float = 22.0
    seat_base_corner_radius: float = 3.0
    leg_size: float = 42.0
    top_rail_height: float = 62.0
    top_rail_thickness: float = 24.0
    lower_shelf_height: float = 120.0
    shelf_rail_height: float = 32.0
    shelf_rail_thickness: float = 24.0
    shelf_slat_thickness: float = 16.0
    shelf_slat_width: float = 30.0
    shelf_slat_count: int = 12
    extension_slat_count: int = 4
    shelf_slat_end_gap: float = 15.0
    extension_shelf_length: float = 260.0
    extension_shelf_angle_deg: float = 25.0
    extension_shelf_front_height: float = 90.0
    extension_shelf_stopper_height: float = 18.0
    extension_shelf_stopper_thickness: float = 12.0
    cushion_length: float = 1140.0
    cushion_depth: float = 350.0
    cushion_thickness: float = 70.0
    cushion_corner_radius: float = 18.0
    cushion_piping_width: float = 5.0
    cushion_piping_height: float = 3.0
    frame_material: str = "warm grey painted beech"
    cushion_material: str = "natural linen-look upholstery"

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> EntrywayBenchSpec:
        allowed = {field.name for field in fields(cls)}
        unknown = sorted(set(values) - allowed)
        if unknown:
            raise ValueError(f"unknown entryway_bench parameter(s): {', '.join(unknown)}")
        spec = cls(**values)
        spec.validate()
        return spec

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> None:
        materials = {
            "frame_material": self.frame_material,
            "cushion_material": self.cushion_material,
        }
        invalid_materials = [
            key
            for key, value in materials.items()
            if not isinstance(value, str) or not value.strip()
        ]
        if invalid_materials:
            raise ValueError(
                f"material names must be non-empty strings: {', '.join(invalid_materials)}"
            )

        numeric = {
            key: value
            for key, value in self.as_dict().items()
            if key not in {*materials, "extension_side"}
        }
        not_numbers = [
            key
            for key, value in numeric.items()
            if not isinstance(value, int | float) or isinstance(value, bool)
        ]
        if not_numbers:
            raise ValueError(f"parameters must be numeric: {', '.join(not_numbers)}")
        if not isinstance(self.shelf_slat_count, int):
            raise ValueError("shelf_slat_count must be an integer")
        if not isinstance(self.extension_slat_count, int):
            raise ValueError("extension_slat_count must be an integer")
        if self.extension_side not in {"left", "right"}:
            raise ValueError("extension_side must be 'left' or 'right'")

        can_be_zero = {"seat_base_corner_radius"}
        non_positive = [
            key for key, value in numeric.items() if value <= 0 and key not in can_be_zero
        ]
        if non_positive:
            raise ValueError(f"parameters must be greater than zero: {', '.join(non_positive)}")
        if self.seat_base_corner_radius < 0:
            raise ValueError("seat_base_corner_radius cannot be negative")
        if self.shelf_slat_count < 2:
            raise ValueError("shelf_slat_count must be at least 2")
        if self.extension_slat_count < 2:
            raise ValueError("extension_slat_count must be at least 2")

        if self.length <= 2 * self.leg_size:
            raise ValueError("length is too small for two legs")
        if self.depth <= 2 * self.leg_size:
            raise ValueError("depth is too small for two legs")
        if self.extension_length <= 2 * self.leg_size:
            raise ValueError("extension_length is too small for its legs")
        if self.extension_depth <= 2 * self.leg_size:
            raise ValueError("extension_depth is too small for two legs")
        if self.extension_depth >= self.depth:
            raise ValueError("extension_depth must be smaller than depth to form an indent")
        if self.seat_base_thickness >= self.frame_height:
            raise ValueError("seat_base_thickness must be smaller than frame_height")
        if self.top_rail_thickness >= self.leg_size:
            raise ValueError("top_rail_thickness must be smaller than leg_size")
        if self.shelf_rail_thickness >= self.leg_size:
            raise ValueError("shelf_rail_thickness must be smaller than leg_size")

        if self.cushion_length > self.length or self.cushion_depth > self.depth:
            raise ValueError("cushion must fit within the seat base")
        if self.seat_base_corner_radius >= min(self.length, self.depth) / 2:
            raise ValueError("seat_base_corner_radius is too large for the seat base")
        if self.seat_base_corner_radius >= self.extension_depth / 2:
            raise ValueError("seat_base_corner_radius is too large for the extension top")
        cushion_radius_limit = (
            min(self.cushion_length, self.cushion_depth, self.cushion_thickness) / 2
        )
        if self.cushion_corner_radius >= cushion_radius_limit:
            raise ValueError("cushion_corner_radius is too large for the cushion")
        if self.cushion_piping_width >= self.cushion_corner_radius:
            raise ValueError("cushion_piping_width must be smaller than cushion_corner_radius")
        if 2 * self.cushion_piping_height >= self.cushion_thickness:
            raise ValueError("cushion_piping_height is too large for the cushion")

        leg_height = self.frame_height - self.seat_base_thickness
        top_rail_bottom = leg_height - self.top_rail_height
        if top_rail_bottom <= 0:
            raise ValueError("top rail leaves no usable leg below it")
        if self.lower_shelf_height <= self.shelf_rail_height:
            raise ValueError("lower_shelf_height is too low for its support rails")
        if self.lower_shelf_height >= top_rail_bottom:
            raise ValueError("lower shelf collides with the top rails")

        usable_slat_span = self.length - 2 * self.leg_size - 2 * self.shelf_slat_end_gap
        if usable_slat_span <= 0:
            raise ValueError("length leaves no usable shelf slat span")
        if self.shelf_slat_count * self.shelf_slat_width > usable_slat_span:
            raise ValueError("shelf slats overlap; reduce their count or width")
        extension_slat_span = self.extension_length - self.leg_size - 2 * self.shelf_slat_end_gap
        if extension_slat_span <= 0:
            raise ValueError("extension_length leaves no usable shelf slat span")
        if self.extension_slat_count * self.shelf_slat_width > extension_slat_span:
            raise ValueError("extension shelf slats overlap; reduce their count or width")

        if self.extension_shelf_angle_deg >= 60:
            raise ValueError("extension_shelf_angle_deg must be smaller than 60 degrees")
        extension_shelf_angle = radians(self.extension_shelf_angle_deg)
        extension_shelf_projection = self.extension_shelf_length * cos(extension_shelf_angle)
        extension_support_span = self.extension_depth - self.leg_size
        if extension_shelf_projection < extension_support_span:
            raise ValueError(
                "extension shelf is too short to reach both support rails; increase "
                "extension_shelf_length or reduce extension_shelf_angle_deg"
            )
        extension_back_leg_y = self.depth / 2 - self.leg_size / 2
        extension_shelf_front_y = extension_back_leg_y - extension_shelf_projection
        if extension_shelf_front_y < -self.depth / 2:
            raise ValueError(
                "extension shelf projects beyond the main bench footprint; reduce "
                "extension_shelf_length or increase extension_shelf_angle_deg"
            )
        extension_shelf_bottom = self.extension_shelf_front_height - (
            self.shelf_slat_thickness * cos(extension_shelf_angle)
        )
        if extension_shelf_bottom <= 0:
            raise ValueError("extension shelf front edge must remain above the floor")
        extension_shelf_back_top = self.extension_shelf_front_height + (
            self.extension_shelf_length * sin(extension_shelf_angle)
        )
        if extension_shelf_back_top >= top_rail_bottom:
            raise ValueError(
                "extension shelf collides with the top rails; lower its front height, "
                "length, or angle"
            )
        if self.extension_shelf_stopper_thickness >= self.extension_shelf_length:
            raise ValueError(
                "extension_shelf_stopper_thickness must be smaller than extension_shelf_length"
            )
        extension_shelf_stopper_top = (
            self.extension_shelf_front_height
            + self.extension_shelf_stopper_thickness * sin(extension_shelf_angle)
            + self.extension_shelf_stopper_height * cos(extension_shelf_angle)
        )
        if extension_shelf_stopper_top >= top_rail_bottom:
            raise ValueError(
                "extension shelf stopper collides with the top rails; reduce its height"
            )


def _prism(
    x: float,
    y: float,
    z: float,
    corner_radius: float = 0.0,
) -> cq.Workplane:
    result = cq.Workplane("XY").box(x, y, z, centered=(True, True, False))
    if corner_radius:
        result = result.edges("|Z").fillet(corner_radius)
    return result


def _soft_prism(x: float, y: float, z: float, radius: float) -> cq.Workplane:
    return cq.Workplane("XY").box(x, y, z, centered=(True, True, False)).edges().fillet(radius)


def _centered_prism(
    x: float,
    y: float,
    z: float,
    corner_radius: float = 0.0,
) -> cq.Workplane:
    """Make a local-coordinate prism centered on its placement rotation origin."""

    return _prism(x, y, z, corner_radius).translate((0.0, 0.0, -z / 2))


def _rounded_ring(
    x: float,
    y: float,
    z: float,
    width: float,
    radius: float,
) -> cq.Workplane:
    outer = _prism(x, y, z, radius)
    inner = _prism(x - 2 * width, y - 2 * width, z + 2.0, radius - width).translate(
        (0.0, 0.0, -1.0)
    )
    return outer.cut(inner)


def build_entryway_bench(name: str, parameters: dict[str, Any]) -> Design:
    spec = EntrywayBenchSpec.from_mapping(parameters)
    leg_height = spec.frame_height - spec.seat_base_thickness
    leg_x = spec.length / 2 - spec.leg_size / 2
    leg_y = spec.depth / 2 - spec.leg_size / 2
    top_rail_z = leg_height - spec.top_rail_height
    long_member_length = spec.length - 2 * spec.leg_size
    end_member_depth = spec.depth - 2 * spec.leg_size
    extension_sign = 1.0 if spec.extension_side == "right" else -1.0
    extension_center_x = extension_sign * (spec.length + spec.extension_length) / 2
    extension_rail_center_x = extension_sign * (
        spec.length / 2 + (spec.extension_length - spec.leg_size) / 2
    )
    extension_far_leg_x = extension_sign * (
        spec.length / 2 + spec.extension_length - spec.leg_size / 2
    )
    extension_transition_leg_x = extension_sign * leg_x
    extension_center_y = (spec.depth - spec.extension_depth) / 2
    extension_front_leg_y = spec.depth / 2 - spec.extension_depth + spec.leg_size / 2
    extension_back_leg_y = leg_y
    extension_long_member_length = spec.extension_length - spec.leg_size
    extension_end_member_depth = spec.extension_depth - 2 * spec.leg_size
    extension_shelf_angle = radians(spec.extension_shelf_angle_deg)
    extension_shelf_sin = sin(extension_shelf_angle)
    extension_shelf_cos = cos(extension_shelf_angle)
    extension_shelf_projection = spec.extension_shelf_length * extension_shelf_cos
    extension_shelf_front_y = extension_back_leg_y - extension_shelf_projection
    extension_shelf_center_y = (extension_shelf_front_y + extension_back_leg_y) / 2
    extension_shelf_center_z = (
        spec.extension_shelf_front_height
        + spec.extension_shelf_length * extension_shelf_sin / 2
        - spec.shelf_slat_thickness * extension_shelf_cos / 2
    )
    extension_shelf_rail_center_offset = (spec.shelf_slat_thickness + spec.shelf_rail_height) / 2
    extension_shelf_rail_y_offset = extension_shelf_rail_center_offset * extension_shelf_sin
    extension_shelf_rail_z_offset = extension_shelf_rail_center_offset * extension_shelf_cos
    extension_front_rail_contact_y = extension_front_leg_y + spec.shelf_rail_thickness / 2
    extension_back_rail_contact_y = extension_back_leg_y - spec.shelf_rail_thickness / 2
    extension_front_rail_contact_z = extension_shelf_center_z + (
        (extension_front_rail_contact_y - extension_shelf_center_y)
        * extension_shelf_sin
        / extension_shelf_cos
    )
    extension_back_rail_contact_z = extension_shelf_center_z + (
        (extension_back_rail_contact_y - extension_shelf_center_y)
        * extension_shelf_sin
        / extension_shelf_cos
    )
    extension_usable_slat_span = extension_long_member_length - 2 * spec.shelf_slat_end_gap
    extension_stopper_local_y = (
        -spec.extension_shelf_length / 2 + spec.extension_shelf_stopper_thickness / 2
    )
    extension_stopper_local_z = (
        spec.shelf_slat_thickness / 2 + spec.extension_shelf_stopper_height / 2
    )
    extension_stopper_center_y = (
        extension_shelf_center_y
        + extension_stopper_local_y * extension_shelf_cos
        - extension_stopper_local_z * extension_shelf_sin
    )
    extension_stopper_center_z = (
        extension_shelf_center_z
        + extension_stopper_local_y * extension_shelf_sin
        + extension_stopper_local_z * extension_shelf_cos
    )

    paint = (0.43, 0.42, 0.39, 1.0)
    fabric = (0.78, 0.74, 0.66, 1.0)
    piping = (0.68, 0.64, 0.56, 1.0)

    seat_base = Part(
        number="SEAT-BASE-001",
        description="Rounded seat support board",
        material=spec.frame_material,
        shape=_prism(
            spec.length,
            spec.depth,
            spec.seat_base_thickness,
            spec.seat_base_corner_radius,
        ),
        stock_size_mm=(spec.length, spec.depth, spec.seat_base_thickness),
        placements=(Placement("seat_base", (0.0, 0.0, leg_height)),),
        color=paint,
    )

    leg = Part(
        number="LEG-001",
        description="Square bench leg",
        material=spec.frame_material,
        shape=_prism(spec.leg_size, spec.leg_size, leg_height),
        stock_size_mm=(spec.leg_size, spec.leg_size, leg_height),
        placements=(
            *(
                Placement(f"leg_{x_name}_{y_name}", (x, y, 0.0))
                for x_name, x in (("left", -leg_x), ("right", leg_x))
                for y_name, y in (("front", -leg_y), ("back", leg_y))
            ),
            Placement(
                "leg_extension_transition_front",
                (extension_transition_leg_x, extension_front_leg_y, 0.0),
            ),
            Placement(
                "leg_extension_end_front",
                (extension_far_leg_x, extension_front_leg_y, 0.0),
            ),
            Placement(
                "leg_extension_end_back",
                (extension_far_leg_x, extension_back_leg_y, 0.0),
            ),
        ),
        color=paint,
    )

    top_rail_long = Part(
        number="TOP-RAIL-LONG-001",
        description="Long rail below seat",
        material=spec.frame_material,
        shape=_prism(long_member_length, spec.top_rail_thickness, spec.top_rail_height),
        stock_size_mm=(
            long_member_length,
            spec.top_rail_thickness,
            spec.top_rail_height,
        ),
        placements=(
            Placement("top_rail_front", (0.0, -leg_y, top_rail_z)),
            Placement("top_rail_back", (0.0, leg_y, top_rail_z)),
        ),
        color=paint,
    )

    top_rail_end = Part(
        number="TOP-RAIL-END-001",
        description="End rail below seat",
        material=spec.frame_material,
        shape=_prism(spec.top_rail_thickness, end_member_depth, spec.top_rail_height),
        stock_size_mm=(
            spec.top_rail_thickness,
            end_member_depth,
            spec.top_rail_height,
        ),
        placements=(
            Placement("top_rail_left", (-leg_x, 0.0, top_rail_z)),
            Placement("top_rail_right", (leg_x, 0.0, top_rail_z)),
        ),
        color=paint,
    )

    shelf_rail = Part(
        number="SHELF-RAIL-001",
        description="Long shelf support rail",
        material=spec.frame_material,
        shape=_prism(
            long_member_length,
            spec.shelf_rail_thickness,
            spec.shelf_rail_height,
        ),
        stock_size_mm=(
            long_member_length,
            spec.shelf_rail_thickness,
            spec.shelf_rail_height,
        ),
        placements=tuple(
            Placement(
                f"shelf_rail_lower_{side_name}",
                (0.0, y, spec.lower_shelf_height - spec.shelf_rail_height),
            )
            for side_name, y in (("front", -leg_y), ("back", leg_y))
        ),
        color=paint,
    )

    usable_slat_span = long_member_length - 2 * spec.shelf_slat_end_gap
    slat_pitch = (usable_slat_span - spec.shelf_slat_width) / (spec.shelf_slat_count - 1)
    first_slat_x = -usable_slat_span / 2 + spec.shelf_slat_width / 2
    slat_depth = 2 * leg_y
    shelf_slat = Part(
        number="SHELF-SLAT-001",
        description="Front-to-back shoe shelf slat",
        material=spec.frame_material,
        shape=_prism(spec.shelf_slat_width, slat_depth, spec.shelf_slat_thickness, 2.0),
        stock_size_mm=(
            spec.shelf_slat_width,
            slat_depth,
            spec.shelf_slat_thickness,
        ),
        placements=tuple(
            Placement(
                f"shelf_slat_lower_{index + 1:02d}",
                (
                    first_slat_x + index * slat_pitch,
                    0.0,
                    spec.lower_shelf_height - spec.shelf_slat_thickness,
                ),
            )
            for index in range(spec.shelf_slat_count)
        ),
        color=paint,
    )

    extension_top = Part(
        number="EXTENSION-TOP-001",
        description="Uncovered indented extension top",
        material=spec.frame_material,
        shape=_prism(
            spec.extension_length,
            spec.extension_depth,
            spec.seat_base_thickness,
            spec.seat_base_corner_radius,
        ),
        stock_size_mm=(
            spec.extension_length,
            spec.extension_depth,
            spec.seat_base_thickness,
        ),
        placements=(
            Placement(
                "extension_top",
                (extension_center_x, extension_center_y, leg_height),
            ),
        ),
        color=paint,
    )

    extension_top_rail_long = Part(
        number="EXTENSION-TOP-RAIL-LONG-001",
        description="Long rail below extension top",
        material=spec.frame_material,
        shape=_prism(
            extension_long_member_length,
            spec.top_rail_thickness,
            spec.top_rail_height,
        ),
        stock_size_mm=(
            extension_long_member_length,
            spec.top_rail_thickness,
            spec.top_rail_height,
        ),
        placements=(
            Placement(
                "extension_top_rail_front",
                (extension_rail_center_x, extension_front_leg_y, top_rail_z),
            ),
            Placement(
                "extension_top_rail_back",
                (extension_rail_center_x, extension_back_leg_y, top_rail_z),
            ),
        ),
        color=paint,
    )

    extension_top_rail_end = Part(
        number="EXTENSION-TOP-RAIL-END-001",
        description="End rail below extension top",
        material=spec.frame_material,
        shape=_prism(
            spec.top_rail_thickness,
            extension_end_member_depth,
            spec.top_rail_height,
        ),
        stock_size_mm=(
            spec.top_rail_thickness,
            extension_end_member_depth,
            spec.top_rail_height,
        ),
        placements=(
            Placement(
                "extension_top_rail_end",
                (extension_far_leg_x, extension_center_y, top_rail_z),
            ),
        ),
        color=paint,
    )

    extension_shelf_rail = Part(
        number="EXTENSION-SHELF-RAIL-001",
        description="Angled long rail below indented extension shelf",
        material=spec.frame_material,
        shape=_centered_prism(
            extension_long_member_length,
            spec.shelf_rail_thickness,
            spec.shelf_rail_height,
        ),
        stock_size_mm=(
            extension_long_member_length,
            spec.shelf_rail_thickness,
            spec.shelf_rail_height,
        ),
        placements=(
            Placement(
                "extension_shelf_rail_front",
                (
                    extension_rail_center_x,
                    extension_front_rail_contact_y + extension_shelf_rail_y_offset,
                    extension_front_rail_contact_z - extension_shelf_rail_z_offset,
                ),
                (spec.extension_shelf_angle_deg, 0.0, 0.0),
            ),
            Placement(
                "extension_shelf_rail_back",
                (
                    extension_rail_center_x,
                    extension_back_rail_contact_y + extension_shelf_rail_y_offset,
                    extension_back_rail_contact_z - extension_shelf_rail_z_offset,
                ),
                (spec.extension_shelf_angle_deg, 0.0, 0.0),
            ),
        ),
        color=paint,
    )

    extension_slat_pitch = (extension_usable_slat_span - spec.shelf_slat_width) / (
        spec.extension_slat_count - 1
    )
    extension_first_slat_x = (
        extension_rail_center_x - extension_usable_slat_span / 2 + spec.shelf_slat_width / 2
    )
    extension_shelf_slat = Part(
        number="EXTENSION-SHELF-SLAT-001",
        description="Angled front-to-back slat for indented extension shoe shelf",
        material=spec.frame_material,
        shape=_centered_prism(
            spec.shelf_slat_width,
            spec.extension_shelf_length,
            spec.shelf_slat_thickness,
            2.0,
        ),
        stock_size_mm=(
            spec.shelf_slat_width,
            spec.extension_shelf_length,
            spec.shelf_slat_thickness,
        ),
        placements=tuple(
            Placement(
                f"extension_shelf_slat_{index + 1:02d}",
                (
                    extension_first_slat_x + index * extension_slat_pitch,
                    extension_shelf_center_y,
                    extension_shelf_center_z,
                ),
                (spec.extension_shelf_angle_deg, 0.0, 0.0),
            )
            for index in range(spec.extension_slat_count)
        ),
        color=paint,
    )

    extension_shelf_stopper = Part(
        number="EXTENSION-SHELF-STOPPER-001",
        description="Low retaining lip at front of angled shoe shelf",
        material=spec.frame_material,
        shape=_centered_prism(
            extension_usable_slat_span,
            spec.extension_shelf_stopper_thickness,
            spec.extension_shelf_stopper_height,
            2.0,
        ),
        stock_size_mm=(
            extension_usable_slat_span,
            spec.extension_shelf_stopper_thickness,
            spec.extension_shelf_stopper_height,
        ),
        placements=(
            Placement(
                "extension_shelf_front_stopper",
                (
                    extension_rail_center_x,
                    extension_stopper_center_y,
                    extension_stopper_center_z,
                ),
                (spec.extension_shelf_angle_deg, 0.0, 0.0),
            ),
        ),
        color=paint,
    )

    cushion = Part(
        number="CUSHION-001",
        description="Loose upholstered seat cushion",
        material=spec.cushion_material,
        shape=_soft_prism(
            spec.cushion_length,
            spec.cushion_depth,
            spec.cushion_thickness,
            spec.cushion_corner_radius,
        ),
        stock_size_mm=(spec.cushion_length, spec.cushion_depth, spec.cushion_thickness),
        placements=(Placement("seat_cushion", (0.0, 0.0, spec.frame_height)),),
        color=fabric,
    )

    piping_shape = _rounded_ring(
        spec.cushion_length - 4.0,
        spec.cushion_depth - 4.0,
        spec.cushion_piping_height,
        spec.cushion_piping_width,
        spec.cushion_corner_radius - 2.0,
    )
    cushion_piping = Part(
        number="CUSHION-PIPING-001",
        description="Cushion perimeter piping",
        material=spec.cushion_material,
        shape=piping_shape,
        stock_size_mm=(
            spec.cushion_length - 4.0,
            spec.cushion_depth - 4.0,
            spec.cushion_piping_height,
        ),
        placements=(
            Placement(
                "cushion_piping_lower",
                (0.0, 0.0, spec.frame_height + 6.0),
            ),
            Placement(
                "cushion_piping_upper",
                (
                    0.0,
                    0.0,
                    spec.frame_height + spec.cushion_thickness - spec.cushion_piping_height - 6.0,
                ),
            ),
        ),
        color=piping,
    )

    return Design(
        name=name,
        model="entryway_bench",
        parameters=spec.as_dict(),
        parts=(
            seat_base,
            leg,
            top_rail_long,
            top_rail_end,
            shelf_rail,
            shelf_slat,
            extension_top,
            extension_top_rail_long,
            extension_top_rail_end,
            extension_shelf_rail,
            extension_shelf_slat,
            extension_shelf_stopper,
            cushion,
            cushion_piping,
        ),
    )
