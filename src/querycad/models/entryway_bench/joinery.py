"""Assembly-sequenced joinery schedule for the entryway bench."""

from __future__ import annotations

from querycad.furniture import JoineryPlan, JoinerySchedule, PartCatalog
from querycad.models.entryway_bench.joinery_operations import (
    BenchFasteners,
    add_frame_connections,
    add_shelf_connections,
    add_storage_connections,
    add_top_connections,
    add_transfer_pilots,
)
from querycad.models.entryway_bench.layout import BenchLayout
from querycad.models.entryway_bench.spec import EntrywayBenchSpec


def _qualification_notes(spec: EntrywayBenchSpec) -> tuple[str, ...]:
    if spec.extension_mode == "none":
        return (
            "Indoor four-leg prototype without an extension; no design loads have been certified.",
            "Confirm material grades, moisture, edge distances, pilots, and jig settings on "
            "full-scale offcuts before fabrication.",
            "Pocket-hole locations are jig marks; slat clearance holes are cut CAD.",
        )
    return (
        "Indoor six-leg prototype with a plywood seat deck; no design loads have been certified.",
        "The extension module transfers seat load through the flush apron joint. Load-test "
        "the selected storage module and its junction before use.",
        "Confirm material grades, connector system, moisture, edge distances, pilots, and jig "
        "settings on full-scale offcuts before fabrication.",
        "Pocket and connector locations are jig marks; slat clearance holes are cut CAD.",
    )


def build_joinery_schedule(
    spec: EntrywayBenchSpec,
    layout: BenchLayout,
    catalog: PartCatalog,
) -> JoinerySchedule:
    """Build a count-safe schedule from the same part catalog used for geometry."""

    hardware = BenchFasteners.from_spec(spec)
    plan = JoineryPlan(
        catalog.quantity,
        status="prototype_not_structurally_certified",
        notes=_qualification_notes(spec),
    ).add_fasteners(hardware.frame, hardware.top, hardware.slat)
    if spec.extension_mode != "none":
        plan.add_fasteners(hardware.connector, hardware.dowel)

    add_frame_connections(plan, spec, layout, hardware)
    add_top_connections(plan, spec, layout, hardware)
    add_shelf_connections(plan, spec, layout, hardware)
    add_transfer_pilots(plan, spec, layout, hardware)
    add_storage_connections(plan, spec, layout, hardware)
    return plan.build()
