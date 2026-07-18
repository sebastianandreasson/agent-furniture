"""Derived, geometry-free layout shared by bench parts and joinery."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

from querycad.furniture import linear_centers
from querycad.models.entryway_bench.spec import EntrywayBenchSpec


@dataclass(frozen=True)
class BenchLayout:
    leg_height: float
    leg_x: float
    leg_y: float
    top_rail_z: float
    long_member_length: float
    end_member_depth: float
    main_slat_span: float
    main_slat_centers: tuple[float, ...]
    main_slat_depth: float
    main_slat_hole_inset: float

    extension_center_x: float
    extension_center_y: float
    extension_rail_center_x: float
    extension_far_leg_x: float
    extension_transition_leg_x: float
    extension_front_leg_y: float
    extension_back_leg_y: float
    extension_long_member_length: float
    extension_end_member_depth: float
    extension_slat_span: float
    extension_slat_centers: tuple[float, ...]
    extension_slat_pitch: float

    shelf_angle_sin: float
    shelf_angle_cos: float
    extension_shelf_center_y: float
    extension_shelf_center_z: float
    extension_shelf_rail_y_offset: float
    extension_shelf_rail_z_offset: float
    extension_front_rail_contact_y: float
    extension_front_rail_contact_z: float
    extension_back_rail_contact_y: float
    extension_back_rail_contact_z: float
    extension_front_screw_y: float
    extension_back_screw_y: float
    extension_stopper_center_y: float
    extension_stopper_center_z: float

    @classmethod
    def from_spec(cls, spec: EntrywayBenchSpec) -> BenchLayout:
        leg_height = spec.frame_height - spec.seat_base_thickness
        leg_x = spec.length / 2 - spec.leg_size / 2
        leg_y = spec.depth / 2 - spec.leg_size / 2
        top_rail_z = leg_height - spec.top_rail_height
        long_member_length = spec.length - 2 * spec.leg_size
        end_member_depth = spec.depth - 2 * spec.leg_size
        main_slat_span = long_member_length - 2 * spec.shelf_slat_end_gap
        main_slat_centers = linear_centers(
            main_slat_span, spec.shelf_slat_width, spec.shelf_slat_count
        )
        main_slat_depth = 2 * leg_y
        main_slat_hole_inset = spec.shelf_rail_thickness / 4

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
        extension_slat_span = extension_long_member_length - 2 * spec.shelf_slat_end_gap
        extension_slat_local = linear_centers(
            extension_slat_span, spec.shelf_slat_width, spec.extension_slat_count
        )
        extension_slat_centers = tuple(
            extension_rail_center_x + center for center in extension_slat_local
        )
        extension_slat_pitch = extension_slat_local[1] - extension_slat_local[0]

        shelf_angle = radians(spec.extension_shelf_angle_deg)
        shelf_angle_sin = sin(shelf_angle)
        shelf_angle_cos = cos(shelf_angle)
        shelf_projection = spec.extension_shelf_length * shelf_angle_cos
        shelf_front_y = extension_back_leg_y - shelf_projection
        shelf_center_y = (shelf_front_y + extension_back_leg_y) / 2
        shelf_center_z = (
            spec.extension_shelf_front_height
            + spec.extension_shelf_length * shelf_angle_sin / 2
            - spec.shelf_slat_thickness * shelf_angle_cos / 2
        )
        rail_center_offset = (spec.shelf_slat_thickness + spec.shelf_rail_height) / 2
        rail_y_offset = rail_center_offset * shelf_angle_sin
        rail_z_offset = rail_center_offset * shelf_angle_cos
        front_rail_contact_y = extension_front_leg_y + spec.shelf_rail_thickness / 2
        back_rail_contact_y = extension_back_leg_y - spec.shelf_rail_thickness / 2
        front_rail_contact_z = shelf_center_z + (
            (front_rail_contact_y - shelf_center_y) * shelf_angle_sin / shelf_angle_cos
        )
        back_rail_contact_z = shelf_center_z + (
            (back_rail_contact_y - shelf_center_y) * shelf_angle_sin / shelf_angle_cos
        )
        front_screw_y = (front_rail_contact_y - shelf_center_y) / shelf_angle_cos
        back_screw_y = (back_rail_contact_y - shelf_center_y) / shelf_angle_cos

        stopper_local_y = (
            -spec.extension_shelf_length / 2 + spec.extension_shelf_stopper_thickness / 2
        )
        stopper_local_z = spec.shelf_slat_thickness / 2 + spec.extension_shelf_stopper_height / 2
        stopper_center_y = (
            shelf_center_y + stopper_local_y * shelf_angle_cos - stopper_local_z * shelf_angle_sin
        )
        stopper_center_z = (
            shelf_center_z + stopper_local_y * shelf_angle_sin + stopper_local_z * shelf_angle_cos
        )

        return cls(
            leg_height=leg_height,
            leg_x=leg_x,
            leg_y=leg_y,
            top_rail_z=top_rail_z,
            long_member_length=long_member_length,
            end_member_depth=end_member_depth,
            main_slat_span=main_slat_span,
            main_slat_centers=main_slat_centers,
            main_slat_depth=main_slat_depth,
            main_slat_hole_inset=main_slat_hole_inset,
            extension_center_x=extension_center_x,
            extension_center_y=extension_center_y,
            extension_rail_center_x=extension_rail_center_x,
            extension_far_leg_x=extension_far_leg_x,
            extension_transition_leg_x=extension_transition_leg_x,
            extension_front_leg_y=extension_front_leg_y,
            extension_back_leg_y=extension_back_leg_y,
            extension_long_member_length=extension_long_member_length,
            extension_end_member_depth=extension_end_member_depth,
            extension_slat_span=extension_slat_span,
            extension_slat_centers=extension_slat_centers,
            extension_slat_pitch=extension_slat_pitch,
            shelf_angle_sin=shelf_angle_sin,
            shelf_angle_cos=shelf_angle_cos,
            extension_shelf_center_y=shelf_center_y,
            extension_shelf_center_z=shelf_center_z,
            extension_shelf_rail_y_offset=rail_y_offset,
            extension_shelf_rail_z_offset=rail_z_offset,
            extension_front_rail_contact_y=front_rail_contact_y,
            extension_front_rail_contact_z=front_rail_contact_z,
            extension_back_rail_contact_y=back_rail_contact_y,
            extension_back_rail_contact_z=back_rail_contact_z,
            extension_front_screw_y=front_screw_y,
            extension_back_screw_y=back_screw_y,
            extension_stopper_center_y=stopper_center_y,
            extension_stopper_center_z=stopper_center_z,
        )
