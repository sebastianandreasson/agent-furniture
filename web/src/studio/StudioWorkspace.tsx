import { useState } from 'react'
import type { CatalogDesign } from '../types'
import { AssetPanel } from './AssetPanel'
import { InspectorPanel } from './InspectorPanel'
import { StudioViewport } from './StudioViewport'

export function StudioWorkspace({
  designs,
  activeDesign,
  catalogError,
  onSelectDesign,
}: {
  designs: CatalogDesign[]
  activeDesign: CatalogDesign | null
  catalogError: string | null
  onSelectDesign: (id: string) => void
}) {
  const [splatError, setSplatError] = useState<string | null>(null)

  return (
    <div className="workspace">
      <AssetPanel
        designs={designs}
        activeDesign={activeDesign}
        catalogError={catalogError}
        splatError={splatError}
        onSelectDesign={onSelectDesign}
      />
      <StudioViewport design={activeDesign} onSplatError={setSplatError} />
      <InspectorPanel design={activeDesign} />
    </div>
  )
}
