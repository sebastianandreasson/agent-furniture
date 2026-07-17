"""Standard, scriptable exports for furniture designs."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections.abc import Iterable
from importlib.metadata import version
from pathlib import Path
from typing import Any

import cadquery as cq

from querycad import __version__
from querycad.core import Design

SUPPORTED_FORMATS = frozenset({"step", "glb", "stl", "svg", "bom"})
DEFAULT_FORMATS = ("step", "glb", "stl", "svg", "bom")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-.").lower()
    if not slug:
        raise ValueError("design name must contain at least one filename-safe character")
    return slug


def _bom_rows(design: Design) -> list[dict[str, Any]]:
    rows = []
    for part in design.parts:
        x, y, z = part.stock_size_mm
        rows.append(
            {
                "part_number": part.number,
                "description": part.description,
                "material": part.material,
                "quantity": part.quantity,
                "size_x_mm": round(x, 6),
                "size_y_mm": round(y, 6),
                "size_z_mm": round(z, 6),
                "unit_volume_mm3": round(part.volume_mm3, 3),
            }
        )
    return rows


def _write_bom(design: Design, path: Path) -> None:
    rows = _bom_rows(design)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _manifest(design: Design, artifacts: Iterable[Path], root: Path) -> dict[str, Any]:
    size = design.overall_size_mm()
    return {
        "schema_version": 1,
        "name": design.name,
        "model": design.model,
        "units": "mm",
        "generator": {"querycad": __version__, "cadquery": version("cadquery")},
        "parameters": design.parameters,
        "overall_size_mm": {"x": size[0], "y": size[1], "z": size[2]},
        "part_occurrences": design.total_occurrences(),
        "parts": [
            {**row, "placements": [item.as_dict() for item in part.placements]}
            for row, part in zip(_bom_rows(design), design.parts, strict=True)
        ],
        "artifacts": sorted(str(path.relative_to(root)) for path in artifacts),
    }


def _artifact_url(path: Path, build_root: Path) -> str:
    return f"/{path.relative_to(build_root).as_posix()}"


def _file_revision(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def write_catalog(build_root: Path) -> Path:
    """Index complete builds for the Vite viewer without duplicating model metadata."""
    build_root.mkdir(parents=True, exist_ok=True)
    designs: list[dict[str, Any]] = []
    for manifest_path in sorted(build_root.glob("*/manifest.json")):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        build_dir = manifest_path.parent
        glb_files = sorted(build_dir.glob("*.glb"))
        if not glb_files:
            continue
        glb_path = glb_files[0]
        artifacts: dict[str, str] = {
            "manifest": _artifact_url(manifest_path, build_root),
            "glb": _artifact_url(glb_path, build_root),
        }
        patterns = {
            "step": "*.step",
            "stl": "*.stl",
            "svg": "*.svg",
            "bom": "bom.csv",
        }
        for key, pattern in patterns.items():
            matches = sorted(build_dir.glob(pattern))
            if matches:
                artifacts[key] = _artifact_url(matches[0], build_root)

        designs.append(
            {
                "id": build_dir.name,
                "name": manifest["name"],
                "model": manifest["model"],
                "revision": _file_revision(glb_path),
                "overallSizeMm": manifest["overall_size_mm"],
                "partOccurrences": manifest["part_occurrences"],
                "parameters": manifest["parameters"],
                "artifacts": artifacts,
            }
        )

    catalog = {
        "schemaVersion": 1,
        "units": "mm",
        "designs": designs,
    }
    catalog_path = build_root / "catalog.json"
    catalog_path.write_text(
        json.dumps(catalog, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return catalog_path


def export_design(design: Design, output_dir: Path, formats: Iterable[str]) -> list[Path]:
    requested = tuple(dict.fromkeys(item.lower() for item in formats))
    unknown = sorted(set(requested) - SUPPORTED_FORMATS)
    if unknown:
        supported = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ValueError(f"unsupported format(s): {', '.join(unknown)}; choose from {supported}")
    if not requested:
        raise ValueError("at least one export format is required")

    design.validate_solids()
    output_dir.mkdir(parents=True, exist_ok=True)
    name = _slug(design.name)
    assembly = design.assembly()
    compound = assembly.toCompound()
    artifacts: list[Path] = []

    if "step" in requested:
        path = output_dir / f"{name}.step"
        assembly.export(str(path))
        artifacts.append(path)

    if "glb" in requested:
        path = output_dir / f"{name}.glb"
        assembly.export(str(path))
        artifacts.append(path)

    if "stl" in requested:
        path = output_dir / f"{name}.stl"
        cq.exporters.export(compound, str(path), tolerance=0.1, angularTolerance=0.1)
        artifacts.append(path)
        parts_dir = output_dir / "parts"
        parts_dir.mkdir(exist_ok=True)
        for part in design.parts:
            part_path = parts_dir / f"{part.number.lower()}.stl"
            cq.exporters.export(
                part.shape,
                str(part_path),
                tolerance=0.1,
                angularTolerance=0.1,
            )
            artifacts.append(part_path)

    if "svg" in requested:
        path = output_dir / f"{name}.svg"
        cq.exporters.export(
            compound,
            str(path),
            opt={
                "width": 1200,
                "height": 800,
                "marginLeft": 40,
                "marginTop": 40,
                "projectionDir": (1.0, -1.0, 1.0),
                "showAxes": False,
                "showHidden": False,
                "strokeWidth": 0.8,
            },
        )
        artifacts.append(path)

    if "bom" in requested:
        path = output_dir / "bom.csv"
        _write_bom(design, path)
        artifacts.append(path)

    manifest_path = output_dir / "manifest.json"
    manifest = _manifest(design, [*artifacts, manifest_path], output_dir)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    artifacts.append(manifest_path)
    return artifacts
