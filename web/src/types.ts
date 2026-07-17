export type Vector3Tuple = [number, number, number]

export type BuildArtifacts = {
  manifest: string
  glb: string
  step?: string
  stl?: string
  svg?: string
  bom?: string
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

export type FurnitureManifest = {
  schemaVersion: 1
  name: string
  model: string
  units: 'mm'
  partOccurrences: number
  parts: ManifestPart[]
}
