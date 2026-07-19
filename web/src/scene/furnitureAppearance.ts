import {
  Box3,
  BufferAttribute,
  Color,
  Mesh,
  MeshStandardMaterial,
  Vector3,
  type BufferGeometry,
  type Material,
  type Object3D,
  type Texture,
} from 'three'
import type { CatalogDesign } from '../types'

export const DARK_WOOD_BOOKSHELF_MODEL = 'built_in_bookshelf'

export type WoodTextureSet = {
  color: Texture
  normal: Texture
  roughness: Texture
}

export type FurnitureSceneCopy = {
  scene: Object3D
  dispose: () => void
}

const WOOD_TEXTURE_SPAN_MM = 760
const PANEL_TINT_FLOOR = 0.86

export function usesDarkWoodTexture(design: Pick<CatalogDesign, 'model'>) {
  return design.model === DARK_WOOD_BOOKSHELF_MODEL
}

function coordinate(
  position: BufferAttribute,
  vertex: number,
  axis: 0 | 1 | 2,
) {
  if (axis === 0) return position.getX(vertex)
  if (axis === 1) return position.getY(vertex)
  return position.getZ(vertex)
}

/**
 * CadQuery's GLB export has positions and normals but no UVs. Project each face
 * in its own plane, putting the grain along that face's longest model axis.
 */
export function addBoxProjectionUvs(
  geometry: BufferGeometry,
  textureSpanMm = WOOD_TEXTURE_SPAN_MM,
) {
  const position = geometry.getAttribute('position')
  const normal = geometry.getAttribute('normal')
  if (!(position instanceof BufferAttribute) || position.count === 0) return

  geometry.computeBoundingBox()
  const bounds = geometry.boundingBox ?? new Box3()
  const size = bounds.getSize(new Vector3())
  const axisSizes = [size.x, size.y, size.z]
  const uv = new Float32Array(position.count * 2)

  for (let vertex = 0; vertex < position.count; vertex += 1) {
    let normalAxis: 0 | 1 | 2 = 2
    if (normal instanceof BufferAttribute) {
      const absoluteNormal = [
        Math.abs(normal.getX(vertex)),
        Math.abs(normal.getY(vertex)),
        Math.abs(normal.getZ(vertex)),
      ]
      normalAxis = absoluteNormal.indexOf(Math.max(...absoluteNormal)) as
        0 | 1 | 2
    }
    const faceAxes = ([0, 1, 2] as const).filter((axis) => axis !== normalAxis)
    const [uAxis, vAxis] =
      axisSizes[faceAxes[0]] >= axisSizes[faceAxes[1]]
        ? faceAxes
        : [faceAxes[1], faceAxes[0]]

    uv[vertex * 2] = coordinate(position, vertex, uAxis) / textureSpanMm
    uv[vertex * 2 + 1] = coordinate(position, vertex, vAxis) / textureSpanMm
  }

  geometry.setAttribute('uv', new BufferAttribute(uv, 2))
}

function hasKnobAncestor(object: Object3D, scene: Object3D) {
  let current: Object3D | null = object
  while (current && current !== scene) {
    if (/^knob(?:_|$)/i.test(current.name)) return true
    current = current.parent
  }
  return false
}

function materialsOf(mesh: Mesh) {
  return Array.isArray(mesh.material) ? mesh.material : [mesh.material]
}

function materialLightness(material: Material) {
  if (!(material instanceof MeshStandardMaterial)) return 1
  return material.color.getHSL({ h: 0, s: 0, l: 0 }).l
}

function configureWoodMaterial(
  material: Material,
  textures: WoodTextureSet,
  tint: number,
) {
  if (!(material instanceof MeshStandardMaterial)) return material
  material.map = textures.color
  material.normalMap = textures.normal
  material.roughnessMap = textures.roughness
  material.color.copy(new Color(tint, tint, tint))
  material.metalness = 0
  material.roughness = 0.82
  material.normalScale.set(0.34, 0.34)
  material.needsUpdate = true
  return material
}

/** Clone a loaded GLB scene without mutating drei's shared loader cache. */
export function copyFurnitureScene(
  sourceScene: Object3D,
  woodTextures?: WoodTextureSet,
): FurnitureSceneCopy {
  const scene = sourceScene.clone(true)
  const disposableMaterials = new Set<Material>()
  const disposableGeometries = new Set<BufferGeometry>()
  const woodMaterials = new Set<Material>()

  if (woodTextures) {
    scene.traverse((object) => {
      if (!(object instanceof Mesh) || hasKnobAncestor(object, scene)) return
      for (const material of materialsOf(object)) woodMaterials.add(material)
    })
  }

  const lightnesses = [...woodMaterials].map(materialLightness)
  const darkest = lightnesses.length > 0 ? Math.min(...lightnesses) : 1
  const lightest = lightnesses.length > 0 ? Math.max(...lightnesses) : 1
  const lightnessRange = lightest - darkest
  const geometryCopies = new Map<BufferGeometry, BufferGeometry>()

  scene.traverse((object) => {
    if (!(object instanceof Mesh)) return
    const isWood = Boolean(woodTextures) && !hasKnobAncestor(object, scene)

    if (isWood) {
      const sourceGeometry = object.geometry
      let copiedGeometry = geometryCopies.get(sourceGeometry)
      if (!copiedGeometry) {
        const createdGeometry = sourceGeometry.clone()
        addBoxProjectionUvs(createdGeometry)
        geometryCopies.set(sourceGeometry, createdGeometry)
        disposableGeometries.add(createdGeometry)
        copiedGeometry = createdGeometry
      }
      object.geometry = copiedGeometry
    }

    const copyMaterial = (source: Material) => {
      const material = source.clone()
      if (isWood && woodTextures) {
        const relativeLightness =
          lightnessRange > 0
            ? (materialLightness(source) - darkest) / lightnessRange
            : 1
        const tint =
          PANEL_TINT_FLOOR + (1 - PANEL_TINT_FLOOR) * relativeLightness
        configureWoodMaterial(material, woodTextures, tint)
      }
      disposableMaterials.add(material)
      return material
    }

    object.material = Array.isArray(object.material)
      ? object.material.map(copyMaterial)
      : copyMaterial(object.material)
    object.castShadow = true
    object.receiveShadow = true
  })

  return {
    scene,
    dispose: () => {
      for (const material of disposableMaterials) material.dispose()
      for (const geometry of disposableGeometries) geometry.dispose()
    },
  }
}
