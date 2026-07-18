"""Validated fabrication metadata and reusable joinery authoring helpers."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from querycad.furniture.design import Part, Vector3

AxisName = Literal["x", "y", "z"]


@dataclass(frozen=True)
class FastenerSpec:
    """One fully specified hardware item used by a design."""

    code: str
    description: str
    length_mm: float
    nominal_size: str
    head: str
    drive: str
    thread: str
    finish: str
    application: str
    manufacturer: str = "project-specified"
    product_code: str = ""
    source_url: str = ""
    status: str = "prototype_assumption"
    notes: str = ""

    def as_dict(self, quantity: int) -> dict[str, Any]:
        return {
            "code": self.code,
            "description": self.description,
            "quantity": quantity,
            "length_mm": self.length_mm,
            "nominal_size": self.nominal_size,
            "head": self.head,
            "drive": self.drive,
            "thread": self.thread,
            "finish": self.finish,
            "application": self.application,
            "manufacturer": self.manufacturer,
            "product_code": self.product_code,
            "source_url": self.source_url,
            "status": self.status,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class DrillPoint:
    """A hole location in part-stock coordinates, measured from its minimum corner."""

    position_mm: Vector3
    axis: Vector3
    label: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "position_mm": list(self.position_mm),
            "axis": list(self.axis),
            "label": self.label,
        }


@dataclass(frozen=True)
class DrillOperation:
    """A repeatable drilling operation on every occurrence of a unique part."""

    operation_id: str
    part_number: str
    label: str
    kind: str
    face: str
    view_axes: tuple[AxisName, AxisName]
    diameter_mm: float
    points: tuple[DrillPoint, ...]
    depth_mm: float | None = None
    countersink_diameter_mm: float | None = None
    angle_deg: float | None = None
    fastener_code: str | None = None
    counts_fastener: bool = False
    geometry_mode: Literal["cut", "marked_only"] = "marked_only"
    notes: str = ""

    def as_dict(self, part_quantity: int) -> dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "part_number": self.part_number,
            "label": self.label,
            "kind": self.kind,
            "face": self.face,
            "view_axes": list(self.view_axes),
            "diameter_mm": self.diameter_mm,
            "depth_mm": self.depth_mm,
            "countersink_diameter_mm": self.countersink_diameter_mm,
            "angle_deg": self.angle_deg,
            "fastener_code": self.fastener_code,
            "counts_fastener": self.counts_fastener,
            "geometry_mode": self.geometry_mode,
            "points_per_part": len(self.points),
            "part_quantity": part_quantity,
            "total_holes": len(self.points) * part_quantity,
            "points": [point.as_dict() for point in self.points],
            "notes": self.notes,
        }


@dataclass(frozen=True)
class JointSpec:
    """An assembly connection tied to hardware and source-part drill marks."""

    joint_id: str
    description: str
    source_part_number: str
    target_part_number: str
    fastener_code: str
    quantity: int
    drill_operation_ids: tuple[str, ...]
    assembly_step: int
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "joint_id": self.joint_id,
            "description": self.description,
            "source_part_number": self.source_part_number,
            "target_part_number": self.target_part_number,
            "fastener_code": self.fastener_code,
            "quantity": self.quantity,
            "drill_operation_ids": list(self.drill_operation_ids),
            "assembly_step": self.assembly_step,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class JoinerySchedule:
    """Immutable, self-validating fabrication schedule for one design."""

    status: str = "unspecified"
    notes: tuple[str, ...] = ()
    fasteners: tuple[FastenerSpec, ...] = ()
    drill_operations: tuple[DrillOperation, ...] = ()
    joints: tuple[JointSpec, ...] = ()

    def hardware_quantities(self) -> dict[str, int]:
        quantities = {fastener.code: 0 for fastener in self.fasteners}
        for joint in self.joints:
            quantities[joint.fastener_code] += joint.quantity
        return quantities

    def validate(self, parts: Iterable[Part]) -> None:
        part_by_number = {part.number: part for part in parts}
        fastener_by_code: dict[str, FastenerSpec] = {}
        for fastener in self.fasteners:
            if not fastener.code.strip():
                raise ValueError("fastener code cannot be empty")
            if fastener.code in fastener_by_code:
                raise ValueError(f"duplicate fastener code: {fastener.code}")
            if fastener.length_mm <= 0:
                raise ValueError(f"fastener {fastener.code} must have a positive length")
            fastener_by_code[fastener.code] = fastener

        axes = {"x", "y", "z"}
        operation_by_id: dict[str, DrillOperation] = {}
        counted_hardware = {code: 0 for code in fastener_by_code}
        for operation in self.drill_operations:
            if operation.operation_id in operation_by_id:
                raise ValueError(f"duplicate drill operation: {operation.operation_id}")
            operation_by_id[operation.operation_id] = operation
            if operation.part_number not in part_by_number:
                raise ValueError(
                    f"drill operation {operation.operation_id} references unknown part "
                    f"{operation.part_number}"
                )
            if operation.diameter_mm <= 0:
                raise ValueError(
                    f"drill operation {operation.operation_id} must have a positive diameter"
                )
            if operation.depth_mm is not None and operation.depth_mm <= 0:
                raise ValueError(
                    f"drill operation {operation.operation_id} must have a positive depth"
                )
            if (
                operation.countersink_diameter_mm is not None
                and operation.countersink_diameter_mm <= operation.diameter_mm
            ):
                raise ValueError(
                    f"drill operation {operation.operation_id} has an invalid countersink"
                )
            if (
                len(operation.view_axes) != 2
                or any(axis not in axes for axis in operation.view_axes)
                or operation.view_axes[0] == operation.view_axes[1]
            ):
                raise ValueError(f"drill operation {operation.operation_id} has invalid view axes")
            if not operation.points:
                raise ValueError(f"drill operation {operation.operation_id} has no points")
            if operation.fastener_code is not None:
                if operation.fastener_code not in fastener_by_code:
                    raise ValueError(
                        f"drill operation {operation.operation_id} references unknown fastener "
                        f"{operation.fastener_code}"
                    )
            elif operation.counts_fastener:
                raise ValueError(
                    f"drill operation {operation.operation_id} counts hardware without a fastener"
                )

            part = part_by_number[operation.part_number]
            for point in operation.points:
                if not any(abs(component) > 1e-9 for component in point.axis):
                    raise ValueError(
                        f"drill operation {operation.operation_id} has a zero-length drill axis"
                    )
                for coordinate, limit, axis in zip(
                    point.position_mm,
                    part.stock_size_mm,
                    ("x", "y", "z"),
                    strict=True,
                ):
                    if coordinate < -1e-6 or coordinate > limit + 1e-6:
                        raise ValueError(
                            f"drill operation {operation.operation_id} point lies outside "
                            f"{part.number} on {axis}"
                        )
            if operation.counts_fastener and operation.fastener_code is not None:
                counted_hardware[operation.fastener_code] += len(operation.points) * part.quantity

        joint_ids: set[str] = set()
        joint_hardware = {code: 0 for code in fastener_by_code}
        for joint in self.joints:
            if joint.joint_id in joint_ids:
                raise ValueError(f"duplicate joint: {joint.joint_id}")
            joint_ids.add(joint.joint_id)
            if joint.source_part_number not in part_by_number:
                raise ValueError(f"joint {joint.joint_id} has an unknown source part")
            if joint.target_part_number not in part_by_number:
                raise ValueError(f"joint {joint.joint_id} has an unknown target part")
            if joint.fastener_code not in fastener_by_code:
                raise ValueError(f"joint {joint.joint_id} has an unknown fastener")
            if joint.quantity <= 0 or joint.assembly_step <= 0:
                raise ValueError(f"joint {joint.joint_id} must have positive quantity and step")
            for operation_id in joint.drill_operation_ids:
                operation = operation_by_id.get(operation_id)
                if operation is None:
                    raise ValueError(
                        f"joint {joint.joint_id} references unknown drill operation {operation_id}"
                    )
                if operation.part_number != joint.source_part_number:
                    raise ValueError(
                        f"joint {joint.joint_id} drill operation belongs to a different part"
                    )
                if operation.fastener_code != joint.fastener_code:
                    raise ValueError(
                        f"joint {joint.joint_id} drill operation uses a different fastener"
                    )
            joint_hardware[joint.fastener_code] += joint.quantity

        if counted_hardware != joint_hardware:
            raise ValueError(
                "drill-operation screw counts do not match the joint schedule: "
                f"drills={counted_hardware}, joints={joint_hardware}"
            )


class JoineryPlan:
    """Authoring helper that derives joint quantities from part occurrences."""

    def __init__(
        self,
        quantity_for_part: Callable[[str], int],
        *,
        status: str,
        notes: tuple[str, ...] = (),
    ) -> None:
        self._quantity_for_part = quantity_for_part
        self._status = status
        self._notes = notes
        self._fasteners: list[FastenerSpec] = []
        self._operations: list[DrillOperation] = []
        self._joints: list[JointSpec] = []

    def add_fasteners(self, *fasteners: FastenerSpec) -> JoineryPlan:
        self._fasteners.extend(fasteners)
        return self

    def add_operation(self, operation: DrillOperation) -> JoineryPlan:
        self._operations.append(operation)
        return self

    def add_joint(
        self,
        *,
        joint_id: str,
        description: str,
        source_part_number: str,
        target_part_number: str,
        fastener_code: str,
        quantity: int,
        drill_operation_ids: tuple[str, ...],
        assembly_step: int,
        notes: str = "",
    ) -> JoineryPlan:
        """Add an explicitly counted joint for mixed-target repeated parts."""

        self._joints.append(
            JointSpec(
                joint_id=joint_id,
                description=description,
                source_part_number=source_part_number,
                target_part_number=target_part_number,
                fastener_code=fastener_code,
                quantity=quantity,
                drill_operation_ids=drill_operation_ids,
                assembly_step=assembly_step,
                notes=notes,
            )
        )
        return self

    def add_connection(
        self,
        *,
        joint_id: str,
        description: str,
        target_part_number: str,
        operation: DrillOperation,
        assembly_step: int,
        notes: str = "",
    ) -> JoineryPlan:
        if not operation.counts_fastener or operation.fastener_code is None:
            raise ValueError("a connection operation must count a named fastener")
        self.add_operation(operation)
        self._joints.append(
            JointSpec(
                joint_id=joint_id,
                description=description,
                source_part_number=operation.part_number,
                target_part_number=target_part_number,
                fastener_code=operation.fastener_code,
                quantity=(len(operation.points) * self._quantity_for_part(operation.part_number)),
                drill_operation_ids=(operation.operation_id,),
                assembly_step=assembly_step,
                notes=notes,
            )
        )
        return self

    def build(self) -> JoinerySchedule:
        return JoinerySchedule(
            status=self._status,
            notes=self._notes,
            fasteners=tuple(self._fasteners),
            drill_operations=tuple(self._operations),
            joints=tuple(self._joints),
        )


def rail_end_pocket_holes(
    *,
    operation_id: str,
    part_number: str,
    label: str,
    run_axis: Literal["x", "y"],
    length: float,
    levels: tuple[float, ...],
    setback: float,
    face: str,
    bit_diameter: float,
    angle_deg: float,
    fastener_code: str,
    notes: str,
) -> DrillOperation:
    """Create jig marks for one or more pocket holes at both ends of a rail."""

    if run_axis == "x":
        endpoints = (
            (setback, (-1.0, 0.0, 0.0), "left end"),
            (length - setback, (1.0, 0.0, 0.0), "right end"),
        )
        points = tuple(
            DrillPoint((position, 0.0, level), axis, point_label)
            for position, axis, point_label in endpoints
            for level in levels
        )
        view_axes: tuple[AxisName, AxisName] = ("x", "z")
    else:
        endpoints = (
            (setback, (0.0, -1.0, 0.0), "front end"),
            (length - setback, (0.0, 1.0, 0.0), "back end"),
        )
        points = tuple(
            DrillPoint((0.0, position, level), axis, point_label)
            for position, axis, point_label in endpoints
            for level in levels
        )
        view_axes = ("y", "z")
    return DrillOperation(
        operation_id=operation_id,
        part_number=part_number,
        label=label,
        kind="pocket_hole",
        face=face,
        view_axes=view_axes,
        diameter_mm=bit_diameter,
        points=points,
        angle_deg=angle_deg,
        fastener_code=fastener_code,
        counts_fastener=True,
        notes=notes,
    )
