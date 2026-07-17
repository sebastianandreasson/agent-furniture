from __future__ import annotations

from pathlib import Path

import pytest

from querycad.preview import acquire_preview_lock, changed_files, watched_snapshot


def test_snapshot_detects_design_edits_and_new_python_files(tmp_path: Path) -> None:
    source_root = tmp_path / "src/querycad"
    source_root.mkdir(parents=True)
    model = source_root / "model.py"
    model.write_text("HEIGHT = 400\n")
    design = tmp_path / "design.json"
    design.write_text('{"height": 400}\n')
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\n")

    before = watched_snapshot(source_root, design, pyproject)
    design.write_text('{"height": 450, "thickness": 22}\n')
    new_model = source_root / "details.py"
    new_model.write_text("THICKNESS = 22\n")
    after = watched_snapshot(source_root, design, pyproject)

    assert set(changed_files(before, after)) == {design.resolve(), new_model.resolve()}


def test_snapshot_detects_deleted_files(tmp_path: Path) -> None:
    source_root = tmp_path / "src/querycad"
    source_root.mkdir(parents=True)
    model = source_root / "model.py"
    model.write_text("HEIGHT = 400\n")
    design = tmp_path / "design.json"
    design.write_text("{}\n")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\n")

    before = watched_snapshot(source_root, design, pyproject)
    model.unlink()
    after = watched_snapshot(source_root, design, pyproject)

    assert changed_files(before, after) == (model.resolve(),)


def test_preview_lock_prevents_duplicate_watchers(tmp_path: Path) -> None:
    design = tmp_path / "bench.json"
    first = acquire_preview_lock(tmp_path / "build", design)
    try:
        with pytest.raises(ValueError, match="another preview watcher is already running"):
            acquire_preview_lock(tmp_path / "build", design)
    finally:
        first.release()

    replacement = acquire_preview_lock(tmp_path / "build", design)
    replacement.release()
