import type { AxisName, ManifestDrillOperation, ManifestPart } from '../types'
import {
  coordinateSummary,
  groupDrillOperations,
  operationSpecification,
} from './drilling'
import { formatDimension, rgbaCss } from './inventory'
import { axisIndex, stockFace } from './schematic'

function FaceDiagram({
  part,
  operations,
  axes,
  scale,
  primary,
  compact,
}: {
  part: ManifestPart
  operations: ManifestDrillOperation[]
  axes: [AxisName, AxisName]
  scale: number
  primary: boolean
  compact: boolean
}) {
  const [lengthAxis, widthAxis] = axes
  const length = part.sizeMm[axisIndex(lengthAxis)]
  const width = part.sizeMm[axisIndex(widthAxis)]
  const diagramWidth = compact ? 180 : 360
  const diagramHeight = compact ? 116 : 124
  const drawingAreaHeight = compact ? 78 : 88
  const drawingScale = Math.min(
    scale,
    (compact ? 140 : 270) / length,
    (compact ? 68 : 84) / width,
  )
  const drawingWidth = Math.max(2, length * drawingScale)
  const drawingHeight = Math.max(2, width * drawingScale)
  const drawingY = (drawingAreaHeight - drawingHeight) / 2
  const dimensionY = compact ? 91 : 101
  const dimensionTextY = compact ? 108 : 119
  const shortDimension = drawingWidth < (compact ? 52 : 64)
  const dimensionLabelX = shortDimension ? 12 : 12 + drawingWidth / 2
  const dimensionTextAnchor = shortDimension ? 'start' : 'middle'
  const markers = operations.flatMap((operation) =>
    operation.points.map((point, pointIndex) => ({
      operation,
      point,
      pointIndex,
    })),
  )

  return (
    <div className="schematic-face">
      <span className="schematic-face-label">
        {operations.length > 0
          ? [...new Set(operations.map((operation) => operation.face))].join(
              ' + ',
            )
          : `${lengthAxis}${widthAxis} stock face`}
      </span>
      <svg
        viewBox={`0 0 ${diagramWidth} ${diagramHeight}`}
        role={primary ? 'img' : 'presentation'}
        aria-label={
          primary ? `${part.description}, quantity ${part.quantity}` : undefined
        }
      >
        <rect
          x="12"
          y={drawingY}
          width={drawingWidth}
          height={drawingHeight}
          rx="2"
          fill={rgbaCss(part.colorRgba)}
          fillOpacity="0.72"
          stroke="currentColor"
          strokeWidth="1"
        />
        {markers.map(({ operation, point, pointIndex }) => {
          const x = 12 + point.positionMm[axisIndex(lengthAxis)] * drawingScale
          const y =
            drawingY +
            drawingHeight -
            point.positionMm[axisIndex(widthAxis)] * drawingScale
          return (
            <g
              className={`drill-marker is-${operation.kind}`}
              key={`${operation.operationId}-${pointIndex}`}
              transform={`translate(${x} ${y})`}
            >
              <circle className="connection-dot" r="2" />
            </g>
          )
        })}
        <g className="schematic-dimension">
          <line
            x1="12"
            y1={dimensionY}
            x2={12 + drawingWidth}
            y2={dimensionY}
          />
          <line x1="12" y1={dimensionY - 4} x2="12" y2={dimensionY + 4} />
          <line
            x1={12 + drawingWidth}
            y1={dimensionY - 4}
            x2={12 + drawingWidth}
            y2={dimensionY + 4}
          />
          <text
            className="schematic-dimension-label"
            x={dimensionLabelX}
            y={dimensionTextY}
            textAnchor={dimensionTextAnchor}
          >
            {formatDimension(length)} mm ({lengthAxis.toUpperCase()})
          </text>
        </g>
      </svg>
    </div>
  )
}

export function PartSchematic({
  part,
  scale,
  index,
  active,
  onHover,
  onOpen,
  drillOperations,
}: {
  part: ManifestPart
  scale: number
  index: number
  active: boolean
  onHover: (partNumber: string | null) => void
  onOpen: (partNumber: string) => void
  drillOperations: ManifestDrillOperation[]
}) {
  const { length, width, thickness } = stockFace(part)
  const faceGroups = groupDrillOperations(part, drillOperations)

  return (
    <button
      className={`schematic-piece ${active ? 'is-active' : ''}`}
      type="button"
      aria-label={`${part.description}, quantity ${part.quantity}`}
      aria-pressed={active}
      onPointerEnter={() => onHover(part.partNumber)}
      onPointerLeave={() => onHover(null)}
      onFocus={() => onHover(part.partNumber)}
      onBlur={() => onHover(null)}
      onClick={() => onOpen(part.partNumber)}
    >
      <div className="schematic-piece-heading">
        <div>
          <span>
            {String(index + 1).padStart(2, '0')} · {part.partNumber}
          </span>
          <strong>{part.description}</strong>
        </div>
        <b>×{part.quantity}</b>
      </div>
      <div className="schematic-face-grid">
        {faceGroups.map(([key, operations], faceIndex) => (
          <FaceDiagram
            key={key}
            part={part}
            operations={operations}
            axes={key.split('') as [AxisName, AxisName]}
            scale={scale}
            primary={faceIndex === 0}
            compact={faceGroups.length > 1}
          />
        ))}
      </div>
      <div className="drill-operation-list">
        {drillOperations.map((operation) => (
          <div
            className={`drill-operation is-${operation.kind}`}
            key={operation.operationId}
          >
            <span>
              <i aria-hidden="true" />
              {operation.label}
            </span>
            <strong>
              {operationSpecification(operation)} · {operation.pointsPerPart}
              /part
            </strong>
            <small>{coordinateSummary(operation)}</small>
          </div>
        ))}
        {drillOperations.length === 0 && (
          <span className="no-drill-operation">No drilling on this part</span>
        )}
      </div>
      <div className="schematic-piece-meta">
        <span>{part.material}</span>
        <span>
          {formatDimension(length)} × {formatDimension(width)} ×{' '}
          {formatDimension(thickness)} mm
        </span>
      </div>
    </button>
  )
}
