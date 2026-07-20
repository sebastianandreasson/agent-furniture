"""Load and validate text-based furniture design specifications."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from querycad.furniture import Design
from querycad.registry import build_model


def load_design(path: Path) -> Design:
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ValueError("design configuration must be a JSON object")

    required = {"name", "model", "parameters"}
    allowed = required | {"family", "variant", "variant_label"}
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ValueError(f"unknown top-level field(s): {', '.join(unknown)}")

    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"missing top-level field(s): {', '.join(missing)}")

    name = raw["name"]
    model = raw["model"]
    parameters = raw["parameters"]
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("model must be a non-empty string")
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be a JSON object")

    family = raw.get("family", name)
    variant = raw.get("variant", "default")
    variant_label = raw.get("variant_label", "Default")
    for field_name, value in (
        ("family", family),
        ("variant", variant),
        ("variant_label", variant_label),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string")

    design = build_model(model, name, parameters)
    design = replace(
        design,
        family=family,
        variant=variant,
        variant_label=variant_label,
    )
    design.validate()
    return design
