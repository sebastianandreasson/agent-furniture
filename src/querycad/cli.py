"""Command-line control surface for agents and humans."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from querycad.config import load_design
from querycad.core import Design
from querycad.export import DEFAULT_FORMATS, SUPPORTED_FORMATS, export_design
from querycad.registry import MODELS


def _summary(design: Design) -> dict[str, object]:
    # Kept local to avoid a presentation dependency in the domain layer.
    return {
        "name": design.name,
        "model": design.model,
        "overall_size_mm": list(design.overall_size_mm()),
        "unique_parts": len(design.parts),
        "part_occurrences": design.total_occurrences(),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="querycad",
        description="Validate and export parametric furniture designs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="list registered furniture model families")

    validate = subparsers.add_parser("validate", help="validate a JSON design without exporting")
    validate.add_argument("design", type=Path)

    build = subparsers.add_parser("build", help="validate and export a JSON design")
    build.add_argument("design", type=Path)
    build.add_argument(
        "--formats",
        default=",".join(DEFAULT_FORMATS),
        help=f"comma-separated formats (available: {', '.join(sorted(SUPPORTED_FORMATS))})",
    )
    build.add_argument("--output", type=Path, help="output directory (default: build/<design>)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "list":
            for name, definition in sorted(MODELS.items()):
                print(f"{name}: {definition.description}")
            return 0

        design = load_design(args.design)
        if args.command == "validate":
            print(json.dumps(_summary(design), indent=2))
            return 0

        output = args.output or Path("build") / args.design.stem
        formats = tuple(item.strip() for item in args.formats.split(",") if item.strip())
        artifacts = export_design(design, output, formats)
        result = {**_summary(design), "artifacts": [str(path) for path in artifacts]}
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
