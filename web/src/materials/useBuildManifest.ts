import { useEffect, useState } from 'react'
import { loadManifest } from '../lib/manifest'
import type { CatalogDesign, FurnitureManifest } from '../types'

export function useBuildManifest(activeDesign: CatalogDesign | null) {
  const [manifest, setManifest] = useState<FurnitureManifest | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState(0)

  useEffect(() => {
    if (!activeDesign) {
      setManifest(null)
      return
    }

    const controller = new AbortController()
    setManifest(null)
    setError(null)
    void loadManifest(activeDesign, controller.signal)
      .then(setManifest)
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') {
          return
        }
        setError(
          reason instanceof Error
            ? reason.message
            : 'Could not load the part inventory.',
        )
      })
    return () => controller.abort()
  }, [activeDesign, refreshToken])

  return {
    manifest,
    error,
    retry: () => setRefreshToken((value) => value + 1),
  }
}
