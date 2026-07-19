"""User-facing dimensions and site assumptions for the built-in bookshelf."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from querycad.furniture import FurnitureSpec


@dataclass(frozen=True)
class BuiltInBookshelfSpec(FurnitureSpec):
    """Editable site envelope, cabinet proportions, materials, and hardware assumptions."""

    model_name: ClassVar[str] = "built_in_bookshelf"

    left_opening_width: float = 1100.0
    middle_opening_width: float = 1450.0
    right_opening_width: float = 670.0
    opening_depth: float = 145.0
    left_post_width: float = 360.0
    middle_post_width: float = 140.0
    right_boundary_post_width: float = 360.0
    height_under_beam: float = 2400.0
    cabinet_top_height: float = 700.0
    lower_depth: float = 330.0
    shelf_depth: float = 160.0
    shelf_count: int = 4
    shelf_pitch: float = 300.0
    shelf_thickness: float = 24.0
    divider_thickness: float = 24.0
    masonry_offset_ratio: float = 0.42
    installation_clearance: float = 3.0
    core_upright_thickness: float = 30.0
    core_anchor_depth_inset: float = 40.0
    core_anchor_end_inset: float = 180.0

    base_panel_thickness: float = 18.0
    counter_thickness: float = 28.0
    plinth_height: float = 80.0
    plinth_recess: float = 45.0
    face_frame_width: float = 42.0
    face_frame_thickness: float = 20.0
    door_thickness: float = 22.0
    door_frame_width: float = 55.0
    door_gap: float = 3.0
    door_panel_recess: float = 6.0
    knob_diameter: float = 18.0
    knob_projection: float = 18.0
    knob_edge_inset: float = 27.5
    knob_height_ratio: float = 0.5

    post_trim_thickness: float = 18.0
    display_ledge_depth: float = 55.0
    display_ledge_thickness: float = 18.0
    display_lip_height: float = 16.0
    display_lip_thickness: float = 10.0
    crown_height: float = 36.0
    crown_depth: float = 28.0

    right_slope_start_x: float = 150.0
    right_slope_start_above_beam: float = 100.0
    right_slope_end_below_beam: float = 200.0

    cabinet_screw_diameter: float = 5.0
    cabinet_screw_length: float = 50.0
    shelf_screw_diameter: float = 4.5
    shelf_screw_length: float = 45.0
    core_shelf_screw_diameter: float = 5.0
    core_shelf_screw_length: float = 60.0
    structural_screw_diameter: float = 6.0
    structural_screw_length: float = 90.0
    hinge_screw_diameter: float = 3.5
    hinge_screw_length: float = 16.0
    knob_screw_diameter: float = 4.0
    knob_screw_length: float = 25.0
    pilot_hole_diameter: float = 3.0
    structural_pilot_hole_diameter: float = 4.0

    finish_material: str = "dark stained oak"
    panel_material: str = "dark stained oak veneer plywood"
    metal_material: str = "aged brass"
    site_anchor_strategy: str = (
        "fasten only to verified existing vertical posts and the top horizontal beam; "
        "do not anchor into the brick wall"
    )

    @property
    def opening_widths(self) -> tuple[float, float, float]:
        return (
            self.left_opening_width,
            self.middle_opening_width,
            self.right_opening_width,
        )

    @property
    def internal_post_widths(self) -> tuple[float, float]:
        """Widths of the two posts included inside the furniture span."""

        return (self.left_post_width, self.middle_post_width)

    @property
    def furniture_width(self) -> float:
        """Modeled span, ending at the near edge of the right boundary post."""

        return sum(self.opening_widths) + sum(self.internal_post_widths)

    @property
    def measured_site_sequence_width(self) -> float:
        """Measured span including the right boundary post itself."""

        return self.furniture_width + self.right_boundary_post_width

    @property
    def clear_opening_widths(self) -> tuple[float, float, float]:
        """Usable widths between the new full-height core uprights."""

        return tuple(width - 2 * self.core_upright_thickness for width in self.opening_widths)

    @property
    def right_slope_end_height(self) -> float:
        return self.height_under_beam - self.right_slope_end_below_beam

    @property
    def last_shelf_bottom(self) -> float:
        return self.cabinet_top_height + self.shelf_count * self.shelf_pitch

    def right_slope_height_at(self, offset_x: float) -> float:
        """Return the sloped ceiling height at an X offset inside the right opening."""

        slope_start_height = self.height_under_beam + self.right_slope_start_above_beam
        slope_run = self.right_opening_width - self.right_slope_start_x
        return (
            slope_start_height
            + (self.right_slope_end_height - slope_start_height)
            * (offset_x - self.right_slope_start_x)
            / slope_run
        )

    def validate(self) -> None:
        self.validate_basics(
            text_fields=(
                "finish_material",
                "panel_material",
                "metal_material",
                "site_anchor_strategy",
            )
        )
        if not isinstance(self.shelf_count, int):
            raise ValueError("shelf_count must be an integer")
        if self.shelf_count < 2:
            raise ValueError("shelf_count must be at least 2")
        if self.shelf_depth <= self.opening_depth:
            raise ValueError(
                "shelf_depth must project beyond opening_depth for the requested post "
                "display ledges"
            )
        if self.lower_depth <= self.shelf_depth:
            raise ValueError("lower_depth must be deeper than shelf_depth")
        if self.cabinet_top_height >= self.height_under_beam:
            raise ValueError("cabinet_top_height must remain below the top beam")
        if self.plinth_height + self.counter_thickness >= self.cabinet_top_height:
            raise ValueError("plinth and counter leave no usable base cabinet height")
        if self.plinth_recess >= self.lower_depth:
            raise ValueError("plinth_recess must be smaller than lower_depth")
        if self.base_panel_thickness >= self.counter_thickness:
            raise ValueError("base_panel_thickness must be smaller than counter_thickness")
        if self.face_frame_thickness >= self.lower_depth:
            raise ValueError("face_frame_thickness must fit within lower_depth")
        if self.door_panel_recess >= self.door_thickness:
            raise ValueError("door_panel_recess must be smaller than door_thickness")
        if self.door_frame_width * 2 >= self.door_height_limit:
            raise ValueError("door_frame_width leaves no usable recessed door panel")
        if self.knob_projection < self.knob_diameter / 2:
            raise ValueError("knob_projection is too small for the selected knob diameter")
        knob_radius = self.knob_diameter / 2
        if not knob_radius <= self.knob_edge_inset <= self.door_frame_width - knob_radius:
            raise ValueError("knob_edge_inset must keep the knob entirely on the door frame stile")
        if not 0.25 <= self.knob_height_ratio <= 0.75:
            raise ValueError("knob_height_ratio must remain between 0.25 and 0.75")

        minimum_opening = 3 * self.face_frame_width + 2 * self.door_frame_width + 4 * self.door_gap
        if min(self.clear_opening_widths[:2]) <= minimum_opening:
            raise ValueError("wide openings are too narrow for paired framed doors")
        single_door_minimum = (
            2 * self.face_frame_width + 2 * self.door_frame_width + 2 * self.door_gap
        )
        if self.clear_opening_widths[2] <= single_door_minimum:
            raise ValueError("right opening is too narrow for its framed cabinet door")
        if min(self.clear_opening_widths) <= 2 * self.installation_clearance:
            raise ValueError("core uprights leave no usable width inside an opening")
        if self.core_upright_thickness <= self.shelf_thickness:
            raise ValueError("core_upright_thickness must exceed shelf_thickness")
        if self.core_anchor_depth_inset * 2 >= self.shelf_depth:
            raise ValueError("core anchor depth insets leave no separation between fixing rows")
        if self.core_anchor_end_inset * 2 >= self.right_slope_end_height:
            raise ValueError("core anchor end insets leave no vertical fixing span")
        if min(self.internal_post_widths) <= 60.0:
            raise ValueError("internal post widths must allow two fixing columns with 30 mm insets")

        if not 0.3 <= self.masonry_offset_ratio <= 0.7:
            raise ValueError("masonry_offset_ratio must remain between 0.3 and 0.7")
        if abs(self.masonry_offset_ratio - 0.5) < 0.02:
            raise ValueError("masonry_offset_ratio must be visibly staggered away from centre")
        divider_edge_clearance = min(self.clear_opening_widths[:2]) * min(
            self.masonry_offset_ratio, 1 - self.masonry_offset_ratio
        )
        if divider_edge_clearance <= self.door_frame_width + self.divider_thickness:
            raise ValueError("masonry dividers are too close to an opening edge")

        if self.right_slope_start_x >= self.right_opening_width:
            raise ValueError("right_slope_start_x must lie inside the right opening")
        if self.right_slope_end_height >= (
            self.height_under_beam + self.right_slope_start_above_beam
        ):
            raise ValueError("right slope must descend toward the outer wall")
        required_top_clearance = (
            self.last_shelf_bottom + self.shelf_thickness + self.crown_height + 120.0
        )
        if self.right_slope_end_height <= required_top_clearance:
            raise ValueError(
                "right slope leaves too little clearance above the highest shelf; "
                "reduce shelf_count or shelf_pitch"
            )
        if self.height_under_beam - self.crown_height <= (
            self.last_shelf_bottom + self.shelf_thickness
        ):
            raise ValueError("highest shelf collides with the crown below the top beam")
        if self.display_ledge_depth <= self.display_lip_thickness:
            raise ValueError("display_ledge_depth must exceed display_lip_thickness")
        if self.display_ledge_thickness >= self.shelf_pitch:
            raise ValueError("display ledge is too thick for the shelf spacing")
        minimum_core_screw_length = self.core_upright_thickness + self.installation_clearance + 25.0
        if self.core_shelf_screw_length < minimum_core_screw_length:
            raise ValueError(
                "core shelf screws must pass through the upright and embed 25 mm into a shelf end"
            )
        if self.cabinet_screw_length <= self.base_panel_thickness:
            raise ValueError("cabinet screws must reach beyond one base panel")
        if self.structural_screw_length <= max(
            self.post_trim_thickness, self.core_upright_thickness
        ):
            raise ValueError("structural screws must reach through the post trim and core uprights")

    @property
    def door_height_limit(self) -> float:
        return (
            self.cabinet_top_height
            - self.counter_thickness
            - self.plinth_height
            - 2 * self.face_frame_width
            - 2 * self.door_gap
        )
