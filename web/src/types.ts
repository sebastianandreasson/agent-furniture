export type Vector3Tuple = [number, number, number]

export type BuildArtifacts = {
  manifest: string
  glb: string
  step?: string
  stl?: string
  svg?: string
  bom?: string
  hardware?: string
}

export type CatalogDesign = {
  id: string
  name: string
  model: string
  revision: string
  overallSizeMm: { x: number; y: number; z: number }
  partOccurrences: number
  parameters: Record<string, string | number>
  artifacts: BuildArtifacts
}

export type BuildCatalog = {
  schemaVersion: 1
  units: 'mm'
  designs: CatalogDesign[]
}

export type Placement = {
  positionMm: Vector3Tuple
  rotationDeg: Vector3Tuple
}

export type TransformMode = 'translate' | 'rotate'
export type CameraView = 'perspective' | 'top' | 'front' | 'side'

export type ColorTuple = [number, number, number, number]

export type ManifestPart = {
  partNumber: string
  description: string
  material: string
  quantity: number
  sizeMm: Vector3Tuple
  unitVolumeMm3: number
  colorRgba: ColorTuple
  placementNames: string[]
}

export type AxisName = 'x' | 'y' | 'z'

export type ManifestFastener = {
  code: string
  description: string
  quantity: number
  lengthMm: number
  nominalSize: string
  head: string
  drive: string
  thread: string
  finish: string
  application: string
  manufacturer: string
  productCode: string
  sourceUrl: string
  status: string
  notes: string
}

export type ManifestDrillPoint = {
  positionMm: Vector3Tuple
  axis: Vector3Tuple
  label: string
}

export type ManifestDrillOperation = {
  operationId: string
  partNumber: string
  label: string
  kind: string
  face: string
  viewAxes: [AxisName, AxisName]
  diameterMm: number
  depthMm: number | null
  countersinkDiameterMm: number | null
  angleDeg: number | null
  fastenerCode: string | null
  countsFastener: boolean
  geometryMode: 'cut' | 'marked_only'
  pointsPerPart: number
  partQuantity: number
  totalHoles: number
  points: ManifestDrillPoint[]
  notes: string
}

export type ManifestJoint = {
  jointId: string
  description: string
  sourcePartNumber: string
  targetPartNumber: string
  fastenerCode: string
  quantity: number
  drillOperationIds: string[]
  assemblyStep: number
  notes: string
}

export type ManifestJoinery = {
  status: string
  notes: string[]
  fasteners: ManifestFastener[]
  drillOperations: ManifestDrillOperation[]
  joints: ManifestJoint[]
}

export type FurnitureManifest = {
  schemaVersion: 1
  name: string
  model: string
  units: 'mm'
  partOccurrences: number
  parts: ManifestPart[]
  joinery: ManifestJoinery
}
