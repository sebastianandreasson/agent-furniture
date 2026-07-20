import { useEffect, useMemo, useState } from 'react'
import './App.css'
import './studio/StudioWorkspace.css'
import './AppResponsive.css'
import { useBuildCatalog } from './hooks/useBuildCatalog'
import { AppHeader, type AppPage } from './layout/AppHeader'
import { MaterialPreview } from './materials/MaterialPreview'
import { useEditorStore } from './state/editor'
import { StudioWorkspace } from './studio/StudioWorkspace'
import type { CatalogDesign } from './types'

function App() {
  const [activePage, setActivePage] = useState<AppPage>('studio')
  const { catalog, error, refreshing, lastSync, refresh } = useBuildCatalog()
  const activeDesignId = useEditorStore((state) => state.activeDesignId)
  const setActiveDesign = useEditorStore((state) => state.setActiveDesign)

  useEffect(() => {
    if (!catalog?.designs.length) return
    if (
      !activeDesignId ||
      !catalog.designs.some((design) => design.id === activeDesignId)
    ) {
      setActiveDesign(catalog.designs[0].id)
    }
  }, [activeDesignId, catalog, setActiveDesign])

  const activeDesign = useMemo<CatalogDesign | null>(
    () =>
      catalog?.designs.find((design) => design.id === activeDesignId) ?? null,
    [activeDesignId, catalog],
  )
  const designs = catalog?.designs ?? []

  return (
    <main className="app-shell">
      <AppHeader
        activePage={activePage}
        onNavigate={setActivePage}
        designCount={designs.length}
        catalogError={error}
        lastSync={lastSync}
        refreshing={refreshing}
        onRefresh={() => void refresh()}
      />
      {activePage === 'materials' ? (
        <MaterialPreview
          designs={designs}
          activeDesign={activeDesign}
          onSelectDesign={setActiveDesign}
        />
      ) : (
        <StudioWorkspace
          designs={designs}
          activeDesign={activeDesign}
          catalogError={error}
          onSelectDesign={setActiveDesign}
        />
      )}
    </main>
  )
}

export default App
