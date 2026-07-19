# QueryCAD domain context

QueryCAD is a code-first furniture-design system. Python is the source of parametric geometry and
fabrication metadata; generated files are disposable projections for CAD tools and the web studio.

## Glossary

### Furniture family

A registered kind of furniture with one parameter schema and one build function. Examples are the
entryway bench and apron table.

### Design specification

The frozen, user-facing parameter object for a furniture family. It owns defaults, input mapping,
and actionable validation of impossible combinations. JSON values are optional variant overrides.

### Derived layout

Immutable geometry-free calculations resolved from a design specification: spans, centres, offsets,
angles, and other dimensions shared by multiple subassemblies. It prevents the same spatial formula
from being reimplemented in parts and joinery.

### Part definition

One stable physical part type: part number, description, material, local-coordinate solid, nominal
stock envelope, and display colour.

### Part occurrence

One named placement of a part definition in a furniture design. Repeated occurrences share a part
number so export filenames and bill-of-material quantities remain stable.

### Part catalog

The furniture-authoring collection that defines each part once, accepts occurrences from multiple
subassemblies, and freezes into validated design parts. It is the seam between modular construction
code and the immutable design aggregate.

### Subassembly

A coherent portion of a furniture family that contributes part definitions or occurrences to a part
catalog. A subassembly is an authoring concept, not a separately transformed browser object.

### Joinery schedule

The immutable collection of fasteners, drill operations, connection groups, assumptions, and
qualification status for a design. It owns cross-reference and hardware-count validation.

### Drill operation

A repeatable machining instruction on every occurrence of one part definition. Hole centres use
local cut-stock coordinates from the minimum X/Y/Z corner.

### Design aggregate

The immutable resolved furniture result containing parts, parameters, and a joinery schedule. It is
the single input to validation, CAD assembly, and artifact export.

### Artifact contract

The generated manifest and catalog schemas consumed by downstream tools and the web studio. STEP,
GLB, STL, SVG, and CSV files are referenced by this contract and are never hand-maintained sources.

### Materials document

The web presentation derived from an artifact contract: material roll-up, part schematics, hardware,
drill coordinates, connection sequence, and an interactive assembly preview.

### Interference audit

An exact placed-solid check on a design aggregate. It reports positive shared volume between part
occurrences while allowing zero-volume construction contacts such as one panel resting on another.
It is a regression gate for accidental clipping; it does not replace joinery, tolerance, clearance,
or structural review.

## Invariants

- Units are millimetres.
- CadQuery authoring is X length, Y depth, Z height, with the floor at Z=0.
- Parts are modeled in local coordinates; only occurrences carry assembly placement.
- Part numbers and occurrence names are stable public identifiers.
- Repeated parts with identical stock and machining share one part definition.
- Artifact consumers never import or recreate individual furniture-family geometry.
- A valid solid or successful export does not imply structural or fabrication certification.
