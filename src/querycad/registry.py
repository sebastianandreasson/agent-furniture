"""Explicit registry of furniture model families."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from querycad.core import Design
from querycad.models.apron_table import ApronTableSpec, build_apron_table

Builder = Callable[[str, dict[str, Any]], Design]


@dataclass(frozen=True)
class ModelDefinition:
    name: str
    description: str
    builder: Builder
    defaults: dict[str, Any]


MODELS: dict[str, ModelDefinition] = {
    "apron_table": ModelDefinition(
        name="apron_table",
        description="Four-leg rectangular table with a solid top and inset aprons",
        builder=build_apron_table,
        defaults=ApronTableSpec().as_dict(),
    )
}


def build_model(model: str, name: str, parameters: dict[str, Any]) -> Design:
    try:
        definition = MODELS[model]
    except KeyError as error:
        available = ", ".join(sorted(MODELS))
        raise ValueError(f"unknown model {model!r}; available models: {available}") from error
    return definition.builder(name, parameters)
