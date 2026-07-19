import type { CatalogDesign } from '../types'
import { formatDimension } from './inventory'
import type { AssemblyStep } from './materialsViewModel'

export function AssemblyGuide({
  design,
  steps,
  activeStepNumber,
  completedSteps,
  onSelectStep,
  onToggleStep,
  onHoverPart,
}: {
  design: CatalogDesign
  steps: AssemblyStep[]
  activeStepNumber: number | null
  completedSteps: Set<number>
  onSelectStep: (stepNumber: number) => void
  onToggleStep: (stepNumber: number) => void
  onHoverPart: (partNumber: string | null) => void
}) {
  return (
    <section
      id="materials-panel-assembly"
      className="mw-paper-panel mw-assembly-guide"
      role="tabpanel"
      aria-labelledby="materials-tab-assembly"
    >
      <header className="mw-panel-heading">
        <div>
          <p className="eyebrow">Assembly sequence · {design.name}</p>
          <h3>
            Build it in {steps.length} {steps.length === 1 ? 'step' : 'steps'}
          </h3>
          <p>
            Select a step to highlight every involved part, then tick it off as
            the assembly progresses.
          </p>
        </div>
        <span>
          {completedSteps.size} of {steps.length} complete
        </span>
      </header>

      <div className="mw-step-list">
        {steps.map((step) => {
          const active = step.number === activeStepNumber
          const complete = completedSteps.has(step.number)
          return (
            <article
              key={step.number}
              className={`mw-step-card ${active ? 'is-active' : ''} ${complete ? 'is-complete' : ''}`}
              onPointerEnter={() =>
                onHoverPart(step.joints[0]?.sourcePartNumber ?? null)
              }
              onPointerLeave={() => onHoverPart(null)}
            >
              <button
                type="button"
                className="mw-step-main"
                aria-pressed={active}
                onClick={() => onSelectStep(step.number)}
              >
                <span className="mw-step-number">
                  {String(step.number).padStart(2, '0')}
                </span>
                <span className="mw-step-content">
                  <strong>{step.title}</strong>
                  <span className="mw-step-routes">
                    {step.joints
                      .map(
                        (joint) =>
                          `${joint.sourcePartNumber} → ${joint.targetPartNumber}`,
                      )
                      .join(' · ')}
                  </span>
                  <span className="mw-step-chips">
                    {step.fasteners.map(({ code, quantity, fastener }) => (
                      <span className="is-fastener" key={code}>
                        <i aria-hidden="true" />
                        {code} ×{quantity}
                        {fastener &&
                          ` · ${formatDimension(fastener.lengthMm)} mm`}
                      </span>
                    ))}
                    <span>{step.drillSummary}</span>
                    {step.parts.map((part) => (
                      <span key={part.partNumber}>
                        {part.partNumber} ×{part.quantity}
                      </span>
                    ))}
                    {step.externalTargets.map((target) => (
                      <span key={target.code} title={target.notes}>
                        Existing: {target.description}
                      </span>
                    ))}
                  </span>
                  <small>{step.instruction}</small>
                </span>
              </button>
              <label className="mw-step-done">
                <input
                  type="checkbox"
                  aria-label={`Mark step ${step.number}: ${step.title} as complete`}
                  checked={complete}
                  onChange={() => onToggleStep(step.number)}
                />
                Done
              </label>
            </article>
          )
        })}
      </div>
      <p className="mw-panel-footnote">
        Prototype joinery schedule · verify fasteners against stocked hardware
        and test every jig setting on matching offcuts.
      </p>
    </section>
  )
}
