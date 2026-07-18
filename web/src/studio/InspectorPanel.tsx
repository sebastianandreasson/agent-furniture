import { DEFAULT_PLACEMENT, useEditorStore } from '../state/editor'
import type { CatalogDesign, Vector3Tuple } from '../types'
import { formatModelName } from './format'
import { ArtifactLink, NumericField } from './presentation'

export function InspectorPanel({ design }: { design: CatalogDesign | null }) {
  const placements = useEditorStore((state) => state.placements)
  const setPosition = useEditorStore((state) => state.setPosition)
  const setRotation = useEditorStore((state) => state.setRotation)
  const resetPlacement = useEditorStore((state) => state.resetPlacement)
  const placement = design
    ? (placements[design.id] ?? DEFAULT_PLACEMENT)
    : DEFAULT_PLACEMENT

  const updatePositionAxis = (axis: number, value: number) => {
    if (!design || !Number.isFinite(value)) return
    const next = [...placement.positionMm] as Vector3Tuple
    next[axis] = value
    setPosition(design.id, next)
  }

  const updateYaw = (value: number) => {
    if (!design || !Number.isFinite(value)) return
    setRotation(design.id, [0, value, 0])
  }

  return (
    <aside className="panel inspector-panel">
      <section className="panel-section inspector-title">
        <p className="eyebrow">Selected object</p>
        <h2>{design?.name ?? 'No furniture build'}</h2>
        <p>
          {design
            ? formatModelName(design.model)
            : 'Waiting for build/catalog.json'}
        </p>
      </section>

      {design && (
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
                setPosition(design.id, [
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
                  {design.overallSizeMm.x} × {design.overallSizeMm.y} ×{' '}
                  {design.overallSizeMm.z} mm
                </dd>
              </div>
              <div>
                <dt>Parts</dt>
                <dd>{design.partOccurrences} occurrences</dd>
              </div>
              <div>
                <dt>Revision</dt>
                <dd>{design.revision}</dd>
              </div>
            </dl>
          </section>

          <section className="panel-section">
            <div className="section-heading">Resolved parameters</div>
            <dl className="spec-list">
              {Object.entries(design.parameters)
                .sort(([left], [right]) => left.localeCompare(right))
                .map(([name, value]) => (
                  <div key={name}>
                    <dt>{formatModelName(name)}</dt>
                    <dd>{value}</dd>
                  </div>
                ))}
            </dl>
          </section>

          <section className="panel-section artifact-list">
            <div className="section-heading">Artifacts</div>
            <ArtifactLink href={design.artifacts.step} label="Exact STEP" />
            <ArtifactLink href={design.artifacts.bom} label="Cut list CSV" />
            <ArtifactLink
              href={design.artifacts.manifest}
              label="Build manifest"
            />
            <ArtifactLink href={design.artifacts.glb} label="Preview GLB" />
          </section>

          <section className="panel-section">
            <button
              className="wide-button danger"
              type="button"
              onClick={() => resetPlacement(design.id)}
            >
              Reset placement
            </button>
          </section>
        </>
      )}
    </aside>
  )
}
