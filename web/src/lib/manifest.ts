import type {
  CatalogDesign,
  ColorTuple,
  FurnitureManifest,
  ManifestPart,
  Vector3Tuple,
} from '../types'

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function parseColor(value: unknown): ColorTuple {
  if (
    !Array.isArray(value) ||
    value.length !== 4 ||
    !value.every(isFiniteNumber)
  ) {
    throw new Error('A manifest part has an invalid CAD color.')
  }
  return value as ColorTuple
}

function parsePart(value: unknown): ManifestPart {
  if (
    !isRecord(value) ||
    typeof value.part_number !== 'string' ||
    typeof value.description !== 'string' ||
    typeof value.material !== 'string' ||
    !isFiniteNumber(value.quantity) ||
    !Number.isInteger(value.quantity) ||
    value.quantity < 1 ||
    !isFiniteNumber(value.size_x_mm) ||
    !isFiniteNumber(value.size_y_mm) ||
    !isFiniteNumber(value.size_z_mm) ||
    !isFiniteNumber(value.unit_volume_mm3) ||
    !Array.isArray(value.placements) ||
    !value.placements.every(
      (placement) => isRecord(placement) && typeof placement.name === 'string',
    )
  ) {
    throw new Error('The build manifest contains an invalid part entry.')
  }

  const placementNames = value.placements.map((placement) =>
    String((placement as Record<string, unknown>).name),
  )
  if (
    placementNames.length !== value.quantity ||
    new Set(placementNames).size !== placementNames.length
  ) {
    throw new Error('A manifest part has an invalid placement inventory.')
  }

  return {
    partNumber: value.part_number,
    description: value.description,
    material: value.material,
    quantity: value.quantity,
    sizeMm: [value.size_x_mm, value.size_y_mm, value.size_z_mm] as Vector3Tuple,
    unitVolumeMm3: value.unit_volume_mm3,
    colorRgba: parseColor(value.color_rgba),
    placementNames,
  }
}

export function parseManifest(value: unknown): FurnitureManifest {
  if (
    !isRecord(value) ||
    value.schema_version !== 1 ||
    value.units !== 'mm' ||
    typeof value.name !== 'string' ||
    typeof value.model !== 'string' ||
    !isFiniteNumber(value.part_occurrences) ||
    !Number.isInteger(value.part_occurrences) ||
    !Array.isArray(value.parts)
  ) {
    throw new Error(
      'Unsupported build manifest. Rebuild the furniture exports with QueryCAD.',
    )
  }

  const parts = value.parts.map(parsePart)
  const countedOccurrences = parts.reduce(
    (total, part) => total + part.quantity,
    0,
  )
  if (countedOccurrences !== value.part_occurrences) {
    throw new Error(
      'The build manifest part count does not match its inventory.',
    )
  }

  return {
    schemaVersion: 1,
    name: value.name,
    model: value.model,
    units: 'mm',
    partOccurrences: value.part_occurrences,
    parts,
  }
}

export async function loadManifest(
  design: CatalogDesign,
  signal?: AbortSignal,
): Promise<FurnitureManifest> {
  const separator = design.artifacts.manifest.includes('?') ? '&' : '?'
  const url = `${design.artifacts.manifest}${separator}revision=${design.revision}`
  const response = await fetch(url, { cache: 'no-store', signal })
  if (!response.ok) {
    throw new Error(
      `Build manifest unavailable (${response.status}). Rebuild ${design.name}.`,
    )
  }
  return parseManifest(await response.json())
}
