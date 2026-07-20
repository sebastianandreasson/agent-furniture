import { ROOM_SPLAT } from '../scene/roomSplatConfig'
import { useEditorStore } from '../state/editor'
import type { CatalogDesign } from '../types'
import { VariantSelect } from '../VariantSelect'
import { groupDesignFamilies } from '../variants'
import { formatModelName } from './format'

const LAYERS = [
  ['splat', 'Room capture', 'Real photographs · local SPZ'],
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
  const families = groupDesignFamilies(designs)

  return (
    <aside className="panel asset-panel">
      <section className="panel-section">
        <div className="section-heading">
          <span>Furniture families</span>
          <span className="count-badge">{families.length}</span>
        </div>
        {catalogError && <p className="inline-error">{catalogError}</p>}
        {families.map((family) => {
          const selected =
            family.designs.find((design) => design.id === activeDesign?.id) ??
            family.designs[0]
          const isActive = activeDesign?.familyId === family.id
          return (
            <div className="build-family" key={family.id}>
              <button
                className={`build-card ${isActive ? 'is-active' : ''}`}
                type="button"
                onClick={() => onSelectDesign(selected.id)}
              >
                <span className="build-icon" aria-hidden="true">
                  ▱
                </span>
                <span className="build-copy">
                  <strong>{formatModelName(family.id)}</strong>
                  <small>
                    {family.designs.length > 1
                      ? selected.variantLabel
                      : formatModelName(selected.model)}
                  </small>
                </span>
                <span className="revision">
                  {selected.revision.slice(0, 5)}
                </span>
              </button>
              {isActive && activeDesign && (
                <VariantSelect
                  designs={designs}
                  activeDesign={activeDesign}
                  onSelectDesign={onSelectDesign}
                  className="asset-variant-select"
                />
              )}
            </div>
          )
        })}
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
            aria-pressed={layers[key]}
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
            The room capture could not load. Furniture editing remains active.
            <small>{splatError}</small>
          </p>
        )}
      </section>

      <section className="panel-section source-note">
        <span className="source-kicker">VISUAL CONTEXT · SAMPLE</span>
        <p>
          The included real-photo room is visually registered to the millimetre
          workspace, not survey geometry or collision authority.
        </p>
        <a href={ROOM_SPLAT.sourceUrl} target="_blank" rel="noreferrer">
          View room source ↗
        </a>
        <a href={ROOM_SPLAT.datasetUrl} target="_blank" rel="noreferrer">
          Mip-NeRF 360 dataset ↗
        </a>
        <a href={ROOM_SPLAT.rendererUrl} target="_blank" rel="noreferrer">
          Spark renderer (MIT) ↗
        </a>
      </section>
    </aside>
  )
}
