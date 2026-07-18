import { useEffect } from 'react'
import { EditorScene } from '../scene/EditorScene'
import { useEditorStore } from '../state/editor'
import type { CameraView, CatalogDesign } from '../types'

const CAMERA_VIEWS: CameraView[] = ['perspective', 'top', 'front', 'side']

export function StudioViewport({
  design,
  onSplatError,
}: {
  design: CatalogDesign | null
  onSplatError: (error: string | null) => void
}) {
  const mode = useEditorStore((state) => state.transformMode)
  const setMode = useEditorStore((state) => state.setTransformMode)
  const snapping = useEditorStore((state) => state.snapping)
  const setSnapping = useEditorStore((state) => state.setSnapping)
  const showHelpers = useEditorStore((state) => state.showHelpers)
  const setShowHelpers = useEditorStore((state) => state.setShowHelpers)
  const cameraView = useEditorStore((state) => state.cameraView)
  const setCameraView = useEditorStore((state) => state.setCameraView)

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLSelectElement
      ) {
        return
      }
      if (event.key.toLowerCase() === 'w') setMode('translate')
      if (event.key.toLowerCase() === 'e') setMode('rotate')
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [setMode])

  return (
    <section className="viewport-wrap">
      <div className="viewport-toolbar">
        <div className="segmented-control" aria-label="Transform tool">
          <button
            className={mode === 'translate' ? 'is-active' : ''}
            type="button"
            onClick={() => setMode('translate')}
          >
            Move <kbd>W</kbd>
          </button>
          <button
            className={mode === 'rotate' ? 'is-active' : ''}
            type="button"
            onClick={() => setMode('rotate')}
          >
            Rotate <kbd>E</kbd>
          </button>
        </div>
        <button
          className={`toolbar-button ${snapping ? 'is-active' : ''}`}
          type="button"
          onClick={() => setSnapping(!snapping)}
        >
          ⊞ Snap {snapping ? '50 mm / 15°' : 'off'}
        </button>
        <button
          className={`toolbar-button ${showHelpers ? 'is-active' : ''}`}
          type="button"
          aria-pressed={showHelpers}
          title="Show or hide transform gizmos and object bounds"
          onClick={() => setShowHelpers(!showHelpers)}
        >
          ◇ Helpers {showHelpers ? 'on' : 'off'}
        </button>
        <div className="toolbar-spacer" />
        <div className="view-switcher">
          {CAMERA_VIEWS.map((view) => (
            <button
              className={cameraView === view ? 'is-active' : ''}
              type="button"
              key={view}
              onClick={() => setCameraView(view)}
            >
              {view.slice(0, 1).toUpperCase() + view.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="viewport" data-testid="cad-viewport">
        <EditorScene design={design} onSplatError={onSplatError} />
        <div className="metric-chip">MM · Y UP</div>
        <div className="viewport-help">
          Drag the gizmo to place furniture · Orbit with the mouse
        </div>
      </div>
    </section>
  )
}
