import { describe, expect, it } from 'vitest'
import { parseCatalog } from './catalog'

describe('parseCatalog', () => {
  it('accepts the QueryCAD catalog contract', () => {
    const result = parseCatalog({
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
          },
        },
      ],
    })

    expect(result.designs[0].overallSizeMm.x).toBe(1600)
  })

  it('rejects malformed data with a useful error', () => {
    expect(() =>
      parseCatalog({ schemaVersion: 2, units: 'mm', designs: [] }),
    ).toThrow('Unsupported build catalog')
  })
})
