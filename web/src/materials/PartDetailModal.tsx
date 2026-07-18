import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import type {
  AxisName,
  ManifestDrillOperation,
  ManifestDrillPoint,
  ManifestPart,
} from '../types'
import {
  consecutiveHoleSpacings,
  groupDrillOperations,
  operationSpecification,
  pointMeasurements,
} from './drilling'
import { formatDimension, rgbaCss } from './inventory'
import { axisIndex, stockFace } from './schematic'

const DETAIL_WIDTH = 720
const DETAIL_HEIGHT = 440
const DETAIL_LEFT = 104
const DETAIL_TOP = 56
const DETAIL_MAX_WIDTH = 530
const DETAIL_MAX_HEIGHT = 270
const POINT_CALLOUT_WIDTH = 272
const POINT_CALLOUT_HEIGHT = 76

function pointPosition(
  point: ManifestDrillPoint,
  axes: [AxisName, AxisName],
  scale: number,
  drawingHeight: number,
) {
  return {
    x: DETAIL_LEFT + point.positionMm[axisIndex(axes[0])] * scale,
    y:
      DETAIL_TOP + drawingHeight - point.positionMm[axisIndex(axes[1])] * scale,
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
  drawingBottom,
  drawingRight,
}: {
  point: ManifestDrillPoint
  markerNumber: number
  axes: [AxisName, AxisName]
  position: { x: number; y: number }
  length: number
  width: number
  drawingHeight: number
  drawingBottom: number
  drawingRight: number
}) {
  const [horizontalAxis, verticalAxis] = axes
  const horizontalOffset = point.positionMm[axisIndex(horizontalAxis)]
  const verticalOffset = point.positionMm[axisIndex(verticalAxis)]
  const horizontalMaximumOffset = length - horizontalOffset
  const verticalMaximumOffset = width - verticalOffset
  const boxX = clamp(
    position.x - POINT_CALLOUT_WIDTH / 2,
    12,
    DETAIL_WIDTH - POINT_CALLOUT_WIDTH - 12,
  )
  const drawingMiddle = DETAIL_TOP + drawingHeight / 2
  let boxY =
    position.y <= drawingMiddle
      ? position.y - POINT_CALLOUT_HEIGHT - 18
      : position.y + 18
  const dimensionBandStart = drawingBottom + 35
  const dimensionBandEnd = drawingBottom + 84
  const overlapsOverallDimension =
    boxY < dimensionBandEnd && boxY + POINT_CALLOUT_HEIGHT > dimensionBandStart

  if (overlapsOverallDimension) {
    const belowDimensions = dimensionBandEnd + 10
    boxY =
      belowDimensions + POINT_CALLOUT_HEIGHT <= DETAIL_HEIGHT - 8
        ? belowDimensions
        : position.y - POINT_CALLOUT_HEIGHT - 18
  }
  boxY = clamp(boxY, 8, DETAIL_HEIGHT - POINT_CALLOUT_HEIGHT - 8)

  const leaderAnchorX = clamp(
    position.x,
    boxX + 16,
    boxX + POINT_CALLOUT_WIDTH - 16,
  )
  const leaderAnchorY = boxY > position.y ? boxY : boxY + POINT_CALLOUT_HEIGHT

  return (
    <g className="part-detail-point-overlay" pointerEvents="none">
      <line
        className="is-horizontal"
        x1={DETAIL_LEFT}
        y1={position.y}
        x2={drawingRight}
        y2={position.y}
      />
      <line
        className="is-vertical"
        x1={position.x}
        y1={DETAIL_TOP}
        x2={position.x}
        y2={drawingBottom}
      />
      <circle cx={position.x} cy={position.y} r="14" />
      <line
        className="part-detail-point-leader"
        x1={position.x}
        y1={position.y}
        x2={leaderAnchorX}
        y2={leaderAnchorY}
      />
      <g
        className="part-detail-point-callout"
        transform={`translate(${boxX} ${boxY})`}
      >
        <rect
          width={POINT_CALLOUT_WIDTH}
          height={POINT_CALLOUT_HEIGHT}
          rx="7"
        />
        <text x="15" y="20" className="part-detail-point-callout-title">
          H{markerNumber} · edge offsets
        </text>
        <text x="15" y="43">
          {horizontalAxis.toUpperCase()} min {formatDimension(horizontalOffset)}{' '}
          mm · max {formatDimension(horizontalMaximumOffset)} mm
        </text>
        <text x="15" y="62">
          {verticalAxis.toUpperCase()} min {formatDimension(verticalOffset)} mm
          · max {formatDimension(verticalMaximumOffset)} mm
        </text>
      </g>
    </g>
  )
}

function DetailedFaceDiagram({
  part,
  operations,
  axes,
}: {
  part: ManifestPart
  operations: ManifestDrillOperation[]
  axes: [AxisName, AxisName]
}) {
  const [activeMarkerIndex, setActiveMarkerIndex] = useState<number | null>(
    null,
  )
  const [horizontalAxis, verticalAxis] = axes
  const length = part.sizeMm[axisIndex(horizontalAxis)]
  const width = part.sizeMm[axisIndex(verticalAxis)]
  const scale = Math.min(DETAIL_MAX_WIDTH / length, DETAIL_MAX_HEIGHT / width)
  const drawingWidth = Math.max(4, length * scale)
  const drawingHeight = Math.max(4, width * scale)
  const drawingBottom = DETAIL_TOP + drawingHeight
  const drawingRight = DETAIL_LEFT + drawingWidth
  const markers = operations.flatMap((operation) =>
    operation.points.map((point) => ({ operation, point })),
  )

  return (
    <svg
      className="part-detail-drawing"
      viewBox={`0 0 ${DETAIL_WIDTH} ${DETAIL_HEIGHT}`}
      role="img"
      aria-label={`${part.description}, ${horizontalAxis}${verticalAxis} face with connection dimensions`}
    >
      <rect
        className="part-detail-stock"
        x={DETAIL_LEFT}
        y={DETAIL_TOP}
        width={drawingWidth}
        height={drawingHeight}
        rx="3"
        fill={rgbaCss(part.colorRgba)}
      />

      <g className="part-detail-overall-dimension">
        <line
          x1={DETAIL_LEFT}
          y1={drawingBottom + 50}
          x2={drawingRight}
          y2={drawingBottom + 50}
        />
        <line
          x1={DETAIL_LEFT}
          y1={drawingBottom + 43}
          x2={DETAIL_LEFT}
          y2={drawingBottom + 57}
        />
        <line
          x1={drawingRight}
          y1={drawingBottom + 43}
          x2={drawingRight}
          y2={drawingBottom + 57}
        />
        <text
          x={DETAIL_LEFT + drawingWidth / 2}
          y={drawingBottom + 72}
          textAnchor="middle"
        >
          {formatDimension(length)} mm · {horizontalAxis.toUpperCase()}
        </text>
        <line
          x1={DETAIL_LEFT - 50}
          y1={DETAIL_TOP}
          x2={DETAIL_LEFT - 50}
          y2={drawingBottom}
        />
        <line
          x1={DETAIL_LEFT - 57}
          y1={DETAIL_TOP}
          x2={DETAIL_LEFT - 43}
          y2={DETAIL_TOP}
        />
        <line
          x1={DETAIL_LEFT - 57}
          y1={drawingBottom}
          x2={DETAIL_LEFT - 43}
          y2={drawingBottom}
        />
        <text
          x={DETAIL_LEFT - 68}
          y={DETAIL_TOP + drawingHeight / 2}
          textAnchor="middle"
          transform={`rotate(-90 ${DETAIL_LEFT - 68} ${DETAIL_TOP + drawingHeight / 2})`}
        >
          {formatDimension(width)} mm · {verticalAxis.toUpperCase()}
        </text>
      </g>

      {markers.map(({ operation, point }, index) => {
        const position = pointPosition(point, axes, scale, drawingHeight)
        const verticalOffset = point.positionMm[axisIndex(verticalAxis)]
        const labelAbove = verticalOffset >= width / 2
        const labelToLeft = drawingRight - position.x < 34
        return (
          <g
            className={`part-detail-marker is-${operation.kind}`}
            key={`${operation.operationId}-${index}`}
            transform={`translate(${position.x} ${position.y})`}
            tabIndex={0}
            aria-label={`H${index + 1}: ${horizontalAxis.toUpperCase()} ${formatDimension(point.positionMm[axisIndex(horizontalAxis)])} millimetres from minimum edge and ${formatDimension(length - point.positionMm[axisIndex(horizontalAxis)])} from maximum edge; ${verticalAxis.toUpperCase()} ${formatDimension(point.positionMm[axisIndex(verticalAxis)])} millimetres from minimum edge and ${formatDimension(width - point.positionMm[axisIndex(verticalAxis)])} from maximum edge`}
            onMouseEnter={() => setActiveMarkerIndex(index)}
            onMouseLeave={() => setActiveMarkerIndex(null)}
            onFocus={() => setActiveMarkerIndex(index)}
            onBlur={() => setActiveMarkerIndex(null)}
          >
            <circle r="6" />
            <line x1="-10" y1="0" x2="10" y2="0" />
            <line x1="0" y1="-10" x2="0" y2="10" />
            <text
              x={labelToLeft ? -12 : 12}
              y={labelAbove ? -12 : 22}
              textAnchor={labelToLeft ? 'end' : 'start'}
            >
              H{index + 1}
            </text>
          </g>
        )
      })}

      {activeMarkerIndex !== null && markers[activeMarkerIndex] && (
        <PointOffsetOverlay
          point={markers[activeMarkerIndex].point}
          markerNumber={activeMarkerIndex + 1}
          axes={axes}
          position={pointPosition(
            markers[activeMarkerIndex].point,
            axes,
            scale,
            drawingHeight,
          )}
          length={length}
          width={width}
          drawingHeight={drawingHeight}
          drawingBottom={drawingBottom}
          drawingRight={drawingRight}
        />
      )}
    </svg>
  )
}

function OperationMeasurements({
  part,
  operation,
  markerOffset,
}: {
  part: ManifestPart
  operation: ManifestDrillOperation
  markerOffset: number
}) {
  const measurements = pointMeasurements(part, operation)
  const spacings = consecutiveHoleSpacings(operation)
  const [horizontalAxis, verticalAxis] = operation.viewAxes

  return (
    <article className="part-detail-operation">
      <div className="part-detail-operation-heading">
        <div>
          <span>{operation.operationId}</span>
          <h4>{operation.label}</h4>
        </div>
        <strong>{operationSpecification(operation)}</strong>
      </div>
      <div className="part-detail-table-wrap">
        <table>
          <thead>
            <tr>
              <th>Hole</th>
              <th>{horizontalAxis.toUpperCase()} from min</th>
              <th>{horizontalAxis.toUpperCase()} to max</th>
              <th>{verticalAxis.toUpperCase()} from min</th>
              <th>{verticalAxis.toUpperCase()} to max</th>
              <th>Reference</th>
            </tr>
          </thead>
          <tbody>
            {measurements.map((measurement, index) => (
              <tr key={`${operation.operationId}-${index}`}>
                <td>H{markerOffset + index + 1}</td>
                <td>{formatDimension(measurement.fromHorizontalMin)} mm</td>
                <td>{formatDimension(measurement.toHorizontalMax)} mm</td>
                <td>{formatDimension(measurement.fromVerticalMin)} mm</td>
                <td>{formatDimension(measurement.toVerticalMax)} mm</td>
                <td>{measurement.point.label || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {spacings.length > 0 && (
        <div className="part-detail-spacing-list">
          {spacings.map((spacing, index) => (
            <div key={`${operation.operationId}-spacing-${index}`}>
              <span>
                H{markerOffset + index + 1} → H{markerOffset + index + 2}
              </span>
              <strong>
                {formatDimension(spacing.centerToCenter)} mm center-to-center
              </strong>
              <small>
                Δ{horizontalAxis.toUpperCase()}{' '}
                {formatDimension(Math.abs(spacing.deltaHorizontal))} · Δ
                {verticalAxis.toUpperCase()}{' '}
                {formatDimension(Math.abs(spacing.deltaVertical))} mm
              </small>
            </div>
          ))}
        </div>
      )}
      {operation.notes && <p>{operation.notes}</p>}
    </article>
  )
}

function DetailFace({
  part,
  operations,
  axes,
}: {
  part: ManifestPart
  operations: ManifestDrillOperation[]
  axes: [AxisName, AxisName]
}) {
  const faceNames =
    operations.length > 0
      ? [...new Set(operations.map((operation) => operation.face))].join(' + ')
      : `${axes[0]}${axes[1]} stock face`
  let markerOffset = 0
  const operationEntries = operations.map((operation) => {
    const entry = { operation, markerOffset }
    markerOffset += operation.points.length
    return entry
  })

  return (
    <section className="part-detail-face">
      <div className="part-detail-face-heading">
        <div>
          <span>{faceNames}</span>
          <h3>
            {axes[0].toUpperCase()} × {axes[1].toUpperCase()} face
          </h3>
        </div>
        <small>Datum: minimum stock corner</small>
      </div>
      <DetailedFaceDiagram part={part} operations={operations} axes={axes} />
      {operationEntries.length > 0 && (
        <div
          className="part-detail-connection-key"
          aria-label="Connection marker index"
        >
          <p>
            <strong>Connection index</strong>
            <span>
              Hover or focus a marker for its edge offsets. Exact centre spacing
              is listed below.
            </span>
          </p>
          <div>
            {operationEntries.map(({ operation, markerOffset: offset }) => {
              const first = offset + 1
              const last = offset + operation.points.length
              return (
                <span
                  className={`is-${operation.kind}`}
                  key={`${operation.operationId}-key`}
                >
                  <i aria-hidden="true" />
                  <b>{first === last ? `H${first}` : `H${first}–H${last}`}</b>
                  {operation.label}
                </span>
              )
            })}
          </div>
        </div>
      )}
      <div className="part-detail-operations">
        {operationEntries.map(({ operation, markerOffset: offset }) => (
          <OperationMeasurements
            key={operation.operationId}
            part={part}
            operation={operation}
            markerOffset={offset}
          />
        ))}
        {operations.length === 0 && (
          <div className="part-detail-empty">
            No connection or drilling operations on this face.
          </div>
        )}
      </div>
    </section>
  )
}

export function PartDetailModal({
  part,
  drillOperations,
  onClose,
}: {
  part: ManifestPart
  drillOperations: ManifestDrillOperation[]
  onClose: () => void
}) {
  const faces = groupDrillOperations(part, drillOperations)
  const stock = stockFace(part)

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [onClose])

  return createPortal(
    <div
      className="part-detail-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <section
        className="part-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="part-detail-title"
      >
        <header className="part-detail-header">
          <div>
            <p className="eyebrow">Connection detail · millimetres</p>
            <span>{part.partNumber}</span>
            <h2 id="part-detail-title">{part.description}</h2>
            <p>
              {part.material} · quantity {part.quantity} · nominal stock{' '}
              {formatDimension(stock.length)} × {formatDimension(stock.width)} ×{' '}
              {formatDimension(stock.thickness)} mm
            </p>
          </div>
          <button type="button" onClick={onClose} autoFocus>
            <span>Close detail</span>
            <b aria-hidden="true">×</b>
          </button>
        </header>
        <main className="part-detail-content">
          {faces.map(([key, operations]) => (
            <DetailFace
              key={key}
              part={part}
              operations={operations}
              axes={key.split('') as [AxisName, AxisName]}
            />
          ))}
        </main>
        <footer className="part-detail-footer">
          Hole centres are measured from the minimum corner of nominal cut
          stock. Confirm face orientation, hardware, jig settings, tolerances,
          and edge distances on matching offcuts before fabrication.
        </footer>
      </section>
    </div>,
    document.body,
  )
}
