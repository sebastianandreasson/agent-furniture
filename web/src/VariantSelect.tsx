import type { CatalogDesign } from './types'
import { formatFurnitureName } from './variants'

export function VariantSelect({
  designs,
  activeDesign,
  onSelectDesign,
  className = '',
}: {
  designs: CatalogDesign[]
  activeDesign: CatalogDesign
  onSelectDesign: (id: string) => void
  className?: string
}) {
  const variants = designs.filter(
    (candidate) => candidate.familyId === activeDesign.familyId,
  )
  if (variants.length < 2) return null

  return (
    <label className={`variant-select ${className}`.trim()}>
      <span>Variant</span>
      <select
        aria-label={`${formatFurnitureName(activeDesign.familyId)} variant`}
        value={activeDesign.id}
        onChange={(event) => onSelectDesign(event.target.value)}
      >
        {variants.map((variant) => (
          <option key={variant.id} value={variant.id}>
            {variant.variantLabel}
          </option>
        ))}
      </select>
    </label>
  )
}
