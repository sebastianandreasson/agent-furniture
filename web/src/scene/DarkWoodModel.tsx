import type { Object3D } from 'three'
import { useDarkWoodTextures, useFurnitureSceneCopy } from './darkWoodTextures'

export function DarkWoodModel({
  sourceScene,
  position,
}: {
  sourceScene: Object3D
  position?: [number, number, number]
}) {
  const textures = useDarkWoodTextures()
  const copy = useFurnitureSceneCopy(sourceScene, textures)
  return <primitive object={copy.scene} position={position} />
}
