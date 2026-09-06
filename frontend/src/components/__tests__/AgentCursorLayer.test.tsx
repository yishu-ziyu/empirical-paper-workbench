import { describe, expect, test, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import type { Ref } from 'react'
import AgentCursorRoot from '../AgentCursorLayer'
import { useSemanticTarget } from '../../lib/agentCursor/useSemanticTarget'
import { semanticTargetRegistry } from '../../lib/agentCursor/registry'
import { useAgentCursor } from '../../lib/agentCursor/context'
import { travelDurationMs } from '../../lib/agentCursor/player'

function Target({ id }: { id: string }) {
  const ref = useSemanticTarget(id)
  return (
    <div ref={ref as Ref<HTMLDivElement>} data-semantic-id={id} data-testid={id}>
      {id}
    </div>
  )
}

function Controls() {
  const { playShowMe, cancel, replay, presentation } = useAgentCursor()
  return (
    <div>
      <button type="button" data-testid="agent-cursor-show-me" data-agent-cursor-control="" onClick={playShowMe}>
        Show me
      </button>
      <button type="button" data-testid="agent-cursor-cancel" data-agent-cursor-control="" onClick={cancel}>
        Cancel
      </button>
      <button type="button" data-testid="agent-cursor-replay" data-agent-cursor-control="" onClick={replay}>
        Replay
      </button>
      <span data-testid="cursor-status">{presentation.status}</span>
    </div>
  )
}

describe('AgentCursorLayer', () => {
  beforeEach(() => {
    semanticTargetRegistry.clear()
  })
  afterEach(() => {
    semanticTargetRegistry.clear()
  })

  test('mounts overlay with pointer-events none and Agent identity', () => {
    render(
      <AgentCursorRoot
        workbenchTab="evidence"
        research={null}
        onOpenEvidence={vi.fn()}
        onRunPreview={vi.fn(async () => undefined)}
      >
        <Target id="evidence.spec.ols" />
        <Controls />
      </AgentCursorRoot>,
    )
    const layer = screen.getByTestId('agent-cursor-layer')
    expect(layer).toHaveClass('pointer-events-none')
    expect(screen.getByTestId('agent-cursor')).toHaveClass('pointer-events-none')
    expect(screen.getByTestId('agent-cursor')).toHaveTextContent('Agent')
  })

  test('Show me / cancel / replay are available', () => {
    render(
      <AgentCursorRoot
        workbenchTab="evidence"
        research={null}
        onOpenEvidence={vi.fn()}
        onRunPreview={vi.fn(async () => undefined)}
      >
        <Target id="evidence.spec.ols" />
        <Target id="evidence.spec.iv" />
        <Target id="evidence.choice.estimator" />
        <Controls />
      </AgentCursorRoot>,
    )
    fireEvent.click(screen.getByTestId('agent-cursor-show-me'))
    fireEvent.click(screen.getByTestId('agent-cursor-cancel'))
    expect(screen.getByTestId('cursor-status')).toHaveTextContent('idle')
    fireEvent.click(screen.getByTestId('agent-cursor-replay'))
  })

  test('reduced-motion attribute path exists', () => {
    const restore = window.matchMedia
    window.matchMedia = ((query: string) =>
      ({
        matches: query.includes('prefers-reduced-motion'),
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      }) as unknown as MediaQueryList)
    render(
      <AgentCursorRoot
        workbenchTab="evidence"
        research={null}
        onOpenEvidence={vi.fn()}
        onRunPreview={vi.fn(async () => undefined)}
      >
        <Controls />
      </AgentCursorRoot>,
    )
    expect(screen.getByTestId('agent-cursor')).toHaveAttribute('data-reduced-motion', 'true')
    expect(travelDurationMs(true)).toBe(0)
    window.matchMedia = restore
  })
})
