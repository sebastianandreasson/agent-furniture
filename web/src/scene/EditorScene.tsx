import { GizmoHelper, GizmoViewport, Html } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { memo, Suspense } from 'react'
import { useEditorStore } from '../state/editor'
import type { CatalogDesign } from '../types'
import { CameraRig } from './CameraRig'
import { FurnitureModel } from './FurnitureModel'
import { RoomProxy } from './RoomProxy'
import { StarterSplat } from './StarterSplat'

export const EditorScene = memo(function EditorScene({
  design,
  onSplatError,
}: {
  design: CatalogDesign | null
  onSplatError: (message: string) => void
}) {
  const cameraView = useEditorStore((state) => state.cameraView)
  const layers = useEditorStore((state) => state.layers)
  const showHelpers = useEditorStore((state) => state.showHelpers)

  return (
    <Canvas
      shadows="basic"
      dpr={[1, 1.75]}
      camera={{
        position: [2700, 1900, 3000],
        fov: 42,
        near: 1,
        far: 30000,
      }}
      gl={{ antialias: true, alpha: false }}
      onPointerMissed={() => undefined}
    >
      <color attach="background" args={['#f3f2ee']} />
      <fog attach="fog" args={['#f3f2ee', 7000, 12500]} />
      <ambientLight intensity={1.65} />
      <directionalLight
        castShadow
        position={[2200, 4200, 1800]}
        intensity={3.15}
        shadow-mapSize={[2048, 2048]}
        shadow-camera-far={10000}
      />
      <directionalLight position={[-1800, 2100, -1400]} intensity={1.25} />
      <hemisphereLight args={['#ffffff', '#d8d5ce', 1.1]} />

      {layers.room && <RoomProxy showGrid={layers.grid} />}
      {layers.splat && <StarterSplat onError={onSplatError} />}
      {layers.furniture && design && (
        <Suspense
          fallback={
            <Html position={[0, 500, 0]} center>
              <span className="scene-label">Loading CadQuery GLB…</span>
            </Html>
          }
        >
          <FurnitureModel
            key={`${design.id}-${design.revision}`}
            design={design}
          />
        </Suspense>
      )}

      <CameraRig view={cameraView} />
      {showHelpers && (
        <GizmoHelper alignment="bottom-right" margin={[88, 80]}>
          <GizmoViewport
            axisColors={['#ff8f7a', '#83d7a5', '#70a7ff']}
            labelColor="#26333a"
          />
        </GizmoHelper>
      )}
    </Canvas>
  )
})
