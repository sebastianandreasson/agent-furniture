// @vitest-environment jsdom

import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react'
import { useState } from 'react'
import { afterEach, describe, expect, it } from 'vitest'
import { MaterialsTabs, type MaterialsTab } from './MaterialsTabs'

afterEach(cleanup)

function Harness() {
  const [activeTab, setActiveTab] = useState<MaterialsTab>('assembly')
  return (
    <MaterialsTabs
      activeTab={activeTab}
      stepCount={2}
      partCount={8}
      fastenerCount={12}
      onChange={setActiveTab}
    />
  )
}

describe('MaterialsTabs', () => {
  it('uses roving keyboard focus and selects tabs with arrow keys', async () => {
    render(<Harness />)
    const assembly = screen.getByRole('tab', { name: /Assembly guide/ })
    assembly.focus()

    fireEvent.keyDown(assembly, { key: 'ArrowRight' })

    const parts = screen.getByRole('tab', { name: /Parts & cut list/ })
    await waitFor(() => expect(document.activeElement).toBe(parts))
    expect(parts.getAttribute('aria-selected')).toBe('true')
    expect(assembly.tabIndex).toBe(-1)

    fireEvent.keyDown(parts, { key: 'End' })
    const hardware = screen.getByRole('tab', { name: /Hardware/ })
    await waitFor(() => expect(document.activeElement).toBe(hardware))
    expect(hardware.getAttribute('aria-selected')).toBe('true')
  })
})
