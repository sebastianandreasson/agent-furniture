"""Orchestration and public identifiers for the complete base-cabinet run."""

from __future__ import annotations

from querycad.furniture import PartCatalog
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.base_carcasses import (
    add_base_carcasses,
    add_post_carcass_bridges,
)
from querycad.models.built_in_bookshelf.subassemblies.base_parts import (
    BASE_BOTTOMS,
    BASE_DIVIDER,
    BASE_VERTICAL,
    COUNTERS,
    DOOR_KNOB,
    DOORS,
    FACE_FRAME_CENTER_STILE,
    FACE_FRAME_RAILS,
    FACE_FRAME_STILE,
    PLINTH_FRONTS,
    POST_COUNTER_BRIDGES,
    POST_FIXED_PANELS,
    POST_PLINTH_BRIDGES,
)
from querycad.models.built_in_bookshelf.subassemblies.cabinet_fronts import (
    add_cabinet_fronts,
    add_fixed_post_panel,
)

__all__ = [
    "BASE_BOTTOMS",
    "BASE_DIVIDER",
    "BASE_VERTICAL",
    "COUNTERS",
    "DOORS",
    "DOOR_KNOB",
    "FACE_FRAME_CENTER_STILE",
    "FACE_FRAME_RAILS",
    "FACE_FRAME_STILE",
    "PLINTH_FRONTS",
    "POST_COUNTER_BRIDGES",
    "POST_FIXED_PANELS",
    "POST_PLINTH_BRIDGES",
    "add_base_cabinets",
]


def add_base_cabinets(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    """Add cases and continue them across each existing post."""

    add_base_carcasses(catalog, spec, layout)
    for post in layout.posts:
        add_post_carcass_bridges(catalog, spec, layout, post.name)
        add_fixed_post_panel(catalog, spec, layout, post.name)
    add_cabinet_fronts(catalog, spec, layout)
