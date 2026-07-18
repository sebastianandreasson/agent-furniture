import { describe, expect, it } from 'vitest'
import type { ManifestDrillOperation, ManifestPart } from '../types'
import {
  groupDrillOperationsByPart,
  sortParts,
  summarizeMaterials,
} from './inventory'
import { schematicScale, stockFace } from './schematic'

function part(
  partNumber: string,
  material: string,
  sizeMm: [number, number, number],
  quantity: number,
): ManifestPart {
  return {
    partNumber,
    description: partNumber,
    material,
    quantity,
    sizeMm,
    unitVolumeMm3: sizeMm[0] * sizeMm[1] * sizeMm[2],
    colorRgba: [0.4, 0.3, 0.2, 1],
    placementNames: Array.from(
      { length: quantity },
      (_, index) => `${partNumber}-${index}`,
    ),
  }
}

describe('materials inventory projections', () => {
  it('groups occurrence counts and finished volume by material', () => {
    const summary = summarizeMaterials([
      part('RAIL-001', 'ash', [500, 40, 20], 2),
      part('LEG-001', 'ash', [40, 40, 400], 4),
      part('TOP-001', 'oak', [1000, 300, 20], 1),
    ])

    expect(
      summary.map(({ name, occurrences, partTypes, volumeMm3 }) => ({
        name,
        occurrences,
        partTypes,
        volumeMm3,
      })),
    ).toEqual([
      { name: 'ash', occurrences: 6, partTypes: 2, volumeMm3: 3_360_000 },
      { name: 'oak', occurrences: 1, partTypes: 1, volumeMm3: 6_000_000 },
    ])
  })

  it('sorts parts by material and then stable part number', () => {
    const parts = [
      part('TOP-001', 'oak', [1000, 300, 20], 1),
      part('RAIL-001', 'ash', [500, 40, 20], 2),
      part('LEG-001', 'ash', [40, 40, 400], 4),
    ]

    expect(sortParts(parts).map((item) => item.partNumber)).toEqual([
      'LEG-001',
      'RAIL-001',
      'TOP-001',
    ])
  })

  it('derives a consistent stock face and shared document scale', () => {
    const top = part('TOP-001', 'oak', [1000, 20, 300], 1)

    expect(stockFace(top)).toEqual({
      length: 1000,
      width: 300,
      thickness: 20,
      lengthAxis: 'x',
      widthAxis: 'z',
    })
    expect(schematicScale([top])).toBeCloseTo(0.27)
  })

  it('indexes drill operations by their stable part number', () => {
    const operation = {
      operationId: 'DR-001',
      partNumber: 'LEG-001',
    } as ManifestDrillOperation

    expect(groupDrillOperationsByPart([operation]).get('LEG-001')).toEqual([
      operation,
    ])
  })
})
