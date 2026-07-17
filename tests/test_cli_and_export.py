from __future__ import annotations

import json
from pathlib import Path

from querycad.cli import main
from querycad.config import load_design
from querycad.export import export_design, write_catalog

DESIGN = Path("designs/dining-table.json")


def test_load_example_design() -> None:
    design = load_design(DESIGN)

    assert design.name == "dining-table"
    assert design.model == "apron_table"
    assert design.overall_size_mm() == (1600.0, 800.0, 750.0)


def test_validate_cli(capsys: object) -> None:
    assert main(["validate", str(DESIGN)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["part_occurrences"] == 9


def test_export_bom_svg_and_stl(tmp_path: Path) -> None:
    design = load_design(DESIGN)

    artifacts = export_design(design, tmp_path, ("bom", "svg", "stl"))
    relative = {path.relative_to(tmp_path).as_posix() for path in artifacts}

    assert "bom.csv" in relative
    assert "dining-table.svg" in relative
    assert "dining-table.stl" in relative
    assert "parts/top-001.stl" in relative
    assert "manifest.json" in relative
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["overall_size_mm"] == {"x": 1600.0, "y": 800.0, "z": 750.0}
    assert manifest["part_occurrences"] == 9


def test_catalog_indexes_a_complete_glb_build(tmp_path: Path) -> None:
    design = load_design(DESIGN)
    build_dir = tmp_path / "dining-table"
    export_design(design, build_dir, ("glb", "step", "bom"))

    catalog_path = write_catalog(tmp_path)
    catalog = json.loads(catalog_path.read_text())

    assert catalog["schemaVersion"] == 1
    assert catalog["units"] == "mm"
    assert len(catalog["designs"]) == 1
    entry = catalog["designs"][0]
    assert entry["id"] == "dining-table"
    assert entry["overallSizeMm"] == {"x": 1600.0, "y": 800.0, "z": 750.0}
    assert entry["artifacts"]["glb"] == "/dining-table/dining-table.glb"
    assert len(entry["revision"]) == 16
