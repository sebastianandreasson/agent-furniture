import { useEffect, useMemo, useState } from 'react'

function readProgress(key: string, validSteps: Set<number>) {
  try {
    const stored = JSON.parse(localStorage.getItem(key) ?? '[]') as unknown
    if (!Array.isArray(stored)) return new Set<number>()
    return new Set(
      stored.filter(
        (value): value is number =>
          typeof value === 'number' && validSteps.has(value),
      ),
    )
  } catch {
    return new Set<number>()
  }
}

export function useAssemblyProgress(
  designId: string,
  revision: string,
  stepNumbers: number[],
) {
  const key = `querycad:assembly-progress:${designId}:${revision}`
  const validSteps = useMemo(() => new Set(stepNumbers), [stepNumbers])
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(() =>
    readProgress(key, validSteps),
  )

  useEffect(() => {
    setCompletedSteps(readProgress(key, validSteps))
  }, [key, validSteps])

  const toggleStep = (stepNumber: number) => {
    setCompletedSteps((current) => {
      const next = new Set(current)
      if (next.has(stepNumber)) next.delete(stepNumber)
      else next.add(stepNumber)
      localStorage.setItem(key, JSON.stringify([...next].sort((a, b) => a - b)))
      return next
    })
  }

  return { completedSteps, toggleStep }
}
