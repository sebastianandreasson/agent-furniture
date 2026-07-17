// @vitest-environment jsdom

import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { DEFAULT_PLACEMENT, useEditorStore } from './state/editor'

vi.mock('@react-three/drei', () => ({ Loader: () => null }))
vi.mock('./scene/StarterSplat', () => ({
  STARTER_SPLAT_URL: 'https://example.test/sample.splat',
}))
vi.mock('./scene/EditorScene', () => ({
  EditorScene: ({ design }: { design: { id: string } | null }) => (
    <div data-testid="mock-scene">{design?.id ?? 'empty'}</div>
  ),
}))
vi.mock('./lib/catalog', () => ({
  loadCatalog: vi.fn(async () => ({
    schemaVersion: 1,
    units: 'mm',
    designs: [
      {
        id: 'dining-table',
        name: 'dining-table',
        model: 'apron_table',
        revision: '1234567890abcdef',
        overallSizeMm: { x: 1600, y: 800, z: 750 },
        partOccurrences: 9,
        parameters: { length: 1600 },
        artifacts: {
          glb: '/dining-table/dining-table.glb',
          manifest: '/dining-table/manifest.json',
          step: '/dining-table/dining-table.step',
          bom: '/dining-table/bom.csv',
        },
      },
    ],
  })),
}))

describe('QueryCAD editor shell', () => {
  beforeEach(() => {
    localStorage.clear()
    useEditorStore.setState({
      activeDesignId: null,
      placements: {},
      transformMode: 'translate',
      snapping: true,
    })
  })

  afterEach(cleanup)

  it('discovers a build and persists numeric placement controls', async () => {
    const user = userEvent.setup()
    render(<App />)

    await waitFor(() =>
      expect(screen.getByTestId('mock-scene').textContent).toBe('dining-table'),
    )
    await user.clear(screen.getByRole('spinbutton', { name: 'X mm' }))
    await user.type(screen.getByRole('spinbutton', { name: 'X mm' }), '450')
    await user.click(screen.getByRole('button', { name: '+90°' }))

    expect(useEditorStore.getState().placements['dining-table']).toEqual({
      ...DEFAULT_PLACEMENT,
      positionMm: [450, 0, 0],
      rotationDeg: [0, 90, 0],
    })
  })

  it('switches between move and rotate tools', async () => {
    const user = userEvent.setup()
    render(<App />)
    await screen.findByTestId('mock-scene')

    await user.click(screen.getByRole('button', { name: /Rotate/ }))

    expect(useEditorStore.getState().transformMode).toBe('rotate')
  })
})
