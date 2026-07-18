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

const JOINERY = {
  status: 'prototype_not_structurally_certified',
  notes: ['Verify on an offcut.'],
  fasteners: [
    {
      code: 'PH-38-FINE',
      description: '38 mm pocket-hole screw',
      quantity: 4,
      length_mm: 38,
      nominal_size: 'fine thread',
      head: 'washer head',
      drive: '#2 square',
      thread: 'fine',
      finish: 'zinc',
      application: 'Leg attachment',
      manufacturer: 'Example',
      product_code: 'PH38',
      source_url: 'https://example.test/ph38',
      status: 'prototype_assumption',
      notes: 'Test first.',
    },
  ],
  drill_operations: [
    {
      operation_id: 'DR-LEG',
      part_number: 'LEG-001',
      label: 'Pocket hole',
      kind: 'pocket_hole',
      face: 'inside face',
      view_axes: ['z', 'x'],
      diameter_mm: 9.5,
      depth_mm: null,
      countersink_diameter_mm: null,
      angle_deg: 15,
      fastener_code: 'PH-38-FINE',
      counts_fastener: true,
      geometry_mode: 'marked_only',
      points_per_part: 1,
      part_quantity: 4,
      total_holes: 4,
      points: [
        {
          position_mm: [21, 0, 40],
          axis: [0, 1, 0],
          label: 'rail',
        },
      ],
      notes: 'Jig controlled.',
    },
  ],
  joints: [
    {
      joint_id: 'J01',
      description: 'Leg joint',
      source_part_number: 'LEG-001',
      target_part_number: 'LEG-001',
      fastener_code: 'PH-38-FINE',
      quantity: 4,
      drill_operation_ids: ['DR-LEG'],
      assembly_step: 1,
      notes: '',
    },
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

  it('maps and cross-checks a generated joinery schedule', () => {
    const manifest = parseManifest({
      schema_version: 1,
      name: 'entryway-bench',
      model: 'entryway_bench',
      units: 'mm',
      part_occurrences: 4,
      parts: [PART],
      joinery: JOINERY,
    })

    expect(manifest.joinery.fasteners[0]).toMatchObject({
      code: 'PH-38-FINE',
      quantity: 4,
      lengthMm: 38,
    })
    expect(manifest.joinery.drillOperations[0]).toMatchObject({
      operationId: 'DR-LEG',
      totalHoles: 4,
    })
  })

  it('rejects joinery whose hardware total disagrees with its joints', () => {
    const joinery = structuredClone(JOINERY)
    joinery.fasteners[0].quantity = 3

    expect(() =>
      parseManifest({
        schema_version: 1,
        name: 'entryway-bench',
        model: 'entryway_bench',
        units: 'mm',
        part_occurrences: 4,
        parts: [PART],
        joinery,
      }),
    ).toThrow('hardware totals do not match')
  })
})
