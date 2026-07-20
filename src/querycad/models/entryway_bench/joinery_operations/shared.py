"""Shared fasteners and drill-operation factories for bench joinery."""

from __future__ import annotations

from dataclasses import dataclass

from querycad.furniture import DrillOperation, DrillPoint, FastenerSpec
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.spec import EntrywayBenchSpec

END_SETBACK = 18.0
POCKET_NOTE = (
    "Use a 9.5 mm stepped pocket-hole bit and 15° jig. Datum all dimensions from "
    "the cut-stock minimum corner; verify the jig setting on an offcut."
)
JUNCTION_NOTE = (
    "Dry-fit the extension against the flush main end rail. Use the dowels for alignment, "
    "then tighten the concealed connector bolt from the extension side. Transfer receiver "
    "holes in assembly; do not infer certified capacity from the CAD joint."
)


@dataclass(frozen=True)
class BenchFasteners:
    frame: FastenerSpec
    top: FastenerSpec
    slat: FastenerSpec
    connector: FastenerSpec
    dowel: FastenerSpec

    @classmethod
    def from_spec(cls, spec: EntrywayBenchSpec) -> BenchFasteners:
        frame_length = f"{spec.frame_pocket_screw_length:g}"
        top_length = f"{spec.top_pocket_screw_length:g}"
        slat_diameter = f"{spec.slat_screw_diameter:g}"
        slat_length = f"{spec.slat_screw_length:g}"
        connector_diameter = f"{spec.connector_bolt_diameter:g}"
        connector_length = f"{spec.connector_bolt_length:g}"
        dowel_diameter = f"{spec.alignment_dowel_diameter:g}"
        dowel_length = f"{spec.alignment_dowel_length:g}"
        return cls(
            frame=FastenerSpec(
                code=f"PH-{frame_length}-T20",
                description=f"{frame_length} mm fine-thread pocket-hole screw",
                length_mm=spec.frame_pocket_screw_length,
                nominal_size="hardwood pocket screw",
                head="washer head",
                drive="T20",
                thread="fine, self-tapping",
                finish="indoor zinc",
                application="Rail-to-leg frame joints",
                notes=(
                    "Prototype selection for 24 mm hardwood rails. Confirm collar setting, "
                    "withdrawal resistance, and breakthrough on an offcut."
                ),
            ),
            top=FastenerSpec(
                code=f"PH-{top_length}-T20",
                description=f"{top_length} mm fine-thread pocket-hole screw",
                length_mm=spec.top_pocket_screw_length,
                nominal_size="hardwood pocket screw",
                head="washer head",
                drive="T20",
                thread="fine, self-tapping",
                finish="indoor zinc",
                application="Rail-to-L-shaped seat deck attachment",
                notes=(
                    "Prototype selection for the 22 mm plywood deck. Verify point location and "
                    "no show-face breakthrough on scrap."
                ),
            ),
            slat=FastenerSpec(
                code=f"CSK-{slat_diameter}X{slat_length}-T20",
                description=f"{spec.slat_screw_diameter:.1f} × {slat_length} mm slat screw",
                length_mm=spec.slat_screw_length,
                nominal_size=f"{spec.slat_screw_diameter:.1f} mm",
                head="90° countersunk",
                drive="T20",
                thread="partial-thread wood screw",
                finish="indoor zinc",
                application="Shelf slats, shoe stop, and extension storage panels",
                notes=(
                    "The 3.0 mm pilot is a hardwood prototype assumption; confirm against the "
                    "selected screw root diameter and an offcut."
                ),
            ),
            connector=FastenerSpec(
                code=f"CB-M{connector_diameter}X{connector_length}",
                description=(
                    f"M{connector_diameter} × {connector_length} mm concealed connector bolt"
                ),
                length_mm=spec.connector_bolt_length,
                nominal_size=f"M{connector_diameter}",
                head="low-profile furniture connector",
                drive="hex or Torx to suit selected system",
                thread="machine thread into matched receiver",
                finish="indoor zinc",
                application="Demountable inner ends of extension rails",
                notes=(
                    "Select a matched bolt and cross-dowel or threaded receiver system, then "
                    "verify edge distances and tightening access in a full-scale joint sample."
                ),
            ),
            dowel=FastenerSpec(
                code=f"DOWEL-{dowel_diameter}X{dowel_length}",
                description=(
                    f"{dowel_diameter} × {dowel_length} mm fluted hardwood alignment dowel"
                ),
                length_mm=spec.alignment_dowel_length,
                nominal_size=f"{dowel_diameter} mm",
                head="none",
                drive="none",
                thread="none",
                finish="unfinished hardwood",
                application="Alignment of upper extension rails at the clean junction",
                notes=(
                    "Use dry at the demountable interface unless the final assembly is intended "
                    "to be permanent. Confirm fit and moisture movement on offcuts."
                ),
            ),
        )


def upward_pocket_holes(
    *,
    operation_id: str,
    part_number: str,
    label: str,
    length: float,
    count: int,
    rail_height: float,
    bit_diameter: float,
    angle_deg: float,
    fastener_code: str,
) -> DrillOperation:
    return DrillOperation(
        operation_id=operation_id,
        part_number=part_number,
        label=label,
        kind="pocket_hole",
        face="inside face",
        view_axes=("x", "z"),
        diameter_mm=bit_diameter,
        points=tuple(
            DrillPoint(
                (length * index / (count + 1), 0.0, rail_height - END_SETBACK),
                (0.0, 0.0, 1.0),
                f"deck attachment {index}",
            )
            for index in range(1, count + 1)
        ),
        angle_deg=angle_deg,
        fastener_code=fastener_code,
        counts_fastener=True,
        notes=POCKET_NOTE,
    )


def extension_end_x(
    layout: BenchLayout,
    length: float,
    *,
    inner: bool,
    setback: float,
) -> tuple[float, tuple[float, float, float], str]:
    use_minimum = (layout.extension_sign > 0) == inner
    label = "inner end" if inner else "outer end"
    if use_minimum:
        return setback, (-1.0, 0.0, 0.0), label
    return length - setback, (1.0, 0.0, 0.0), label


def one_end_pocket_holes(
    *,
    operation_id: str,
    part_number: str,
    label: str,
    length: float,
    levels: tuple[float, ...],
    layout: BenchLayout,
    bit_diameter: float,
    angle_deg: float,
    fastener_code: str,
) -> DrillOperation:
    position, axis, end_label = extension_end_x(layout, length, inner=False, setback=END_SETBACK)
    return DrillOperation(
        operation_id=operation_id,
        part_number=part_number,
        label=label,
        kind="pocket_hole",
        face="inside face",
        view_axes=("x", "z"),
        diameter_mm=bit_diameter,
        points=tuple(DrillPoint((position, 0.0, level), axis, end_label) for level in levels),
        angle_deg=angle_deg,
        fastener_code=fastener_code,
        counts_fastener=True,
        notes=POCKET_NOTE,
    )


def inner_end_holes(
    *,
    operation_id: str,
    part_number: str,
    label: str,
    length: float,
    rail_thickness: float,
    levels: tuple[float, ...],
    layout: BenchLayout,
    diameter: float,
    fastener_code: str,
    kind: str,
) -> DrillOperation:
    position, axis, end_label = extension_end_x(layout, length, inner=True, setback=0.0)
    return DrillOperation(
        operation_id=operation_id,
        part_number=part_number,
        label=label,
        kind=kind,
        face="inner end",
        view_axes=("y", "z"),
        diameter_mm=diameter,
        points=tuple(
            DrillPoint(
                (position, rail_thickness / 2, level),
                axis,
                f"{end_label} level {index}",
            )
            for index, level in enumerate(levels, start=1)
        ),
        depth_mm=None,
        fastener_code=fastener_code,
        counts_fastener=True,
        notes=JUNCTION_NOTE,
    )
