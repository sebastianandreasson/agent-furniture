// @vitest-environment jsdom

import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { DEFAULT_PLACEMENT, useEditorStore } from './state/editor'

const testDoubles = vi.hoisted(() => ({
  loadCatalog: vi.fn(),
  loadManifest: vi.fn(),
  renderScene: vi.fn(),
}))

const TEST_CATALOG = {
  schemaVersion: 1 as const,
  units: 'mm' as const,
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
        hardware: '/dining-table/hardware.csv',
      },
    },
  ],
}

const TEST_MANIFEST = {
  schemaVersion: 1 as const,
  name: 'dining-table',
  model: 'apron_table',
  units: 'mm' as const,
  partOccurrences: 9,
  parts: [
    {
      partNumber: 'TOP-001',
      description: 'Table top',
      material: 'oak',
      quantity: 1,
      sizeMm: [1600, 800, 30] as [number, number, number],
      unitVolumeMm3: 38_400_000,
      colorRgba: [0.72, 0.52, 0.3, 1] as [number, number, number, number],
      placementNames: ['table_top'],
    },
    {
      partNumber: 'LEG-001',
      description: 'Square table leg',
      material: 'ash',
      quantity: 4,
      sizeMm: [70, 70, 720] as [number, number, number],
      unitVolumeMm3: 3_528_000,
      colorRgba: [0.62, 0.46, 0.28, 1] as [number, number, number, number],
      placementNames: [
        'leg_front_left',
        'leg_front_right',
        'leg_back_left',
        'leg_back_right',
      ],
    },
    {
      partNumber: 'APRON-001',
      description: 'Table apron',
      material: 'ash',
      quantity: 4,
      sizeMm: [1400, 22, 110] as [number, number, number],
      unitVolumeMm3: 3_388_000,
      colorRgba: [0.62, 0.46, 0.28, 1] as [number, number, number, number],
      placementNames: [
        'apron_front',
        'apron_back',
        'apron_left',
        'apron_right',
      ],
    },
  ],
  joinery: {
    status: 'prototype_not_structurally_certified',
    notes: ['Confirm the drilling setup on matching offcuts.'],
    fasteners: [
      {
        code: 'PH-32-FINE',
        description: '32 mm fine-thread pocket-hole screw',
        quantity: 2,
        lengthMm: 32,
        nominalSize: 'fine thread',
        head: 'washer head',
        drive: '#2 square',
        thread: 'fine',
        finish: 'zinc',
        application: 'Top attachment',
        manufacturer: 'Example',
        productCode: 'PH32',
        sourceUrl: 'https://example.test/ph32',
        status: 'prototype_assumption',
        notes: 'Verify on scrap.',
      },
    ],
    drillOperations: [
      {
        operationId: 'DR-TOP',
        partNumber: 'TOP-001',
        label: 'Top attachment holes',
        kind: 'pocket_hole',
        face: 'bottom face',
        viewAxes: ['x', 'y'] as ['x', 'y'],
        diameterMm: 9.5,
        depthMm: null,
        countersinkDiameterMm: null,
        angleDeg: 15,
        fastenerCode: 'PH-32-FINE',
        countsFastener: true,
        geometryMode: 'marked_only' as const,
        pointsPerPart: 2,
        partQuantity: 1,
        totalHoles: 2,
        points: [
          {
            positionMm: [300, 100, 0] as [number, number, number],
            axis: [0, 0, 1] as [number, number, number],
            label: 'left',
          },
          {
            positionMm: [1300, 100, 0] as [number, number, number],
            axis: [0, 0, 1] as [number, number, number],
            label: 'right',
          },
        ],
        notes: 'Jig controlled.',
      },
    ],
    joints: [
      {
        jointId: 'J01-TOP',
        description: 'Table top to frame',
        sourcePartNumber: 'TOP-001',
        targetPartNumber: 'LEG-001',
        fastenerCode: 'PH-32-FINE',
        quantity: 2,
        drillOperationIds: ['DR-TOP'],
        assemblyStep: 1,
        notes: '',
      },
    ],
  },
}

vi.mock('./scene/StarterSplat', () => ({
  STARTER_SPLAT_URL: 'https://example.test/sample.splat',
}))
vi.mock('./scene/EditorScene', () => ({
  EditorScene: ({
    design,
  }: {
    design: {
      id: string
      revision: string
      overallSizeMm: { z: number }
    } | null
  }) => {
    testDoubles.renderScene(design)
    return <div data-testid="mock-scene">{design?.id ?? 'empty'}</div>
  },
}))
vi.mock('./lib/catalog', () => ({
  catalogSignature: (catalog: unknown) => JSON.stringify(catalog),
  loadCatalog: testDoubles.loadCatalog,
}))
vi.mock('./lib/manifest', () => ({
  loadManifest: testDoubles.loadManifest,
}))
vi.mock('./materials/AssemblyPreview', () => ({
  AssemblyPreview: ({
    selectedParts,
  }: {
    selectedParts: Array<{ partNumber: string }>
  }) => (
    <div data-testid="mock-assembly-preview">
      {selectedParts.map((part) => part.partNumber).join(', ') || 'all parts'}
    </div>
  ),
}))

describe('QueryCAD editor shell', () => {
  beforeEach(() => {
    testDoubles.loadCatalog.mockReset().mockResolvedValue(TEST_CATALOG)
    testDoubles.loadManifest.mockReset().mockResolvedValue(TEST_MANIFEST)
    testDoubles.renderScene.mockReset()
    localStorage.clear()
    useEditorStore.setState({
      activeDesignId: null,
      placements: {},
      transformMode: 'translate',
      snapping: true,
      showHelpers: true,
    })
  })

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

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

  it('shows scene helpers by default and toggles them together', async () => {
    const user = userEvent.setup()
    render(<App />)
    await screen.findByTestId('mock-scene')

    const toggle = screen.getByRole('button', { name: '◇ Helpers on' })
    expect(toggle.getAttribute('aria-pressed')).toBe('true')

    await user.click(toggle)

    expect(useEditorStore.getState().showHelpers).toBe(false)
    expect(screen.getByRole('button', { name: '◇ Helpers off' })).toBeTruthy()
  })

  it('shows a generated material and assembly-parts breakdown', async () => {
    const user = userEvent.setup()
    const print = vi.spyOn(window, 'print').mockImplementation(() => undefined)
    render(<App />)
    await screen.findByTestId('mock-scene')

    await user.click(screen.getByRole('button', { name: 'Materials' }))

    expect(
      await screen.findByRole('heading', { name: 'Build it in 1 step' }),
    ).toBeTruthy()
    expect(screen.getByLabelText('Build summary').textContent).toContain(
      '9 pieces',
    )
    expect(
      screen.getByRole('tab', { name: /Assembly guide.*1 step/ }),
    ).toBeTruthy()

    await user.click(screen.getByRole('tab', { name: /Parts & cut list.*3/ }))
    expect(
      screen.getByRole('heading', { name: 'Every part, by material' }),
    ).toBeTruthy()
    expect(screen.getByText('Ø9.5 · jig depth · 15° · 2/part')).toBeTruthy()
    expect(screen.getAllByRole('img', { name: /quantity/ })).toHaveLength(3)

    await user.hover(
      screen.getByRole('button', {
        name: 'Square table leg, quantity 4',
      }),
    )
    expect(screen.getByTestId('mock-assembly-preview').textContent).toBe(
      'LEG-001',
    )

    await user.click(screen.getByRole('button', { name: 'Print / PDF' }))
    expect(print).toHaveBeenCalledOnce()

    await user.click(screen.getByRole('button', { name: 'Cut list' }))
    expect(
      screen.getByRole('button', { name: /LEG-001.*Square table leg.*×4/ }),
    ).toBeTruthy()

    await user.click(screen.getByRole('tab', { name: /Hardware.*2 fasteners/ }))
    expect(screen.getByRole('heading', { name: 'Shopping list' })).toBeTruthy()
    expect(screen.getByText('PH-32-FINE')).toBeTruthy()

    await user.click(screen.getByRole('button', { name: 'Studio' }))
    expect(await screen.findByTestId('mock-scene')).toBeTruthy()
    print.mockRestore()
  })

  it('persists assembly checklist progress for a design revision', async () => {
    const user = userEvent.setup()
    render(<App />)
    await screen.findByTestId('mock-scene')

    await user.click(screen.getByRole('button', { name: 'Materials' }))
    const done = await screen.findByRole('checkbox', { name: 'Done' })
    await user.click(done)

    expect((done as HTMLInputElement).checked).toBe(true)
    expect(
      localStorage.getItem(
        'querycad:assembly-progress:dining-table:1234567890abcdef',
      ),
    ).toBe('[1]')

    await user.click(screen.getByRole('button', { name: 'Studio' }))
    await user.click(screen.getByRole('button', { name: 'Materials' }))
    expect(
      (await screen.findByRole('checkbox', {
        name: 'Done',
      })) as HTMLInputElement,
    ).toHaveProperty('checked', true)
  })

  it('does not rerender the 3D scene when catalog polling finds no changes', async () => {
    vi.useFakeTimers()
    try {
      render(<App />)
      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })
      expect(screen.getByTestId('mock-scene').textContent).toBe('dining-table')
      const settledRenderCount = testDoubles.renderScene.mock.calls.length

      await act(async () => {
        await vi.advanceTimersByTimeAsync(3100)
      })

      expect(testDoubles.loadCatalog.mock.calls.length).toBeGreaterThanOrEqual(
        4,
      )
      expect(testDoubles.renderScene).toHaveBeenCalledTimes(settledRenderCount)
    } finally {
      vi.useRealTimers()
    }
  })

  it('publishes a changed model revision from a catalog poll', async () => {
    const changedCatalog = structuredClone(TEST_CATALOG)
    changedCatalog.designs[0].revision = 'fedcba0987654321'
    changedCatalog.designs[0].overallSizeMm.z = 810
    testDoubles.loadCatalog
      .mockResolvedValueOnce(TEST_CATALOG)
      .mockResolvedValue(changedCatalog)

    vi.useFakeTimers()
    try {
      render(<App />)
      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })
      await act(async () => {
        await vi.advanceTimersByTimeAsync(1100)
      })

      expect(testDoubles.renderScene).toHaveBeenLastCalledWith(
        expect.objectContaining({
          revision: 'fedcba0987654321',
          overallSizeMm: expect.objectContaining({ z: 810 }),
        }),
      )
    } finally {
      vi.useRealTimers()
    }
  })
})
