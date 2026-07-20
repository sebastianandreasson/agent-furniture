// @vitest-environment jsdom

import { cleanup, render, screen } from '@testing-library/react'
import type { ReactNode } from 'react'
import { Group } from 'three'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { CatalogDesign } from '../types'
import { AssemblyPreview } from './AssemblyPreview'

vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children }: { children: ReactNode }) => <div>{children}</div>,
}))

vi.mock('@react-three/drei', () => {
  const useGLTF = Object.assign(() => ({ scene: new Group() }), {
    clear: vi.fn(),
  })
  return {
    Bounds: ({ children }: { children: ReactNode }) => <>{children}</>,
    Html: ({ children }: { children: ReactNode }) => <>{children}</>,
    OrbitControls: () => null,
    useGLTF,
  }
})

const DESIGN: CatalogDesign = {
  id: 'bench',
  name: 'bench',
  model: 'bench',
  familyId: 'bench',
  variantId: 'default',
  variantLabel: 'Default',
  revision: 'abc',
  overallSizeMm: { x: 1000, y: 300, z: 500 },
  partOccurrences: 0,
  parameters: {},
  artifacts: { glb: '/bench.glb', manifest: '/manifest.json' },
}

afterEach(cleanup)

describe('AssemblyPreview', () => {
  it('describes non-contiguous step progress by identity and position', () => {
    render(
      <AssemblyPreview
        design={DESIGN}
        selectedParts={[]}
        navigation={{
          currentPosition: 1,
          steps: [
            { number: 2, complete: false },
            { number: 5, complete: true },
          ],
          onPrevious: () => undefined,
          onNext: () => undefined,
        }}
      />,
    )

    expect(screen.getByText('Step 1 of 2')).toBeTruthy()
    expect(
      screen
        .getByRole('listitem', { name: 'Step 2, current' })
        .getAttribute('aria-current'),
    ).toBe('step')
    expect(
      screen.getByRole('listitem', { name: 'Step 5, complete' }),
    ).toBeTruthy()
    expect(
      (
        screen.getByRole('button', {
          name: 'Previous assembly step',
        }) as HTMLButtonElement
      ).disabled,
    ).toBe(true)
    expect(
      (
        screen.getByRole('button', {
          name: 'Next assembly step',
        }) as HTMLButtonElement
      ).disabled,
    ).toBe(false)
  })
})
