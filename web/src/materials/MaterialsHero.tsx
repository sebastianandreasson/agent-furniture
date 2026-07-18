import type { CatalogDesign } from '../types'
import { formatVolume, rgbaCss } from './inventory'
import type { MaterialsViewModel } from './materialsViewModel'

export function MaterialsHero({
  designs,
  design,
  model,
  onSelectDesign,
}: {
  designs: CatalogDesign[]
  design: CatalogDesign
  model: MaterialsViewModel
  onSelectDesign: (id: string) => void
}) {
  return (
    <section className="mw-hero">
      <div className="mw-hero-copy">
        <p className="eyebrow">Material preview</p>
        <h2>Build inventory</h2>
        <div className="mw-summary-chips" aria-label="Build summary">
          <span>
            <b>{model.partOccurrences}</b>{' '}
            {model.partOccurrences === 1 ? 'piece' : 'pieces'}
          </span>
          <span>
            <b>{model.parts.length}</b> unique{' '}
            {model.parts.length === 1 ? 'part' : 'parts'}
          </span>
          <span>
            <b>{model.materialGroups.length}</b>{' '}
            {model.materialGroups.length === 1 ? 'material' : 'materials'}
          </span>
          <span className="is-accent">
            <b>{model.hardware.totalFasteners}</b>{' '}
            {model.hardware.totalFasteners === 1 ? 'fastener' : 'fasteners'}
          </span>
          <span>
            <b>{formatVolume(model.totalSolidVolumeMm3)}</b> solid volume
          </span>
        </div>
      </div>

      <div className="mw-hero-tools">
        <div className="mw-material-rollup" aria-label="Material summary">
          {model.materialGroups.map((material) => (
            <article key={material.name}>
              <i
                style={{ backgroundColor: rgbaCss(material.colorRgba) }}
                aria-hidden="true"
              />
              <div>
                <strong>{material.name}</strong>
                <small>
                  {material.occurrences}{' '}
                  {material.occurrences === 1 ? 'piece' : 'pieces'} ·{' '}
                  {formatVolume(material.volumeMm3)}
                </small>
              </div>
            </article>
          ))}
        </div>
        <label className="build-select mw-build-select">
          <span>Furniture build</span>
          <select
            value={design.id}
            onChange={(event) => onSelectDesign(event.target.value)}
          >
            {designs.map((candidate) => (
              <option key={candidate.id} value={candidate.id}>
                {candidate.name}
              </option>
            ))}
          </select>
        </label>
      </div>
    </section>
  )
}
