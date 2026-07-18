import type { AxisName, ManifestDrillOperation, ManifestPart } from '../types'
import { formatDimension, rgbaCss } from './inventory'
import { axisIndex, stockFace } from './schematic'

function groupDrillOperations(
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

function operationSpecification(operation: ManifestDrillOperation) {
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

function coordinateSummary(operation: ManifestDrillOperation) {
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

function FaceDiagram({
  part,
  operations,
  axes,
  scale,
  primary,
}: {
  part: ManifestPart
  operations: ManifestDrillOperation[]
  axes: [AxisName, AxisName]
  scale: number
  primary: boolean
}) {
  const [lengthAxis, widthAxis] = axes
  const length = part.sizeMm[axisIndex(lengthAxis)]
  const width = part.sizeMm[axisIndex(widthAxis)]
  const drawingWidth = Math.max(2, length * scale)
  const drawingHeight = Math.max(2, width * scale)
  const drawingY = (96 - drawingHeight) / 2
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
        viewBox="0 0 360 116"
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
        {markers.map(({ operation, point, pointIndex }, markerIndex) => {
          const x = 12 + point.positionMm[axisIndex(lengthAxis)] * scale
          const y =
            drawingY +
            drawingHeight -
            point.positionMm[axisIndex(widthAxis)] * scale
          return (
            <g
              className={`drill-marker is-${operation.kind}`}
              key={`${operation.operationId}-${pointIndex}`}
              transform={`translate(${x} ${y})`}
            >
              <circle r={operation.kind === 'pilot' ? 3.2 : 5.1} />
              <line x1="-7" y1="0" x2="7" y2="0" />
              <line x1="0" y1="-7" x2="0" y2="7" />
              <text x="7" y="-6">
                {markerIndex + 1}
              </text>
            </g>
          )
        })}
        <line
          x1="12"
          y1="104"
          x2={12 + drawingWidth}
          y2="104"
          stroke="currentColor"
          strokeWidth="0.75"
        />
        <line x1="12" y1="100" x2="12" y2="108" stroke="currentColor" />
        <line
          x1={12 + drawingWidth}
          y1="100"
          x2={12 + drawingWidth}
          y2="108"
          stroke="currentColor"
        />
        <text x={12 + drawingWidth / 2} y="114" textAnchor="middle">
          {formatDimension(length)} mm ({lengthAxis.toUpperCase()})
        </text>
        {primary && (
          <text
            className="schematic-quantity"
            x={Math.min(326, 22 + drawingWidth)}
            y={drawingY + drawingHeight / 2 + 5}
          >
            ×{part.quantity}
          </text>
        )}
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
  drillOperations,
}: {
  part: ManifestPart
  scale: number
  index: number
  active: boolean
  onHover: (partNumber: string | null) => void
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
      {faceGroups.map(([key, operations], faceIndex) => (
        <FaceDiagram
          key={key}
          part={part}
          operations={operations}
          axes={key.split('') as [AxisName, AxisName]}
          scale={scale}
          primary={faceIndex === 0}
        />
      ))}
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
