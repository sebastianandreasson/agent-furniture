// @vitest-environment jsdom

import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { ManifestDrillOperation, ManifestPart } from '../types'
import { PartDetailModal } from './PartDetailModal'

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

const OPERATION: ManifestDrillOperation = {
  operationId: 'DR-EXT-SHELF-SLAT-CLEARANCE',
  partNumber: PART.partNumber,
  label: 'Countersunk clearance holes through each angled shelf slat',
  kind: 'countersunk_clearance',
  face: 'top face',
  viewAxes: ['y', 'x'],
  diameterMm: 4.5,
  depthMm: 16,
  countersinkDiameterMm: 8,
  angleDeg: 90,
  fastenerCode: 'CSK-4X35',
  countsFastener: true,
  geometryMode: 'cut',
  pointsPerPart: 2,
  partQuantity: PART.quantity,
  totalHoles: 8,
  points: [
    {
      positionMm: [15, 110, 16],
      axis: [0, 0, -1],
      label: 'front support rail',
    },
    {
      positionMm: [15, 246.8, 16],
      axis: [0, 0, -1],
      label: 'back support rail',
    },
  ],
  notes: 'Confirm the countersink on matching offcuts.',
}

const DENSE_RAIL: ManifestPart = {
  partNumber: 'EXTENSION-TOP-RAIL-LONG-001',
  description: 'Long rail below extension top',
  material: 'warm grey painted beech',
  quantity: 2,
  sizeMm: [358, 24, 62],
  unitVolumeMm3: 532_704,
  colorRgba: [0.5, 0.48, 0.42, 1],
  placementNames: ['extension-front-rail', 'extension-back-rail'],
}

const DENSE_RAIL_OPERATIONS: ManifestDrillOperation[] = [
  {
    operationId: 'DR-EXT-TOP-RAIL-ENDS',
    partNumber: DENSE_RAIL.partNumber,
    label: 'Pocket holes at both extension-rail ends',
    kind: 'pocket',
    face: 'inside face',
    viewAxes: ['x', 'z'],
    diameterMm: 9.5,
    depthMm: null,
    countersinkDiameterMm: null,
    angleDeg: 15,
    fastenerCode: 'PH-38-FINE',
    countsFastener: true,
    geometryMode: 'marked_only',
    pointsPerPart: 4,
    partQuantity: DENSE_RAIL.quantity,
    totalHoles: 8,
    points: [
      { positionMm: [18, 12, 18], axis: [0, 1, 0], label: 'left lower' },
      { positionMm: [18, 12, 44], axis: [0, 1, 0], label: 'left upper' },
      { positionMm: [340, 12, 18], axis: [0, 1, 0], label: 'right lower' },
      { positionMm: [340, 12, 44], axis: [0, 1, 0], label: 'right upper' },
    ],
    notes: '',
  },
  {
    operationId: 'DR-EXT-TOP-RAIL-UPWARD',
    partNumber: DENSE_RAIL.partNumber,
    label: 'Upward pocket holes for the extension top',
    kind: 'pocket',
    face: 'inside face',
    viewAxes: ['x', 'z'],
    diameterMm: 9.5,
    depthMm: null,
    countersinkDiameterMm: null,
    angleDeg: 15,
    fastenerCode: 'PH-32-FINE',
    countsFastener: true,
    geometryMode: 'marked_only',
    pointsPerPart: 2,
    partQuantity: DENSE_RAIL.quantity,
    totalHoles: 4,
    points: [
      {
        positionMm: [119.3, 12, 44],
        axis: [0, 0, 1],
        label: 'left top attachment',
      },
      {
        positionMm: [238.7, 12, 44],
        axis: [0, 0, 1],
        label: 'right top attachment',
      },
    ],
    notes: '',
  },
]

describe('PartDetailModal', () => {
  it('shows edge offsets and center-to-center connection measurements', () => {
    const onClose = vi.fn()
    render(
      <PartDetailModal
        part={PART}
        drillOperations={[OPERATION]}
        onClose={onClose}
      />,
    )

    expect(screen.getByRole('dialog')).toBeTruthy()
    expect(screen.getByRole('heading', { name: PART.description })).toBeTruthy()
    expect(
      screen.getByRole('columnheader', { name: 'Y from min' }),
    ).toBeTruthy()
    expect(screen.getByText('136.8 mm center-to-center')).toBeTruthy()
    expect(screen.getByText('front support rail')).toBeTruthy()

    fireEvent.keyDown(window, { key: 'Escape' })
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('keeps dense connection dimensions in the schedule instead of over the face drawing', () => {
    render(
      <PartDetailModal
        part={DENSE_RAIL}
        drillOperations={DENSE_RAIL_OPERATIONS}
        onClose={() => {}}
      />,
    )

    const drawings = screen.getAllByRole('img', {
      name: /Long rail below extension top, xz face/i,
    })
    const drawing = drawings[drawings.length - 1]
    expect(drawing.querySelectorAll('.part-detail-projection')).toHaveLength(0)
    expect(drawing.querySelectorAll('.part-detail-spacing')).toHaveLength(0)
    expect(drawing.textContent).toContain('H1')
    expect(drawing.textContent).toContain('H6')
    expect(screen.getByText('323 mm center-to-center')).toBeTruthy()
    expect(
      screen.getAllByRole('columnheader', { name: 'X from min' }).length,
    ).toBeGreaterThan(0)
  })

  it('reveals one marker edge-offset callout on hover or keyboard focus', () => {
    render(
      <PartDetailModal
        part={DENSE_RAIL}
        drillOperations={DENSE_RAIL_OPERATIONS}
        onClose={() => {}}
      />,
    )

    const drawings = screen.getAllByRole('img', {
      name: /Long rail below extension top, xz face/i,
    })
    const drawing = drawings[drawings.length - 1]
    const markers = drawing.querySelectorAll<SVGGElement>('.part-detail-marker')

    expect(drawing.querySelector('.part-detail-point-overlay')).toBeNull()
    fireEvent.mouseEnter(markers[0])
    expect(drawing.querySelector('.part-detail-point-overlay')).toBeTruthy()
    expect(drawing.textContent).toContain('X min 18 mm · max 340 mm')
    expect(drawing.textContent).toContain('Z min 18 mm · max 44 mm')

    fireEvent.mouseLeave(markers[0])
    expect(drawing.querySelector('.part-detail-point-overlay')).toBeNull()

    expect(markers[4].getAttribute('tabindex')).toBe('0')
    fireEvent.focus(markers[4])
    expect(drawing.textContent).toContain('X min 119.3 mm · max 238.7 mm')
    expect(drawing.textContent).toContain('Z min 44 mm · max 18 mm')
  })
})
