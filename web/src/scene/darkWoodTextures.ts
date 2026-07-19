import { useTexture } from '@react-three/drei'
import { useThree } from '@react-three/fiber'
import { useEffect, useMemo } from 'react'
import {
  NoColorSpace,
  RepeatWrapping,
  SRGBColorSpace,
  type Object3D,
  type Texture,
} from 'three'
import {
  copyFurnitureScene,
  type FurnitureSceneCopy,
  type WoodTextureSet,
} from './furnitureAppearance'
import colorTextureUrl from '../../public/textures/dark_wood/color.png?url'
import normalTextureUrl from '../../public/textures/dark_wood/normal.png?url'
import roughnessTextureUrl from '../../public/textures/dark_wood/roughness.png?url'

const DARK_WOOD_TEXTURES = [
  colorTextureUrl,
  normalTextureUrl,
  roughnessTextureUrl,
] as const

function configureTexture(texture: Texture, anisotropy: number) {
  texture.wrapS = RepeatWrapping
  texture.wrapT = RepeatWrapping
  texture.anisotropy = anisotropy
  texture.needsUpdate = true
}

export function useDarkWoodTextures(): WoodTextureSet {
  const [color, normal, roughness] = useTexture([
    ...DARK_WOOD_TEXTURES,
  ]) as Texture[]
  const anisotropy = useThree((state) =>
    state.gl.capabilities.getMaxAnisotropy(),
  )

  return useMemo(() => {
    configureTexture(color, anisotropy)
    configureTexture(normal, anisotropy)
    configureTexture(roughness, anisotropy)
    color.colorSpace = SRGBColorSpace
    normal.colorSpace = NoColorSpace
    roughness.colorSpace = NoColorSpace
    return { color, normal, roughness }
  }, [anisotropy, color, normal, roughness])
}

export function useFurnitureSceneCopy(
  sourceScene: Object3D,
  textures?: WoodTextureSet,
): FurnitureSceneCopy {
  const copy = useMemo(
    () => copyFurnitureScene(sourceScene, textures),
    [sourceScene, textures],
  )
  useEffect(() => copy.dispose, [copy])
  return copy
}
