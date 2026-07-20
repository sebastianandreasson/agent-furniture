import type { CatalogDesign } from '../types'
import { AssemblyGuide } from './AssemblyGuide'
import { AssemblyPreview } from './AssemblyPreview'
import { HardwarePanel } from './HardwarePanel'
import { MaterialsHero } from './MaterialsHero'
import { MaterialsTabs } from './MaterialsTabs'
import { PartsPanel } from './PartsPanel'
import { schematicScale } from './schematic'
import { useMaterialsWorkspace } from './useMaterialsWorkspace'
import './MaterialsPage.css'
import './PartSchematic.css'
import './AssemblyCanvas.css'
import './PartDetail.css'
import './MaterialsLayout.css'
import './MaterialsInventory.css'
import './MaterialsPreview.css'
import './MaterialsResponsive.css'

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
  const workspace = useMaterialsWorkspace(activeDesign)
  const { manifest, error, retry, model } = workspace

  return (
    <div className="materials-page">
      <div className="materials-inner mw-inner">
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

        {activeDesign && manifest && model && (
          <>
            <MaterialsHero
              designs={designs}
              design={activeDesign}
              model={model}
              onSelectDesign={onSelectDesign}
            />
            <div className="mw-workbench">
              <div className="mw-document-column">
                <MaterialsTabs
                  activeTab={workspace.activeTab}
                  stepCount={model.assemblySteps.length}
                  partCount={model.parts.length}
                  fastenerCount={model.hardware.totalFasteners}
                  onChange={workspace.setActiveTab}
                />
                {workspace.activeTab === 'assembly' && (
                  <AssemblyGuide
                    design={activeDesign}
                    steps={model.assemblySteps}
                    activeStepNumber={workspace.activeStepNumber}
                    completedSteps={workspace.completedSteps}
                    onSelectStep={workspace.setActiveStepNumber}
                    onToggleStep={workspace.toggleStep}
                    onHoverPart={workspace.setHoveredPartNumber}
                  />
                )}
                {workspace.activeTab === 'parts' && (
                  <PartsPanel
                    design={activeDesign}
                    groups={model.materialGroups}
                    scale={schematicScale(model.parts)}
                    selectedPartNumber={workspace.hoveredPartNumber}
                    drillOperationsByPart={model.drillOperationsByPart}
                    view={workspace.partsView}
                    showCoordinates={workspace.showCoordinates}
                    onViewChange={workspace.setPartsView}
                    onCoordinatesChange={workspace.setShowCoordinates}
                    onHoverPart={workspace.setHoveredPartNumber}
                  />
                )}
                {workspace.activeTab === 'hardware' && (
                  <HardwarePanel
                    design={activeDesign}
                    hardware={model.hardware}
                  />
                )}
              </div>
              <AssemblyPreview
                design={activeDesign}
                selectedParts={workspace.selectedParts}
                context={workspace.previewContext}
                navigation={workspace.navigation}
              />
            </div>
          </>
        )}
      </div>
    </div>
  )
}
