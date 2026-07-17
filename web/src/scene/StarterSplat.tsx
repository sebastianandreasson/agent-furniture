import { Html, Splat } from '@react-three/drei'
import { Component, Suspense, type ErrorInfo, type ReactNode } from 'react'

export const STARTER_SPLAT_URL =
  'https://raw.githubusercontent.com/GitHubDragonFly/GitHubDragonFly.github.io/main/viewers/examples/legobrick.splat'

class SplatErrorBoundary extends Component<
  { children: ReactNode; onError: (message: string) => void },
  { failed: boolean }
> {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Starter splat failed to load', error, info)
    this.props.onError(error.message)
  }

  render() {
    return this.state.failed ? null : this.props.children
  }
}

export function StarterSplat({
  onError,
}: {
  onError: (message: string) => void
}) {
  return (
    <SplatErrorBoundary onError={onError}>
      <Suspense
        fallback={
          <Html position={[-1800, 700, -1500]} center>
            <span className="scene-label">Streaming starter splat…</span>
          </Html>
        }
      >
        <Splat
          src={STARTER_SPLAT_URL}
          position={[-1850, 350, -1450]}
          rotation={[0, -0.45, 0]}
          scale={14}
          alphaTest={0.08}
          chunkSize={20000}
        />
      </Suspense>
    </SplatErrorBoundary>
  )
}
