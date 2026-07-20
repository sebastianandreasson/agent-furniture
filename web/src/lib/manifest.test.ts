import { afterEach, describe, expect, it, vi } from 'vitest'
import type { CatalogDesign } from '../types'
import {
  assertManifestMatchesDesign,
  loadManifest,
  parseManifest,
} from './manifest'

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

const DESIGN: CatalogDesign = {
  id: 'entryway-bench',
  name: 'entryway-bench',
  model: 'entryway_bench',
  familyId: 'entryway-bench',
  variantId: 'shoe-shelf',
  variantLabel: 'Shoe shelf',
  revision: 'abc123',
  overallSizeMm: { x: 1200, y: 338, z: 480 },
  partOccurrences: 4,
  parameters: {},
  artifacts: {
    manifest: '/entryway-bench/manifest.json',
    glb: '/entryway-bench/entryway-bench.glb',
  },
}

function manifestJson(overrides: Record<string, unknown> = {}) {
  return {
    schema_version: 1,
    name: 'entryway-bench',
    model: 'entryway_bench',
    family: 'entryway-bench',
    variant: 'shoe-shelf',
    variant_label: 'Shoe shelf',
    units: 'mm',
    part_occurrences: 4,
    parts: [PART],
    ...overrides,
  }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('parseManifest', () => {
  it('maps the generated part inventory into the web contract', () => {
    const manifest = parseManifest(manifestJson())

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
    expect(() => parseManifest(manifestJson({ part_occurrences: 5 }))).toThrow(
      'part count does not match',
    )
  })

  it('rejects manifest units outside the shared millimetre contract', () => {
    expect(() => parseManifest(manifestJson({ units: 'in' }))).toThrow(
      'Unsupported build manifest',
    )
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

  it('allows declared site targets without adding fake BOM parts', () => {
    const manifest = parseManifest({
      schema_version: 1,
      name: 'entryway-bench',
      model: 'entryway_bench',
      units: 'mm',
      part_occurrences: 4,
      parts: [PART],
      joinery: {
        ...JOINERY,
        external_targets: [
          {
            code: 'SITE-POST',
            description: 'Verified existing timber post',
            notes: 'Do not anchor into brick.',
          },
        ],
        joints: [
          {
            ...JOINERY.joints[0],
            target_part_number: 'SITE-POST',
          },
        ],
      },
    })

    expect(manifest.joinery.externalTargets).toEqual([
      {
        code: 'SITE-POST',
        description: 'Verified existing timber post',
        notes: 'Do not anchor into brick.',
      },
    ])
    expect(manifest.parts).toHaveLength(1)
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

  it.each([
    ['name', { name: 'stale-bench' }, 'name is "stale-bench"'],
    ['model', { model: 'stale_model' }, 'model is "stale_model"'],
    ['variant', { variant: 'stale' }, 'variant is "stale"'],
  ])(
    'rejects a manifest whose %s disagrees with the selected catalog design',
    (_field, overrides, expectedMessage) => {
      const manifest = parseManifest(manifestJson(overrides))

      expect(() => assertManifestMatchesDesign(manifest, DESIGN)).toThrow(
        expectedMessage,
      )
    },
  )

  it('rejects a manifest whose occurrence count disagrees with the catalog', () => {
    const manifest = parseManifest(manifestJson())

    expect(() =>
      assertManifestMatchesDesign(manifest, {
        ...DESIGN,
        partOccurrences: 5,
      }),
    ).toThrow('part count is 4 in the manifest but 5 in the catalog')
  })

  it('checks compatibility when loading a selected design', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(manifestJson({ model: 'stale_model' })), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    )

    await expect(loadManifest(DESIGN)).rejects.toThrow(
      'build catalog and manifest for "entryway-bench" are out of sync',
    )
    expect(fetch).toHaveBeenCalledWith(
      '/entryway-bench/manifest.json?revision=abc123',
      expect.objectContaining({ cache: 'no-store' }),
    )
  })
})
