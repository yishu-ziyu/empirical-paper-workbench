import type { ResearchLab } from '../workspace'
import { parseSemanticId } from './control'
import { PREVIEW_EXPERIENCE } from './scripts'

function choiceValue(
  choices: Array<{ dimension?: string; value?: string }> | undefined,
  dimension: string,
): string | undefined {
  return choices?.find((item) => item.dimension === dimension)?.value
}

export function resolvePreviewSpecId(command: unknown, research: ResearchLab | null | undefined): string | null {
  const id = parseSemanticId(command)
  if (id !== PREVIEW_EXPERIENCE) return null
  const defs = research?.specification_space?.definitions ?? []
  const linear = defs.find((def) => {
    if (!def.admissible) return false
    const choices = def.choices ?? []
    return (
      choiceValue(choices, 'experience') === 'linear' &&
      choiceValue(choices, 'estimator') === 'ols'
    )
  })
  return linear?.id ?? 'ols_linear_exper'
}

export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}
