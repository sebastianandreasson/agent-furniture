import { useEffect, useMemo, useState } from 'react'
import { loadManifest } from '../lib/manifest'
import type {
  CatalogDesign,
  ColorTuple,
  FurnitureManifest,
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

function stockFace(part: ManifestPart): [number, number, number] {
  const [longest, faceWidth, thickness] = [...part.sizeMm].sort(
    (left, right) => right - left,
  )
  return [longest, faceWidth, thickness]
}

function PartSchematic({
  part,
  scale,
  index,
  active,
  onHover,
}: {
  part: ManifestPart
  scale: number
  index: number
  active: boolean
  onHover: (partNumber: string | null) => void
}) {
  const [length, width, thickness] = stockFace(part)
  const drawingWidth = Math.max(2, length * scale)
  const drawingHeight = Math.max(2, width * scale)
  const drawingY = (96 - drawingHeight) / 2

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
      <svg
        viewBox="0 0 360 116"
        role="img"
        aria-label={`${part.description}, quantity ${part.quantity}`}
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
          {formatDimension(length)} mm
        </text>
        <text
          className="schematic-quantity"
          x={Math.min(326, 22 + drawingWidth)}
          y={drawingY + drawingHeight / 2 + 5}
        >
          ×{part.quantity}
        </text>
      </svg>
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
    const longest = Math.max(...faces.map(([length]) => length), 1)
    const widest = Math.max(...faces.map(([, width]) => width), 1)
    return Math.min(270 / longest, 84 / widest)
  }, [sortedParts])
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
              Every unique part, repeated occurrence, stock size, and material
              needed for the selected furniture build.
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
                      Hover a part to locate every occurrence in the model. Use
                      the written millimetre dimensions for fabrication.
                    </p>
                  </div>
                  <div className="schematic-actions">
                    <span>
                      {manifest.parts.length} types · {manifest.partOccurrences}{' '}
                      pieces
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
                <div className="schematic-grid">
                  {sortedParts.map((part, index) => (
                    <PartSchematic
                      key={part.partNumber}
                      part={part}
                      scale={schematicScale}
                      index={index}
                      active={part.partNumber === hoveredPartNumber}
                      onHover={setHoveredPartNumber}
                    />
                  ))}
                </div>
                <p className="schematic-footer">
                  QueryCAD generated inventory · quantities are assembly
                  occurrences · verify joinery, hardware, tolerances, and stock
                  waste separately.
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
