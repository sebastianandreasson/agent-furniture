import type { CatalogDesign, ManifestPart } from '../types'
import {
  formatDimension,
  formatVolume,
  rgbaCss,
  type MaterialSummary,
} from './inventory'

export function InventorySummary({
  partOccurrences,
  uniqueParts,
  materials,
  totalSolidVolume,
}: {
  partOccurrences: number
  uniqueParts: number
  materials: number
  totalSolidVolume: number
}) {
  return (
    <section className="inventory-summary" aria-label="Inventory summary">
      <article>
        <span>Assembly pieces</span>
        <strong>{partOccurrences}</strong>
        <small>individual occurrences</small>
      </article>
      <article>
        <span>Unique parts</span>
        <strong>{uniqueParts}</strong>
        <small>cut or purchased types</small>
      </article>
      <article>
        <span>Materials</span>
        <strong>{materials}</strong>
        <small>specified finishes</small>
      </article>
      <article>
        <span>Solid volume</span>
        <strong>{formatVolume(totalSolidVolume)}</strong>
        <small>geometry, not purchase volume</small>
      </article>
    </section>
  )
}

export function MaterialRollup({
  materials,
}: {
  materials: MaterialSummary[]
}) {
  return (
    <section className="materials-section">
      <div className="materials-section-heading">
        <div>
          <p className="eyebrow">Material roll-up</p>
          <h3>What it is made from</h3>
        </div>
        <span>{materials.length} specifications</span>
      </div>
      <div className="material-card-grid">
        {materials.map((material) => (
          <article className="material-card" key={material.name}>
            <span
              className="material-swatch"
              style={{ backgroundColor: rgbaCss(material.colorRgba) }}
              aria-hidden="true"
            />
            <div>
              <h4>{material.name}</h4>
              <p>
                {material.occurrences} pieces · {material.partTypes} part{' '}
                {material.partTypes === 1 ? 'type' : 'types'}
              </p>
            </div>
            <strong>{formatVolume(material.volumeMm3)}</strong>
          </article>
        ))}
      </div>
    </section>
  )
}

export function PartsInventory({
  design,
  parts,
}: {
  design: CatalogDesign
  parts: ManifestPart[]
}) {
  return (
    <section className="materials-section assembly-section">
      <div className="materials-section-heading">
        <div>
          <p className="eyebrow">Assembly inventory</p>
          <h3>Parts to put together</h3>
        </div>
        <div className="inventory-actions">
          <span>Revision {design.revision.slice(0, 8)}</span>
          {design.artifacts.bom && (
            <a href={design.artifacts.bom} target="_blank" rel="noreferrer">
              Download CSV ↗
            </a>
          )}
        </div>
      </div>

      <div className="parts-table-wrap">
        <table className="parts-table">
          <thead>
            <tr>
              <th scope="col">Part</th>
              <th scope="col">Material</th>
              <th scope="col">Stock size</th>
              <th scope="col">Qty</th>
              <th scope="col">Solid volume</th>
            </tr>
          </thead>
          <tbody>
            {parts.map((part) => (
              <tr key={part.partNumber}>
                <td>
                  <span className="part-number">{part.partNumber}</span>
                  <strong>{part.description}</strong>
                </td>
                <td>
                  <span className="material-name">
                    <i
                      style={{ backgroundColor: rgbaCss(part.colorRgba) }}
                      aria-hidden="true"
                    />
                    {part.material}
                  </span>
                </td>
                <td className="part-dimensions">
                  {part.sizeMm.map(formatDimension).join(' × ')} mm
                </td>
                <td>
                  <strong className="quantity-badge">×{part.quantity}</strong>
                </td>
                <td>{formatVolume(part.unitVolumeMm3 * part.quantity)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="inventory-note">
        Quantities count placed occurrences. Solid volume comes from finished
        CAD geometry and does not include stock waste, upholstery allowances,
        hardware, joinery, or machining tolerances.
      </p>
    </section>
  )
}
