"""Parametric three-bay built-in bookshelf for an existing beam wall."""

from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.model import build_built_in_bookshelf
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec

__all__ = ["BuiltInBookshelfSpec", "BuiltInLayout", "build_built_in_bookshelf"]
