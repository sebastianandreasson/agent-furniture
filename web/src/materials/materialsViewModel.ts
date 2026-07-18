import type {
  FurnitureManifest,
  ManifestDrillOperation,
  ManifestFastener,
  ManifestJoint,
  ManifestPart,
} from '../types'
import {
  groupDrillOperationsByPart,
  sortParts,
  summarizeMaterials,
  type MaterialSummary,
} from './inventory'

export type MaterialGroup = MaterialSummary & {
  parts: ManifestPart[]
}

export type StepFastener = {
  fastener: ManifestFastener | null
  code: string
  quantity: number
}

export type AssemblyStep = {
  number: number
  position: number
  title: string
  joints: ManifestJoint[]
  partNumbers: string[]
  parts: ManifestPart[]
  fasteners: StepFastener[]
  drillOperations: ManifestDrillOperation[]
  notes: string[]
  drillSummary: string
  instruction: string
  previewContext: PreviewContext
}

export type PreviewContext = {
  eyebrow: string
  title: string
  detail: string
}

export type MaterialsHardware = {
  fasteners: ManifestFastener[]
  totalFasteners: number
  status: string
  notes: string[]
}

export type MaterialsViewModel = {
  partOccurrences: number
  parts: ManifestPart[]
  materialGroups: MaterialGroup[]
  drillOperationsByPart: Map<string, ManifestDrillOperation[]>
  assemblySteps: AssemblyStep[]
  totalSolidVolumeMm3: number
  hardware: MaterialsHardware
}

function unique<T>(values: T[]) {
  return [...new Set(values)]
}

function summarizeDrilling(operations: ManifestDrillOperation[]) {
  if (operations.length === 0) return 'No drilling marks'
  const holes = operations.reduce(
    (total, operation) => total + operation.totalHoles,
    0,
  )
  return `${operations.length} drill setup${operations.length === 1 ? '' : 's'} · ${holes} holes`
}

function assemblyInstruction(
  notes: string[],
  operations: ManifestDrillOperation[],
) {
  if (notes.length > 0) return notes.join(' ')
  const operationNote = operations.find((operation) => operation.notes)?.notes
  return (
    operationNote ??
    'Dry-fit the connection, confirm the marked face, and test the setup on matching offcuts.'
  )
}

export function partPreviewContext(part: ManifestPart): PreviewContext {
  return {
    eyebrow: part.partNumber,
    title: part.description,
    detail: `Highlighting ${part.quantity} occurrence${part.quantity === 1 ? '' : 's'}`,
  }
}

function buildAssemblySteps(manifest: FurnitureManifest) {
  const partByNumber = new Map(
    manifest.parts.map((part) => [part.partNumber, part]),
  )
  const fastenerByCode = new Map(
    manifest.joinery.fasteners.map((fastener) => [fastener.code, fastener]),
  )
  const operationById = new Map(
    manifest.joinery.drillOperations.map((operation) => [
      operation.operationId,
      operation,
    ]),
  )
  const grouped = new Map<number, ManifestJoint[]>()

  for (const joint of manifest.joinery.joints) {
    const current = grouped.get(joint.assemblyStep) ?? []
    current.push(joint)
    grouped.set(joint.assemblyStep, current)
  }

  return [...grouped.entries()]
    .sort(([left], [right]) => left - right)
    .map(([number, joints], index): AssemblyStep => {
      const partNumbers = unique(
        joints.flatMap((joint) => [
          joint.sourcePartNumber,
          joint.targetPartNumber,
        ]),
      )
      const quantities = new Map<string, number>()
      for (const joint of joints) {
        quantities.set(
          joint.fastenerCode,
          (quantities.get(joint.fastenerCode) ?? 0) + joint.quantity,
        )
      }
      const drillOperations = unique(
        joints.flatMap((joint) => joint.drillOperationIds),
      )
        .map((operationId) => operationById.get(operationId))
        .filter((operation): operation is ManifestDrillOperation => !!operation)

      const title =
        joints.length === 1
          ? joints[0].description
          : `${joints[0].description} + ${joints.length - 1} more connection${joints.length === 2 ? '' : 's'}`
      const parts = partNumbers
        .map((partNumber) => partByNumber.get(partNumber))
        .filter((part): part is ManifestPart => !!part)
      const notes = unique(joints.map((joint) => joint.notes).filter(Boolean))

      return {
        number,
        position: index + 1,
        title,
        joints,
        partNumbers,
        parts,
        fasteners: [...quantities.entries()].map(([code, quantity]) => ({
          code,
          quantity,
          fastener: fastenerByCode.get(code) ?? null,
        })),
        drillOperations,
        notes,
        drillSummary: summarizeDrilling(drillOperations),
        instruction: assemblyInstruction(notes, drillOperations),
        previewContext: {
          eyebrow: `Assembly step ${String(number).padStart(2, '0')}`,
          title,
          detail: `${parts.length} part types · ${joints.length} connection groups`,
        },
      }
    })
}

export function buildMaterialsViewModel(
  manifest: FurnitureManifest,
): MaterialsViewModel {
  const parts = sortParts(manifest.parts)
  const summaries = summarizeMaterials(parts)
  const partsByMaterial = new Map<string, ManifestPart[]>()

  for (const part of parts) {
    const current = partsByMaterial.get(part.material) ?? []
    current.push(part)
    partsByMaterial.set(part.material, current)
  }

  return {
    partOccurrences: manifest.partOccurrences,
    parts,
    materialGroups: summaries.map((summary) => ({
      ...summary,
      parts: partsByMaterial.get(summary.name) ?? [],
    })),
    drillOperationsByPart: groupDrillOperationsByPart(
      manifest.joinery.drillOperations,
    ),
    assemblySteps: buildAssemblySteps(manifest),
    totalSolidVolumeMm3: summaries.reduce(
      (total, material) => total + material.volumeMm3,
      0,
    ),
    hardware: {
      fasteners: manifest.joinery.fasteners,
      totalFasteners: manifest.joinery.fasteners.reduce(
        (total, fastener) => total + fastener.quantity,
        0,
      ),
      status: manifest.joinery.status,
      notes: manifest.joinery.notes,
    },
  }
}
