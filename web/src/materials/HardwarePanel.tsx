import type { CatalogDesign } from '../types'
import { formatDimension } from './inventory'
import type { MaterialsHardware } from './materialsViewModel'

export function HardwarePanel({
  design,
  hardware,
}: {
  design: CatalogDesign
  hardware: MaterialsHardware
}) {
  return (
    <section
      id="materials-panel-hardware"
      className="mw-paper-panel mw-hardware-panel"
      role="tabpanel"
      aria-labelledby="materials-tab-hardware"
    >
      <header className="mw-panel-heading">
        <div>
          <p className="eyebrow">Hardware schedule · exact BOM quantities</p>
          <h3>Shopping list</h3>
          <p>
            {hardware.totalFasteners} specified pieces across{' '}
            {hardware.fasteners.length} hardware{' '}
            {hardware.fasteners.length === 1 ? 'type' : 'types'}. Purchase
            allowance is not included.
          </p>
        </div>
        {design.artifacts.hardware && (
          <a
            className="mw-header-link"
            href={design.artifacts.hardware}
            target="_blank"
            rel="noreferrer"
          >
            Hardware CSV ↗
          </a>
        )}
      </header>

      <div className="mw-shopping-list">
        {hardware.fasteners.map((fastener) => (
          <article key={fastener.code}>
            <div className="mw-hardware-quantity">
              <strong>{fastener.quantity}</strong>
              <span>pieces</span>
            </div>
            <div className="mw-hardware-copy">
              <span>{fastener.code}</span>
              <h4>{fastener.description}</h4>
              <div className="mw-hardware-chips">
                <span>{formatDimension(fastener.lengthMm)} mm long</span>
                <span>{fastener.drive}</span>
                <span>{fastener.application}</span>
              </div>
              <p>{fastener.notes}</p>
              {fastener.sourceUrl && (
                <a href={fastener.sourceUrl} target="_blank" rel="noreferrer">
                  {fastener.manufacturer || 'Product'}{' '}
                  {fastener.productCode || 'guidance'} ↗
                </a>
              )}
            </div>
          </article>
        ))}
      </div>

      <section className="mw-drill-key" aria-label="Drill mark legend">
        <div>
          <span className="is-pocket_hole" />
          <strong>Pocket / jig</strong>
          <small>Angled pocket-hole setup</small>
        </div>
        <div>
          <span className="is-countersunk_clearance" />
          <strong>Countersunk</strong>
          <small>Clearance hole with recessed head</small>
        </div>
        <div>
          <span className="is-pilot" />
          <strong>Pilot</strong>
          <small>Straight pilot or receiver hole</small>
        </div>
      </section>

      {(hardware.notes.length > 0 || hardware.status) && (
        <aside className="mw-joinery-caveat">
          <strong>{hardware.status.replaceAll('_', ' ')}</strong>
          <ul>
            {hardware.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </aside>
      )}
    </section>
  )
}
