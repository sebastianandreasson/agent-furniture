import { useState } from 'react'
import type {
  AxisName,
  ManifestDrillOperation,
  ManifestDrillPoint,
  ManifestPart,
} from '../types'
import { formatDimension, rgbaCss } from './inventory'
import { axisIndex } from './schematic'

const WIDTH = 720
const HEIGHT = 440
const LEFT = 104
const TOP = 56
const MAX_WIDTH = 530
const MAX_HEIGHT = 270
const CALLOUT_WIDTH = 272
const CALLOUT_HEIGHT = 76

function pointPosition(
  point: ManifestDrillPoint,
  axes: [AxisName, AxisName],
  scale: number,
  drawingHeight: number,
) {
  return {
    x: LEFT + point.positionMm[axisIndex(axes[0])] * scale,
    y: TOP + drawingHeight - point.positionMm[axisIndex(axes[1])] * scale,
  }
}

function clamp(value: number, minimum: number, maximum: number) {
  return Math.min(Math.max(value, minimum), maximum)
}

function PointOffsetOverlay({
  point,
  markerNumber,
  axes,
  position,
  length,
  width,
  drawingHeight,
}: {
  point: ManifestDrillPoint
  markerNumber: number
  axes: [AxisName, AxisName]
  position: { x: number; y: number }
  length: number
  width: number
  drawingHeight: number
}) {
  const [horizontalAxis, verticalAxis] = axes
  const horizontalOffset = point.positionMm[axisIndex(horizontalAxis)]
  const verticalOffset = point.positionMm[axisIndex(verticalAxis)]
  const drawingBottom = TOP + drawingHeight
  const drawingRight =
    LEFT + length * Math.min(MAX_WIDTH / length, MAX_HEIGHT / width)
  const boxX = clamp(
    position.x - CALLOUT_WIDTH / 2,
    12,
    WIDTH - CALLOUT_WIDTH - 12,
  )
  const above = position.y - CALLOUT_HEIGHT - 18
  const below = position.y + 18
  const dimensionBandEnd = drawingBottom + 84
  let boxY = position.y <= TOP + drawingHeight / 2 ? above : below
  if (boxY < dimensionBandEnd && boxY + CALLOUT_HEIGHT > drawingBottom + 35) {
    boxY =
      dimensionBandEnd + 10 + CALLOUT_HEIGHT <= HEIGHT - 8
        ? dimensionBandEnd + 10
        : above
  }
  boxY = clamp(boxY, 8, HEIGHT - CALLOUT_HEIGHT - 8)
  const leaderX = clamp(position.x, boxX + 16, boxX + CALLOUT_WIDTH - 16)

  return (
    <g className="part-detail-point-overlay" pointerEvents="none">
      <line
        className="is-horizontal"
        x1={LEFT}
        y1={position.y}
        x2={drawingRight}
        y2={position.y}
      />
      <line
        className="is-vertical"
        x1={position.x}
        y1={TOP}
        x2={position.x}
        y2={drawingBottom}
      />
      <circle cx={position.x} cy={position.y} r="14" />
      <line
        className="part-detail-point-leader"
        x1={position.x}
        y1={position.y}
        x2={leaderX}
        y2={boxY > position.y ? boxY : boxY + CALLOUT_HEIGHT}
      />
      <g
        className="part-detail-point-callout"
        transform={`translate(${boxX} ${boxY})`}
      >
        <rect width={CALLOUT_WIDTH} height={CALLOUT_HEIGHT} rx="7" />
        <text x="15" y="20" className="part-detail-point-callout-title">
          H{markerNumber} · edge offsets
        </text>
        <text x="15" y="43">
          {horizontalAxis.toUpperCase()} min {formatDimension(horizontalOffset)}{' '}
          mm · max {formatDimension(length - horizontalOffset)} mm
        </text>
        <text x="15" y="62">
          {verticalAxis.toUpperCase()} min {formatDimension(verticalOffset)} mm
          · max {formatDimension(width - verticalOffset)} mm
        </text>
      </g>
    </g>
  )
}

export function PartDetailDiagram({
  part,
  operations,
  axes,
}: {
  part: ManifestPart
  operations: ManifestDrillOperation[]
  axes: [AxisName, AxisName]
}) {
  const [activeMarker, setActiveMarker] = useState<number | null>(null)
  const [horizontalAxis, verticalAxis] = axes
  const length = part.sizeMm[axisIndex(horizontalAxis)]
  const width = part.sizeMm[axisIndex(verticalAxis)]
  const scale = Math.min(MAX_WIDTH / length, MAX_HEIGHT / width)
  const drawingWidth = Math.max(4, length * scale)
  const drawingHeight = Math.max(4, width * scale)
  const drawingBottom = TOP + drawingHeight
  const drawingRight = LEFT + drawingWidth
  const markers = operations.flatMap((operation) =>
    operation.points.map((point) => ({ operation, point })),
  )

  return (
    <svg
      className="part-detail-drawing"
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      role="img"
      aria-label={`${part.description}, ${horizontalAxis}${verticalAxis} face with connection dimensions`}
    >
      <rect
        className="part-detail-stock"
        x={LEFT}
        y={TOP}
        width={drawingWidth}
        height={drawingHeight}
        rx="3"
        fill={rgbaCss(part.colorRgba)}
      />
      <g className="part-detail-overall-dimension">
        <line
          x1={LEFT}
          y1={drawingBottom + 50}
          x2={drawingRight}
          y2={drawingBottom + 50}
        />
        <line
          x1={LEFT}
          y1={drawingBottom + 43}
          x2={LEFT}
          y2={drawingBottom + 57}
        />
        <line
          x1={drawingRight}
          y1={drawingBottom + 43}
          x2={drawingRight}
          y2={drawingBottom + 57}
        />
        <text
          x={LEFT + drawingWidth / 2}
          y={drawingBottom + 72}
          textAnchor="middle"
        >
          {formatDimension(length)} mm · {horizontalAxis.toUpperCase()}
        </text>
        <line x1={LEFT - 50} y1={TOP} x2={LEFT - 50} y2={drawingBottom} />
        <line x1={LEFT - 57} y1={TOP} x2={LEFT - 43} y2={TOP} />
        <line
          x1={LEFT - 57}
          y1={drawingBottom}
          x2={LEFT - 43}
          y2={drawingBottom}
        />
        <text
          x={LEFT - 68}
          y={TOP + drawingHeight / 2}
          textAnchor="middle"
          transform={`rotate(-90 ${LEFT - 68} ${TOP + drawingHeight / 2})`}
        >
          {formatDimension(width)} mm · {verticalAxis.toUpperCase()}
        </text>
      </g>

      {markers.map(({ operation, point }, index) => {
        const position = pointPosition(point, axes, scale, drawingHeight)
        const horizontalOffset = point.positionMm[axisIndex(horizontalAxis)]
        const verticalOffset = point.positionMm[axisIndex(verticalAxis)]
        return (
          <g
            className={`part-detail-marker is-${operation.kind}`}
            key={`${operation.operationId}-${index}`}
            transform={`translate(${position.x} ${position.y})`}
            tabIndex={0}
            aria-label={`H${index + 1}: ${horizontalAxis.toUpperCase()} ${formatDimension(horizontalOffset)} millimetres from minimum edge and ${formatDimension(length - horizontalOffset)} from maximum edge; ${verticalAxis.toUpperCase()} ${formatDimension(verticalOffset)} millimetres from minimum edge and ${formatDimension(width - verticalOffset)} from maximum edge`}
            onMouseEnter={() => setActiveMarker(index)}
            onMouseLeave={() => setActiveMarker(null)}
            onFocus={() => setActiveMarker(index)}
            onBlur={() => setActiveMarker(null)}
          >
            <circle r="6" />
            <line x1="-10" y1="0" x2="10" y2="0" />
            <line x1="0" y1="-10" x2="0" y2="10" />
            <text
              x={drawingRight - position.x < 34 ? -12 : 12}
              y={verticalOffset >= width / 2 ? -12 : 22}
              textAnchor={drawingRight - position.x < 34 ? 'end' : 'start'}
            >
              H{index + 1}
            </text>
          </g>
        )
      })}

      {activeMarker !== null && markers[activeMarker] && (
        <PointOffsetOverlay
          point={markers[activeMarker].point}
          markerNumber={activeMarker + 1}
          axes={axes}
          position={pointPosition(
            markers[activeMarker].point,
            axes,
            scale,
            drawingHeight,
          )}
          length={length}
          width={width}
          drawingHeight={drawingHeight}
        />
      )}
    </svg>
  )
}
