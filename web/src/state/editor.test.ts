import { beforeEach, describe, expect, it } from 'vitest'
import { DEFAULT_LAYERS, useEditorStore } from './editor'

describe('editor scene layers', () => {
  beforeEach(() => {
    useEditorStore.setState({ layers: { ...DEFAULT_LAYERS } })
  })

  it('starts with the captured room instead of the opaque studio proxy', () => {
    expect(useEditorStore.getState().layers).toEqual({
      splat: true,
      furniture: true,
      room: false,
      grid: false,
    })
  })

  it('keeps the captured room and white studio mutually exclusive', () => {
    useEditorStore.getState().toggleLayer('room')
    expect(useEditorStore.getState().layers.room).toBe(true)
    expect(useEditorStore.getState().layers.splat).toBe(false)

    useEditorStore.getState().toggleLayer('splat')
    expect(useEditorStore.getState().layers.splat).toBe(true)
    expect(useEditorStore.getState().layers.room).toBe(false)
  })

  it('leaves furniture and grid controls independent', () => {
    useEditorStore.getState().toggleLayer('grid')
    useEditorStore.getState().toggleLayer('furniture')
    expect(useEditorStore.getState().layers.grid).toBe(true)
    expect(useEditorStore.getState().layers.furniture).toBe(false)
    expect(useEditorStore.getState().layers.splat).toBe(true)
  })
})
