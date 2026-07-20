import { useEffect, useMemo, useState } from 'react'
import type { CatalogDesign } from '../types'
import type { AssemblyNavigation } from './AssemblyPreview'
import type { MaterialsTab } from './MaterialsTabs'
import {
  buildMaterialsViewModel,
  partPreviewContext,
} from './materialsViewModel'
import type { PartsView } from './PartsPanel'
import { useAssemblyProgress } from './useAssemblyProgress'
import { useBuildManifest } from './useBuildManifest'

export function useMaterialsWorkspace(activeDesign: CatalogDesign | null) {
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
    : activeTab === 'assembly'
      ? activeStep?.previewContext
      : undefined

  const selectAdjacentStep = (offset: number) => {
    if (!model) return
    const currentIndex = model.assemblySteps.findIndex(
      (step) => step.number === activeStepNumber,
    )
    const candidate = model.assemblySteps[currentIndex + offset]
    if (candidate) setActiveStepNumber(candidate.number)
  }
  const navigation: AssemblyNavigation | undefined =
    activeTab === 'assembly' &&
    activeStep &&
    activeStepIndex !== undefined &&
    activeStepIndex >= 0 &&
    model
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

  return {
    manifest,
    error,
    retry,
    model,
    activeTab,
    setActiveTab,
    partsView,
    setPartsView,
    showCoordinates,
    setShowCoordinates,
    hoveredPartNumber,
    setHoveredPartNumber,
    activeStep,
    activeStepNumber,
    setActiveStepNumber,
    completedSteps,
    toggleStep,
    selectedParts,
    previewContext,
    navigation,
  }
}
