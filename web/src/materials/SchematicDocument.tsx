import { useState } from 'react'
import type {
  CatalogDesign,
  FurnitureManifest,
  ManifestDrillOperation,
  ManifestPart,
} from '../types'
import { HardwareSchedule, JointSchedule } from './JoinerySchedules'
import { PartDetailModal } from './PartDetailModal'
import { PartSchematic } from './PartSchematic'

export function SchematicDocument({
  design,
  manifest,
  parts,
  scale,
  selectedPartNumber,
  drillOperationsByPart,
  onHoverPart,
}: {
  design: CatalogDesign
  manifest: FurnitureManifest
  parts: ManifestPart[]
  scale: number
  selectedPartNumber: string | null
  drillOperationsByPart: Map<string, ManifestDrillOperation[]>
  onHoverPart: (partNumber: string | null) => void
}) {
  const [detailPartNumber, setDetailPartNumber] = useState<string | null>(null)
  const totalFasteners = manifest.joinery.fasteners.reduce(
    (total, fastener) => total + fastener.quantity,
    0,
  )
  const detailPart =
    parts.find((part) => part.partNumber === detailPartNumber) ?? null

  return (
    <>
      <section className="materials-section schematic-document">
        <div className="schematic-document-header">
          <div>
            <p className="eyebrow">Interactive build document</p>
            <h3>Part schematic</h3>
            <p>
              Hover a part to locate it in the model. Connection dots mark
              approximate centres; click a part for full dimensions.
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
          <span>{design.name}</span>
          <span>Revision {design.revision}</span>
          <span>Units: millimetres</span>
        </div>
        <HardwareSchedule
          joinery={manifest.joinery}
          hardwareArtifact={design.artifacts.hardware}
        />
        <div className="schematic-grid">
          {parts.map((part, index) => (
            <PartSchematic
              key={part.partNumber}
              part={part}
              scale={scale}
              index={index}
              active={part.partNumber === selectedPartNumber}
              onHover={onHoverPart}
              onOpen={setDetailPartNumber}
              drillOperations={drillOperationsByPart.get(part.partNumber) ?? []}
            />
          ))}
        </div>
        <JointSchedule joinery={manifest.joinery} onHover={onHoverPart} />
        <p className="schematic-footer">
          QueryCAD generated inventory and prototype joinery schedule ·
          dimensions are from nominal cut stock · always test drilling and screw
          settings on matching offcuts.
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
