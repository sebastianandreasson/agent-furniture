import type { ManifestJoinery } from '../types'
import { formatDimension } from './inventory'

export function HardwareSchedule({
  joinery,
  hardwareArtifact,
}: {
  joinery: ManifestJoinery
  hardwareArtifact?: string
}) {
  if (joinery.fasteners.length === 0) return null
  const totalFasteners = joinery.fasteners.reduce(
    (total, fastener) => total + fastener.quantity,
    0,
  )

  return (
    <section className="hardware-schedule" aria-label="Hardware schedule">
      <div className="document-subheading">
        <div>
          <p className="eyebrow">Fastener schedule</p>
          <h4>{totalFasteners} screws specified</h4>
        </div>
        <div className="drill-legend" aria-label="Drill mark legend">
          <span className="is-pocket_hole">Pocket / jig</span>
          <span className="is-countersunk_clearance">Countersunk</span>
          <span className="is-pilot">Pilot</span>
        </div>
      </div>
      <div className="hardware-grid">
        {joinery.fasteners.map((fastener) => (
          <article className="hardware-card" key={fastener.code}>
            <div>
              <span>{fastener.code}</span>
              <strong>×{fastener.quantity}</strong>
            </div>
            <h5>{fastener.description}</h5>
            <dl>
              <div>
                <dt>Length</dt>
                <dd>{formatDimension(fastener.lengthMm)} mm</dd>
              </div>
              <div>
                <dt>Drive</dt>
                <dd>{fastener.drive}</dd>
              </div>
              <div>
                <dt>Use</dt>
                <dd>{fastener.application}</dd>
              </div>
            </dl>
            <p>{fastener.notes}</p>
            {fastener.sourceUrl && (
              <a href={fastener.sourceUrl} target="_blank" rel="noreferrer">
                {fastener.manufacturer} {fastener.productCode || 'guidance'} ↗
              </a>
            )}
          </article>
        ))}
      </div>
      {hardwareArtifact && (
        <a
          className="hardware-download"
          href={hardwareArtifact}
          target="_blank"
          rel="noreferrer"
        >
          Download hardware CSV ↗
        </a>
      )}
    </section>
  )
}

export function JointSchedule({
  joinery,
  onHover,
}: {
  joinery: ManifestJoinery
  onHover: (partNumber: string | null) => void
}) {
  return (
    <>
      {joinery.joints.length > 0 && (
        <section
          className="joint-schedule"
          aria-label="Assembly joint schedule"
        >
          <div className="document-subheading">
            <div>
              <p className="eyebrow">Assembly sequence</p>
              <h4>{joinery.joints.length} connection groups</h4>
            </div>
            <span>Hover a row to locate its drilled part</span>
          </div>
          <div className="joint-list">
            {joinery.joints.map((joint) => (
              <div
                className="joint-row"
                key={joint.jointId}
                onPointerEnter={() => onHover(joint.sourcePartNumber)}
                onPointerLeave={() => onHover(null)}
              >
                <b>{String(joint.assemblyStep).padStart(2, '0')}</b>
                <div>
                  <strong>{joint.description}</strong>
                  <span>
                    {joint.sourcePartNumber} → {joint.targetPartNumber}
                  </span>
                </div>
                <small>
                  {joint.fastenerCode} ×{joint.quantity}
                </small>
              </div>
            ))}
          </div>
        </section>
      )}
      {joinery.notes.length > 0 && (
        <aside className="joinery-caveat">
          <strong>{joinery.status.replaceAll('_', ' ')}</strong>
          <ul>
            {joinery.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </aside>
      )}
    </>
  )
}
