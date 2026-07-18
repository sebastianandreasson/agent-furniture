import { describe, expect, it } from 'vitest'
import type { FurnitureManifest } from '../types'
import { buildMaterialsViewModel } from './materialsViewModel'

const MANIFEST = {
  schemaVersion: 1,
  name: 'test-bench',
  model: 'bench',
  units: 'mm',
  partOccurrences: 3,
  parts: [
    {
      partNumber: 'LEG-001',
      description: 'Leg',
      material: 'beech',
      quantity: 2,
      sizeMm: [40, 40, 400],
      unitVolumeMm3: 640_000,
      colorRgba: [0.5, 0.4, 0.3, 1],
      placementNames: ['leg-1', 'leg-2'],
    },
    {
      partNumber: 'RAIL-001',
      description: 'Rail',
      material: 'beech',
      quantity: 1,
      sizeMm: [500, 20, 60],
      unitVolumeMm3: 600_000,
      colorRgba: [0.5, 0.4, 0.3, 1],
      placementNames: ['rail-1'],
    },
  ],
  joinery: {
    status: 'prototype',
    notes: [],
    fasteners: [
      {
        code: 'PH-38',
        description: 'Pocket screw',
        quantity: 4,
        lengthMm: 38,
        nominalSize: '4 mm',
        head: 'washer',
        drive: 'T20',
        thread: 'fine',
        finish: 'zinc',
        application: 'Frame',
        manufacturer: '',
        productCode: '',
        sourceUrl: '',
        status: 'prototype',
        notes: '',
      },
    ],
    drillOperations: [
      {
        operationId: 'DR-RAIL',
        partNumber: 'RAIL-001',
        label: 'Rail pockets',
        kind: 'pocket_hole',
        face: 'inside face',
        viewAxes: ['x', 'z'],
        diameterMm: 9.5,
        depthMm: null,
        countersinkDiameterMm: null,
        angleDeg: 15,
        fastenerCode: 'PH-38',
        countsFastener: true,
        geometryMode: 'marked_only',
        pointsPerPart: 2,
        partQuantity: 1,
        totalHoles: 2,
        points: [],
        notes: '',
      },
    ],
    joints: [
      {
        jointId: 'J-1',
        description: 'Rail to left leg',
        sourcePartNumber: 'RAIL-001',
        targetPartNumber: 'LEG-001',
        fastenerCode: 'PH-38',
        quantity: 2,
        drillOperationIds: ['DR-RAIL'],
        assemblyStep: 1,
        notes: 'Dry fit first.',
      },
      {
        jointId: 'J-2',
        description: 'Rail to right leg',
        sourcePartNumber: 'RAIL-001',
        targetPartNumber: 'LEG-001',
        fastenerCode: 'PH-38',
        quantity: 2,
        drillOperationIds: ['DR-RAIL'],
        assemblyStep: 1,
        notes: 'Dry fit first.',
      },
    ],
  },
} satisfies FurnitureManifest

describe('materials view model', () => {
  it('groups parts and derives assembly steps from the manifest', () => {
    const model = buildMaterialsViewModel(MANIFEST)

    expect(model.materialGroups).toHaveLength(1)
    expect(model.materialGroups[0].occurrences).toBe(3)
    expect(model.totalFasteners).toBe(4)
    expect(model.totalSolidVolumeMm3).toBe(1_880_000)
    expect(model.assemblySteps).toHaveLength(1)
    expect(model.assemblySteps[0]).toMatchObject({
      number: 1,
      partNumbers: ['RAIL-001', 'LEG-001'],
      notes: ['Dry fit first.'],
    })
    expect(model.assemblySteps[0].fasteners).toEqual([
      expect.objectContaining({ code: 'PH-38', quantity: 4 }),
    ])
    expect(model.assemblySteps[0].drillOperations).toHaveLength(1)
  })
})
