import { useEffect, useMemo, useState } from 'react'
import type { CatalogDesign } from '../types'
import { AssemblyPreview } from './AssemblyPreview'
import {
  InventorySummary,
  MaterialRollup,
  PartsInventory,
} from './InventorySections'
import {
  groupDrillOperationsByPart,
  sortParts,
  summarizeMaterials,
} from './inventory'
import { schematicScale } from './schematic'
import { SchematicDocument } from './SchematicDocument'
import { useBuildManifest } from './useBuildManifest'

type MaterialPreviewProps = {
  designs: CatalogDesign[]
  activeDesign: CatalogDesign | null
  onSelectDesign: (id: string) => void
}

export function MaterialPreview({
  designs,
  activeDesign,
  onSelectDesign,
}: MaterialPreviewProps) {
  const { manifest, error, retry } = useBuildManifest(activeDesign)
  const [hoveredPartNumber, setHoveredPartNumber] = useState<string | null>(
    null,
  )

  useEffect(() => setHoveredPartNumber(null), [activeDesign?.id])

  const materialSummaries = useMemo(
    () => summarizeMaterials(manifest?.parts ?? []),
    [manifest],
  )
  const sortedParts = useMemo(
    () => sortParts(manifest?.parts ?? []),
    [manifest],
  )
  const scale = useMemo(() => schematicScale(sortedParts), [sortedParts])
  const drillOperationsByPart = useMemo(
    () => groupDrillOperationsByPart(manifest?.joinery.drillOperations ?? []),
    [manifest],
  )
  const totalSolidVolume = materialSummaries.reduce(
    (total, material) => total + material.volumeMm3,
    0,
  )
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
            <button type="button" onClick={retry}>
              Try again
            </button>
          </div>
        )}

        {activeDesign && manifest && (
          <>
            <InventorySummary
              partOccurrences={manifest.partOccurrences}
              uniqueParts={manifest.parts.length}
              materials={materialSummaries.length}
              totalSolidVolume={totalSolidVolume}
            />
            <MaterialRollup materials={materialSummaries} />

            <div className="schematic-workbench">
              <SchematicDocument
                design={activeDesign}
                manifest={manifest}
                parts={sortedParts}
                scale={scale}
                selectedPartNumber={hoveredPartNumber}
                drillOperationsByPart={drillOperationsByPart}
                onHoverPart={setHoveredPartNumber}
              />
              <AssemblyPreview
                design={activeDesign}
                selectedPart={hoveredPart}
              />
            </div>

            <PartsInventory design={activeDesign} parts={sortedParts} />
          </>
        )}
      </div>
    </div>
  )
}
