import { describe, expect, it } from 'vitest'
import { parseManifest } from './manifest'

const PART = {
  part_number: 'LEG-001',
  description: 'Square leg',
  material: 'painted beech',
  quantity: 4,
  size_x_mm: 42,
  size_y_mm: 42,
  size_z_mm: 408,
  unit_volume_mm3: 719712,
  color_rgba: [0.43, 0.42, 0.39, 1],
  placements: [
    { name: 'leg_front_left' },
    { name: 'leg_front_right' },
    { name: 'leg_back_left' },
    { name: 'leg_back_right' },
  ],
}

describe('parseManifest', () => {
  it('maps the generated part inventory into the web contract', () => {
    const manifest = parseManifest({
      schema_version: 1,
      name: 'entryway-bench',
      model: 'entryway_bench',
      units: 'mm',
      part_occurrences: 4,
      parts: [PART],
    })

    expect(manifest.parts[0]).toEqual({
      partNumber: 'LEG-001',
      description: 'Square leg',
      material: 'painted beech',
      quantity: 4,
      sizeMm: [42, 42, 408],
      unitVolumeMm3: 719712,
      colorRgba: [0.43, 0.42, 0.39, 1],
      placementNames: [
        'leg_front_left',
        'leg_front_right',
        'leg_back_left',
        'leg_back_right',
      ],
    })
  })

  it('rejects a manifest whose inventory does not add up', () => {
    expect(() =>
      parseManifest({
        schema_version: 1,
        name: 'entryway-bench',
        model: 'entryway_bench',
        units: 'mm',
        part_occurrences: 5,
        parts: [PART],
      }),
    ).toThrow('part count does not match')
  })
})
