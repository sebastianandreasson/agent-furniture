import type { KeyboardEvent } from 'react'

export type MaterialsTab = 'assembly' | 'parts' | 'hardware'

const TAB_LABELS: Array<{ id: MaterialsTab; label: string }> = [
  { id: 'assembly', label: 'Assembly guide' },
  { id: 'parts', label: 'Parts & cut list' },
  { id: 'hardware', label: 'Hardware' },
]

export function MaterialsTabs({
  activeTab,
  stepCount,
  partCount,
  fastenerCount,
  onChange,
}: {
  activeTab: MaterialsTab
  stepCount: number
  partCount: number
  fastenerCount: number
  onChange: (tab: MaterialsTab) => void
}) {
  const counts: Record<MaterialsTab, string> = {
    assembly: `${stepCount} ${stepCount === 1 ? 'step' : 'steps'}`,
    parts: String(partCount),
    hardware: `${fastenerCount} ${fastenerCount === 1 ? 'fastener' : 'fasteners'}`,
  }

  const moveFocus = (
    event: KeyboardEvent<HTMLButtonElement>,
    currentIndex: number,
  ) => {
    let nextIndex = currentIndex
    if (event.key === 'ArrowRight')
      nextIndex = (currentIndex + 1) % TAB_LABELS.length
    else if (event.key === 'ArrowLeft')
      nextIndex = (currentIndex - 1 + TAB_LABELS.length) % TAB_LABELS.length
    else if (event.key === 'Home') nextIndex = 0
    else if (event.key === 'End') nextIndex = TAB_LABELS.length - 1
    else return

    event.preventDefault()
    const nextTab = TAB_LABELS[nextIndex].id
    onChange(nextTab)
    requestAnimationFrame(() =>
      document.getElementById(`materials-tab-${nextTab}`)?.focus(),
    )
  }

  return (
    <div className="mw-tabs" role="tablist" aria-label="Materials sections">
      {TAB_LABELS.map((tab, index) => (
        <button
          key={tab.id}
          id={`materials-tab-${tab.id}`}
          type="button"
          role="tab"
          aria-selected={activeTab === tab.id}
          aria-controls={`materials-panel-${tab.id}`}
          tabIndex={activeTab === tab.id ? 0 : -1}
          className={activeTab === tab.id ? 'is-active' : ''}
          onClick={() => onChange(tab.id)}
          onKeyDown={(event) => moveFocus(event, index)}
        >
          {tab.label}
          <span>{counts[tab.id]}</span>
        </button>
      ))}
    </div>
  )
}
