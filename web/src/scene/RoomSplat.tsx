import { SparkRenderer, SplatMesh } from '@sparkjsdev/spark'
import { Html } from '@react-three/drei'
import { useThree } from '@react-three/fiber'
import {
  Component,
  useEffect,
  useRef,
  useState,
  type ErrorInfo,
  type ReactNode,
} from 'react'
import type { Group } from 'three'
import { ROOM_SPLAT } from './roomSplatConfig'

class RoomSplatErrorBoundary extends Component<
  { children: ReactNode; onError: (message: string) => void },
  { failed: boolean }
> {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Room splat failed to render', error, info)
    this.props.onError(error.message)
  }

  render() {
    return this.state.failed ? null : this.props.children
  }
}

function RoomSplatScene({
  onError,
}: {
  onError: (message: string | null) => void
}) {
  const renderer = useThree((state) => state.gl)
  const invalidate = useThree((state) => state.invalidate)
  const [progress, setProgress] = useState(0)
  const [ready, setReady] = useState(false)
  const [failed, setFailed] = useState(false)
  const sceneRoot = useRef<Group>(null)

  useEffect(() => {
    const root = sceneRoot.current
    if (!root) return

    let active = true
    setProgress(0)
    setReady(false)
    setFailed(false)
    onError(null)

    const sparkRenderer = new SparkRenderer({
      renderer,
      onDirty: invalidate,
    })
    const room = new SplatMesh({
      url: ROOM_SPLAT.assetUrl,
      onProgress: (event) => {
        if (active && event.lengthComputable && event.total > 0) {
          setProgress(event.loaded / event.total)
        }
      },
    })
    room.scale.setScalar(ROOM_SPLAT.mmPerSourceUnit)
    room.position.set(...ROOM_SPLAT.positionMm)
    room.rotation.set(...ROOM_SPLAT.rotationRad)
    root.add(sparkRenderer, room)

    room.initialized
      .then(() => {
        if (!active) return
        setProgress(1)
        setReady(true)
        invalidate()
      })
      .catch((error: unknown) => {
        if (!active) return
        const message =
          error instanceof Error
            ? error.message
            : String(error ?? 'Unknown splat loading error')
        setFailed(true)
        onError(message)
      })

    return () => {
      active = false
      root.remove(sparkRenderer, room)
      room.dispose()
      sparkRenderer.dispose()
    }
  }, [invalidate, onError, renderer])

  return (
    <group ref={sceneRoot} name="room-splat">
      {!ready && !failed && (
        <Html position={[0, 1100, 0]} center>
          <span className="scene-label">
            Loading room capture… {Math.round(progress * 100)}%
          </span>
        </Html>
      )}
    </group>
  )
}

export function RoomSplat({
  onError,
}: {
  onError: (message: string | null) => void
}) {
  return (
    <RoomSplatErrorBoundary onError={onError}>
      <RoomSplatScene onError={onError} />
    </RoomSplatErrorBoundary>
  )
}
