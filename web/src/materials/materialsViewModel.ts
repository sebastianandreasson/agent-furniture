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
  title: string
  joints: ManifestJoint[]
  partNumbers: string[]
  parts: ManifestPart[]
  fasteners: StepFastener[]
  drillOperations: ManifestDrillOperation[]
  notes: string[]
}

export type MaterialsViewModel = {
  parts: ManifestPart[]
  materialGroups: MaterialGroup[]
  drillOperationsByPart: Map<string, ManifestDrillOperation[]>
  assemblySteps: AssemblyStep[]
  totalSolidVolumeMm3: number
  totalFasteners: number
}

function unique<T>(values: T[]) {
  return [...new Set(values)]
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
    .map(([number, joints]): AssemblyStep => {
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

      return {
        number,
        title:
          joints.length === 1
            ? joints[0].description
            : `${joints[0].description} + ${joints.length - 1} more connection${joints.length === 2 ? '' : 's'}`,
        joints,
        partNumbers,
        parts: partNumbers
          .map((partNumber) => partByNumber.get(partNumber))
          .filter((part): part is ManifestPart => !!part),
        fasteners: [...quantities.entries()].map(([code, quantity]) => ({
          code,
          quantity,
          fastener: fastenerByCode.get(code) ?? null,
        })),
        drillOperations,
        notes: unique(joints.map((joint) => joint.notes).filter(Boolean)),
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
    totalFasteners: manifest.joinery.fasteners.reduce(
      (total, fastener) => total + fastener.quantity,
      0,
    ),
  }
}
