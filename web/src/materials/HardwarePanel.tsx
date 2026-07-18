import type { CatalogDesign, ManifestJoinery } from '../types'
import { formatDimension } from './inventory'

export function HardwarePanel({
  design,
  joinery,
}: {
  design: CatalogDesign
  joinery: ManifestJoinery
}) {
  const totalFasteners = joinery.fasteners.reduce(
    (total, fastener) => total + fastener.quantity,
    0,
  )

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
            {totalFasteners} specified pieces across {joinery.fasteners.length}{' '}
            hardware {joinery.fasteners.length === 1 ? 'type' : 'types'}.
            Purchase allowance is not included.
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
        {joinery.fasteners.map((fastener) => (
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

      {(joinery.notes.length > 0 || joinery.status) && (
        <aside className="mw-joinery-caveat">
          <strong>{joinery.status.replaceAll('_', ' ')}</strong>
          <ul>
            {joinery.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </aside>
      )}
    </section>
  )
}
