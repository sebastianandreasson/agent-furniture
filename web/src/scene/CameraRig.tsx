import { OrbitControls } from '@react-three/drei'
import { useThree } from '@react-three/fiber'
import { useEffect } from 'react'
import type { CameraView } from '../types'

const VIEW_POSITIONS: Record<CameraView, [number, number, number]> = {
  perspective: [2700, 1900, 3000],
  top: [0, 5000, 0.001],
  front: [0, 900, 4200],
  side: [4200, 900, 0],
}

export function CameraRig({ view }: { view: CameraView }) {
  const camera = useThree((state) => state.camera)

  useEffect(() => {
    const [x, y, z] = VIEW_POSITIONS[view]
    camera.up.set(0, view === 'top' ? 0 : 1, view === 'top' ? -1 : 0)
    camera.position.set(x, y, z)
    camera.lookAt(0, 420, 0)
    camera.updateProjectionMatrix()
  }, [camera, view])

  return (
    <OrbitControls
      makeDefault
      target={[0, 420, 0]}
      minDistance={350}
      maxDistance={12000}
      maxPolarAngle={Math.PI / 2 - 0.015}
      enableDamping
      dampingFactor={0.08}
    />
  )
}
