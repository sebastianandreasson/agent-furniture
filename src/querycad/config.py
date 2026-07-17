"""Load and validate text-based furniture design specifications."""

from __future__ import annotations

import json
from pathlib import Path

from querycad.core import Design
from querycad.registry import build_model


def load_design(path: Path) -> Design:
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ValueError("design configuration must be a JSON object")

    allowed = {"name", "model", "parameters"}
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ValueError(f"unknown top-level field(s): {', '.join(unknown)}")

    missing = sorted(allowed - set(raw))
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

    design = build_model(model, name, parameters)
    design.validate_solids()
    return design
