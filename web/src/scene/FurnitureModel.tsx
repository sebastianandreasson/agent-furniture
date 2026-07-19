import { Clone, TransformControls, useGLTF } from '@react-three/drei'
import { useEffect, useMemo, useRef } from 'react'
import { Box3, MathUtils, Vector3, type Object3D } from 'three'
import type { TransformControls as TransformControlsImpl } from 'three-stdlib'
import { DEFAULT_PLACEMENT, useEditorStore } from '../state/editor'
import type { CatalogDesign, Placement } from '../types'
import { DarkWoodModel } from './DarkWoodModel'
import { usesDarkWoodTexture } from './furnitureAppearance'

function rounded(value: number, precision = 1) {
  const factor = 10 ** precision
  return Math.round(value * factor) / factor
}

export function FurnitureModel({ design }: { design: CatalogDesign }) {
  const controlsRef = useRef<TransformControlsImpl>(null)
  const placement =
    useEditorStore((state) => state.placements[design.id]) ?? DEFAULT_PLACEMENT
  const setPlacement = useEditorStore((state) => state.setPlacement)
  const mode = useEditorStore((state) => state.transformMode)
  const snapping = useEditorStore((state) => state.snapping)
  const showHelpers = useEditorStore((state) => state.showHelpers)
  const showTextures = useEditorStore((state) => state.showTextures)
  const source = `${design.artifacts.glb}?revision=${design.revision}`
  const { scene } = useGLTF(source)

  useEffect(() => () => useGLTF.clear(source), [source])

  const normalized = useMemo(() => {
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
    const scale = sourceLongest > 0 ? expectedLongest / sourceLongest : 1
    const center = bounds.getCenter(new Vector3())
    return {
      scale,
      offset: [-center.x, -bounds.min.y, -center.z] as [number, number, number],
    }
  }, [design, scene])

  const commitTransform = () => {
    const root = (
      controlsRef.current as unknown as { object: Object3D | null } | null
    )?.object
    if (!root) return
    const next: Placement = {
      positionMm: [
        rounded(root.position.x),
        rounded(root.position.y),
        rounded(root.position.z),
      ],
      rotationDeg: [
        rounded(MathUtils.radToDeg(root.rotation.x), 2),
        rounded(MathUtils.radToDeg(root.rotation.y), 2),
        rounded(MathUtils.radToDeg(root.rotation.z), 2),
      ],
    }
    setPlacement(design.id, next)
  }

  const rotation = placement.rotationDeg.map(MathUtils.degToRad) as [
    number,
    number,
    number,
  ]
  const model = (
    <group name={`placement-${design.id}`}>
      <group scale={normalized.scale}>
        {showTextures && usesDarkWoodTexture(design) ? (
          <DarkWoodModel sourceScene={scene} position={normalized.offset} />
        ) : (
          <Clone
            object={scene}
            position={normalized.offset}
            deep="materialsOnly"
            castShadow
            receiveShadow
          />
        )}
      </group>
      {showHelpers && (
        <mesh
          position={[0, design.overallSizeMm.z / 2, 0]}
          raycast={() => null}
        >
          <boxGeometry
            args={[
              design.overallSizeMm.x + 12,
              design.overallSizeMm.z + 12,
              design.overallSizeMm.y + 12,
            ]}
          />
          <meshBasicMaterial
            color="#ffb86b"
            wireframe
            transparent
            opacity={0.36}
            depthTest={false}
          />
        </mesh>
      )}
    </group>
  )

  if (!showHelpers) {
    return (
      <group position={placement.positionMm} rotation={rotation}>
        {model}
      </group>
    )
  }

  return (
    <TransformControls
      ref={controlsRef}
      mode={mode}
      space="world"
      size={0.82}
      translationSnap={snapping ? 50 : null}
      rotationSnap={snapping ? MathUtils.degToRad(15) : null}
      showX={mode === 'translate'}
      showY
      showZ={mode === 'translate'}
      onMouseUp={commitTransform}
      position={placement.positionMm}
      rotation={rotation}
    >
      {model}
    </TransformControls>
  )
}
