import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import type { AxisName, ManifestDrillOperation, ManifestPart } from '../types'
import { groupDrillOperations } from './drilling'
import { formatDimension } from './inventory'
import { PartDetailFace } from './PartDetailFace'
import { stockFace } from './schematic'

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
  const dialogRef = useRef<HTMLElement>(null)
  const previouslyFocused = useRef<HTMLElement | null>(
    document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null,
  )

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    const restoreFocusTo = previouslyFocused.current
    const appShell = document.querySelector<HTMLElement>('.app-shell')
    const previousAriaHidden = appShell?.getAttribute('aria-hidden')
    const wasInert = appShell?.hasAttribute('inert') ?? false
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
        return
      }
      if (event.key !== 'Tab' || !dialogRef.current) return

      const focusable = Array.from(
        dialogRef.current.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ),
      ).filter((element) => !element.hasAttribute('hidden'))
      if (focusable.length === 0) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
    document.body.style.overflow = 'hidden'
    appShell?.setAttribute('inert', '')
    appShell?.setAttribute('aria-hidden', 'true')
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', onKeyDown)
      if (!wasInert) appShell?.removeAttribute('inert')
      if (previousAriaHidden == null) appShell?.removeAttribute('aria-hidden')
      else appShell?.setAttribute('aria-hidden', previousAriaHidden)
      restoreFocusTo?.focus()
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
        ref={dialogRef}
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
        <div className="part-detail-content">
          {faces.map(([key, operations]) => (
            <PartDetailFace
              key={key}
              part={part}
              operations={operations}
              axes={key.split('') as [AxisName, AxisName]}
            />
          ))}
        </div>
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
