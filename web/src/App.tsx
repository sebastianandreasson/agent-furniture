import { Loader } from '@react-three/drei'
import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'
import { loadCatalog } from './lib/catalog'
import { EditorScene } from './scene/EditorScene'
import { STARTER_SPLAT_URL } from './scene/StarterSplat'
import { DEFAULT_PLACEMENT, useEditorStore } from './state/editor'
import type {
  BuildCatalog,
  CameraView,
  CatalogDesign,
  Vector3Tuple,
} from './types'

const CAMERA_VIEWS: CameraView[] = ['perspective', 'top', 'front', 'side']

function formatModelName(value: string) {
  return value.replaceAll('_', ' ')
}

function NumericField({
  label,
  value,
  onChange,
}: {
  label: string
  value: number
  onChange: (value: number) => void
}) {
  return (
    <label className="numeric-field">
      <span>{label}</span>
      <input
        type="number"
        value={value}
        step={10}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  )
}

function ArtifactLink({ href, label }: { href?: string; label: string }) {
  if (!href) return null
  return (
    <a className="artifact-link" href={href} target="_blank" rel="noreferrer">
      <span>{label}</span>
      <span aria-hidden="true">↗</span>
    </a>
  )
}

function App() {
  const [catalog, setCatalog] = useState<BuildCatalog | null>(null)
  const [catalogError, setCatalogError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(true)
  const [lastSync, setLastSync] = useState<Date | null>(null)
  const [splatError, setSplatError] = useState<string | null>(null)

  const activeDesignId = useEditorStore((state) => state.activeDesignId)
  const setActiveDesign = useEditorStore((state) => state.setActiveDesign)
  const placements = useEditorStore((state) => state.placements)
  const setPosition = useEditorStore((state) => state.setPosition)
  const setRotation = useEditorStore((state) => state.setRotation)
  const resetPlacement = useEditorStore((state) => state.resetPlacement)
  const mode = useEditorStore((state) => state.transformMode)
  const setMode = useEditorStore((state) => state.setTransformMode)
  const snapping = useEditorStore((state) => state.snapping)
  const setSnapping = useEditorStore((state) => state.setSnapping)
  const cameraView = useEditorStore((state) => state.cameraView)
  const setCameraView = useEditorStore((state) => state.setCameraView)
  const layers = useEditorStore((state) => state.layers)
  const toggleLayer = useEditorStore((state) => state.toggleLayer)

  const refreshCatalog = useCallback(
    async (showSpinner = true, signal?: AbortSignal) => {
      if (showSpinner) setRefreshing(true)
      try {
        const next = await loadCatalog(signal)
        setCatalog(next)
        setCatalogError(null)
        setLastSync(new Date())
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') return
        setCatalogError(
          error instanceof Error
            ? error.message
            : 'Could not load furniture builds.',
        )
      } finally {
        if (showSpinner) setRefreshing(false)
      }
    },
    [],
  )

  useEffect(() => {
    const controller = new AbortController()
    void refreshCatalog(true, controller.signal)
    const interval = window.setInterval(() => void refreshCatalog(false), 5000)
    return () => {
      controller.abort()
      window.clearInterval(interval)
    }
  }, [refreshCatalog])

  useEffect(() => {
    if (!catalog?.designs.length) return
    if (
      !activeDesignId ||
      !catalog.designs.some((design) => design.id === activeDesignId)
    ) {
      setActiveDesign(catalog.designs[0].id)
    }
  }, [activeDesignId, catalog, setActiveDesign])

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLSelectElement
      )
        return
      if (event.key.toLowerCase() === 'w') setMode('translate')
      if (event.key.toLowerCase() === 'e') setMode('rotate')
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [setMode])

  const activeDesign = useMemo<CatalogDesign | null>(
    () =>
      catalog?.designs.find((design) => design.id === activeDesignId) ?? null,
    [activeDesignId, catalog],
  )
  const placement = activeDesign
    ? (placements[activeDesign.id] ?? DEFAULT_PLACEMENT)
    : DEFAULT_PLACEMENT

  const updatePositionAxis = (axis: number, value: number) => {
    if (!activeDesign || !Number.isFinite(value)) return
    const next = [...placement.positionMm] as Vector3Tuple
    next[axis] = value
    setPosition(activeDesign.id, next)
  }

  const updateYaw = (value: number) => {
    if (!activeDesign || !Number.isFinite(value)) return
    setRotation(activeDesign.id, [0, value, 0])
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="brand-block">
          <div className="brand-mark" aria-hidden="true">
            Q
          </div>
          <div>
            <p className="eyebrow">Metric furniture lab</p>
            <h1>QueryCAD Studio</h1>
          </div>
        </div>
        <div className="header-status">
          <span className={`status-dot ${catalogError ? 'is-error' : ''}`} />
          <span>
            {catalogError
              ? 'Build folder offline'
              : `${catalog?.designs.length ?? 0} build ready`}
          </span>
          <span className="status-divider" />
          <span>
            {lastSync
              ? `Synced ${lastSync.toLocaleTimeString()}`
              : 'Connecting…'}
          </span>
          <button
            className="icon-button"
            type="button"
            onClick={() => void refreshCatalog()}
            aria-label="Refresh build catalog"
            title="Refresh build catalog"
          >
            {refreshing ? '···' : '↻'}
          </button>
        </div>
      </header>

      <div className="workspace">
        <aside className="panel asset-panel">
          <section className="panel-section">
            <div className="section-heading">
              <span>Furniture builds</span>
              <span className="count-badge">
                {catalog?.designs.length ?? 0}
              </span>
            </div>
            {catalogError && <p className="inline-error">{catalogError}</p>}
            {catalog?.designs.map((design) => (
              <button
                className={`build-card ${activeDesign?.id === design.id ? 'is-active' : ''}`}
                key={design.id}
                type="button"
                onClick={() => setActiveDesign(design.id)}
              >
                <span className="build-icon" aria-hidden="true">
                  ▱
                </span>
                <span className="build-copy">
                  <strong>{design.name}</strong>
                  <small>{formatModelName(design.model)}</small>
                </span>
                <span className="revision">{design.revision.slice(0, 5)}</span>
              </button>
            ))}
            {!catalogError && catalog?.designs.length === 0 && (
              <p className="empty-state">
                No GLB builds found. Run the model build command.
              </p>
            )}
          </section>

          <section className="panel-section">
            <div className="section-heading">Scene layers</div>
            {(
              [
                ['splat', 'Starter splat', 'Online visual reference'],
                ['furniture', 'Furniture', 'Exact CadQuery preview'],
                ['room', 'Room proxy', 'Metric collision layer'],
                ['grid', '100 mm grid', '1 m major divisions'],
              ] as const
            ).map(([key, title, subtitle]) => (
              <button
                className="layer-row"
                type="button"
                key={key}
                onClick={() => toggleLayer(key)}
              >
                <span
                  className={`visibility-toggle ${layers[key] ? 'is-on' : ''}`}
                  aria-hidden="true"
                />
                <span>
                  <strong>{title}</strong>
                  <small>{subtitle}</small>
                </span>
              </button>
            ))}
            {splatError && (
              <p className="splat-warning">
                The online splat could not load. Furniture editing remains
                active.
              </p>
            )}
          </section>

          <section className="panel-section source-note">
            <span className="source-kicker">VISUAL TRUTH · SAMPLE</span>
            <p>
              The starter splat is uncalibrated and never used for measurement
              or collision.
            </p>
            <a href={STARTER_SPLAT_URL} target="_blank" rel="noreferrer">
              View sample source ↗
            </a>
          </section>
        </aside>

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
            <EditorScene design={activeDesign} onSplatError={setSplatError} />
            <div className="metric-chip">MM · Y UP</div>
            <div className="viewport-help">
              Drag the gizmo to place furniture · Orbit with the mouse
            </div>
          </div>
        </section>

        <aside className="panel inspector-panel">
          <section className="panel-section inspector-title">
            <p className="eyebrow">Selected object</p>
            <h2>{activeDesign?.name ?? 'No furniture build'}</h2>
            <p>
              {activeDesign
                ? formatModelName(activeDesign.model)
                : 'Waiting for build/catalog.json'}
            </p>
          </section>

          {activeDesign && (
            <>
              <section className="panel-section">
                <div className="section-heading">Position</div>
                <div className="numeric-grid">
                  <NumericField
                    label="X mm"
                    value={placement.positionMm[0]}
                    onChange={(value) => updatePositionAxis(0, value)}
                  />
                  <NumericField
                    label="Y mm"
                    value={placement.positionMm[1]}
                    onChange={(value) => updatePositionAxis(1, value)}
                  />
                  <NumericField
                    label="Z mm"
                    value={placement.positionMm[2]}
                    onChange={(value) => updatePositionAxis(2, value)}
                  />
                </div>
                <button
                  className="wide-button"
                  type="button"
                  onClick={() =>
                    setPosition(activeDesign.id, [
                      placement.positionMm[0],
                      0,
                      placement.positionMm[2],
                    ])
                  }
                >
                  ↓ Snap to floor
                </button>
              </section>

              <section className="panel-section">
                <div className="section-heading">Rotation</div>
                <NumericField
                  label="Y angle °"
                  value={placement.rotationDeg[1]}
                  onChange={updateYaw}
                />
                <div className="button-pair">
                  <button
                    type="button"
                    onClick={() => updateYaw(placement.rotationDeg[1] - 90)}
                  >
                    −90°
                  </button>
                  <button
                    type="button"
                    onClick={() => updateYaw(placement.rotationDeg[1] + 90)}
                  >
                    +90°
                  </button>
                </div>
              </section>

              <section className="panel-section">
                <div className="section-heading">Exact build</div>
                <dl className="spec-list">
                  <div>
                    <dt>Overall</dt>
                    <dd>
                      {activeDesign.overallSizeMm.x} ×{' '}
                      {activeDesign.overallSizeMm.y} ×{' '}
                      {activeDesign.overallSizeMm.z} mm
                    </dd>
                  </div>
                  <div>
                    <dt>Parts</dt>
                    <dd>{activeDesign.partOccurrences} occurrences</dd>
                  </div>
                  <div>
                    <dt>Revision</dt>
                    <dd>{activeDesign.revision}</dd>
                  </div>
                </dl>
              </section>

              <section className="panel-section artifact-list">
                <div className="section-heading">Artifacts</div>
                <ArtifactLink
                  href={activeDesign.artifacts.step}
                  label="Exact STEP"
                />
                <ArtifactLink
                  href={activeDesign.artifacts.bom}
                  label="Cut list CSV"
                />
                <ArtifactLink
                  href={activeDesign.artifacts.manifest}
                  label="Build manifest"
                />
                <ArtifactLink
                  href={activeDesign.artifacts.glb}
                  label="Preview GLB"
                />
              </section>

              <section className="panel-section">
                <button
                  className="wide-button danger"
                  type="button"
                  onClick={() => resetPlacement(activeDesign.id)}
                >
                  Reset placement
                </button>
              </section>
            </>
          )}
        </aside>
      </div>
      <Loader
        containerStyles={{ background: '#0d1116' }}
        innerStyles={{ width: '240px', background: '#28313a' }}
        barStyles={{ background: '#ff9f68' }}
        dataStyles={{
          color: '#dce5ec',
          fontFamily: 'Inter, sans-serif',
        }}
      />
    </main>
  )
}

export default App
