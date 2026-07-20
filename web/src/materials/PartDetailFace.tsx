import type { AxisName, ManifestDrillOperation, ManifestPart } from '../types'
import {
  consecutiveHoleSpacings,
  operationSpecification,
  pointMeasurements,
} from './drilling'
import { formatDimension } from './inventory'
import { PartDetailDiagram } from './PartDetailDiagram'

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

export function PartDetailFace({
  part,
  operations,
  axes,
}: {
  part: ManifestPart
  operations: ManifestDrillOperation[]
  axes: [AxisName, AxisName]
}) {
  let markerOffset = 0
  const entries = operations.map((operation) => {
    const entry = { operation, markerOffset }
    markerOffset += operation.points.length
    return entry
  })
  const faceNames =
    operations.length > 0
      ? [...new Set(operations.map((operation) => operation.face))].join(' + ')
      : `${axes[0]}${axes[1]} stock face`

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
      <PartDetailDiagram part={part} operations={operations} axes={axes} />
      {entries.length > 0 && (
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
            {entries.map(({ operation, markerOffset: offset }) => {
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
        {entries.map(({ operation, markerOffset: offset }) => (
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
