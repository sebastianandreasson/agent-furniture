import type { ColorTuple, ManifestDrillOperation, ManifestPart } from '../types'

export type MaterialSummary = {
  name: string
  colorRgba: ColorTuple
  occurrences: number
  partTypes: number
  volumeMm3: number
}

export function rgbaCss([red, green, blue, alpha]: ColorTuple) {
  const channel = (value: number) =>
    Math.round(Math.min(1, Math.max(0, value)) * 255)
  return `rgba(${channel(red)}, ${channel(green)}, ${channel(blue)}, ${Math.min(1, Math.max(0, alpha))})`
}

export function formatDimension(value: number) {
  return new Intl.NumberFormat('en', { maximumFractionDigits: 1 }).format(value)
}

export function formatVolume(volumeMm3: number) {
  const litres = volumeMm3 / 1_000_000
  if (litres >= 0.1) return `${litres.toFixed(litres >= 10 ? 1 : 2)} L`
  return `${Math.round(volumeMm3 / 1_000)} cm³`
}

export function summarizeMaterials(parts: ManifestPart[]): MaterialSummary[] {
  const groups = new Map<string, MaterialSummary>()
  for (const part of parts) {
    const current = groups.get(part.material) ?? {
      name: part.material,
      colorRgba: part.colorRgba,
      occurrences: 0,
      partTypes: 0,
      volumeMm3: 0,
    }
    current.occurrences += part.quantity
    current.partTypes += 1
    current.volumeMm3 += part.unitVolumeMm3 * part.quantity
    groups.set(part.material, current)
  }
  return [...groups.values()].sort((left, right) =>
    left.name.localeCompare(right.name),
  )
}

export function sortParts(parts: ManifestPart[]) {
  return [...parts].sort(
    (left, right) =>
      left.material.localeCompare(right.material) ||
      left.partNumber.localeCompare(right.partNumber),
  )
}

export function groupDrillOperationsByPart(
  operations: ManifestDrillOperation[],
) {
  const grouped = new Map<string, ManifestDrillOperation[]>()
  for (const operation of operations) {
    const current = grouped.get(operation.partNumber) ?? []
    current.push(operation)
    grouped.set(operation.partNumber, current)
  }
  return grouped
}
