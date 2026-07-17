"""Convenience entry point for the live QueryCAD preview loop."""

import sys

from querycad.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["preview", *sys.argv[1:]]))
