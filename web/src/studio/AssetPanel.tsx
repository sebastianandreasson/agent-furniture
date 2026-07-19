import { STARTER_SPLAT_URL } from '../scene/StarterSplat'
import { useEditorStore } from '../state/editor'
import type { CatalogDesign } from '../types'
import { formatModelName } from './format'

const LAYERS = [
  ['splat', 'Starter splat', 'Online visual reference'],
  ['furniture', 'Furniture', 'Exact CadQuery preview'],
  ['room', 'White room', 'Neutral contrast backdrop'],
  ['grid', '100 mm grid', '1 m major divisions'],
] as const

export function AssetPanel({
  designs,
  activeDesign,
  catalogError,
  splatError,
  onSelectDesign,
}: {
  designs: CatalogDesign[]
  activeDesign: CatalogDesign | null
  catalogError: string | null
  splatError: string | null
  onSelectDesign: (id: string) => void
}) {
  const layers = useEditorStore((state) => state.layers)
  const toggleLayer = useEditorStore((state) => state.toggleLayer)

  return (
    <aside className="panel asset-panel">
      <section className="panel-section">
        <div className="section-heading">
          <span>Furniture builds</span>
          <span className="count-badge">{designs.length}</span>
        </div>
        {catalogError && <p className="inline-error">{catalogError}</p>}
        {designs.map((design) => (
          <button
            className={`build-card ${activeDesign?.id === design.id ? 'is-active' : ''}`}
            key={design.id}
            type="button"
            onClick={() => onSelectDesign(design.id)}
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
        {!catalogError && designs.length === 0 && (
          <p className="empty-state">
            No GLB builds found. Run the model build command.
          </p>
        )}
      </section>

      <section className="panel-section">
        <div className="section-heading">Scene layers</div>
        {LAYERS.map(([key, title, subtitle]) => (
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
            The online splat could not load. Furniture editing remains active.
          </p>
        )}
      </section>

      <section className="panel-section source-note">
        <span className="source-kicker">VISUAL TRUTH · SAMPLE</span>
        <p>
          The starter splat is uncalibrated and never used for measurement or
          collision.
        </p>
        <a href={STARTER_SPLAT_URL} target="_blank" rel="noreferrer">
          View sample source ↗
        </a>
      </section>
    </aside>
  )
}
