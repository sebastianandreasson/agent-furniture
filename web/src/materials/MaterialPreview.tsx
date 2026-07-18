import { useEffect, useMemo, useState } from 'react'
import { loadManifest } from '../lib/manifest'
import type {
  AxisName,
  CatalogDesign,
  ColorTuple,
  FurnitureManifest,
  ManifestDrillOperation,
  ManifestPart,
} from '../types'
import { AssemblyPreview } from './AssemblyPreview'

type MaterialPreviewProps = {
  designs: CatalogDesign[]
  activeDesign: CatalogDesign | null
  onSelectDesign: (id: string) => void
}

type MaterialSummary = {
  name: string
  colorRgba: ColorTuple
  occurrences: number
  partTypes: number
  volumeMm3: number
}

function rgbaCss([red, green, blue, alpha]: ColorTuple) {
  const channel = (value: number) =>
    Math.round(Math.min(1, Math.max(0, value)) * 255)
  return `rgba(${channel(red)}, ${channel(green)}, ${channel(blue)}, ${Math.min(1, Math.max(0, alpha))})`
}

function formatDimension(value: number) {
  return new Intl.NumberFormat('en', { maximumFractionDigits: 1 }).format(value)
}

function formatVolume(volumeMm3: number) {
  const litres = volumeMm3 / 1_000_000
  if (litres >= 0.1) return `${litres.toFixed(litres >= 10 ? 1 : 2)} L`
  return `${Math.round(volumeMm3 / 1_000)} cm³`
}

function summarizeMaterials(parts: ManifestPart[]): MaterialSummary[] {
  const groups = new Map<string, MaterialSummary>()
  for (const part of parts) {
    const current = groups.get(part.material) ?? {
      name: part.material,
      colorRgba: part.colorRgba,
      occurrences: 0,
      partTypes: 0,
      volumeMm3: 0,
    }
    current.occurrences += part.quantity
    current.partTypes += 1
    current.volumeMm3 += part.unitVolumeMm3 * part.quantity
    groups.set(part.material, current)
  }
  return [...groups.values()].sort((left, right) =>
    left.name.localeCompare(right.name),
  )
}

const AXES: AxisName[] = ['x', 'y', 'z']

type StockFace = {
  length: number
  width: number
  thickness: number
  lengthAxis: AxisName
  widthAxis: AxisName
}

function axisIndex(axis: AxisName) {
  return AXES.indexOf(axis)
}

function stockFace(part: ManifestPart): StockFace {
  const dimensions = AXES.map((axis, index) => ({
    axis,
    value: part.sizeMm[index],
  })).sort((left, right) => right.value - left.value)
  return {
    length: dimensions[0].value,
    width: dimensions[1].value,
    thickness: dimensions[2].value,
    lengthAxis: dimensions[0].axis,
    widthAxis: dimensions[1].axis,
  }
}

function groupDrillOperations(
  part: ManifestPart,
  operations: ManifestDrillOperation[],
) {
  const primary = stockFace(part)
  const groups = new Map<string, ManifestDrillOperation[]>()
  for (const operation of operations) {
    const key = operation.viewAxes.join('')
    const current = groups.get(key) ?? []
    current.push(operation)
    groups.set(key, current)
  }
  const primaryKey = `${primary.lengthAxis}${primary.widthAxis}`
  if (!groups.has(primaryKey)) groups.set(primaryKey, [])
  return [...groups.entries()].sort(([left], [right]) => {
    if (left === primaryKey) return -1
    if (right === primaryKey) return 1
    return left.localeCompare(right)
  })
}

function operationSpecification(operation: ManifestDrillOperation) {
  const details = [`Ø${formatDimension(operation.diameterMm)}`]
  if (operation.countersinkDiameterMm !== null) {
    details.push(`CSK Ø${formatDimension(operation.countersinkDiameterMm)}`)
  }
  if (operation.depthMm !== null) {
    details.push(`${formatDimension(operation.depthMm)} deep`)
  } else if (operation.kind === 'pocket_hole') {
    details.push('jig depth')
  }
  if (operation.angleDeg !== null) {
    details.push(`${formatDimension(operation.angleDeg)}°`)
  }
  return details.join(' · ')
}

function coordinateSummary(operation: ManifestDrillOperation) {
  const [horizontalAxis, verticalAxis] = operation.viewAxes
  const horizontalIndex = axisIndex(horizontalAxis)
  const verticalIndex = axisIndex(verticalAxis)
  const pointText = (index: number) => {
    const point = operation.points[index]
    return `${horizontalAxis.toUpperCase()} ${formatDimension(point.positionMm[horizontalIndex])} / ${verticalAxis.toUpperCase()} ${formatDimension(point.positionMm[verticalIndex])}`
  }
  if (operation.points.length <= 4) {
    return operation.points.map((_, index) => pointText(index)).join(' · ')
  }
  return `${operation.points.length} centres · ${pointText(0)} → ${pointText(operation.points.length - 1)}`
}

function FaceDiagram({
  part,
  operations,
  axes,
  scale,
  primary,
}: {
  part: ManifestPart
  operations: ManifestDrillOperation[]
  axes: [AxisName, AxisName]
  scale: number
  primary: boolean
}) {
  const [lengthAxis, widthAxis] = axes
  const length = part.sizeMm[axisIndex(lengthAxis)]
  const width = part.sizeMm[axisIndex(widthAxis)]
  const drawingWidth = Math.max(2, length * scale)
  const drawingHeight = Math.max(2, width * scale)
  const drawingY = (96 - drawingHeight) / 2
  const markers = operations.flatMap((operation) =>
    operation.points.map((point, pointIndex) => ({
      operation,
      point,
      pointIndex,
    })),
  )

  return (
    <div className="schematic-face">
      <span className="schematic-face-label">
        {operations.length > 0
          ? [...new Set(operations.map((operation) => operation.face))].join(
              ' + ',
            )
          : `${lengthAxis}${widthAxis} stock face`}
      </span>
      <svg
        viewBox="0 0 360 116"
        role={primary ? 'img' : 'presentation'}
        aria-label={
          primary ? `${part.description}, quantity ${part.quantity}` : undefined
        }
      >
        <rect
          x="12"
          y={drawingY}
          width={drawingWidth}
          height={drawingHeight}
          rx="2"
          fill={rgbaCss(part.colorRgba)}
          fillOpacity="0.72"
          stroke="currentColor"
          strokeWidth="1"
        />
        {markers.map(({ operation, point, pointIndex }, markerIndex) => {
          const x = 12 + point.positionMm[axisIndex(lengthAxis)] * scale
          const y =
            drawingY +
            drawingHeight -
            point.positionMm[axisIndex(widthAxis)] * scale
          return (
            <g
              className={`drill-marker is-${operation.kind}`}
              key={`${operation.operationId}-${pointIndex}`}
              transform={`translate(${x} ${y})`}
            >
              <circle r={operation.kind === 'pilot' ? 3.2 : 5.1} />
              <line x1="-7" y1="0" x2="7" y2="0" />
              <line x1="0" y1="-7" x2="0" y2="7" />
              <text x="7" y="-6">
                {markerIndex + 1}
              </text>
            </g>
          )
        })}
        <line
          x1="12"
          y1="104"
          x2={12 + drawingWidth}
          y2="104"
          stroke="currentColor"
          strokeWidth="0.75"
        />
        <line x1="12" y1="100" x2="12" y2="108" stroke="currentColor" />
        <line
          x1={12 + drawingWidth}
          y1="100"
          x2={12 + drawingWidth}
          y2="108"
          stroke="currentColor"
        />
        <text x={12 + drawingWidth / 2} y="114" textAnchor="middle">
          {formatDimension(length)} mm ({lengthAxis.toUpperCase()})
        </text>
        {primary && (
          <text
            className="schematic-quantity"
            x={Math.min(326, 22 + drawingWidth)}
            y={drawingY + drawingHeight / 2 + 5}
          >
            ×{part.quantity}
          </text>
        )}
      </svg>
    </div>
  )
}

function PartSchematic({
  part,
  scale,
  index,
  active,
  onHover,
  drillOperations,
}: {
  part: ManifestPart
  scale: number
  index: number
  active: boolean
  onHover: (partNumber: string | null) => void
  drillOperations: ManifestDrillOperation[]
}) {
  const { length, width, thickness } = stockFace(part)
  const faceGroups = groupDrillOperations(part, drillOperations)

  return (
    <button
      className={`schematic-piece ${active ? 'is-active' : ''}`}
      type="button"
      aria-label={`${part.description}, quantity ${part.quantity}`}
      aria-pressed={active}
      onPointerEnter={() => onHover(part.partNumber)}
      onPointerLeave={() => onHover(null)}
      onFocus={() => onHover(part.partNumber)}
      onBlur={() => onHover(null)}
    >
      <div className="schematic-piece-heading">
        <div>
          <span>
            {String(index + 1).padStart(2, '0')} · {part.partNumber}
          </span>
          <strong>{part.description}</strong>
        </div>
        <b>×{part.quantity}</b>
      </div>
      {faceGroups.map(([key, operations], faceIndex) => (
        <FaceDiagram
          key={key}
          part={part}
          operations={operations}
          axes={key.split('') as [AxisName, AxisName]}
          scale={scale}
          primary={faceIndex === 0}
        />
      ))}
      <div className="drill-operation-list">
        {drillOperations.map((operation) => (
          <div
            className={`drill-operation is-${operation.kind}`}
            key={operation.operationId}
          >
            <span>
              <i aria-hidden="true" />
              {operation.label}
            </span>
            <strong>
              {operationSpecification(operation)} · {operation.pointsPerPart}
              /part
            </strong>
            <small>{coordinateSummary(operation)}</small>
          </div>
        ))}
        {drillOperations.length === 0 && (
          <span className="no-drill-operation">No drilling on this part</span>
        )}
      </div>
      <div className="schematic-piece-meta">
        <span>{part.material}</span>
        <span>
          {formatDimension(length)} × {formatDimension(width)} ×{' '}
          {formatDimension(thickness)} mm
        </span>
      </div>
    </button>
  )
}

export function MaterialPreview({
  designs,
  activeDesign,
  onSelectDesign,
}: MaterialPreviewProps) {
  const [manifest, setManifest] = useState<FurnitureManifest | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState(0)
  const [hoveredPartNumber, setHoveredPartNumber] = useState<string | null>(
    null,
  )

  useEffect(() => {
    if (!activeDesign) {
      setManifest(null)
      return
    }

    const controller = new AbortController()
    setManifest(null)
    setError(null)
    setHoveredPartNumber(null)
    void loadManifest(activeDesign, controller.signal)
      .then(setManifest)
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === 'AbortError')
          return
        setError(
          reason instanceof Error
            ? reason.message
            : 'Could not load the part inventory.',
        )
      })
    return () => controller.abort()
  }, [activeDesign, refreshToken])

  const materialSummaries = useMemo(
    () => summarizeMaterials(manifest?.parts ?? []),
    [manifest],
  )
  const sortedParts = useMemo(
    () =>
      [...(manifest?.parts ?? [])].sort(
        (left, right) =>
          left.material.localeCompare(right.material) ||
          left.partNumber.localeCompare(right.partNumber),
      ),
    [manifest],
  )
  const totalSolidVolume = materialSummaries.reduce(
    (total, material) => total + material.volumeMm3,
    0,
  )
  const schematicScale = useMemo(() => {
    const faces = sortedParts.map(stockFace)
    const longest = Math.max(...faces.map((face) => face.length), 1)
    const widest = Math.max(...faces.map((face) => face.width), 1)
    return Math.min(270 / longest, 84 / widest)
  }, [sortedParts])
  const drillOperationsByPart = useMemo(() => {
    const operations = new Map<string, ManifestDrillOperation[]>()
    for (const operation of manifest?.joinery.drillOperations ?? []) {
      const current = operations.get(operation.partNumber) ?? []
      current.push(operation)
      operations.set(operation.partNumber, current)
    }
    return operations
  }, [manifest])
  const totalFasteners =
    manifest?.joinery.fasteners.reduce(
      (total, fastener) => total + fastener.quantity,
      0,
    ) ?? 0
  const hoveredPart =
    sortedParts.find((part) => part.partNumber === hoveredPartNumber) ?? null

  return (
    <div className="materials-page">
      <div className="materials-inner">
        <section className="materials-hero">
          <div>
            <p className="eyebrow">Material preview</p>
            <h2>Build inventory</h2>
            <p>
              Every unique part, repeated occurrence, stock size, material,
              fastener, and drilling operation for the selected furniture build.
            </p>
          </div>
          <label className="build-select">
            <span>Furniture build</span>
            <select
              value={activeDesign?.id ?? ''}
              onChange={(event) => onSelectDesign(event.target.value)}
            >
              {designs.map((design) => (
                <option key={design.id} value={design.id}>
                  {design.name}
                </option>
              ))}
            </select>
          </label>
        </section>

        {!activeDesign && (
          <div className="materials-message">
            Build a furniture design to see its material inventory.
          </div>
        )}

        {activeDesign && !manifest && !error && (
          <div className="materials-message is-loading">
            Reading the generated part manifest…
          </div>
        )}

        {error && (
          <div className="materials-message is-error" role="alert">
            <span>{error}</span>
            <button
              type="button"
              onClick={() => setRefreshToken((value) => value + 1)}
            >
              Try again
            </button>
          </div>
        )}

        {activeDesign && manifest && (
          <>
            <section
              className="inventory-summary"
              aria-label="Inventory summary"
            >
              <article>
                <span>Assembly pieces</span>
                <strong>{manifest.partOccurrences}</strong>
                <small>individual occurrences</small>
              </article>
              <article>
                <span>Unique parts</span>
                <strong>{manifest.parts.length}</strong>
                <small>cut or purchased types</small>
              </article>
              <article>
                <span>Materials</span>
                <strong>{materialSummaries.length}</strong>
                <small>specified finishes</small>
              </article>
              <article>
                <span>Solid volume</span>
                <strong>{formatVolume(totalSolidVolume)}</strong>
                <small>geometry, not purchase volume</small>
              </article>
            </section>

            <section className="materials-section">
              <div className="materials-section-heading">
                <div>
                  <p className="eyebrow">Material roll-up</p>
                  <h3>What it is made from</h3>
                </div>
                <span>{materialSummaries.length} specifications</span>
              </div>
              <div className="material-card-grid">
                {materialSummaries.map((material) => (
                  <article className="material-card" key={material.name}>
                    <span
                      className="material-swatch"
                      style={{ backgroundColor: rgbaCss(material.colorRgba) }}
                      aria-hidden="true"
                    />
                    <div>
                      <h4>{material.name}</h4>
                      <p>
                        {material.occurrences} pieces · {material.partTypes}{' '}
                        part {material.partTypes === 1 ? 'type' : 'types'}
                      </p>
                    </div>
                    <strong>{formatVolume(material.volumeMm3)}</strong>
                  </article>
                ))}
              </div>
            </section>

            <div className="schematic-workbench">
              <section className="materials-section schematic-document">
                <div className="schematic-document-header">
                  <div>
                    <p className="eyebrow">Interactive build document</p>
                    <h3>Part schematic</h3>
                    <p>
                      Hover a part to locate every occurrence in the model.
                      Crosshairs show hole centres from the cut-stock minimum
                      corner.
                    </p>
                  </div>
                  <div className="schematic-actions">
                    <span>
                      {manifest.parts.length} types · {totalFasteners} screws
                    </span>
                    <button type="button" onClick={() => window.print()}>
                      Print / save PDF
                    </button>
                  </div>
                </div>
                <div className="schematic-build-meta">
                  <span>{activeDesign.name}</span>
                  <span>Revision {activeDesign.revision}</span>
                  <span>Units: millimetres</span>
                </div>
                {manifest.joinery.fasteners.length > 0 && (
                  <section
                    className="hardware-schedule"
                    aria-label="Hardware schedule"
                  >
                    <div className="document-subheading">
                      <div>
                        <p className="eyebrow">Fastener schedule</p>
                        <h4>{totalFasteners} screws specified</h4>
                      </div>
                      <div
                        className="drill-legend"
                        aria-label="Drill mark legend"
                      >
                        <span className="is-pocket_hole">Pocket / jig</span>
                        <span className="is-countersunk_clearance">
                          Countersunk
                        </span>
                        <span className="is-pilot">Pilot</span>
                      </div>
                    </div>
                    <div className="hardware-grid">
                      {manifest.joinery.fasteners.map((fastener) => (
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
                            <a
                              href={fastener.sourceUrl}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {fastener.manufacturer}{' '}
                              {fastener.productCode || 'guidance'} ↗
                            </a>
                          )}
                        </article>
                      ))}
                    </div>
                    {activeDesign.artifacts.hardware && (
                      <a
                        className="hardware-download"
                        href={activeDesign.artifacts.hardware}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Download hardware CSV ↗
                      </a>
                    )}
                  </section>
                )}
                <div className="schematic-grid">
                  {sortedParts.map((part, index) => (
                    <PartSchematic
                      key={part.partNumber}
                      part={part}
                      scale={schematicScale}
                      index={index}
                      active={part.partNumber === hoveredPartNumber}
                      onHover={setHoveredPartNumber}
                      drillOperations={
                        drillOperationsByPart.get(part.partNumber) ?? []
                      }
                    />
                  ))}
                </div>
                {manifest.joinery.joints.length > 0 && (
                  <section
                    className="joint-schedule"
                    aria-label="Assembly joint schedule"
                  >
                    <div className="document-subheading">
                      <div>
                        <p className="eyebrow">Assembly sequence</p>
                        <h4>
                          {manifest.joinery.joints.length} connection groups
                        </h4>
                      </div>
                      <span>Hover a row to locate its drilled part</span>
                    </div>
                    <div className="joint-list">
                      {manifest.joinery.joints.map((joint) => (
                        <div
                          className="joint-row"
                          key={joint.jointId}
                          onPointerEnter={() =>
                            setHoveredPartNumber(joint.sourcePartNumber)
                          }
                          onPointerLeave={() => setHoveredPartNumber(null)}
                        >
                          <b>{String(joint.assemblyStep).padStart(2, '0')}</b>
                          <div>
                            <strong>{joint.description}</strong>
                            <span>
                              {joint.sourcePartNumber} →{' '}
                              {joint.targetPartNumber}
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
                {manifest.joinery.notes.length > 0 && (
                  <aside className="joinery-caveat">
                    <strong>
                      {manifest.joinery.status.replaceAll('_', ' ')}
                    </strong>
                    <ul>
                      {manifest.joinery.notes.map((note) => (
                        <li key={note}>{note}</li>
                      ))}
                    </ul>
                  </aside>
                )}
                <p className="schematic-footer">
                  QueryCAD generated inventory and prototype joinery schedule ·
                  dimensions are from nominal cut stock · always test drilling
                  and screw settings on matching offcuts.
                </p>
              </section>

              <AssemblyPreview
                design={activeDesign}
                selectedPart={hoveredPart}
              />
            </div>

            <section className="materials-section assembly-section">
              <div className="materials-section-heading">
                <div>
                  <p className="eyebrow">Assembly inventory</p>
                  <h3>Parts to put together</h3>
                </div>
                <div className="inventory-actions">
                  <span>Revision {activeDesign.revision.slice(0, 8)}</span>
                  {activeDesign.artifacts.bom && (
                    <a
                      href={activeDesign.artifacts.bom}
                      target="_blank"
                      rel="noreferrer"
                    >
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
                    {sortedParts.map((part) => (
                      <tr key={part.partNumber}>
                        <td>
                          <span className="part-number">{part.partNumber}</span>
                          <strong>{part.description}</strong>
                        </td>
                        <td>
                          <span className="material-name">
                            <i
                              style={{
                                backgroundColor: rgbaCss(part.colorRgba),
                              }}
                              aria-hidden="true"
                            />
                            {part.material}
                          </span>
                        </td>
                        <td className="part-dimensions">
                          {part.sizeMm.map(formatDimension).join(' × ')} mm
                        </td>
                        <td>
                          <strong className="quantity-badge">
                            ×{part.quantity}
                          </strong>
                        </td>
                        <td>
                          {formatVolume(part.unitVolumeMm3 * part.quantity)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="inventory-note">
                Quantities count placed occurrences. Solid volume comes from
                finished CAD geometry and does not include stock waste,
                upholstery allowances, hardware, joinery, or machining
                tolerances.
              </p>
            </section>
          </>
        )}
      </div>
    </div>
  )
}
