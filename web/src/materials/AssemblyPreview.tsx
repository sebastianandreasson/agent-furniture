import { Bounds, Html, OrbitControls, useGLTF } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { Suspense, useEffect, useMemo } from 'react'
import {
  Color,
  Mesh,
  type Material,
  type Object3D,
  type Object3DEventMap,
} from 'three'
import type { CatalogDesign, ManifestPart } from '../types'
import type { PreviewContext } from './materialsViewModel'

type ColorMaterial = Material & {
  color?: Color
  emissive?: Color
  emissiveIntensity?: number
}

type MaterialSnapshot = {
  color?: Color
  emissive?: Color
  emissiveIntensity?: number
  opacity: number
  transparent: boolean
  depthWrite: boolean
}

function meshMaterials(mesh: Mesh) {
  return Array.isArray(mesh.material) ? mesh.material : [mesh.material]
}

function copySceneMaterials(scene: Object3D<Object3DEventMap>) {
  const copy = scene.clone(true)
  copy.traverse((object) => {
    if (!(object instanceof Mesh)) return
    object.material = Array.isArray(object.material)
      ? object.material.map((material) => material.clone())
      : object.material.clone()
  })
  return copy
}

function belongsToPart(
  object: Object3D,
  scene: Object3D,
  placementNames: Set<string>,
) {
  let current: Object3D | null = object
  while (current && current !== scene) {
    if (placementNames.has(current.name)) return true
    current = current.parent
  }
  return false
}

function AssemblyModel({
  design,
  selectedParts,
}: {
  design: CatalogDesign
  selectedParts: ManifestPart[]
}) {
  const source = `${design.artifacts.glb}?revision=${design.revision}`
  const { scene: sourceScene } = useGLTF(source)
  const scene = useMemo(() => copySceneMaterials(sourceScene), [sourceScene])
  const snapshots = useMemo(() => {
    const result = new Map<Material, MaterialSnapshot>()
    scene.traverse((object) => {
      if (!(object instanceof Mesh)) return
      for (const material of meshMaterials(object)) {
        const colorMaterial = material as ColorMaterial
        result.set(material, {
          color: colorMaterial.color?.clone(),
          emissive: colorMaterial.emissive?.clone(),
          emissiveIntensity: colorMaterial.emissiveIntensity,
          opacity: material.opacity,
          transparent: material.transparent,
          depthWrite: material.depthWrite,
        })
      }
    })
    return result
  }, [scene])

  useEffect(() => () => useGLTF.clear(source), [source])
  useEffect(
    () => () => {
      for (const material of snapshots.keys()) material.dispose()
    },
    [snapshots],
  )

  useEffect(() => {
    const names = new Set(selectedParts.flatMap((part) => part.placementNames))
    const filtering = names.size > 0
    scene.traverse((object) => {
      if (!(object instanceof Mesh)) return
      const selected = !filtering || belongsToPart(object, scene, names)
      for (const material of meshMaterials(object)) {
        const original = snapshots.get(material)
        if (!original) continue
        const colorMaterial = material as ColorMaterial
        if (original.color && colorMaterial.color) {
          colorMaterial.color.copy(original.color)
        }
        if (original.emissive && colorMaterial.emissive) {
          colorMaterial.emissive.copy(original.emissive)
        }
        if (colorMaterial.emissiveIntensity !== undefined) {
          colorMaterial.emissiveIntensity = original.emissiveIntensity ?? 1
        }
        material.opacity = original.opacity
        material.transparent = original.transparent
        material.depthWrite = original.depthWrite

        if (filtering && selected) {
          colorMaterial.color?.lerp(new Color('#ff9f68'), 0.58)
          colorMaterial.emissive?.set('#6b2410')
          if (colorMaterial.emissiveIntensity !== undefined) {
            colorMaterial.emissiveIntensity = 1.35
          }
        } else if (filtering) {
          colorMaterial.color?.lerp(new Color('#172029'), 0.46)
          colorMaterial.emissive?.set('#000000')
          material.opacity = 0.42
          material.transparent = true
          material.depthWrite = false
        }
        material.needsUpdate = true
      }
    })
  }, [scene, selectedParts, snapshots])

  return (
    <Bounds fit clip observe margin={1.08}>
      <primitive object={scene} />
    </Bounds>
  )
}

export function AssemblyPreview({
  design,
  selectedParts,
  context,
  navigation,
}: {
  design: CatalogDesign
  selectedParts: ManifestPart[]
  context?: PreviewContext
  navigation?: {
    currentPosition: number
    steps: Array<{ number: number; complete: boolean }>
    onPrevious: () => void
    onNext: () => void
  }
}) {
  return (
    <aside
      className="assembly-preview"
      aria-label="Interactive assembly preview"
    >
      <div className="assembly-preview-heading">
        <div>
          <p className="eyebrow">Assembly context</p>
          <h3>Model preview</h3>
        </div>
        <span className="preview-live-dot">Live GLB</span>
      </div>
      <div className="assembly-preview-canvas">
        <Canvas
          dpr={[1, 1.75]}
          camera={{
            position: [1900, 1300, 2100],
            fov: 34,
            near: 1,
            far: 30000,
          }}
          gl={{ antialias: true, alpha: false }}
        >
          <color attach="background" args={['#0b1015']} />
          <ambientLight intensity={1.3} />
          <directionalLight position={[1600, 2600, 1800]} intensity={3.1} />
          <directionalLight position={[-1400, 900, -1200]} intensity={1.1} />
          <Suspense
            fallback={
              <Html center>
                <span className="scene-label">Loading assembly…</span>
              </Html>
            }
          >
            <AssemblyModel design={design} selectedParts={selectedParts} />
          </Suspense>
          <OrbitControls
            makeDefault
            enablePan={false}
            minPolarAngle={Math.PI / 7}
            maxPolarAngle={Math.PI / 2.05}
            enableDamping
            dampingFactor={0.08}
          />
        </Canvas>
        <div className="assembly-preview-grid" aria-hidden="true" />
        <div className="assembly-preview-hint">
          {context ? (
            <>
              <span>{context.eyebrow}</span>
              <strong>{context.title}</strong>
              <small>{context.detail}</small>
            </>
          ) : (
            <>
              <span>Hover a schematic part</span>
              <strong>Inspect it in the assembly</strong>
              <small>Drag to orbit · scroll to zoom</small>
            </>
          )}
        </div>
      </div>
      {navigation ? (
        <div className="assembly-preview-navigation">
          <div>
            <button
              type="button"
              onClick={navigation.onPrevious}
              disabled={navigation.currentPosition <= 1}
              aria-label="Previous assembly step"
            >
              ←
            </button>
            <span>
              Step {navigation.currentPosition} of {navigation.steps.length}
            </span>
            <button
              type="button"
              onClick={navigation.onNext}
              disabled={navigation.currentPosition >= navigation.steps.length}
              aria-label="Next assembly step"
            >
              →
            </button>
          </div>
          <ol className="assembly-progress-bars" aria-label="Assembly progress">
            {navigation.steps.map((step, index) => (
              <li
                key={step.number}
                aria-label={`Step ${step.number}${step.complete ? ', complete' : ''}${index + 1 === navigation.currentPosition ? ', current' : ''}`}
                aria-current={
                  index + 1 === navigation.currentPosition ? 'step' : undefined
                }
                className={`${index + 1 === navigation.currentPosition ? 'is-current' : ''} ${step.complete ? 'is-complete' : ''}`}
              />
            ))}
          </ol>
        </div>
      ) : (
        <p className="assembly-preview-footer">
          Hover or keyboard-focus a part to isolate every matching placement.
        </p>
      )}
    </aside>
  )
}
