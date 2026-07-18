import type {
  AxisName,
  ManifestDrillOperation,
  ManifestDrillPoint,
  ManifestPart,
} from '../types'
import { formatDimension } from './inventory'
import { axisIndex, stockFace } from './schematic'

export function groupDrillOperations(
  part: ManifestPart,
  operations: ManifestDrillOperation[],
) {
  const primary = stockFace(part)
  const groups = new Map<string, ManifestDrillOperation[]>()
  for (const operation of operations) {
    const key = operation.viewAxes.join('')
    const current = groups.get(key) ?? []
    current.push(operation)
    groups.set(key, current)
  }
  const primaryKey = `${primary.lengthAxis}${primary.widthAxis}`
  if (!groups.has(primaryKey)) groups.set(primaryKey, [])
  return [...groups.entries()].sort(([left], [right]) => {
    if (left === primaryKey) return -1
    if (right === primaryKey) return 1
    return left.localeCompare(right)
  })
}

export function operationSpecification(operation: ManifestDrillOperation) {
  const details = [`Ø${formatDimension(operation.diameterMm)}`]
  if (operation.countersinkDiameterMm !== null) {
    details.push(`CSK Ø${formatDimension(operation.countersinkDiameterMm)}`)
  }
  if (operation.depthMm !== null) {
    details.push(`${formatDimension(operation.depthMm)} deep`)
  } else if (operation.kind === 'pocket_hole') {
    details.push('jig depth')
  }
  if (operation.angleDeg !== null) {
    details.push(`${formatDimension(operation.angleDeg)}°`)
  }
  return details.join(' · ')
}

export function coordinateSummary(operation: ManifestDrillOperation) {
  const [horizontalAxis, verticalAxis] = operation.viewAxes
  const horizontalIndex = axisIndex(horizontalAxis)
  const verticalIndex = axisIndex(verticalAxis)
  const pointText = (index: number) => {
    const point = operation.points[index]
    return `${horizontalAxis.toUpperCase()} ${formatDimension(point.positionMm[horizontalIndex])} / ${verticalAxis.toUpperCase()} ${formatDimension(point.positionMm[verticalIndex])}`
  }
  if (operation.points.length <= 4) {
    return operation.points.map((_, index) => pointText(index)).join(' · ')
  }
  return `${operation.points.length} centres · ${pointText(0)} → ${pointText(operation.points.length - 1)}`
}

export type PointMeasurement = {
  point: ManifestDrillPoint
  horizontalAxis: AxisName
  verticalAxis: AxisName
  fromHorizontalMin: number
  toHorizontalMax: number
  fromVerticalMin: number
  toVerticalMax: number
}

export function pointMeasurements(
  part: ManifestPart,
  operation: ManifestDrillOperation,
): PointMeasurement[] {
  const [horizontalAxis, verticalAxis] = operation.viewAxes
  const horizontalIndex = axisIndex(horizontalAxis)
  const verticalIndex = axisIndex(verticalAxis)
  const horizontalSize = part.sizeMm[horizontalIndex]
  const verticalSize = part.sizeMm[verticalIndex]
  return operation.points.map((point) => {
    const fromHorizontalMin = point.positionMm[horizontalIndex]
    const fromVerticalMin = point.positionMm[verticalIndex]
    return {
      point,
      horizontalAxis,
      verticalAxis,
      fromHorizontalMin,
      toHorizontalMax: horizontalSize - fromHorizontalMin,
      fromVerticalMin,
      toVerticalMax: verticalSize - fromVerticalMin,
    }
  })
}

export type HoleSpacing = {
  fromPoint: ManifestDrillPoint
  toPoint: ManifestDrillPoint
  deltaHorizontal: number
  deltaVertical: number
  centerToCenter: number
}

export function consecutiveHoleSpacings(
  operation: ManifestDrillOperation,
): HoleSpacing[] {
  const [horizontalAxis, verticalAxis] = operation.viewAxes
  const horizontalIndex = axisIndex(horizontalAxis)
  const verticalIndex = axisIndex(verticalAxis)
  const points = [...operation.points].sort(
    (left, right) =>
      left.positionMm[horizontalIndex] - right.positionMm[horizontalIndex] ||
      left.positionMm[verticalIndex] - right.positionMm[verticalIndex],
  )
  return points.slice(1).map((point, index) => {
    const previous = points[index]
    const deltaHorizontal =
      point.positionMm[horizontalIndex] - previous.positionMm[horizontalIndex]
    const deltaVertical =
      point.positionMm[verticalIndex] - previous.positionMm[verticalIndex]
    return {
      fromPoint: previous,
      toPoint: point,
      deltaHorizontal,
      deltaVertical,
      centerToCenter: Math.hypot(deltaHorizontal, deltaVertical),
    }
  })
}
