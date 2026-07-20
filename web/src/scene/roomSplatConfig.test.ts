import { describe, expect, it } from 'vitest'
import { ROOM_SPLAT } from './roomSplatConfig'

describe('ROOM_SPLAT', () => {
  it('uses a local, visually registered real-photo indoor sample', () => {
    expect(ROOM_SPLAT.assetUrl).toContain('mipnerf360-room.spz')
    expect(ROOM_SPLAT.mmPerSourceUnit).toBe(440)
    expect(ROOM_SPLAT.positionMm).toEqual([220, 1200, 690])
    expect(ROOM_SPLAT.rotationRad).toEqual([1.831232, 1.076556, 1.309395])
  })

  it('keeps the upstream source and renderer attribution discoverable', () => {
    expect(ROOM_SPLAT.sourceUrl).toContain('room.ply')
    expect(ROOM_SPLAT.datasetUrl).toContain('mipnerf360')
    expect(ROOM_SPLAT.rendererUrl).toBe('https://github.com/sparkjsdev/spark')
  })
})
