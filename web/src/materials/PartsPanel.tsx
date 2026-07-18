import { useState } from 'react'
import type { CatalogDesign, ManifestDrillOperation } from '../types'
import { operationSpecification } from './drilling'
import { formatDimension, formatVolume, rgbaCss } from './inventory'
import type { MaterialGroup } from './materialsViewModel'
import { PartDetailModal } from './PartDetailModal'
import { PartSchematic } from './PartSchematic'

export type PartsView = 'cards' | 'cut-list'

function drillingSummary(operations: ManifestDrillOperation[]) {
  if (operations.length === 0) return 'No drilling'
  const holes = operations.reduce(
    (total, operation) => total + operation.totalHoles,
    0,
  )
  return `${operations.length} setup${operations.length === 1 ? '' : 's'} · ${holes} holes`
}

export function PartsPanel({
  design,
  groups,
  scale,
  selectedPartNumber,
  drillOperationsByPart,
  view,
  showCoordinates,
  onViewChange,
  onCoordinatesChange,
  onHoverPart,
}: {
  design: CatalogDesign
  groups: MaterialGroup[]
  scale: number
  selectedPartNumber: string | null
  drillOperationsByPart: Map<string, ManifestDrillOperation[]>
  view: PartsView
  showCoordinates: boolean
  onViewChange: (view: PartsView) => void
  onCoordinatesChange: (show: boolean) => void
  onHoverPart: (partNumber: string | null) => void
}) {
  const [detailPartNumber, setDetailPartNumber] = useState<string | null>(null)
  const allParts = groups.flatMap((group) => group.parts)
  const detailPart =
    allParts.find((part) => part.partNumber === detailPartNumber) ?? null
  let partIndex = 0

  return (
    <>
      <section
        id="materials-panel-parts"
        className="mw-paper-panel mw-parts-panel"
        role="tabpanel"
        aria-labelledby="materials-tab-parts"
      >
        <header className="mw-panel-heading">
          <div>
            <p className="eyebrow">
              Part schematic · millimetres · rev {design.revision.slice(0, 8)}
            </p>
            <h3>Every part, by material</h3>
            <p>
              Hover a part to locate it in the model; click it for hole-by-hole
              dimensions.
            </p>
          </div>
          <div className="mw-parts-actions">
            <label>
              <input
                type="checkbox"
                checked={showCoordinates}
                onChange={(event) =>
                  onCoordinatesChange(event.currentTarget.checked)
                }
              />
              Drill coordinates
            </label>
            <div className="mw-segmented" aria-label="Parts presentation">
              <button
                type="button"
                aria-pressed={view === 'cards'}
                onClick={() => onViewChange('cards')}
              >
                Cards
              </button>
              <button
                type="button"
                aria-pressed={view === 'cut-list'}
                onClick={() => onViewChange('cut-list')}
              >
                Cut list
              </button>
            </div>
            {design.artifacts.bom && (
              <a href={design.artifacts.bom} target="_blank" rel="noreferrer">
                CSV ↗
              </a>
            )}
            <button
              className="mw-print-button"
              type="button"
              onClick={() => window.print()}
            >
              Print / PDF
            </button>
          </div>
        </header>

        {groups.map((group) => (
          <section className="mw-material-group" key={group.name}>
            <header>
              <i
                style={{ backgroundColor: rgbaCss(group.colorRgba) }}
                aria-hidden="true"
              />
              <strong>{group.name}</strong>
              <span>
                {group.occurrences}{' '}
                {group.occurrences === 1 ? 'piece' : 'pieces'} ·{' '}
                {group.partTypes} part{' '}
                {group.partTypes === 1 ? 'type' : 'types'} ·{' '}
                {formatVolume(group.volumeMm3)}
              </span>
            </header>

            {view === 'cards' ? (
              <div className="schematic-grid mw-parts-grid">
                {group.parts.map((part) => {
                  const index = partIndex++
                  return (
                    <PartSchematic
                      key={part.partNumber}
                      part={part}
                      scale={scale}
                      index={index}
                      active={part.partNumber === selectedPartNumber}
                      onHover={onHoverPart}
                      onOpen={setDetailPartNumber}
                      drillOperations={
                        drillOperationsByPart.get(part.partNumber) ?? []
                      }
                      showCoordinates={showCoordinates}
                    />
                  )
                })}
              </div>
            ) : (
              <div className="mw-cut-list">
                <div className="mw-cut-header" aria-hidden="true">
                  <span>Part</span>
                  <span>Nominal stock</span>
                  <span>Qty</span>
                  <span>Drilling</span>
                  <span>Volume</span>
                </div>
                {group.parts.map((part) => {
                  const operations =
                    drillOperationsByPart.get(part.partNumber) ?? []
                  return (
                    <button
                      type="button"
                      className="mw-cut-row"
                      key={part.partNumber}
                      onClick={() => setDetailPartNumber(part.partNumber)}
                      onPointerEnter={() => onHoverPart(part.partNumber)}
                      onPointerLeave={() => onHoverPart(null)}
                      onFocus={() => onHoverPart(part.partNumber)}
                      onBlur={() => onHoverPart(null)}
                    >
                      <span>
                        <small>{part.partNumber}</small>
                        <strong>{part.description}</strong>
                      </span>
                      <span>
                        {part.sizeMm.map(formatDimension).join(' × ')} mm
                      </span>
                      <span>
                        <b>×{part.quantity}</b>
                      </span>
                      <span
                        title={operations
                          .map(operationSpecification)
                          .join('; ')}
                      >
                        {drillingSummary(operations)}
                      </span>
                      <span>
                        {formatVolume(part.unitVolumeMm3 * part.quantity)}
                      </span>
                    </button>
                  )
                })}
              </div>
            )}
          </section>
        ))}
        <p className="mw-panel-footnote">
          Dimensions are nominal cut stock · solid volume excludes stock waste,
          upholstery allowances, hardware and tolerances.
        </p>
      </section>

      {detailPart && (
        <PartDetailModal
          part={detailPart}
          drillOperations={
            drillOperationsByPart.get(detailPart.partNumber) ?? []
          }
          onClose={() => setDetailPartNumber(null)}
        />
      )}
    </>
  )
}
