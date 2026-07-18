"""User-facing specification and proportion validation for the entryway bench."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin
from typing import ClassVar

from querycad.furniture import FurnitureSpec


@dataclass(frozen=True)
class EntrywayBenchSpec(FurnitureSpec):
    """Editable dimensions, materials, and hardware assumptions for the bench."""

    model_name: ClassVar[str] = "entryway_bench"

    length: float = 1000.0
    depth: float = 250.0
    extension_length: float = 600.0
    extension_depth: float = 150.0
    extension_side: str = "left"
    frame_height: float = 520.0
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
    shelf_slat_count: int = 10
    extension_slat_count: int = 6
    shelf_slat_end_gap: float = 15.0
    extension_shelf_length: float = 260.0
    extension_shelf_angle_deg: float = 40.0
    extension_shelf_front_height: float = 90.0
    extension_shelf_stopper_height: float = 18.0
    extension_shelf_stopper_thickness: float = 12.0
    frame_pocket_screw_length: float = 38.0
    top_pocket_screw_length: float = 32.0
    pocket_hole_bit_diameter: float = 9.5
    pocket_hole_angle_deg: float = 15.0
    slat_screw_diameter: float = 4.0
    slat_screw_length: float = 35.0
    slat_clearance_hole_diameter: float = 4.5
    slat_pilot_hole_diameter: float = 3.0
    slat_countersink_diameter: float = 8.0
    connector_bolt_diameter: float = 6.0
    connector_bolt_length: float = 50.0
    connector_clearance_hole_diameter: float = 6.5
    alignment_dowel_diameter: float = 8.0
    alignment_dowel_length: float = 40.0
    cushion_length: float = 990.0
    cushion_depth: float = 240.0
    cushion_thickness: float = 30.0
    cushion_corner_radius: float = 10.0
    cushion_piping_width: float = 5.0
    cushion_piping_height: float = 3.0
    frame_material: str = "warm grey painted beech"
    panel_material: str = "warm grey painted beech-faced plywood"
    cushion_material: str = "natural linen-look upholstery"

    def validate(self) -> None:
        self.validate_basics(
            text_fields=("frame_material", "panel_material", "cushion_material"),
            non_numeric_fields=("extension_side",),
            allow_zero=("seat_base_corner_radius",),
        )
        if not isinstance(self.shelf_slat_count, int):
            raise ValueError("shelf_slat_count must be an integer")
        if not isinstance(self.extension_slat_count, int):
            raise ValueError("extension_slat_count must be an integer")
        if self.extension_side not in {"left", "right"}:
            raise ValueError("extension_side must be 'left' or 'right'")
        if self.shelf_slat_count < 2:
            raise ValueError("shelf_slat_count must be at least 2")
        if self.extension_slat_count < 2:
            raise ValueError("extension_slat_count must be at least 2")

        if self.length <= 2 * self.leg_size:
            raise ValueError("length is too small for two legs")
        if self.depth <= 2 * self.leg_size:
            raise ValueError("depth is too small for two legs")
        if self.extension_length <= 2 * self.leg_size:
            raise ValueError("extension_length is too small for its outer legs")
        if self.extension_depth <= 2 * self.leg_size:
            raise ValueError("extension_depth is too small for two outer legs")
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
        if self.pocket_hole_bit_diameter >= min(self.top_rail_thickness, self.shelf_rail_thickness):
            raise ValueError("pocket_hole_bit_diameter must fit within the support rails")
        if self.slat_clearance_hole_diameter <= self.slat_screw_diameter:
            raise ValueError("slat_clearance_hole_diameter must exceed slat_screw_diameter")
        if self.slat_pilot_hole_diameter >= self.slat_screw_diameter:
            raise ValueError("slat_pilot_hole_diameter must be smaller than slat_screw_diameter")
        if self.slat_countersink_diameter >= self.shelf_slat_width:
            raise ValueError("slat_countersink_diameter must fit within a shelf slat")
        if not (
            self.shelf_slat_thickness
            < self.slat_screw_length
            < self.shelf_slat_thickness + self.shelf_rail_height
        ):
            raise ValueError(
                "slat_screw_length must pass through the slat without exiting its support rail"
            )
        if self.connector_clearance_hole_diameter <= self.connector_bolt_diameter:
            raise ValueError(
                "connector_clearance_hole_diameter must exceed connector_bolt_diameter"
            )
        if self.connector_bolt_length <= self.top_rail_thickness:
            raise ValueError("connector_bolt_length must reach beyond the extension rail")
        if self.alignment_dowel_length <= self.top_rail_thickness:
            raise ValueError("alignment_dowel_length must reach beyond the extension rail")
