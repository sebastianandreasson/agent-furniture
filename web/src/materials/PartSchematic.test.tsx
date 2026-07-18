// @vitest-environment jsdom

import { fireEvent, render } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { ManifestDrillOperation, ManifestPart } from '../types'
import { PartSchematic } from './PartSchematic'

const PART: ManifestPart = {
  partNumber: 'EXTENSION-SHELF-SLAT-001',
  description: 'Angled front-to-back slat for indented extension shoe shelf',
  material: 'warm grey painted beech',
  quantity: 4,
  sizeMm: [30, 260, 16],
  unitVolumeMm3: 124_800,
  colorRgba: [0.5, 0.48, 0.42, 1],
  placementNames: ['slat-1', 'slat-2', 'slat-3', 'slat-4'],
}

const LARGE_PART: ManifestPart = {
  partNumber: 'SEAT-BASE-001',
  description: 'Rounded seat support board',
  material: 'warm grey painted beech',
  quantity: 1,
  sizeMm: [1200, 380, 22],
  unitVolumeMm3: 10_032_000,
  colorRgba: [0.5, 0.48, 0.42, 1],
  placementNames: ['seat-base'],
}

function drillOperation(
  operationId: string,
  viewAxes: ManifestDrillOperation['viewAxes'],
  positionMm: [number, number, number],
  kind: string,
): ManifestDrillOperation {
  return {
    operationId,
    partNumber: PART.partNumber,
    label: operationId,
    kind,
    face: 'test face',
    viewAxes,
    diameterMm: 3,
    depthMm: 20,
    countersinkDiameterMm: null,
    angleDeg: null,
    fastenerCode: null,
    countsFastener: false,
    geometryMode: 'marked_only',
    pointsPerPart: 1,
    partQuantity: PART.quantity,
    totalHoles: PART.quantity,
    points: [{ positionMm, axis: [0, 0, 1], label: 'test hole' }],
    notes: '',
  }
}

describe('PartSchematic', () => {
  it('places multiple stock faces in a compact row with safe dimension labels', () => {
    const onOpen = vi.fn()
    const { container } = render(
      <PartSchematic
        part={PART}
        scale={0.225}
        index={3}
        active={false}
        onHover={() => undefined}
        onOpen={onOpen}
        drillOperations={[
          drillOperation(
            'top holes',
            ['y', 'x'],
            [15, 110, 16],
            'countersunk_clearance',
          ),
          drillOperation('front pilot', ['x', 'z'], [15, 0, 8], 'pilot'),
        ]}
      />,
    )

    const faceGrid = container.querySelector('.schematic-face-grid')
    const faces = faceGrid?.querySelectorAll('.schematic-face')
    const diagrams = faceGrid?.querySelectorAll('svg')

    expect(faces).toHaveLength(2)
    expect(diagrams).toHaveLength(2)
    expect(
      [...diagrams!].map((diagram) => diagram.getAttribute('viewBox')),
    ).toEqual(['0 0 180 116', '0 0 180 116'])

    const narrowDimension = [...diagrams![1].querySelectorAll('text')].find(
      (text) => text.textContent === '30 mm (X)',
    )
    expect(narrowDimension?.getAttribute('class')).toBe(
      'schematic-dimension-label',
    )
    expect(narrowDimension?.getAttribute('x')).toBe('12')
    expect(narrowDimension?.getAttribute('y')).toBe('108')
    expect(narrowDimension?.getAttribute('text-anchor')).toBe('start')
    expect(
      container
        .querySelector('.drill-marker.is-countersunk_clearance circle')
        ?.getAttribute('r'),
    ).toBe('2')
    expect(
      container
        .querySelector('.drill-marker.is-pilot circle')
        ?.getAttribute('r'),
    ).toBe('2')
    expect(container.querySelector('.drill-marker line')).toBeNull()
    expect(container.querySelector('.schematic-quantity')).toBeNull()
    expect(
      container.querySelector('.schematic-piece-heading > b')?.textContent,
    ).toBe('×4')

    fireEvent.click(container.querySelector('.schematic-piece')!)
    expect(onOpen).toHaveBeenCalledWith(PART.partNumber)
  })

  it('reserves a caption row and a separate dimension band for a large stock face', () => {
    const { container } = render(
      <PartSchematic
        part={LARGE_PART}
        scale={0.225}
        index={9}
        active={false}
        onHover={() => undefined}
        onOpen={() => undefined}
        drillOperations={[]}
      />,
    )

    const face = container.querySelector('.schematic-face')!
    const caption = face.querySelector('.schematic-face-label')!
    const diagram = face.querySelector('svg')!
    const stock = diagram.querySelector('rect')!
    const dimension = diagram.querySelector('.schematic-dimension')!
    const dimensionLabel = dimension.querySelector('text')!

    expect(caption.nextElementSibling).toBe(diagram)
    expect(diagram.getAttribute('viewBox')).toBe('0 0 360 124')
    expect(stock.getAttribute('y')).toBe('2')
    expect(stock.getAttribute('height')).toBe('84')
    expect(dimension.querySelector('line')?.getAttribute('y1')).toBe('101')
    expect(dimensionLabel.getAttribute('y')).toBe('119')
    expect(dimensionLabel.getAttribute('text-anchor')).toBe('middle')
  })
})
