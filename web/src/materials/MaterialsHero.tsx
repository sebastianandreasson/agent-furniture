import type { CatalogDesign } from '../types'
import { VariantSelect } from '../VariantSelect'
import {
  formatFurnitureName,
  groupDesignFamilies,
  selectFamilyDesign,
} from '../variants'
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
  const families = groupDesignFamilies(designs)

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
        <div className="mw-design-picker">
          <label className="build-select mw-build-select">
            <span>Furniture</span>
            <select
              value={design.familyId}
              onChange={(event) => {
                const family = families.find(
                  (candidate) => candidate.id === event.target.value,
                )
                if (family) {
                  onSelectDesign(
                    selectFamilyDesign(family, design.variantId).id,
                  )
                }
              }}
            >
              {families.map((family) => (
                <option key={family.id} value={family.id}>
                  {formatFurnitureName(family.id)}
                </option>
              ))}
            </select>
          </label>
          <VariantSelect
            designs={designs}
            activeDesign={design}
            onSelectDesign={onSelectDesign}
            className="materials-variant-select"
          />
        </div>
      </div>
    </section>
  )
}
