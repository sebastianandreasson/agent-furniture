"""Part-catalog orchestration for the built-in bookshelf subassemblies."""

from __future__ import annotations

from querycad.furniture import PartCatalog
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.base_cabinets import (
    BASE_BOTTOMS,
    BASE_DIVIDER,
    BASE_VERTICAL,
    DOOR_KNOB,
    DOORS,
    FACE_FRAME_CENTER_STILE,
    FACE_FRAME_STILE,
    POST_FIXED_PANELS,
    add_base_cabinets,
)
from querycad.models.built_in_bookshelf.subassemblies.core_uprights import (
    CORE_UPRIGHT_LEFT,
    CORE_UPRIGHT_RIGHT,
    CORE_UPRIGHT_RIGHT_SCRIBED,
    add_core_uprights,
)
from querycad.models.built_in_bookshelf.subassemblies.crown import CROWNS, add_crown
from querycad.models.built_in_bookshelf.subassemblies.post_displays import (
    POST_CLADDINGS,
    POST_DISPLAY_LEDGES,
    POST_DISPLAY_LIPS,
    add_post_displays,
)
from querycad.models.built_in_bookshelf.subassemblies.upper_bookcase import (
    DIVIDER_LOWER,
    DIVIDER_MIDDLE,
    DIVIDER_TOP,
    SHELVES,
    add_upper_bookcase,
)

__all__ = [
    "BASE_BOTTOMS",
    "BASE_DIVIDER",
    "BASE_VERTICAL",
    "CORE_UPRIGHT_LEFT",
    "CORE_UPRIGHT_RIGHT",
    "CORE_UPRIGHT_RIGHT_SCRIBED",
    "CROWNS",
    "DIVIDER_LOWER",
    "DIVIDER_MIDDLE",
    "DIVIDER_TOP",
    "DOOR_KNOB",
    "DOORS",
    "FACE_FRAME_CENTER_STILE",
    "FACE_FRAME_STILE",
    "POST_CLADDINGS",
    "POST_DISPLAY_LEDGES",
    "POST_DISPLAY_LIPS",
    "POST_FIXED_PANELS",
    "SHELVES",
    "build_part_catalog",
]


def build_part_catalog(
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> PartCatalog:
    """Build the five physical construction modules into one stable part catalog."""

    catalog = PartCatalog()
    add_core_uprights(catalog, spec, layout)
    add_base_cabinets(catalog, spec, layout)
    add_upper_bookcase(catalog, spec, layout)
    add_post_displays(catalog, spec, layout)
    add_crown(catalog, spec, layout)
    return catalog
