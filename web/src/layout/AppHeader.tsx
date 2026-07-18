export type AppPage = 'studio' | 'materials'

export function AppHeader({
  activePage,
  onNavigate,
  designCount,
  catalogError,
  lastSync,
  refreshing,
  onRefresh,
}: {
  activePage: AppPage
  onNavigate: (page: AppPage) => void
  designCount: number
  catalogError: string | null
  lastSync: Date | null
  refreshing: boolean
  onRefresh: () => void
}) {
  return (
    <header className="app-header">
      <div className="brand-block">
        <div className="brand-mark" aria-hidden="true">
          Q
        </div>
        <div>
          <p className="eyebrow">Metric furniture lab</p>
          <h1>QueryCAD Studio</h1>
        </div>
      </div>
      <nav className="primary-nav" aria-label="Primary navigation">
        <button
          className={activePage === 'studio' ? 'is-active' : ''}
          type="button"
          onClick={() => onNavigate('studio')}
        >
          Studio
        </button>
        <button
          className={activePage === 'materials' ? 'is-active' : ''}
          type="button"
          onClick={() => onNavigate('materials')}
        >
          Materials
        </button>
      </nav>
      <div className="header-status">
        <span className={`status-dot ${catalogError ? 'is-error' : ''}`} />
        <span>
          {catalogError ? 'Build folder offline' : `${designCount} build ready`}
        </span>
        <span className="status-divider" />
        <span>
          {lastSync ? `Synced ${lastSync.toLocaleTimeString()}` : 'Connecting…'}
        </span>
        <button
          className="icon-button"
          type="button"
          onClick={onRefresh}
          aria-label="Refresh build catalog"
          title="Refresh build catalog"
        >
          {refreshing ? '···' : '↻'}
        </button>
      </div>
    </header>
  )
}
