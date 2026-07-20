import type {
  AxisName,
  CatalogDesign,
  ColorTuple,
  FurnitureManifest,
  ManifestDrillOperation,
  ManifestExternalTarget,
  ManifestFastener,
  ManifestJoinery,
  ManifestJoint,
  ManifestPart,
  Vector3Tuple,
} from '../types'
import { expectFields, field, isRecord } from './contract'

function parseColor(value: unknown): ColorTuple {
  if (
    !Array.isArray(value) ||
    value.length !== 4 ||
    !value.every(field.finite)
  ) {
    throw new Error('A manifest part has an invalid CAD color.')
  }
  return value as ColorTuple
}

function parseVector(value: unknown, message: string): Vector3Tuple {
  if (
    !Array.isArray(value) ||
    value.length !== 3 ||
    !value.every(field.finite)
  ) {
    throw new Error(message)
  }
  return value as Vector3Tuple
}

function nullableNumber(value: unknown, message: string): number | null {
  if (value === null || value === undefined) return null
  if (!field.finite(value)) throw new Error(message)
  return value
}

function identityString(value: unknown, fallback: string) {
  if (value === undefined) return fallback
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error('The build manifest contains invalid variant identity.')
  }
  return value
}

function isNullableString(value: unknown): value is string | null {
  return value === null || typeof value === 'string'
}

function isGeometryMode(
  value: unknown,
): value is ManifestDrillOperation['geometryMode'] {
  return value === 'cut' || value === 'marked_only'
}

function isViewAxes(value: unknown): value is [AxisName, AxisName] {
  const axes = new Set<AxisName>(['x', 'y', 'z'])
  return (
    Array.isArray(value) &&
    value.length === 2 &&
    value.every(
      (axis) => typeof axis === 'string' && axes.has(axis as AxisName),
    ) &&
    value[0] !== value[1]
  )
}

function parsePart(value: unknown): ManifestPart {
  const part = expectFields(
    value,
    {
      part_number: field.string,
      description: field.string,
      material: field.string,
      quantity: field.positiveInteger,
      size_x_mm: field.finite,
      size_y_mm: field.finite,
      size_z_mm: field.finite,
      unit_volume_mm3: field.finite,
      placements: field.array,
    },
    'The build manifest contains an invalid part entry.',
  )
  if (
    !part.placements.every(
      (placement) => isRecord(placement) && field.string(placement.name),
    )
  )
    throw new Error('The build manifest contains an invalid part entry.')

  const placementNames = part.placements.map((placement) =>
    String((placement as Record<string, unknown>).name),
  )
  if (
    placementNames.length !== part.quantity ||
    new Set(placementNames).size !== placementNames.length
  ) {
    throw new Error('A manifest part has an invalid placement inventory.')
  }

  return {
    partNumber: part.part_number,
    description: part.description,
    material: part.material,
    quantity: part.quantity,
    sizeMm: [part.size_x_mm, part.size_y_mm, part.size_z_mm],
    unitVolumeMm3: part.unit_volume_mm3,
    colorRgba: parseColor(part.color_rgba),
    placementNames,
  }
}

function parseFastener(value: unknown): ManifestFastener {
  const fastener = expectFields(
    value,
    {
      code: field.string,
      description: field.string,
      quantity: field.nonnegativeInteger,
      length_mm: field.positive,
      nominal_size: field.string,
      head: field.string,
      drive: field.string,
      thread: field.string,
      finish: field.string,
      application: field.string,
      manufacturer: field.string,
      product_code: field.string,
      source_url: field.string,
      status: field.string,
      notes: field.string,
    },
    'The build manifest contains an invalid fastener entry.',
  )
  return {
    code: fastener.code,
    description: fastener.description,
    quantity: fastener.quantity,
    lengthMm: fastener.length_mm,
    nominalSize: fastener.nominal_size,
    head: fastener.head,
    drive: fastener.drive,
    thread: fastener.thread,
    finish: fastener.finish,
    application: fastener.application,
    manufacturer: fastener.manufacturer,
    productCode: fastener.product_code,
    sourceUrl: fastener.source_url,
    status: fastener.status,
    notes: fastener.notes,
  }
}

function parseExternalTarget(value: unknown): ManifestExternalTarget {
  const target = expectFields(
    value,
    {
      code: field.nonEmptyString,
      description: field.nonEmptyString,
      notes: field.string,
    },
    'The build manifest contains an invalid external target.',
  )
  return {
    code: target.code,
    description: target.description,
    notes: target.notes,
  }
}

function parseDrillOperation(value: unknown): ManifestDrillOperation {
  const operation = expectFields(
    value,
    {
      operation_id: field.string,
      part_number: field.string,
      label: field.string,
      kind: field.string,
      face: field.string,
      view_axes: isViewAxes,
      diameter_mm: field.positive,
      counts_fastener: field.boolean,
      geometry_mode: isGeometryMode,
      points_per_part: field.nonnegativeInteger,
      part_quantity: field.nonnegativeInteger,
      total_holes: field.nonnegativeInteger,
      points: field.array,
      notes: field.string,
      fastener_code: isNullableString,
    },
    'The build manifest contains an invalid drill operation.',
  )
  const points = operation.points.map((point) => {
    if (!isRecord(point) || typeof point.label !== 'string') {
      throw new Error('A drill operation contains an invalid point.')
    }
    return {
      positionMm: parseVector(
        point.position_mm,
        'A drill point has an invalid position.',
      ),
      axis: parseVector(point.axis, 'A drill point has an invalid axis.'),
      label: point.label,
    }
  })
  if (
    points.length !== operation.points_per_part ||
    operation.total_holes !==
      operation.points_per_part * operation.part_quantity
  ) {
    throw new Error('A drill operation has inconsistent hole quantities.')
  }

  return {
    operationId: operation.operation_id,
    partNumber: operation.part_number,
    label: operation.label,
    kind: operation.kind,
    face: operation.face,
    viewAxes: operation.view_axes,
    diameterMm: operation.diameter_mm,
    depthMm: nullableNumber(
      operation.depth_mm,
      'A drill operation has an invalid depth.',
    ),
    countersinkDiameterMm: nullableNumber(
      operation.countersink_diameter_mm,
      'A drill operation has an invalid countersink.',
    ),
    angleDeg: nullableNumber(
      operation.angle_deg,
      'A drill operation has an invalid angle.',
    ),
    fastenerCode: operation.fastener_code,
    countsFastener: operation.counts_fastener,
    geometryMode: operation.geometry_mode,
    pointsPerPart: operation.points_per_part,
    partQuantity: operation.part_quantity,
    totalHoles: operation.total_holes,
    points,
    notes: operation.notes,
  }
}

function parseJoint(value: unknown): ManifestJoint {
  const joint = expectFields(
    value,
    {
      joint_id: field.string,
      description: field.string,
      source_part_number: field.string,
      target_part_number: field.string,
      fastener_code: field.string,
      quantity: field.positiveInteger,
      drill_operation_ids: field.stringArray,
      assembly_step: field.positiveInteger,
      notes: field.string,
    },
    'The build manifest contains an invalid joint entry.',
  )
  return {
    jointId: joint.joint_id,
    description: joint.description,
    sourcePartNumber: joint.source_part_number,
    targetPartNumber: joint.target_part_number,
    fastenerCode: joint.fastener_code,
    quantity: joint.quantity,
    drillOperationIds: joint.drill_operation_ids,
    assemblyStep: joint.assembly_step,
    notes: joint.notes,
  }
}

function parseJoinery(value: unknown, parts: ManifestPart[]): ManifestJoinery {
  if (value === undefined) {
    return {
      status: 'unspecified',
      notes: [],
      externalTargets: [],
      fasteners: [],
      drillOperations: [],
      joints: [],
    }
  }
  const schedule = expectFields(
    value,
    {
      status: field.string,
      notes: field.stringArray,
      fasteners: field.array,
      drill_operations: field.array,
      joints: field.array,
    },
    'The build manifest contains an invalid joinery schedule.',
  )
  const fasteners = schedule.fasteners.map(parseFastener)
  const externalTargets = Array.isArray(schedule.external_targets)
    ? schedule.external_targets.map(parseExternalTarget)
    : []
  const drillOperations = schedule.drill_operations.map(parseDrillOperation)
  const joints = schedule.joints.map(parseJoint)
  const partNumbers = new Set(parts.map((part) => part.partNumber))
  const externalTargetCodes = new Set(
    externalTargets.map((target) => target.code),
  )
  if (
    externalTargetCodes.size !== externalTargets.length ||
    [...externalTargetCodes].some((code) => partNumbers.has(code))
  ) {
    throw new Error('The joinery schedule has conflicting external targets.')
  }
  const fastenerCodes = new Set(fasteners.map((fastener) => fastener.code))
  const operationIds = new Set(
    drillOperations.map((operation) => operation.operationId),
  )
  if (
    drillOperations.some(
      (operation) =>
        !partNumbers.has(operation.partNumber) ||
        (operation.fastenerCode !== null &&
          !fastenerCodes.has(operation.fastenerCode)),
    ) ||
    joints.some(
      (joint) =>
        !partNumbers.has(joint.sourcePartNumber) ||
        (!partNumbers.has(joint.targetPartNumber) &&
          !externalTargetCodes.has(joint.targetPartNumber)) ||
        !fastenerCodes.has(joint.fastenerCode) ||
        joint.drillOperationIds.some(
          (operationId) => !operationIds.has(operationId),
        ),
    )
  ) {
    throw new Error(
      'The joinery schedule references an unknown part or fastener.',
    )
  }
  const jointQuantities = new Map<string, number>()
  for (const joint of joints) {
    jointQuantities.set(
      joint.fastenerCode,
      (jointQuantities.get(joint.fastenerCode) ?? 0) + joint.quantity,
    )
  }
  if (
    fasteners.some(
      (fastener) =>
        (jointQuantities.get(fastener.code) ?? 0) !== fastener.quantity,
    )
  ) {
    throw new Error(
      'The joinery hardware totals do not match its joint schedule.',
    )
  }
  return {
    status: schedule.status,
    notes: schedule.notes,
    externalTargets,
    fasteners,
    drillOperations,
    joints,
  }
}

export function parseManifest(value: unknown): FurnitureManifest {
  const manifest = expectFields(
    value,
    {
      schema_version: (candidate): candidate is 1 => candidate === 1,
      units: (candidate): candidate is 'mm' => candidate === 'mm',
      name: field.string,
      model: field.string,
      part_occurrences: field.nonnegativeInteger,
      parts: field.array,
    },
    'Unsupported build manifest. Rebuild the furniture exports with QueryCAD.',
  )

  const parts = manifest.parts.map(parsePart)
  const joinery = parseJoinery(manifest.joinery, parts)
  const familyId = identityString(manifest.family, manifest.name)
  const variantId = identityString(manifest.variant, 'default')
  const variantLabel = identityString(manifest.variant_label, 'Default')
  const countedOccurrences = parts.reduce(
    (total, part) => total + part.quantity,
    0,
  )
  if (countedOccurrences !== manifest.part_occurrences) {
    throw new Error(
      'The build manifest part count does not match its inventory.',
    )
  }

  return {
    schemaVersion: 1,
    name: manifest.name,
    model: manifest.model,
    familyId,
    variantId,
    variantLabel,
    units: 'mm',
    partOccurrences: manifest.part_occurrences,
    parts,
    joinery,
  }
}

export function assertManifestMatchesDesign(
  manifest: FurnitureManifest,
  design: CatalogDesign,
): void {
  const comparisons: Array<[string, string | number, string | number]> = [
    ['name', manifest.name, design.name],
    ['model', manifest.model, design.model],
    ['family', manifest.familyId, design.familyId],
    ['variant', manifest.variantId, design.variantId],
    ['variant label', manifest.variantLabel, design.variantLabel],
    ['part count', manifest.partOccurrences, design.partOccurrences],
  ]
  const mismatches = comparisons
    .filter(([, manifestValue, catalogValue]) => manifestValue !== catalogValue)
    .map(([label, manifestValue, catalogValue]) => {
      const quote = typeof manifestValue === 'string' ? '"' : ''
      return `${label} is ${quote}${manifestValue}${quote} in the manifest but ${quote}${catalogValue}${quote} in the catalog`
    })

  if (mismatches.length > 0) {
    throw new Error(
      `The build catalog and manifest for "${design.name}" are out of sync (${mismatches.join('; ')}). Rebuild the furniture exports with QueryCAD, then refresh the build catalog.`,
    )
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
  const manifest = parseManifest(await response.json())
  assertManifestMatchesDesign(manifest, design)
  return manifest
}
