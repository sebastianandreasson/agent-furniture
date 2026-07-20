import type { CatalogDesign } from './types'

export type DesignFamily = {
  id: string
  designs: CatalogDesign[]
}

export function formatFurnitureName(value: string) {
  return value.replaceAll(/[-_]+/g, ' ')
}

export function groupDesignFamilies(designs: CatalogDesign[]): DesignFamily[] {
  const families = new Map<string, CatalogDesign[]>()
  for (const design of designs) {
    const variants = families.get(design.familyId) ?? []
    variants.push(design)
    families.set(design.familyId, variants)
  }
  return [...families].map(([id, variants]) => ({ id, designs: variants }))
}

export function selectFamilyDesign(
  family: DesignFamily,
  currentVariantId: string,
) {
  return (
    family.designs.find(
      (candidate) => candidate.variantId === currentVariantId,
    ) ?? family.designs[0]
  )
}
