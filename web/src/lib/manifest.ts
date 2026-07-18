import type {
  AxisName,
  CatalogDesign,
  ColorTuple,
  FurnitureManifest,
  ManifestDrillOperation,
  ManifestFastener,
  ManifestJoinery,
  ManifestJoint,
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

function parseVector(value: unknown, message: string): Vector3Tuple {
  if (
    !Array.isArray(value) ||
    value.length !== 3 ||
    !value.every(isFiniteNumber)
  ) {
    throw new Error(message)
  }
  return value as Vector3Tuple
}

function nullableNumber(value: unknown, message: string): number | null {
  if (value === null || value === undefined) return null
  if (!isFiniteNumber(value)) throw new Error(message)
  return value
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

function parseFastener(value: unknown): ManifestFastener {
  if (
    !isRecord(value) ||
    typeof value.code !== 'string' ||
    typeof value.description !== 'string' ||
    !isFiniteNumber(value.quantity) ||
    !Number.isInteger(value.quantity) ||
    value.quantity < 0 ||
    !isFiniteNumber(value.length_mm) ||
    value.length_mm <= 0 ||
    typeof value.nominal_size !== 'string' ||
    typeof value.head !== 'string' ||
    typeof value.drive !== 'string' ||
    typeof value.thread !== 'string' ||
    typeof value.finish !== 'string' ||
    typeof value.application !== 'string' ||
    typeof value.manufacturer !== 'string' ||
    typeof value.product_code !== 'string' ||
    typeof value.source_url !== 'string' ||
    typeof value.status !== 'string' ||
    typeof value.notes !== 'string'
  ) {
    throw new Error('The build manifest contains an invalid fastener entry.')
  }
  return {
    code: value.code,
    description: value.description,
    quantity: value.quantity,
    lengthMm: value.length_mm,
    nominalSize: value.nominal_size,
    head: value.head,
    drive: value.drive,
    thread: value.thread,
    finish: value.finish,
    application: value.application,
    manufacturer: value.manufacturer,
    productCode: value.product_code,
    sourceUrl: value.source_url,
    status: value.status,
    notes: value.notes,
  }
}

function parseDrillOperation(value: unknown): ManifestDrillOperation {
  const axes = new Set<AxisName>(['x', 'y', 'z'])
  if (
    !isRecord(value) ||
    typeof value.operation_id !== 'string' ||
    typeof value.part_number !== 'string' ||
    typeof value.label !== 'string' ||
    typeof value.kind !== 'string' ||
    typeof value.face !== 'string' ||
    !Array.isArray(value.view_axes) ||
    value.view_axes.length !== 2 ||
    !value.view_axes.every(
      (axis) => typeof axis === 'string' && axes.has(axis as AxisName),
    ) ||
    value.view_axes[0] === value.view_axes[1] ||
    !isFiniteNumber(value.diameter_mm) ||
    value.diameter_mm <= 0 ||
    typeof value.counts_fastener !== 'boolean' ||
    (value.geometry_mode !== 'cut' && value.geometry_mode !== 'marked_only') ||
    !isFiniteNumber(value.points_per_part) ||
    !Number.isInteger(value.points_per_part) ||
    !isFiniteNumber(value.part_quantity) ||
    !Number.isInteger(value.part_quantity) ||
    !isFiniteNumber(value.total_holes) ||
    !Number.isInteger(value.total_holes) ||
    !Array.isArray(value.points) ||
    typeof value.notes !== 'string' ||
    (value.fastener_code !== null && typeof value.fastener_code !== 'string')
  ) {
    throw new Error('The build manifest contains an invalid drill operation.')
  }
  const points = value.points.map((point) => {
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
    points.length !== value.points_per_part ||
    value.total_holes !== value.points_per_part * value.part_quantity
  ) {
    throw new Error('A drill operation has inconsistent hole quantities.')
  }

  return {
    operationId: value.operation_id,
    partNumber: value.part_number,
    label: value.label,
    kind: value.kind,
    face: value.face,
    viewAxes: value.view_axes as [AxisName, AxisName],
    diameterMm: value.diameter_mm,
    depthMm: nullableNumber(
      value.depth_mm,
      'A drill operation has an invalid depth.',
    ),
    countersinkDiameterMm: nullableNumber(
      value.countersink_diameter_mm,
      'A drill operation has an invalid countersink.',
    ),
    angleDeg: nullableNumber(
      value.angle_deg,
      'A drill operation has an invalid angle.',
    ),
    fastenerCode: value.fastener_code,
    countsFastener: value.counts_fastener,
    geometryMode: value.geometry_mode,
    pointsPerPart: value.points_per_part,
    partQuantity: value.part_quantity,
    totalHoles: value.total_holes,
    points,
    notes: value.notes,
  }
}

function parseJoint(value: unknown): ManifestJoint {
  if (
    !isRecord(value) ||
    typeof value.joint_id !== 'string' ||
    typeof value.description !== 'string' ||
    typeof value.source_part_number !== 'string' ||
    typeof value.target_part_number !== 'string' ||
    typeof value.fastener_code !== 'string' ||
    !isFiniteNumber(value.quantity) ||
    !Number.isInteger(value.quantity) ||
    value.quantity < 1 ||
    !Array.isArray(value.drill_operation_ids) ||
    !value.drill_operation_ids.every((item) => typeof item === 'string') ||
    !isFiniteNumber(value.assembly_step) ||
    !Number.isInteger(value.assembly_step) ||
    value.assembly_step < 1 ||
    typeof value.notes !== 'string'
  ) {
    throw new Error('The build manifest contains an invalid joint entry.')
  }
  return {
    jointId: value.joint_id,
    description: value.description,
    sourcePartNumber: value.source_part_number,
    targetPartNumber: value.target_part_number,
    fastenerCode: value.fastener_code,
    quantity: value.quantity,
    drillOperationIds: value.drill_operation_ids,
    assemblyStep: value.assembly_step,
    notes: value.notes,
  }
}

function parseJoinery(value: unknown, parts: ManifestPart[]): ManifestJoinery {
  if (value === undefined) {
    return {
      status: 'unspecified',
      notes: [],
      fasteners: [],
      drillOperations: [],
      joints: [],
    }
  }
  if (
    !isRecord(value) ||
    typeof value.status !== 'string' ||
    !Array.isArray(value.notes) ||
    !value.notes.every((note) => typeof note === 'string') ||
    !Array.isArray(value.fasteners) ||
    !Array.isArray(value.drill_operations) ||
    !Array.isArray(value.joints)
  ) {
    throw new Error('The build manifest contains an invalid joinery schedule.')
  }
  const fasteners = value.fasteners.map(parseFastener)
  const drillOperations = value.drill_operations.map(parseDrillOperation)
  const joints = value.joints.map(parseJoint)
  const partNumbers = new Set(parts.map((part) => part.partNumber))
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
        !partNumbers.has(joint.targetPartNumber) ||
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
    status: value.status,
    notes: value.notes,
    fasteners,
    drillOperations,
    joints,
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
  const joinery = parseJoinery(value.joinery, parts)
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
    joinery,
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
