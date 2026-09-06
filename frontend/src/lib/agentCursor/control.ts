/** Agent control plane: semantic ids only. Coordinates / selectors are rejected. */

export class AgentControlPlaneError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'AgentControlPlaneError'
  }
}

const SEMANTIC_ID = /^[a-z][a-z0-9_-]*(?:\.[a-z0-9_-]+)+$/i

function isSelectorString(value: string): boolean {
  const trimmed = value.trim()
  return (
    trimmed.startsWith('.') ||
    trimmed.startsWith('#') ||
    trimmed.startsWith('/') ||
    trimmed.startsWith('(') ||
    trimmed.includes('querySelector') ||
    /xpath/i.test(trimmed) ||
    /\[.*=.*\]/.test(trimmed)
  )
}

export function rejectCoordinateControl(input: unknown): void {
  if (input == null) {
    throw new AgentControlPlaneError('semantic id required')
  }
  if (typeof input === 'object') {
    const rec = input as Record<string, unknown>
    if ('x' in rec || 'y' in rec) {
      throw new AgentControlPlaneError('coordinate control is not allowed')
    }
    if ('selector' in rec || 'xpath' in rec || 'querySelector' in rec || 'css' in rec) {
      throw new AgentControlPlaneError('selector control is not allowed')
    }
  }
  if (typeof input === 'string' && isSelectorString(input)) {
    throw new AgentControlPlaneError('selector control is not allowed')
  }
}

export function parseSemanticId(input: unknown): string {
  rejectCoordinateControl(input)
  if (typeof input !== 'string' || !SEMANTIC_ID.test(input.trim())) {
    throw new AgentControlPlaneError('expected a semantic target id')
  }
  return input.trim()
}
