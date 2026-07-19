"""Public furniture-authoring interface for QueryCAD model families."""

from querycad.furniture.catalog import PartCatalog, PartHandle
from querycad.furniture.design import Color4, Design, Part, Placement, Vector3
from querycad.furniture.geometry import (
    centered_box,
    rounded_ring,
    soft_box,
    stock_box,
    top_countersunk_holes,
)
from querycad.furniture.joinery import (
    AxisName,
    DrillOperation,
    DrillPoint,
    ExternalTargetSpec,
    FastenerSpec,
    JoineryPlan,
    JoinerySchedule,
    JointSpec,
    rail_end_pocket_holes,
)
from querycad.furniture.layout import linear_centers
from querycad.furniture.specification import FurnitureSpec

__all__ = [
    "AxisName",
    "Color4",
    "Design",
    "DrillOperation",
    "DrillPoint",
    "ExternalTargetSpec",
    "FastenerSpec",
    "FurnitureSpec",
    "JoineryPlan",
    "JoinerySchedule",
    "JointSpec",
    "Part",
    "PartCatalog",
    "PartHandle",
    "Placement",
    "Vector3",
    "centered_box",
    "linear_centers",
    "rail_end_pocket_holes",
    "rounded_ring",
    "soft_box",
    "stock_box",
    "top_countersunk_holes",
]
