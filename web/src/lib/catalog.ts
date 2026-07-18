import type { BuildCatalog, CatalogDesign } from '../types'

export const CATALOG_URL = '/catalog.json'

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function isDesign(value: unknown): value is CatalogDesign {
  if (
    !isRecord(value) ||
    !isRecord(value.artifacts) ||
    !isRecord(value.overallSizeMm)
  ) {
    return false
  }
  return (
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    typeof value.model === 'string' &&
    typeof value.revision === 'string' &&
    typeof value.artifacts.glb === 'string' &&
    typeof value.artifacts.manifest === 'string' &&
    typeof value.partOccurrences === 'number' &&
    Number.isInteger(value.partOccurrences) &&
    value.partOccurrences >= 0 &&
    typeof value.overallSizeMm.x === 'number' &&
    typeof value.overallSizeMm.y === 'number' &&
    typeof value.overallSizeMm.z === 'number'
  )
}

export function parseCatalog(value: unknown): BuildCatalog {
  if (!isRecord(value) || value.schemaVersion !== 1 || value.units !== 'mm') {
    throw new Error(
      'Unsupported build catalog. Rebuild the furniture exports with QueryCAD.',
    )
  }
  if (!Array.isArray(value.designs) || !value.designs.every(isDesign)) {
    throw new Error('The build catalog contains an invalid furniture entry.')
  }
  return value as BuildCatalog
}

export function catalogSignature(catalog: BuildCatalog): string {
  return JSON.stringify(catalog)
}

export async function loadCatalog(signal?: AbortSignal): Promise<BuildCatalog> {
  const response = await fetch(`${CATALOG_URL}?refresh=${Date.now()}`, {
    cache: 'no-store',
    signal,
  })
  if (!response.ok) {
    throw new Error(
      `Furniture catalog unavailable (${response.status}). Run the QueryCAD build command first.`,
    )
  }
  return parseCatalog(await response.json())
}
