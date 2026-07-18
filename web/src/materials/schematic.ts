import type { AxisName, ManifestPart } from '../types'

export const SCHEMATIC_AXES: AxisName[] = ['x', 'y', 'z']

export type StockFace = {
  length: number
  width: number
  thickness: number
  lengthAxis: AxisName
  widthAxis: AxisName
}

export function axisIndex(axis: AxisName) {
  return SCHEMATIC_AXES.indexOf(axis)
}

export function stockFace(part: ManifestPart): StockFace {
  const dimensions = SCHEMATIC_AXES.map((axis, index) => ({
    axis,
    value: part.sizeMm[index],
  })).sort((left, right) => right.value - left.value)
  return {
    length: dimensions[0].value,
    width: dimensions[1].value,
    thickness: dimensions[2].value,
    lengthAxis: dimensions[0].axis,
    widthAxis: dimensions[1].axis,
  }
}

export function schematicScale(parts: ManifestPart[]) {
  const faces = parts.map(stockFace)
  const longest = Math.max(...faces.map((face) => face.length), 1)
  const widest = Math.max(...faces.map((face) => face.width), 1)
  return Math.min(270 / longest, 84 / widest)
}
