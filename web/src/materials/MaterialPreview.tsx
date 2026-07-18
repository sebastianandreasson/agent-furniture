import { useEffect, useMemo, useState } from 'react'
import type { CatalogDesign } from '../types'
import { AssemblyGuide } from './AssemblyGuide'
import { AssemblyPreview } from './AssemblyPreview'
import { HardwarePanel } from './HardwarePanel'
import { MaterialsHero } from './MaterialsHero'
import { MaterialsTabs, type MaterialsTab } from './MaterialsTabs'
import {
  buildMaterialsViewModel,
  partPreviewContext,
} from './materialsViewModel'
import { PartsPanel, type PartsView } from './PartsPanel'
import { schematicScale } from './schematic'
import { useAssemblyProgress } from './useAssemblyProgress'
import { useBuildManifest } from './useBuildManifest'
import './MaterialsWorkspace.css'

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
  const [activeTab, setActiveTab] = useState<MaterialsTab>('assembly')
  const [partsView, setPartsView] = useState<PartsView>('cards')
  const [showCoordinates, setShowCoordinates] = useState(false)
  const [hoveredPartNumber, setHoveredPartNumber] = useState<string | null>(
    null,
  )
  const [activeStepNumber, setActiveStepNumber] = useState<number | null>(null)
  const model = useMemo(
    () => (manifest ? buildMaterialsViewModel(manifest) : null),
    [manifest],
  )
  const stepNumbers = useMemo(
    () => model?.assemblySteps.map((step) => step.number) ?? [],
    [model],
  )
  const { completedSteps, toggleStep } = useAssemblyProgress(
    activeDesign?.id ?? 'none',
    activeDesign?.revision ?? 'none',
    stepNumbers,
  )

  useEffect(() => {
    setHoveredPartNumber(null)
    setActiveTab('assembly')
    setPartsView('cards')
    setShowCoordinates(false)
  }, [activeDesign?.id, activeDesign?.revision])

  useEffect(() => {
    setActiveStepNumber((current) =>
      stepNumbers.includes(current ?? -1) ? current : (stepNumbers[0] ?? null),
    )
  }, [stepNumbers])

  const activeStep =
    model?.assemblySteps.find((step) => step.number === activeStepNumber) ??
    null
  const activeStepIndex = model?.assemblySteps.findIndex(
    (step) => step.number === activeStepNumber,
  )
  const hoveredPart =
    model?.parts.find((part) => part.partNumber === hoveredPartNumber) ?? null
  const selectedParts = hoveredPart
    ? [hoveredPart]
    : activeTab === 'assembly'
      ? (activeStep?.parts ?? [])
      : []
  const previewContext = hoveredPart
    ? partPreviewContext(hoveredPart)
    : activeTab === 'assembly' && activeStep
      ? activeStep.previewContext
      : undefined

  const selectAdjacentStep = (offset: number) => {
    const currentIndex = model?.assemblySteps.findIndex(
      (step) => step.number === activeStepNumber,
    )
    if (currentIndex === undefined || currentIndex < 0 || !model) return
    const candidate = model.assemblySteps[currentIndex + offset]
    if (candidate) setActiveStepNumber(candidate.number)
  }

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
                  activeTab={activeTab}
                  stepCount={model.assemblySteps.length}
                  partCount={model.parts.length}
                  fastenerCount={model.hardware.totalFasteners}
                  onChange={setActiveTab}
                />
                {activeTab === 'assembly' && (
                  <AssemblyGuide
                    design={activeDesign}
                    steps={model.assemblySteps}
                    activeStepNumber={activeStepNumber}
                    completedSteps={completedSteps}
                    onSelectStep={setActiveStepNumber}
                    onToggleStep={toggleStep}
                    onHoverPart={setHoveredPartNumber}
                  />
                )}
                {activeTab === 'parts' && (
                  <PartsPanel
                    design={activeDesign}
                    groups={model.materialGroups}
                    scale={schematicScale(model.parts)}
                    selectedPartNumber={hoveredPartNumber}
                    drillOperationsByPart={model.drillOperationsByPart}
                    view={partsView}
                    showCoordinates={showCoordinates}
                    onViewChange={setPartsView}
                    onCoordinatesChange={setShowCoordinates}
                    onHoverPart={setHoveredPartNumber}
                  />
                )}
                {activeTab === 'hardware' && (
                  <HardwarePanel
                    design={activeDesign}
                    hardware={model.hardware}
                  />
                )}
              </div>
              <AssemblyPreview
                design={activeDesign}
                selectedParts={selectedParts}
                context={previewContext}
                navigation={
                  activeTab === 'assembly' &&
                  activeStep &&
                  activeStepIndex !== undefined &&
                  activeStepIndex >= 0
                    ? {
                        currentPosition: activeStepIndex + 1,
                        steps: model.assemblySteps.map((step) => ({
                          number: step.number,
                          complete: completedSteps.has(step.number),
                        })),
                        onPrevious: () => selectAdjacentStep(-1),
                        onNext: () => selectAdjacentStep(1),
                      }
                    : undefined
                }
              />
            </div>
          </>
        )}
      </div>
    </div>
  )
}
