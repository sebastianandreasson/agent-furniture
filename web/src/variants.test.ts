import { describe, expect, it } from 'vitest'
import type { CatalogDesign } from './types'
import { groupDesignFamilies, selectFamilyDesign } from './variants'

function design(
  id: string,
  familyId: string,
  variantId: string,
): CatalogDesign {
  return {
    id,
    name: id,
    model: 'entryway_bench',
    familyId,
    variantId,
    variantLabel: variantId,
    revision: id,
    overallSizeMm: { x: 1, y: 1, z: 1 },
    partOccurrences: 1,
    parameters: {},
    artifacts: { glb: `/${id}.glb`, manifest: `/${id}.json` },
  }
}

describe('furniture variants', () => {
  it('groups builds into families without changing catalog order', () => {
    const shoe = design('bench-shoe', 'bench', 'shoe')
    const table = design('table', 'table', 'default')
    const umbrella = design('bench-umbrella', 'bench', 'umbrella')

    expect(groupDesignFamilies([shoe, table, umbrella])).toEqual([
      { id: 'bench', designs: [shoe, umbrella] },
      { id: 'table', designs: [table] },
    ])
  })

  it('preserves a matching variant when changing family and falls back safely', () => {
    const standard = design('table-standard', 'table', 'standard')
    const compact = design('table-compact', 'table', 'compact')
    const family = { id: 'table', designs: [standard, compact] }

    expect(selectFamilyDesign(family, 'compact')).toBe(compact)
    expect(selectFamilyDesign(family, 'missing')).toBe(standard)
  })
})
