"""Derived bay, door, shelf, and sloped-crown layout calculations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec


@dataclass(frozen=True)
class BayLayout:
    name: str
    width: float
    left_x: float
    center_x: float
    right_x: float
    fitted_left_x: float
    fitted_right_x: float
    fitted_width: float
    door_count: int


@dataclass(frozen=True)
class PostLayout:
    """An existing internal post clad and bridged by the furniture."""

    name: str
    width: float
    left_x: float
    center_x: float
    right_x: float


@dataclass(frozen=True)
class DoorLayout:
    name: str
    bay_name: str
    width: float
    center_x: float
    knob_x: float
    hinge_side: Literal["left", "right"]


@dataclass(frozen=True)
class DividerLayout:
    name: str
    row: int
    center_x: float
    bottom_z: float
    height: float


@dataclass(frozen=True)
class BuiltInLayout:
    """Geometry-free coordinates shared by parts, joinery, and tests."""

    furniture_width: float
    bays: tuple[BayLayout, ...]
    posts: tuple[PostLayout, ...]
    shelf_bottoms: tuple[float, ...]
    divider_segments: tuple[DividerLayout, ...]
    doors: tuple[DoorLayout, ...]
    carcass_depth: float
    carcass_bottom_z: float
    carcass_height: float
    face_frame_height: float
    door_bottom_z: float
    door_height: float
    crown_bottom_z: float
    right_crown_base_z: float
    right_slope_crossing_x: float

    @classmethod
    def from_spec(cls, spec: BuiltInBookshelfSpec) -> BuiltInLayout:
        total_width = spec.furniture_width
        left_edge = -total_width / 2
        bays: list[BayLayout] = []
        posts: list[PostLayout] = []
        cursor = left_edge
        door_counts = (2, 2, 1)
        names = ("left", "middle", "right")
        for index, (name, width, door_count) in enumerate(
            zip(names, spec.opening_widths, door_counts, strict=True)
        ):
            bay = BayLayout(
                name=name,
                width=width,
                left_x=cursor,
                center_x=cursor + width / 2,
                right_x=cursor + width,
                fitted_left_x=(cursor + spec.core_upright_thickness + spec.installation_clearance),
                fitted_right_x=(
                    cursor + width - spec.core_upright_thickness - spec.installation_clearance
                ),
                fitted_width=(
                    width - 2 * (spec.core_upright_thickness + spec.installation_clearance)
                ),
                door_count=door_count,
            )
            bays.append(bay)
            cursor += width
            if index < 2:
                post_width = spec.internal_post_widths[index]
                post_name = ("left", "middle")[index]
                posts.append(
                    PostLayout(
                        name=post_name,
                        width=post_width,
                        left_x=cursor,
                        center_x=cursor + post_width / 2,
                        right_x=cursor + post_width,
                    )
                )
                cursor += post_width

        shelf_bottoms = tuple(
            spec.cabinet_top_height + spec.shelf_pitch * index
            for index in range(1, spec.shelf_count + 1)
        )
        crown_bottom = spec.height_under_beam - spec.crown_height
        divider_segments: list[DividerLayout] = []
        wide_bays = bays[:2]
        for bay_index, bay in enumerate(wide_bays):
            for row in range(spec.shelf_count + 1):
                bottom_z = (
                    spec.cabinet_top_height
                    if row == 0
                    else shelf_bottoms[row - 1] + spec.shelf_thickness
                )
                top_z = shelf_bottoms[row] if row < spec.shelf_count else crown_bottom
                alternate = (row + bay_index) % 2
                ratio = (
                    spec.masonry_offset_ratio if alternate == 0 else 1 - spec.masonry_offset_ratio
                )
                divider_segments.append(
                    DividerLayout(
                        name=f"divider_{bay.name}_row_{row + 1:02d}",
                        row=row,
                        center_x=bay.fitted_left_x + bay.fitted_width * ratio,
                        bottom_z=bottom_z,
                        height=top_z - bottom_z,
                    )
                )

        face_frame_height = spec.cabinet_top_height - spec.counter_thickness - spec.plinth_height
        door_bottom = spec.plinth_height + spec.face_frame_width + spec.door_gap
        door_height = face_frame_height - 2 * spec.face_frame_width - 2 * spec.door_gap
        doors: list[DoorLayout] = []
        for bay in bays:
            if bay.door_count == 1:
                aperture_width = bay.fitted_width - 2 * spec.face_frame_width
                door_width = aperture_width - 2 * spec.door_gap
                center_x = bay.center_x
                doors.append(
                    DoorLayout(
                        name=f"door_{bay.name}",
                        bay_name=bay.name,
                        width=door_width,
                        center_x=center_x,
                        knob_x=center_x - door_width / 2 + spec.knob_edge_inset,
                        hinge_side="right",
                    )
                )
                continue

            aperture_width = (bay.fitted_width - 3 * spec.face_frame_width) / 2
            door_width = aperture_width - 2 * spec.door_gap
            left_center = bay.fitted_left_x + spec.face_frame_width + aperture_width / 2
            right_center = bay.fitted_right_x - spec.face_frame_width - aperture_width / 2
            doors.extend(
                (
                    DoorLayout(
                        name=f"door_{bay.name}_left",
                        bay_name=bay.name,
                        width=door_width,
                        center_x=left_center,
                        knob_x=left_center + door_width / 2 - spec.knob_edge_inset,
                        hinge_side="left",
                    ),
                    DoorLayout(
                        name=f"door_{bay.name}_right",
                        bay_name=bay.name,
                        width=door_width,
                        center_x=right_center,
                        knob_x=right_center - door_width / 2 + spec.knob_edge_inset,
                        hinge_side="right",
                    ),
                )
            )

        slope_start_top = spec.height_under_beam + spec.right_slope_start_above_beam
        slope_end_top = spec.right_slope_end_height
        slope_run = spec.right_opening_width - spec.right_slope_start_x
        crossing_fraction = (slope_start_top - spec.height_under_beam) / (
            slope_start_top - slope_end_top
        )
        slope_crossing_x = spec.right_slope_start_x + slope_run * crossing_fraction
        right_bay = bays[2]
        right_fitted_end_offset = right_bay.fitted_right_x - right_bay.left_x
        right_crown_base = spec.right_slope_height_at(right_fitted_end_offset) - spec.crown_height

        return cls(
            furniture_width=total_width,
            bays=tuple(bays),
            posts=tuple(posts),
            shelf_bottoms=shelf_bottoms,
            divider_segments=tuple(divider_segments),
            doors=tuple(doors),
            carcass_depth=spec.lower_depth - spec.face_frame_thickness,
            carcass_bottom_z=spec.plinth_height,
            carcass_height=face_frame_height,
            face_frame_height=face_frame_height,
            door_bottom_z=door_bottom,
            door_height=door_height,
            crown_bottom_z=crown_bottom,
            right_crown_base_z=right_crown_base,
            right_slope_crossing_x=slope_crossing_x,
        )

    def bay(self, name: str) -> BayLayout:
        return next(bay for bay in self.bays if bay.name == name)

    def doors_for_bay(self, name: str) -> tuple[DoorLayout, ...]:
        return tuple(door for door in self.doors if door.bay_name == name)

    def cabinet_bridge_width(self, post_name: str) -> float:
        """Return the full fitted-cabinet gap spanning an internal site post."""

        post_index = next(index for index, post in enumerate(self.posts) if post.name == post_name)
        return self.bays[post_index + 1].fitted_left_x - self.bays[post_index].fitted_right_x
