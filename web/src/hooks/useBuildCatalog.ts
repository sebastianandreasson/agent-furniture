import {
  startTransition,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react'
import { catalogSignature, loadCatalog } from '../lib/catalog'
import type { BuildCatalog } from '../types'

const CATALOG_POLL_INTERVAL_MS = 1000

export function useBuildCatalog() {
  const [catalog, setCatalog] = useState<BuildCatalog | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(true)
  const [lastSync, setLastSync] = useState<Date | null>(null)
  const loadedSignature = useRef<string | null>(null)

  const refresh = useCallback(
    async (showSpinner = true, signal?: AbortSignal) => {
      if (showSpinner) setRefreshing(true)
      try {
        const next = await loadCatalog(signal)
        const signature = catalogSignature(next)
        if (signature !== loadedSignature.current) {
          loadedSignature.current = signature
          startTransition(() => setCatalog(next))
          setLastSync(new Date())
        }
        setError(null)
      } catch (reason) {
        if (reason instanceof DOMException && reason.name === 'AbortError') {
          return
        }
        setError(
          reason instanceof Error
            ? reason.message
            : 'Could not load furniture builds.',
        )
      } finally {
        if (showSpinner) setRefreshing(false)
      }
    },
    [],
  )

  useEffect(() => {
    const controller = new AbortController()
    void refresh(true, controller.signal)
    const interval = window.setInterval(
      () => void refresh(false),
      CATALOG_POLL_INTERVAL_MS,
    )
    return () => {
      controller.abort()
      window.clearInterval(interval)
    }
  }, [refresh])

  return { catalog, error, refreshing, lastSync, refresh }
}
