import type { BuildCatalog, CatalogDesign } from '../types'
import { field, isRecord } from './contract'

export const CATALOG_URL = '/catalog.json'

function isDesign(value: unknown): value is CatalogDesign {
  if (
    !isRecord(value) ||
    !isRecord(value.artifacts) ||
    !isRecord(value.overallSizeMm)
  ) {
    return false
  }
  const artifacts = value.artifacts
  const overallSizeMm = value.overallSizeMm
  return (
    ['id', 'name', 'model', 'revision'].every((name) =>
      field.string(value[name]),
    ) &&
    ['familyId', 'variantId', 'variantLabel'].every((name) =>
      field.nonEmptyString(value[name]),
    ) &&
    field.string(artifacts.glb) &&
    field.string(artifacts.manifest) &&
    field.nonnegativeInteger(value.partOccurrences) &&
    ['x', 'y', 'z'].every((axis) => field.finite(overallSizeMm[axis]))
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
  const identities = new Set<string>()
  const designIds = new Set<string>()
  for (const design of value.designs) {
    const identity = `${design.familyId}\u0000${design.variantId}`
    if (identities.has(identity) || designIds.has(design.id)) {
      throw new Error(
        'The build catalog contains duplicate furniture variants.',
      )
    }
    identities.add(identity)
    designIds.add(design.id)
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
