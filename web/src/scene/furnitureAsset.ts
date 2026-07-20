import { useGLTF } from '@react-three/drei'
import { useEffect, useMemo } from 'react'
import { Box3, Vector3, type Material, type Mesh, type Object3D } from 'three'
import type { CatalogDesign, Vector3Tuple } from '../types'

export function useFurnitureAsset(design: CatalogDesign) {
  const source = `${design.artifacts.glb}?revision=${design.revision}`
  const { scene } = useGLTF(source)
  useEffect(() => () => useGLTF.clear(source), [source])
  return scene
}

export function useFurnitureNormalization(
  scene: Object3D,
  design: CatalogDesign,
) {
  return useMemo(() => {
    scene.updateMatrixWorld(true)
    const bounds = new Box3().setFromObject(scene)
    const sourceSize = bounds.getSize(new Vector3())
    const expectedSize = new Vector3(
      design.overallSizeMm.x,
      design.overallSizeMm.z,
      design.overallSizeMm.y,
    )
    const sourceLongest = Math.max(sourceSize.x, sourceSize.y, sourceSize.z)
    const expectedLongest = Math.max(
      expectedSize.x,
      expectedSize.y,
      expectedSize.z,
    )
    const center = bounds.getCenter(new Vector3())
    return {
      scale: sourceLongest > 0 ? expectedLongest / sourceLongest : 1,
      offset: [-center.x, -bounds.min.y, -center.z] as Vector3Tuple,
    }
  }, [design, scene])
}

export function meshMaterials(mesh: Mesh): Material[] {
  return Array.isArray(mesh.material) ? mesh.material : [mesh.material]
}

export function hasNamedAncestor(
  object: Object3D,
  root: Object3D,
  matches: (name: string) => boolean,
) {
  let current: Object3D | null = object
  while (current && current !== root) {
    if (matches(current.name)) return true
    current = current.parent
  }
  return false
}
